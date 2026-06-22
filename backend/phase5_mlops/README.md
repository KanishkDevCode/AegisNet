<div align="center">
  <img src="https://img.shields.io/badge/Next.js-MLOps_Dashboard-black?style=for-the-badge&logo=next.js" />
  <img src="https://img.shields.io/badge/Recharts-Telemetry-blue?style=for-the-badge" />
  <h2>Phase 5: MLOps Telemetry & Overwatch</h2>
</div>

## 📖 Overview
Initially, Phase 5 utilized external dependencies like Prometheus and Grafana for system tracking. However, to make AegisNet a **100% native** and highly portable solution, we have migrated the entire MLOps suite into a custom **FastAPI Data Store** and a stunning **Next.js Recharts Dashboard**.

## ⚙️ How It Works
1. **Metrics Collector**: Located in `backend/api_gateway/metrics.py`, this acts as the central telemetry store. Every time the Swarm runs, it logs scenario counts, vision model confidence scores, phase latencies, and calculates real-time **Data Drift**.
2. **Wasserstein Data Drift**: The metrics engine calculates the statistical distance between baseline packet distributions and live inputs. If the drift score exceeds `0.15`, the system flags a "CRITICAL" warning that hackers are mutating their attacks.
3. **API Endpoint**: The `main.py` FastAPI server exposes `GET /api/metrics`.
4. **Next.js Dashboard**: The `MetricsDashboard.tsx` component automatically polls this endpoint every 3 seconds to render live Area Charts, Stacked Bar Charts, and Radial Gauges.

## 🧪 Testing Locally
The MLOps telemetry is intrinsically tied to the Next.js frontend.
1. Ensure the FastAPI backend is running.
2. Open `http://localhost:3000` (Next.js server).
3. Click the **MLOps** tab to view live telemetry.
