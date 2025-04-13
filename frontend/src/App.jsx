import { useState } from 'react';
import axios from 'axios';
import LocalityTable from './components/LocalityTable';

function App() {
  const [lat, setLat] = useState('');
  const [lon, setLon] = useState('');
  const [results, setResults] = useState([]);

  const handlePredict = async () => {
    try {
      const res = await axios.post('http://localhost:5000/api/predict', {
        lat, lon, severity
      });
      setResults(res.data);
    } catch (err) {
      console.error('Prediction error', err);
    }
  };

  return (
    <div style={{ padding: '2rem' }}>
      <h2>Vizag Cyclone Impact Predictor</h2>
      <div>
        <input type="number" step="0.0001" placeholder="Cyclone Lat" value={lat} onChange={e => setLat(e.target.value)} />
        <br/>

        <input type="number" step="0.0001" placeholder="Cyclone Lon" value={lon} onChange={e => setLon(e.target.value)} />
        {/* <input type="range" min="0" max="10" step="0.1" value={severity} onChange={e => setSeverity(e.target.value)} /> */}
        <br/>

        <button onClick={handlePredict}>Predict</button>
      </div>
      <LocalityTable data={results} />
    </div>
  );
}

export default App;
