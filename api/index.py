from typing import List

import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Telemetry bundle embedded directly (serverless functions can't rely on local files)
DATA = [{"region": "apac", "service": "recommendations", "latency_ms": 117.07, "uptime_pct": 98.157, "timestamp": 20250301}, {"region": "apac", "service": "payments", "latency_ms": 154.4, "uptime_pct": 99.448, "timestamp": 20250302}, {"region": "apac", "service": "recommendations", "latency_ms": 159.9, "uptime_pct": 99.191, "timestamp": 20250303}, {"region": "apac", "service": "payments", "latency_ms": 121.88, "uptime_pct": 97.759, "timestamp": 20250304}, {"region": "apac", "service": "recommendations", "latency_ms": 122.08, "uptime_pct": 98.075, "timestamp": 20250305}, {"region": "apac", "service": "catalog", "latency_ms": 141.59, "uptime_pct": 97.553, "timestamp": 20250306}, {"region": "apac", "service": "support", "latency_ms": 108.77, "uptime_pct": 99.396, "timestamp": 20250307}, {"region": "apac", "service": "support", "latency_ms": 118.85, "uptime_pct": 99.265, "timestamp": 20250308}, {"region": "apac", "service": "support", "latency_ms": 189.84, "uptime_pct": 98.248, "timestamp": 20250309}, {"region": "apac", "service": "analytics", "latency_ms": 198.85, "uptime_pct": 97.693, "timestamp": 20250310}, {"region": "apac", "service": "payments", "latency_ms": 238.73, "uptime_pct": 98.011, "timestamp": 20250311}, {"region": "apac", "service": "analytics", "latency_ms": 134.85, "uptime_pct": 97.935, "timestamp": 20250312}, {"region": "emea", "service": "analytics", "latency_ms": 182.05, "uptime_pct": 99.263, "timestamp": 20250301}, {"region": "emea", "service": "checkout", "latency_ms": 139.76, "uptime_pct": 99.062, "timestamp": 20250302}, {"region": "emea", "service": "checkout", "latency_ms": 197.17, "uptime_pct": 98.534, "timestamp": 20250303}, {"region": "emea", "service": "checkout", "latency_ms": 235.08, "uptime_pct": 97.739, "timestamp": 20250304}, {"region": "emea", "service": "support", "latency_ms": 178.29, "uptime_pct": 98.928, "timestamp": 20250305}, {"region": "emea", "service": "checkout", "latency_ms": 209.75, "uptime_pct": 97.668, "timestamp": 20250306}, {"region": "emea", "service": "payments", "latency_ms": 110.78, "uptime_pct": 98.006, "timestamp": 20250307}, {"region": "emea", "service": "catalog", "latency_ms": 210.19, "uptime_pct": 97.155, "timestamp": 20250308}, {"region": "emea", "service": "analytics", "latency_ms": 110.47, "uptime_pct": 97.488, "timestamp": 20250309}, {"region": "emea", "service": "recommendations", "latency_ms": 224.48, "uptime_pct": 98.536, "timestamp": 20250310}, {"region": "emea", "service": "catalog", "latency_ms": 166.22, "uptime_pct": 98.382, "timestamp": 20250311}, {"region": "emea", "service": "catalog", "latency_ms": 184.64, "uptime_pct": 98.605, "timestamp": 20250312}, {"region": "amer", "service": "analytics", "latency_ms": 198.3, "uptime_pct": 97.657, "timestamp": 20250301}, {"region": "amer", "service": "catalog", "latency_ms": 177.6, "uptime_pct": 97.194, "timestamp": 20250302}, {"region": "amer", "service": "catalog", "latency_ms": 126.3, "uptime_pct": 98.76, "timestamp": 20250303}, {"region": "amer", "service": "analytics", "latency_ms": 149.33, "uptime_pct": 97.759, "timestamp": 20250304}, {"region": "amer", "service": "recommendations", "latency_ms": 168.86, "uptime_pct": 97.517, "timestamp": 20250305}, {"region": "amer", "service": "analytics", "latency_ms": 179.79, "uptime_pct": 97.166, "timestamp": 20250306}, {"region": "amer", "service": "support", "latency_ms": 155.65, "uptime_pct": 99.327, "timestamp": 20250307}, {"region": "amer", "service": "support", "latency_ms": 231.5, "uptime_pct": 98.498, "timestamp": 20250308}, {"region": "amer", "service": "recommendations", "latency_ms": 207.83, "uptime_pct": 99.167, "timestamp": 20250309}, {"region": "amer", "service": "analytics", "latency_ms": 218.02, "uptime_pct": 97.453, "timestamp": 20250310}, {"region": "amer", "service": "catalog", "latency_ms": 230.53, "uptime_pct": 97.107, "timestamp": 20250311}, {"region": "amer", "service": "catalog", "latency_ms": 198.56, "uptime_pct": 99.417, "timestamp": 20250312}]


class Query(BaseModel):
    regions: List[str]
    threshold_ms: float = 180


def compute(q: Query):
    result = {}
    for region in q.regions:
        rows = [r for r in DATA if r["region"] == region]
        if not rows:
            continue
        lat = np.array([r["latency_ms"] for r in rows], dtype=float)
        up = np.array([r["uptime_pct"] for r in rows], dtype=float)
        result[region] = {
            "avg_latency": float(lat.mean()),
            "p95_latency": float(np.percentile(lat, 95)),
            "avg_uptime": float(up.mean()),
            "breaches": int((lat > q.threshold_ms).sum()),
        }
    return {"regions": result}


@app.post("/")
@app.post("/api")
@app.post("/api/latency")
def latency(q: Query):
    return compute(q)


@app.get("/")
def health():
    return {"status": "ok", "usage": "POST {regions: [...], threshold_ms: number}"}
