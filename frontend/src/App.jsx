import { useEffect, useState } from "react";
import "./index.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [summary, setSummary] = useState(null);
  const [meters, setMeters] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [selectedMeter, setSelectedMeter] = useState(null);
  const [latestReading, setLatestReading] = useState(null);
  const [streamHistory, setStreamHistory] = useState([]);
  const [streamStats, setStreamStats] = useState(null);
  const [historyFilter, setHistoryFilter] = useState("all");

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [
          summaryResponse,
          metersResponse,
          anomaliesResponse,
        ] = await Promise.all([
          fetch(`${API_URL}/summary`),
          fetch(`${API_URL}/meters`),
          fetch(`${API_URL}/anomalies`),
        ]);

        const summaryData = await summaryResponse.json();
        const metersData = await metersResponse.json();
        const anomaliesData = await anomaliesResponse.json();

        setSummary(summaryData);
        setMeters(metersData.meters);
        setAnomalies(anomaliesData.anomalies);
      } catch (error) {
        console.error("Dashboard loading failed:", error);
      }
    }

    loadDashboard();
  }, []);

  useEffect(() => {
    async function loadLatestReading() {
      try {
        const response = await fetch(
          `${API_URL}/stream/latest`
        );

        if (!response.ok) return;

        const data = await response.json();
        setLatestReading(data);
      } catch (error) {
        console.log("Stream unavailable");
      }
    }

    loadLatestReading();

    const interval = setInterval(
      loadLatestReading,
      1000
    );

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    async function loadStreamHistory() {
      try {
        const response = await fetch(
          `${API_URL}/stream/history`
        );

        if (!response.ok) return;

        const data = await response.json();
        setStreamHistory(data.history);
      } catch (error) {
        console.log("Stream history unavailable");
      }
    }

    loadStreamHistory();

    const interval = setInterval(
      loadStreamHistory,
      1000
    );

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    async function loadStreamStats() {
      try {
        const response = await fetch(
          `${API_URL}/stream/stats`
        );

        if (!response.ok) return;

        const data = await response.json();

        setStreamStats(data);
      } catch (error) {
        console.log("Stream stats unavailable");
      }
    }

    loadStreamStats();

    const interval = setInterval(
      loadStreamStats,
      1000
    );

    return () => clearInterval(interval);
  }, []);

  async function handleMeterClick(meterId) {
    try {
      const response = await fetch(
        `${API_URL}/meters/${meterId}`
      );

      if (!response.ok) return;

      const data = await response.json();
      setSelectedMeter(data);
    } catch (error) {
      console.error("Meter loading failed:", error);
    }
  }

  const liveIsAnomaly =
    latestReading &&
    latestReading.classification !== "normal";

  function getSeverity(classification) {
    if (classification === "normal") {
      return "NORMAL";
    }

    if (
      classification === "theft_tampering" ||
      classification === "meter_fault"
    ) {
      return "CRITICAL";
    }

    return "WARNING";
  }

  const filteredHistory = streamHistory.filter(
    (reading) => {
      if (historyFilter === "all") {
        return true;
      }

      if (historyFilter === "normal") {
        return reading.classification === "normal";
      }

      if (historyFilter === "theft") {
        return (
          reading.classification ===
          "theft_tampering"
        );
      }

      if (historyFilter === "fault") {
        return (
          reading.classification ===
          "meter_fault"
        );
      }

      return true;
    }
  );

  const anomalyRate =
    streamStats &&
    streamStats.total_readings > 0
      ? (
          (streamStats.anomalies /
            streamStats.total_readings) *
          100
        ).toFixed(1)
      : "0.0";

  return (
    <div className="app">

      <header>
        <h1>Smart Meter Anomaly Detector</h1>

        <p>
          Real-time electricity monitoring and anomaly detection
        </p>
      </header>

      {summary && (
        <section className="stats-grid">

          <div className="card stat-card">
            <span>Total Meters</span>
            <strong>
              {summary.total_meters}
            </strong>
          </div>

          <div className="card stat-card">
            <span>Total Anomalies</span>
            <strong>
              {summary.total_anomalies}
            </strong>
          </div>

          <div className="card stat-card">
            <span>Theft / Tampering</span>
            <strong>
              {summary.theft_tampering}
            </strong>
          </div>

          <div className="card stat-card">
            <span>Meter Faults</span>
            <strong>
              {summary.meter_faults}
            </strong>
          </div>

        </section>
      )}

      {streamStats && (
        <section className="card">

          <div className="section-header">

            <div>
              <h2>Stream Statistics</h2>

              <p>
                Real-time statistics from the meter stream
              </p>
            </div>

            <span className="history-count">
              {streamStats.total_readings} readings
            </span>

          </div>

          <div className="stats-grid">

            <div className="card stat-card">
              <span>Normal</span>

              <strong>
                {streamStats.normal}
              </strong>
            </div>

            <div className="card stat-card">
              <span>Anomalies</span>

              <strong>
                {streamStats.anomalies}
              </strong>
            </div>

            <div className="card stat-card">
              <span>Theft / Tampering</span>

              <strong>
                {streamStats.theft_tampering}
              </strong>
            </div>

            <div className="card stat-card">
              <span>Meter Faults</span>

              <strong>
                {streamStats.meter_faults}
              </strong>
            </div>

            <div className="card stat-card">
              <span>Anomaly Rate</span>

              <strong>
                {anomalyRate}%
              </strong>
            </div>

          </div>

        </section>
      )}

      {latestReading && (
        <section
          className={
            liveIsAnomaly
              ? "card live-card alert-card"
              : "card live-card"
          }
        >

          <div className="live-header">

            <div>
              <h2>
                {liveIsAnomaly
                  ? "🚨 Anomaly Detected"
                  : "Live Reading"}
              </h2>

              <p>
                Latest reading received from stream
              </p>
            </div>

            <span className="live-indicator">
              ● LIVE
            </span>

          </div>

          <div className="live-reading">

            <div>
              <strong>
                {latestReading.meter_id}
              </strong>

              <span>
                {new Date(
                  latestReading.timestamp
                ).toLocaleString()}
              </span>
            </div>

            <div>
              <strong>
                {latestReading.consumption} kW
              </strong>

              <span
                className={`severity-${getSeverity(
                  latestReading.classification
                ).toLowerCase()}`}
              >
                {getSeverity(
                  latestReading.classification
                )}
              </span>
            </div>

            <div>
              <strong>
                {latestReading.confidence_score}%
              </strong>

              <span>
                Detector Confidence
              </span>
            </div>

          </div>

        </section>
      )}

      <section className="card">

        <h2>Smart Meters</h2>

        <div className="meter-grid">

          {meters.map((meter) => (
            <button
              key={meter}
              className={
                selectedMeter?.meter_id === meter
                  ? "meter-card selected"
                  : "meter-card"
              }
              onClick={() =>
                handleMeterClick(meter)
              }
            >
              <strong>{meter}</strong>

              <span>
                Click to view details
              </span>
            </button>
          ))}

        </div>

      </section>

      {selectedMeter && (
        <section className="card">

          <h2>
            Meter Details: {selectedMeter.meter_id}
          </h2>

          <div className="meter-detail">

            <div>
              <span>Total Readings</span>

              <strong>
                {selectedMeter.total_readings}
              </strong>
            </div>

            <div>
              <span>Anomalies</span>

              <strong>
                {selectedMeter.anomaly_count}
              </strong>
            </div>

          </div>

          <h3>Detected Anomalies</h3>

          {selectedMeter.anomalies.length === 0 ? (
            <p>No anomalies detected.</p>
          ) : (
            <div className="table-container">

              <table>

                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Consumption</th>
                    <th>Classification</th>
                    <th>Confidence</th>
                  </tr>
                </thead>

                <tbody>

                  {selectedMeter.anomalies.map(
                    (anomaly, index) => (
                      <tr key={index}>

                        <td>
                          {anomaly.timestamp}
                        </td>

                        <td>
                          {anomaly.consumption} kW
                        </td>

                        <td>
                          {anomaly.classification}
                        </td>

                        <td>
                          {anomaly.confidence_score}%
                        </td>

                      </tr>
                    )
                  )}

                </tbody>

              </table>

            </div>
          )}

        </section>
      )}

      <section className="card">

        <div className="section-header">

          <div>
            <h2>Live Stream History</h2>

            <p>
              Recent readings received from the stream
            </p>
          </div>

          <span className="history-count">
            {filteredHistory.length} readings
          </span>

        </div>

        <div className="history-filters">

          <button
            className={
              historyFilter === "all"
                ? "filter-button active"
                : "filter-button"
            }
            onClick={() =>
              setHistoryFilter("all")
            }
          >
            All
          </button>

          <button
            className={
              historyFilter === "normal"
                ? "filter-button active"
                : "filter-button"
            }
            onClick={() =>
              setHistoryFilter("normal")
            }
          >
            Normal
          </button>

          <button
            className={
              historyFilter === "theft"
                ? "filter-button active"
                : "filter-button"
            }
            onClick={() =>
              setHistoryFilter("theft")
            }
          >
            Theft / Tampering
          </button>

          <button
            className={
              historyFilter === "fault"
                ? "filter-button active"
                : "filter-button"
            }
            onClick={() =>
              setHistoryFilter("fault")
            }
          >
            Meter Fault
          </button>

        </div>

        {filteredHistory.length === 0 ? (
          <p>No readings found.</p>
        ) : (
          <div className="table-container">

            <table>

              <thead>
                <tr>
                  <th>Meter</th>
                  <th>Timestamp</th>
                  <th>Consumption</th>
                  <th>Severity</th>
                  <th>Detector Confidence</th>
                </tr>
              </thead>

              <tbody>

                {[...filteredHistory]
                  .reverse()
                  .map((reading, index) => (
                    <tr key={index}>

                      <td>
                        {reading.meter_id}
                      </td>

                      <td>
                        {new Date(
                          reading.timestamp
                        ).toLocaleString()}
                      </td>

                      <td>
                        {reading.consumption} kW
                      </td>

                      <td>
                        <span
                          className={`severity-${getSeverity(
                            reading.classification
                          ).toLowerCase()}`}
                        >
                          {getSeverity(
                            reading.classification
                          )}
                        </span>
                      </td>

                      <td>
                        {reading.confidence_score}%
                      </td>

                    </tr>
                  ))}

              </tbody>

            </table>

          </div>
        )}

      </section>

      <section className="card">

        <h2>Recent Anomalies</h2>

        <div className="table-container">

          <table>

            <thead>
              <tr>
                <th>Meter</th>
                <th>Timestamp</th>
                <th>Consumption</th>
                <th>Classification</th>
                <th>Confidence</th>
              </tr>
            </thead>

            <tbody>

              {anomalies.slice(0, 20).map(
                (anomaly, index) => (
                  <tr key={index}>

                    <td>
                      {anomaly.meter_id}
                    </td>

                    <td>
                      {anomaly.timestamp}
                    </td>

                    <td>
                      {anomaly.consumption} kW
                    </td>

                    <td>
                      {anomaly.classification}
                    </td>

                    <td>
                      {anomaly.confidence_score}%
                    </td>

                  </tr>
                )
              )}

            </tbody>

          </table>

        </div>

      </section>

    </div>
  );
}

export default App;