from __future__ import annotations

from fastapi.testclient import TestClient

from ctrltest_mcp.fastapi_app import create_app


def test_analyze_endpoint() -> None:
    app = create_app()
    client = TestClient(app)
    payload = {
        "plant": {
            "natural_frequency_hz": 5.0,
            "damping_ratio": 0.6,
            "settling_tolerance_rad": 0.02,
            "trim_setpoint": 0.0,
        },
        "gains": {"kp": 0.8, "ki": 0.05, "kd": 0.02},
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "overshoot" in data
    assert "gust_rejection_pct" in data
