const LocalityTable = ({ data }) => {
    if (!data.length) return null;
  
    return (
      <table border="1" style={{ marginTop: '1rem', width: '100%' }}>
        <thead>
          <tr>
            <th>Locality</th>
            <th>Predicted Impact</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item, idx) => (
            <tr key={idx}>
              <td>{item.name}</td>
              <td>{item.impact.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    );
  };
  
  export default LocalityTable;
  