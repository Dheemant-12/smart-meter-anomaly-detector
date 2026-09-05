import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [meters, setMeters] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDashboard() {
      try {
        const metersResponse = await fetch(`${API_URL}/meters`);
        const metersData = await metersResponse.json();

        const anomaliesResponse = await fetch(
          `${API_URL}/anomalies`
        );
        const anomaliesData = await anomaliesResponse.json();

        setMeters(metersData.meters);
        setAnomalies(anomaliesData.anomalies);
      } catch (err) {
        setError("Could not connect to backend API.");
      }
    }

    loadDashboard();
  }, []);

  return (
    <div className="app">
      <header>
        <h1>Smart Meter Anomaly Detector</h1>
        <p>Real-time electricity monitoring dashboard</p>
      </header>

      {error && <p className="error">{error}</p>}

      <section className="stats">
        <div className="card">
          <h2>{meters.length}</h2>
          <p>Total Meters</p>
        </div>

        <div className="card">
          <h2>{anomalies.length}</h2>
          <p>Detected Anomalies</p>
        </div>
      </section>

      <section className="card">
        <h2>Meter Status</h2>

        <div className="meter-grid">
          {meters.map((meter) => (
            <div className="meter" key={meter}>
              <strong>{meter}</strong>
              <span>Online</span>
            </div>
          ))}
        </div>
      </section>

      <section className="card">
        <h2>Recent Anomalies</h2>

        {anomalies.length === 0 ? (
          <p>No anomalies detected.</p>
        ) : (
          <div className="anomaly-list">
            {anomalies.slice(0, 10).map((anomaly, index) => (
              <div className="anomaly" key={index}>
                <strong>{anomaly.meter_id}</strong>
                <span>{anomaly.classification}</span>
                <span>
                  Confidence: {anomaly.confidence_score}%
                </span>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default App;