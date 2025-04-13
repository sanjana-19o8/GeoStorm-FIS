# -*- coding: utf-8 -*-
"""
Fuzzy Model for Cyclone Effect Prediction
Automatically processes input data and generates effect predictions.
"""

import numpy as np
import pandas as pd
import skfuzzy as fuzzfrom
from skfuzzy import control as ctrl
import folium
from folium.plugins import HeatMap
import branca.colormap as cm
from math import radians, cos, sin, asin, sqrt
import argparse
import os
from datetime import datetime

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Process cyclone data and generate effect predictions.')
parser.add_argument('--cyclone-lat', type=float, help='Cyclone latitude')
parser.add_argument('--cyclone-lon', type=float, help='Cyclone longitude')
parser.add_argument('--localities-file', type=str, default='localities_with_elevation.csv', help='Path to localities CSV file')
parser.add_argument('--cyclone-data-file', type=str, default='cyclone_data.csv', help='Path to cyclone data CSV file')
parser.add_argument('--output-dir', type=str, default='output', help='Output directory for results')
args = parser.parse_args()

# Create output directory if it doesn't exist
os.makedirs(args.output_dir, exist_ok=True)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2*asin(sqrt(a))
    return R * c

def calculate_bearing(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    delta_lon = lon2 - lon1
    x = sin(delta_lon) * cos(lat2)
    y = cos(lat1)*sin(lat2) - sin(lat1)*cos(lat2)*cos(delta_lon)
    initial_bearing = math.atan2(x, y)
    bearing = math.degrees(initial_bearing)
    return (bearing + 360) % 360

def elevation_membership(elev):
    if elev <= 10:
        return (1.0, 0.0, 0.0)
    elif elev <= 40:
        low = (40 - elev) / 30
        med = (elev - 10) / 30
        return (low, med, 0.0)
    elif elev <= 70:
        med = (70 - elev) / 30
        high = (elev - 40) / 30
        return (0.0, med, high)
    else:
        return (0.0, 0.0, 1.0)

def directional_membership(bearing):
    if bearing <= 30 or bearing >= 330:
        return (1.0, 0.0, 0.0)
    elif bearing <= 60:
        shield = (60 - bearing) / 30
        moderate = (bearing - 30) / 30
        return (shield, moderate, 0.0)
    elif bearing <= 120:
        moderate = (120 - bearing) / 60
        exposed = (bearing - 60) / 60
        return (0.0, moderate, exposed)
    elif bearing <= 240:
        return (0.0, 0.0, 1.0)
    elif bearing <= 300:
        exposed = (300 - bearing) / 60
        moderate = (bearing - 240) / 60
        return (0.0, moderate, exposed)
    elif bearing <= 330:
        moderate = (330 - bearing) / 30
        shield = (bearing - 300) / 30
        return (shield, moderate, 0.0)

def combined_shielding_score(elev, bearing, w_elev=0.4, w_dir=0.6):
    elev_membership = elevation_membership(elev)
    dir_membership = directional_membership(bearing)
    combined = tuple(round(w_elev * e + w_dir * d, 2) for e, d in zip(elev_membership, dir_membership))
    return {
        "Low Shielding": combined[0],
        "Medium Shielding": combined[1],
        "High Shielding": combined[2]
    }

def inference_engine(prox_val, sev_val, shielding_tuple):
    x_proximity = np.linspace(0, 30, 100)
    proximity = ctrl.Antecedent(x_proximity, 'proximity')
    proximity["low"] = fuzz.trimf(x_proximity, [0, 0, 10])
    proximity["medium"] = fuzz.trimf(x_proximity, [5, 15, 25])
    proximity["high"] = fuzz.trimf(x_proximity, [20, 30, 30])

    x_severity = np.arange(1, 3.1, 0.01)
    severity = ctrl.Antecedent(x_severity, 'severity')
    severity['low'] = fuzz.trimf(x_severity, [1.0, 1.0, 2.0])
    severity['medium'] = fuzz.trimf(x_severity, [1.5, 2.0, 2.5])
    severity['high'] = fuzz.trimf(x_severity, [2.0, 3.0, 3.0])

    x_shielding = np.arange(0, 1.01, 0.01)
    shielding = ctrl.Antecedent(x_shielding, 'shielding')
    shielding['low'] = fuzz.trimf(x_shielding, [0, 0, 0.34])
    shielding['medium'] = fuzz.trimf(x_shielding, [0.33, 0.5, 0.67])
    shielding['high'] = fuzz.trimf(x_shielding, [0.66, 1, 1])

    effect = ctrl.Consequent(np.arange(0, 101, 1), 'effect')
    effect['low'] = fuzz.trimf(effect.universe, [0, 0, 50])
    effect['medium'] = fuzz.trimf(effect.universe, [25, 50, 75])
    effect['high'] = fuzz.trimf(effect.universe, [50, 100, 100])

    rules = [
        ctrl.Rule(proximity['high'] & severity['high'] & shielding['low'], effect['high']),
        ctrl.Rule(severity['low'] & shielding['high'], effect['low']),
        ctrl.Rule(severity['high'] & (proximity['medium'] | proximity['high']), effect['high']),
        ctrl.Rule(severity['medium'] & proximity['medium'], effect['medium']),
        ctrl.Rule(proximity['low'] | severity['low'] | shielding['high'], effect['low'])
    ]

    effect_ctrl = ctrl.ControlSystem(rules)
    effect_sim = ctrl.ControlSystemSimulation(effect_ctrl)

    effect_sim.input['proximity'] = prox_val
    effect_sim.input['severity'] = sev_val
    effect_sim.input['shielding'] = shielding_tuple[0]  # Using low shielding for simplicity

    effect_sim.compute()
    return effect_sim.output['effect']

def run_fuzzy_engine():
    # Load localities data
    localities_df = pd.read_csv(args.localities_file)

    # Load cyclone data
    cyclone_df = pd.read_csv(args.cyclone_data_file)
    cyclone_df = cyclone_df[['Year', 'Max Intensity', 'Initial Date', 'Month', 'Lat', 'Lon']]
    intensity_map = {'D': 1, 'CS': 2, 'SCS': 3}
    cyclone_df['Intensity'] = cyclone_df['Max Intensity'].map(intensity_map)
    cyclone_df['Season'] = np.where(cyclone_df['Month'].isin([3,4,5]), 'Summer',
                                    np.where(cyclone_df['Month'].isin([12,1,2]), 'Winter', 'Monsoon'))
    cyclone_df = pd.get_dummies(cyclone_df, columns=['Season'], prefix='Season')

    # Train model
    features = cyclone_df[['Lat', 'Lon', 'Month', 'Season_Monsoon', 'Season_Summer', 'Season_Winter']]
    target = cyclone_df['Intensity']
    from sklearn.ensemble import RandomForestRegressor
    model = RandomForestRegressor(random_state=42)
    model.fit(features, target)

    # Predict cyclone severity
    month = datetime.now().month
    season_monsoon = 1 if month in [6,7,8,9,10,11] else 0
    season_summer = 1 if month in [3,4,5] else 0
    season_winter = 1 if month in [12,1,2] else 0
    pred_score = model.predict([[args.cyclone_lat, args.cyclone_lon, month, season_monsoon, season_summer, season_winter]])

    # Process localities
    results = []
    for _, loc in localities_df.iterrows():
        prox_val = haversine(loc['lat'], loc['lon'], args.cyclone_lat, args.cyclone_lon)
        elevation = loc['Elevation']
        bearing = calculate_bearing(args.cyclone_lat, args.cyclone_lon, loc["lat"], loc["lon"])
        shielding_tuple = tuple(combined_shielding_score(elevation, bearing).values())

        effect = inference_engine(prox_val, pred_score[0], shielding_tuple)
        results.append({
            "Area": loc["name"],
            "Latitude": loc["lat"],
            "Longitude": loc["lon"],
            "Elevation (m)": elevation,
            "Bearing (°)": round(bearing, 2),
            "Proximity": prox_val,
            "Effect": effect
        })

    # Generate output
    output_df = pd.DataFrame(results)
    output_df.to_csv(os.path.join(args.output_dir, 'effect_results.csv'), index=False)

    # Generate map
    map_center = [args.cyclone_lat, args.cyclone_lon]
    m = folium.Map(location=map_center, zoom_start=12)
    folium.Marker([args.cyclone_lat, args.cyclone_lon], popup='Cyclone Origin', icon=folium.Icon(color='red')).add_to(m)

    min_effect = output_df["Effect"].min()
    max_effect = output_df["Effect"].max()
    colormap = cm.LinearColormap(colors=["green", "yellow", "red"], vmin=min_effect, vmax=max_effect, caption='Cyclone Effect Intensity')
    colormap.add_to(m)

    for _, row in output_df.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=6,
            fill=True,
            fill_color=colormap(row['Effect']),
            color='black',
            popup=f"{row['Area']}<br>Effect: {round(row['Effect'], 2)}",
        ).add_to(m)

    m.save(os.path.join(args.output_dir, 'effect_map.html'))