# -*- coding: utf-8 -*-
"""01_proximity_distances.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1mpv66PjRJSiYNIQcBZo2uBVX89Nn8OOG
"""

!pip install geopandas osmnx shapely pandas numpy

import geopandas as gpd
import osmnx as ox
from shapely.geometry import Point
import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

location_name = "Visakhapatnam, India"

gdf_localities = ox.features_from_place(location_name, {"place": ["locality", "suburb"]})
gdf_coastline = ox.features_from_place(location_name, {"natural": "coastline"})

gdf_localities = gdf_localities[gdf_localities.geometry.type == 'Point']

locality_points = gdf_localities[["geometry", "name"]].dropna()
locality_points["lat"] = locality_points.geometry.y
locality_points["lon"] = locality_points.geometry.x

coastline_coords = []
for geom in gdf_coastline.geometry:
    if geom.geom_type == "LineString":
        coastline_coords.extend(list(geom.coords))

gdf_localities, locality_points, coastline_coords

def min_distance_to_coast(lat, lon, coastline_coords):
    distances = [haversine(lat, lon, lat_c, lon_c) for lon_c, lat_c in coastline_coords]
    return min(distances)

locality_points["distance_to_coast_km"] = locality_points.apply(
    lambda row: min_distance_to_coast(row["lat"], row["lon"], coastline_coords), axis=1
)

locality_points[["name", "lat", "lon", "distance_to_coast_km"]].to_csv("gis_distances.csv", index=False)