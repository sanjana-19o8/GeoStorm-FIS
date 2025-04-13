from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from fuzzy_engine import predict_impact

app = Flask(__name__)
CORS(app)

localities = pd.read_csv('vizag_localities.csv')

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.json
    lat = float(data['lat'])
    lon = float(data['lon'])
    output = predict_impact(lat, lon, localities)
    return jsonify(output)

if __name__ == '__main__':
    app.run(debug=True)
