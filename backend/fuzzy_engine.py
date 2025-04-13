from utils import haversine_distance, get_shielding_score
from model.fuzzy_model import run_fuzzy_system

def predict_impact(cyclone_lat, cyclone_lon, severity, df):
    results = []
    for _, row in df.iterrows():
        distance = haversine_distance(cyclone_lat, cyclone_lon, row['lat'], row['lon'])
        shielding = get_shielding_score(cyclone_lat, cyclone_lon, row['lat'], row['lon'])
        impact = run_fuzzy_system(distance, severity, shielding)
        results.append({ 'name': row['name'], 'impact': impact })
    return results
