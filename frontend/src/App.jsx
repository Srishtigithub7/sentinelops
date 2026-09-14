import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import "./App.css";

const fallbackActions = [
  "Investigate possible database connection leaks.",
  "Identify long-running database queries.",
  "Review the latest user-service deployment.",
  "Verify database capacity before increasing the connection pool.",
  "Monitor connection utilization and API error rates after remediation.",
  "Consider rolling back the latest deployment if the incident began immediately after deployment.",
];

const chartData = [
  {
    time: "14:00",
    errors: 0,
    pool: 32,
    latency: 142,
  },
  {
    time: "14:01",
    errors: 2,
    pool: 48,
    latency: 203,
  },
  {
    time: "14:02",
    errors: 11,
    pool: 94,
    latency: 1450,
  },
  {
    time: "14:03",
    errors: 18,
    pool: 100,
    latency: 4201,
  },
  {
    time: "14:04",
    errors: 24,
    pool: 100,
    latency: 5102,
  },
];

function MetricCard({ label, value, unit, alert }) {
  return (
    <div className={`metric-card ${alert ? "metric-alert" : ""}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      {unit && <small>{unit}</small>}
    </div>
  );
}

function PanelHeader({ eyebrow, title }) {
  return (
    <div className="panel-header">
      <div>
        <span className="eyebrow">{eyebrow}</span>
        <h2>{title}</h2>
      </div>
    </div>
  );
}

function App() {
  const [incident, setIncident] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionStates, setActionStates] = useState({});

  /* =====================================
     INITIAL INVESTIGATION
  ====================================== */

  useEffect(() => {
    let cancelled = false;

    fetch("http://127.0.0.1:8000/api/investigate")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Backend returned an error");
        }

        return response.json();
      })
      .then((data) => {
        if (cancelled) {
          return;
        }

        setIncident(data);
        setLoading(false);
        setError("");
      })
      .catch(() => {
        if (cancelled) {
          return;
        }

        setError(
          "Unable to connect to SentinelOps backend. Make sure FastAPI is running."
        );
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  /* =====================================
     MANUAL REFRESH
  ====================================== */

  const fetchInvestigation = () => {
    setLoading(true);
    setError("");

    fetch("http://127.0.0.1:8000/api/investigate")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Backend returned an error");
        }

        return response.json();
      })
      .then((data) => {
        setIncident(data);
        setLoading(false);
        setError("");
      })
      .catch(() => {
        setError(
          "Unable to connect to SentinelOps backend. Make sure FastAPI is running."
        );
        setLoading(false);
      });
  };

  /* =====================================
     BACKEND DATA
  ====================================== */

  const report = incident?.incident || {};
  const analysis = incident?.analysis || {};

  const actions =
    report.recommended_actions &&
    report.recommended_actions.length > 0
      ? report.recommended_actions
      : fallbackActions;

  const rootCause =
    report.root_cause || "Database connection pool exhaustion";

  const confidence = report.confidence ?? 90;

  const metrics = {
    errors: analysis.errors ?? 15,
    warnings: analysis.warnings ?? 8,
    timeouts: analysis.connection_timeouts ?? 3,
    pool: analysis.max_pool_utilization ?? 100,
    latency: analysis.max_response_time ?? 5102,
  };

  const evidence = report.evidence || [
    "Database connection pool reached 100% utilization.",
    "Database connection pool exhaustion was reported.",
    "3 database connection timeouts were detected.",
  ];

  const hypotheses = report.alternative_hypotheses || [
    {
      hypothesis:
        "API degradation caused by downstream dependency failure",
      score: 25,
    },
    {
      hypothesis:
        "Recent deployment may have triggered the incident",
      score: 20,
    },
  ];

  /* =====================================
     ACTION TOGGLE
  ====================================== */

  const toggleAction = (index) => {
    setActionStates((previous) => ({
      ...previous,
      [index]:
        previous[index] === "COMPLETED"
          ? "PENDING"
          : "COMPLETED",
    }));
  };

  /* =====================================
     LOADING SCREEN
  ====================================== */

  if (loading) {
    return (
      <div className="screen-state">
        <div className="loader-ring" />

        <h2>Running incident investigation...</h2>

        <p>
          Correlating logs, evidence and operational signals.
        </p>
      </div>
    );
  }

  /* =====================================
     ERROR SCREEN
  ====================================== */

  if (error) {
    return (
      <div className="screen-state">
        <div className="error-symbol">!</div>

        <h2>SentinelOps connection failed</h2>

        <p>{error}</p>

        <button
          className="refresh-btn"
          onClick={fetchInvestigation}
        >
          Retry Investigation
        </button>
      </div>
    );
  }

  return (
    <div className="app-shell">

      {/* =====================================
          TOP BAR
      ====================================== */}

      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">S</div>

          <div>
            <h1>SENTINELOPS</h1>
            <p>INCIDENT INTELLIGENCE PLATFORM</p>
          </div>
        </div>

        <div className="system-status">
          <span className="status-dot" />
          SYSTEM OPERATIONAL
        </div>
      </header>

      <main className="dashboard">

        {/* =====================================
            INCIDENT HEADER
        ====================================== */}

        <section className="incident-banner">
          <div>
            <span className="eyebrow">
              ACTIVE PRODUCTION INCIDENT
            </span>

            <h2>{rootCause}</h2>

            <p>
              {report.incident_id || "INC-2026-0914-001"}{" "}
              / API PLATFORM
            </p>
          </div>

          <div className="severity">
            <span>SEVERITY</span>
            <strong>CRITICAL</strong>
          </div>
        </section>

        {/* =====================================
            METRIC CARDS
        ====================================== */}

        <section className="metrics-grid">

          <MetricCard
            label="ERROR EVENTS"
            value={metrics.errors}
          />

          <MetricCard
            label="POOL UTILIZATION"
            value={`${metrics.pool}%`}
            alert
          />

          <MetricCard
            label="MAX LATENCY"
            value={metrics.latency}
            unit="ms"
            alert
          />

          <MetricCard
            label="DB TIMEOUTS"
            value={metrics.timeouts}
            alert
          />

        </section>

        {/* =====================================
            ROOT CAUSE + EVIDENCE
        ====================================== */}

        <section className="main-grid">

          <div className="panel root-cause-panel">

            <PanelHeader
              eyebrow="AI CORRELATED"
              title="ROOT CAUSE ANALYSIS"
            />

            <div className="confidence-layout">

              <div
                className="confidence-ring"
                style={{
                  background: `conic-gradient(
                    #67e8f9 ${confidence * 3.6}deg,
                    #17212d 0deg
                  )`,
                }}
              >
                <div className="confidence-inner">
                  <strong>{confidence}%</strong>
                  <span>CONFIDENCE</span>
                </div>
              </div>

              <div className="root-cause-text">

                <h3>{rootCause}</h3>

                <p>
                  {report.root_cause_explanation ||
                    "The database connection pool reached maximum capacity. As available connections were exhausted, database connection attempts began timing out. This dependency failure propagated to the API gateway, resulting in increased latency and HTTP 503 responses."}
                </p>

              </div>

            </div>
          </div>

          <div className="panel evidence-panel">

            <PanelHeader
              eyebrow="CORRELATED SIGNALS"
              title="EVIDENCE CHAIN"
            />

            <div className="evidence-list">

              {evidence.map((item, index) => (
                <div
                  className="evidence-item"
                  key={index}
                >
                  <span className="check">✓</span>

                  <p>{item}</p>
                </div>
              ))}

            </div>

          </div>

        </section>

        {/* =====================================
            INCIDENT METRICS
        ====================================== */}

        <section className="panel chart-panel">

          <PanelHeader
            eyebrow="LIVE SIGNAL CORRELATION"
            title="INCIDENT METRICS"
          />

          <div className="signal-grid">

            {/* ERROR SIGNAL */}

            <div className="signal-card error-signal">

              <div className="signal-header">

                <div>
                  <span className="signal-label">
                    ERROR EVENTS
                  </span>

                  <strong>{metrics.errors}</strong>
                </div>

                <span className="signal-status critical">
                  CRITICAL
                </span>

              </div>

              <div className="signal-chart">

                <ResponsiveContainer
                  width="100%"
                  height={150}
                >
                  <LineChart
                    data={chartData}
                    margin={{
                      top: 10,
                      right: 8,
                      left: -25,
                      bottom: 0,
                    }}
                  >

                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke="#1e2936"
                    />

                    <XAxis
                      dataKey="time"
                      stroke="#475569"
                      tick={{
                        fill: "#64748b",
                        fontSize: 10,
                      }}
                    />

                    <YAxis
                      stroke="#475569"
                      tick={{
                        fill: "#64748b",
                        fontSize: 10,
                      }}
                    />

                    <Tooltip
                      contentStyle={{
                        background: "#0d141c",
                        border: "1px solid #263444",
                        borderRadius: "8px",
                        color: "#ffffff",
                      }}
                    />

                    <Line
                      type="monotone"
                      dataKey="errors"
                      stroke="#f87171"
                      strokeWidth={3}
                      dot={{ r: 3 }}
                      activeDot={{ r: 5 }}
                      name="Errors"
                    />

                  </LineChart>
                </ResponsiveContainer>

              </div>

              <div className="signal-footer">
                <span>BASELINE</span>
                <strong>0–2 events/min</strong>
              </div>

            </div>

            {/* DATABASE POOL SIGNAL */}

            <div className="signal-card pool-signal">

              <div className="signal-header">

                <div>
                  <span className="signal-label">
                    DB POOL UTILIZATION
                  </span>

                  <strong>{metrics.pool}%</strong>
                </div>

                <span className="signal-status saturated">
                  SATURATED
                </span>

              </div>

              <div className="signal-chart">

                <ResponsiveContainer
                  width="100%"
                  height={150}
                >
                  <LineChart
                    data={chartData}
                    margin={{
                      top: 10,
                      right: 8,
                      left: -25,
                      bottom: 0,
                    }}
                  >

                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke="#1e2936"
                    />

                    <XAxis
                      dataKey="time"
                      stroke="#475569"
                      tick={{
                        fill: "#64748b",
                        fontSize: 10,
                      }}
                    />

                    <YAxis
                      domain={[0, 100]}
                      stroke="#475569"
                      tick={{
                        fill: "#64748b",
                        fontSize: 10,
                      }}
                    />

                    <Tooltip
                      contentStyle={{
                        background: "#0d141c",
                        border: "1px solid #263444",
                        borderRadius: "8px",
                        color: "#ffffff",
                      }}
                      formatter={(value) => [
                        `${value}%`,
                        "Pool",
                      ]}
                    />

                    <Line
                      type="monotone"
                      dataKey="pool"
                      stroke="#f59e0b"
                      strokeWidth={3}
                      dot={{ r: 3 }}
                      activeDot={{ r: 5 }}
                      name="Pool"
                    />

                  </LineChart>
                </ResponsiveContainer>

              </div>

              <div className="signal-footer">
                <span>THRESHOLD</span>
                <strong>&gt;90% utilization</strong>
              </div>

            </div>

            {/* API LATENCY SIGNAL */}

            <div className="signal-card latency-signal">

              <div className="signal-header">

                <div>
                  <span className="signal-label">
                    API P95 LATENCY
                  </span>

                  <strong>{metrics.latency} ms</strong>
                </div>

                <span className="signal-status critical">
                  CRITICAL
                </span>

              </div>

              <div className="signal-chart">

                <ResponsiveContainer
                  width="100%"
                  height={150}
                >
                  <LineChart
                    data={chartData}
                    margin={{
                      top: 10,
                      right: 8,
                      left: -25,
                      bottom: 0,
                    }}
                  >

                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke="#1e2936"
                    />

                    <XAxis
                      dataKey="time"
                      stroke="#475569"
                      tick={{
                        fill: "#64748b",
                        fontSize: 10,
                      }}
                    />

                    <YAxis
                      stroke="#475569"
                      tick={{
                        fill: "#64748b",
                        fontSize: 10,
                      }}
                    />

                    <Tooltip
                      contentStyle={{
                        background: "#0d141c",
                        border: "1px solid #263444",
                        borderRadius: "8px",
                        color: "#ffffff",
                      }}
                      formatter={(value) => [
                        `${value} ms`,
                        "Latency",
                      ]}
                    />

                    <Line
                      type="monotone"
                      dataKey="latency"
                      stroke="#67e8f9"
                      strokeWidth={3}
                      dot={{ r: 3 }}
                      activeDot={{ r: 5 }}
                      name="Latency"
                    />

                  </LineChart>
                </ResponsiveContainer>

              </div>

              <div className="signal-footer">
                <span>SLO</span>
                <strong>1,000 ms</strong>
              </div>

            </div>

          </div>

        </section>

        {/* =====================================
            AI INVESTIGATION TRACE
        ====================================== */}

        <section className="panel investigation-trace-panel">

          <PanelHeader
            eyebrow="AI REASONING ENGINE"
            title="INVESTIGATION TRACE"
          />

          <div className="trace-list">

            <div className="trace-item">

              <div className="trace-number">
                01
              </div>

              <div className="trace-content">

                <span className="trace-label">
                  LOG ANOMALY DETECTED
                </span>

                <p>
                  Database connection acquisition latency
                  crossed the 1000ms investigation threshold.
                </p>

              </div>

              <span className="trace-state detected">
                DETECTED
              </span>

            </div>


            <div className="trace-item">

              <div className="trace-number">
                02
              </div>

              <div className="trace-content">

                <span className="trace-label">
                  SIGNAL CORRELATED
                </span>

                <p>
                  Connection pool utilization increased from
                  48% to 94% and reached 100%.
                </p>

              </div>

              <span className="trace-state correlated">
                CORRELATED
              </span>

            </div>


            <div className="trace-item">

              <div className="trace-number">
                03
              </div>

              <div className="trace-content">

                <span className="trace-label">
                  DEPENDENCY FAILURE CONFIRMED
                </span>

                <p>
                  3 database connection timeouts and failed
                  connection acquisition events were detected.
                </p>

              </div>

              <span className="trace-state confirmed">
                CONFIRMED
              </span>

            </div>


            <div className="trace-item">

              <div className="trace-number">
                04
              </div>

              <div className="trace-content">

                <span className="trace-label">
                  CUSTOMER IMPACT CORRELATED
                </span>

                <p>
                  Database saturation propagated to the API,
                  producing HTTP 503 responses and 5102ms latency.
                </p>

              </div>

              <span className="trace-state impact">
                IMPACT
              </span>

            </div>


            <div className="trace-item">

              <div className="trace-number">
                05
              </div>

              <div className="trace-content">

                <span className="trace-label">
                  DEPLOYMENT CORRELATION
                </span>

                <p>
                  user-service v2.4.1 was deployed 104 seconds
                  before the first critical incident.
                </p>

              </div>

              <span className="trace-state review">
                REVIEW
              </span>

            </div>


            <div className="trace-item trace-final">

              <div className="trace-number">
                06
              </div>

              <div className="trace-content">

                <span className="trace-label">
                  ROOT CAUSE SELECTED
                </span>

                <p>
                  {rootCause}
                </p>

              </div>

              <span className="trace-confidence">
                {confidence}% CONFIDENCE
              </span>

            </div>

          </div>

        </section>


        {/* =====================================
            SERVICE HEALTH
        ====================================== */}

        <section className="panel">

          <PanelHeader
            eyebrow="LIVE"
            title="SERVICE HEALTH"
          />

          <div className="service-grid">

            <div className="service-card degraded">

              <span className="service-indicator" />

              <div>
                <strong>API Gateway</strong>
                <p>52% errors</p>
              </div>

              <b>DEGRADED</b>

            </div>


            <div className="service-card critical">

              <span className="service-indicator" />

              <div>
                <strong>User Service</strong>
                <p>Connection failures</p>
              </div>

              <b>CRITICAL</b>

            </div>


            <div className="service-card saturated">

              <span className="service-indicator" />

              <div>
                <strong>Database</strong>
                <p>100% connections</p>
              </div>

              <b>SATURATED</b>

            </div>


            <div className="service-card recent">

              <span className="service-indicator" />

              <div>
                <strong>Deployment</strong>
                <p>v2.4.1</p>
              </div>

              <b>RECENT</b>

            </div>

          </div>

        </section>


        {/* =====================================
            INCIDENT TIMELINE
        ====================================== */}

        <section className="panel">

          <PanelHeader
            eyebrow="CORRELATED EVENTS"
            title="INCIDENT TIMELINE"
          />

          <div className="timeline">

            <div className="timeline-item">

              <span>14:01:18</span>

              <div>
                <strong>Deployment detected</strong>

                <p>
                  user-service v2.4.1 deployed
                </p>
              </div>

            </div>


            <div className="timeline-item">

              <span>14:02:03</span>

              <div>
                <strong>
                  Database pressure detected
                </strong>

                <p>
                  Connection acquisition exceeded
                  1200ms
                </p>
              </div>

            </div>


            <div className="timeline-item">

              <span>14:02:21</span>

              <div>
                <strong>Connection timeout</strong>

                <p>
                  Database connection timeout after
                  3000ms
                </p>
              </div>

            </div>


            <div className="timeline-item critical-event">

              <span>14:03:02</span>

              <div>
                <strong>Pool exhausted</strong>

                <p>
                  Database connection pool reached
                  maximum capacity
                </p>
              </div>

            </div>


            <div className="timeline-item critical-event">

              <span>14:04:52</span>

              <div>
                <strong>API degradation</strong>

                <p>
                  Error rate reached 52%
                </p>
              </div>

            </div>

          </div>

        </section>


        {/* =====================================
            ACTIONS + HYPOTHESES
        ====================================== */}

        <section className="bottom-grid">

          <div className="panel actions-panel">

            <PanelHeader
              eyebrow="REMEDIATION"
              title="RECOMMENDED ACTIONS"
            />

            <div className="actions-list">

              {actions.map((action, index) => {

                const completed =
                  actionStates[index] === "COMPLETED";

                return (
                  <button
                    className={`action-item ${
                      completed ? "completed" : ""
                    }`}
                    key={index}
                    onClick={() =>
                      toggleAction(index)
                    }
                  >

                    <span className="action-number">
                      {String(index + 1).padStart(2, "0")}
                    </span>

                    <span className="action-text">
                      {action}
                    </span>

                    <span className="action-status">
                      {completed
                        ? "✓ COMPLETED"
                        : "PENDING"}
                    </span>

                  </button>
                );
              })}

            </div>

          </div>


          <div className="panel hypotheses-panel">

            <PanelHeader
              eyebrow="INVESTIGATION TREE"
              title="ALTERNATIVE HYPOTHESES"
            />

            <div className="hypotheses">

              {hypotheses.map((item, index) => (

                <div
                  className="hypothesis"
                  key={index}
                >

                  <div>
                    <strong>{item.score}</strong>

                    <span>EVIDENCE SCORE</span>
                  </div>

                  <p>{item.hypothesis}</p>

                </div>

              ))}

            </div>

          </div>

        </section>


        {/* =====================================
            SUMMARY
        ====================================== */}

        <section className="panel summary-panel">

          <PanelHeader
            eyebrow="SYSTEM ANALYSIS"
            title="INVESTIGATION SUMMARY"
          />

          <div className="summary-grid">

            <div>
              <strong>
                {analysis.total_events ?? 32}
              </strong>

              <span>TOTAL EVENTS</span>
            </div>

            <div>
              <strong>{metrics.errors}</strong>
              <span>ERROR EVENTS</span>
            </div>

            <div>
              <strong>{metrics.warnings}</strong>
              <span>WARNING EVENTS</span>
            </div>

            <div>
              <strong>{metrics.timeouts}</strong>
              <span>TIMEOUTS</span>
            </div>

          </div>

        </section>

      </main>


      {/* =====================================
          FOOTER
      ====================================== */}

      <footer>

        <span>SENTINELOPS v1.0</span>

        <span>
          AI INCIDENT INVESTIGATION ENGINE
        </span>

        <button
          className="refresh-btn"
          onClick={fetchInvestigation}
        >
          ↻ REFRESH INVESTIGATION
        </button>

      </footer>

    </div>
  );
}

export default App;