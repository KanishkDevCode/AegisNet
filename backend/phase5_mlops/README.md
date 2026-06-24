<div align="center">
  <img src="https://img.shields.io/badge/Next.js-MLOps_Dashboard-black?style=for-the-badge&logo=next.js" />
  <img src="https://img.shields.io/badge/Recharts-Telemetry-22b3e8?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Phase-5_MLOps-pink?style=for-the-badge" />
  <h2>📊 Phase 5: MLOps Telemetry & Overwatch</h2>
</div>

> **The Overwatch.** A 100% native, highly portable MLOps suite that monitors Data Drift, Phase Latency, and AI Vision Confidence without relying on heavy external dependencies like Prometheus or Grafana.

## 🌊 Pipeline Flow

```mermaid
graph TD
    classDef default fill:#1e1e2e,stroke:#f5c2e7,stroke-width:2px,color:#cdd6f4;
    classDef highlight fill:#cba6f7,stroke:#11111b,color:#11111b,font-weight:bold;
    classDef warning fill:#f38ba8,stroke:#11111b,color:#11111b,font-weight:bold;

    A[🛡️ Phase 4 Contained Threat] -->|Telemetry Payloads| B[(💾 FastAPI In-Memory Metrics Store)];
    B -->|Calculate Statistical Distance| C{📈 Wasserstein Drift Evaluator};
    
    C -->|Drift > 0.15| D[🚨 CRITICAL DRIFT WARNING];
    C -->|Drift <= 0.15| E[✅ Stable Model Distribution];

    B --> F[🖥️ Next.js Recharts Dashboard];
    D --> F;
    E --> F;

    F :::highlight
    D :::warning
```

## ⚙️ How It Works

1. 📥 **Metrics Collector**: Located in `backend/api_gateway/metrics.py`, this acts as the central telemetry store. Every time the Swarm runs, it logs scenario counts, vision model confidence scores, phase latencies, and calculates real-time **Data Drift**.
2. 📉 **Wasserstein Data Drift**: The metrics engine calculates the statistical distance between baseline packet distributions and live inputs. If the drift score exceeds `0.15`, the system flags a "CRITICAL" warning that hackers are mutating their attacks to evade detection.
3. 📡 **API Endpoint**: The `main.py` FastAPI server exposes a lightweight `GET /api/metrics` JSON endpoint for the frontend.
4. 🖥️ **Next.js Dashboard**: The `MetricsDashboard.tsx` component automatically polls this endpoint every 3 seconds to render live Area Charts, Stacked Bar Charts, and Radial Gauges in a stunning, premium UI.

## 🧪 Testing Locally

The MLOps telemetry is intrinsically tied to the Next.js frontend.
1. Ensure the FastAPI backend is running.
2. Open `http://localhost:3000` (Next.js server).
3. Click the **MLOps** tab on the left sidebar to view live, glowing telemetry updates.
