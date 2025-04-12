# -*- coding: utf-8 -*-
"""03_shielding_score.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1KYtGW_MRrL21HpqwimVaiAT_hhOR_SLT

to calculate fuzzy shielding score
"""

import requests
import pandas as pd

def get_elevation(lat, lon):
    url = f'https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['results'][0]['elevation']
    else:
        return None

df = pd.read_csv("localities.csv")

df["Elevation"] = df.apply(lambda row: get_elevation(row["lat"], row["lon"]), axis=1)
df.to_csv("localities_with_elevation.csv", index=False)

"""Bearing & Directional shielding --based on input cyclone origin


"""

cyclone_lat, cyclone_lon = 11.5, 95 #input

import math

def calculate_bearing(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    delta_lon = lon2 - lon1
    x = math.sin(delta_lon) * math.cos(lat2)
    y = math.cos(lat1)*math.sin(lat2) - (math.sin(lat1)*math.cos(lat2)*math.cos(delta_lon))
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

df2 = pd.read_csv("localities_with_elevation.csv")
results = []
for _, loc in df2.iterrows():
    elevation = loc['Elevation']
    bearing = calculate_bearing(cyclone_lat, cyclone_lon, loc["lat"], loc["lon"])
    shielding_score = combined_shielding_score(elevation, bearing)

    results.append({
        "Area": loc["name"],
        "Latitude": loc["lat"],
        "Longitude": loc["lon"],
        "Elevation (m)": elevation,
        "Bearing (°)": round(bearing, 2),
        "Combined Shielding Score": shielding_score
    })

pd.DataFrame(results)
shielding_df = pd.DataFrame(results)
shielding_df