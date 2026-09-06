import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [summary, setSummary] = useState(null);
  const [meters, setMeters] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [summaryResponse, metersResponse, anomaliesResponse] =
          await Promise.all([
            fetch(`${API_URL}/summary`),
            fetch(`${API_URL}/meters`),
            fetch(`${API_URL}/anomalies`),
          ]);

        if (
          !summaryResponse.ok ||
          !metersResponse.ok ||
          !anomaliesResponse.ok
        ) {
          throw new Error("API request failed");
        }

        const summaryData = await summaryResponse.json();
        const metersData = await metersResponse.json();
        const anomaliesData = await anomaliesResponse.json();

        setSummary(summaryData);
        setMeters(metersData.meters);
        setAnomalies(anomaliesData.anomalies);
      } catch (err) {
        setError("Could not connect to backend API.");
      }
    }

    loadDashboard();
  }, []);

  if (error) {
    return (
      <div className="app">
        <p className="error">{error}</p>
      </div>
    );
  }

  return (
    <div className="app">
      <header>
        <h1>Smart Meter Anomaly Detector</h1>
        <p>
          Real-time electricity monitoring and anomaly detection
        </p>
      </header>

      {summary && (
        <section className="stats">
          <div className="card">
            <h2>{summary.total_meters}</h2>
            <p>Total Meters</p>
          </div>

          <div className="card">
            <h2>{summary.total_anomalies}</h2>
            <p>Total Anomalies</p>
          </div>

          <div className="card">
            <h2>{summary.theft_tampering}</h2>
            <p>Theft / Tampering</p>
          </div>

          <div className="card">
            <h2>{summary.meter_faults}</h2>
            <p>Meter Faults</p>
          </div>
        </section>
      )}

      <section className="card">
        <h2>Meter Status</h2>

        <div className="meter-grid">
          {meters.map((meter) => (
            <div className="meter" key={meter}>
              <strong>{meter}</strong>
              <span>● Online</span>
            </div>
          ))}
        </div>
      </section>

      <section className="card">
        <h2>Recent Anomalies</h2>

        {anomalies.length === 0 ? (
          <p>No anomalies detected.</p>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Meter</th>
                  <th>Time</th>
                  <th>Type</th>
                  <th>Consumption</th>
                  <th>Confidence</th>
                </tr>
              </thead>

              <tbody>
                {anomalies
                  .slice(0, 15)
                  .map((anomaly, index) => (
                    <tr key={index}>
                      <td>{anomaly.meter_id}</td>
                      <td>
                        {new Date(
                          anomaly.timestamp
                        ).toLocaleString()}
                      </td>
                      <td>
                        {anomaly.classification}
                      </td>
                      <td>
                        {Number(
                          anomaly.consumption
                        ).toFixed(3)}
                      </td>
                      <td>
                        {anomaly.confidence_score}%
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

export default App;