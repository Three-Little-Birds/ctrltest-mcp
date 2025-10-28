# ctrltest-mcp

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-brightgreen.svg)](pyproject.toml)
[![CI](https://github.com/yevheniikravchuk/ctrltest-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/yevheniikravchuk/ctrltest-mcp/actions/workflows/ci.yml)

Control-system regression utilities for Model Context Protocol services. It evaluates PID gains against a second-order plant (using [python-control](https://python-control.readthedocs.io/)), computes gust-rejection metrics, and blends optional diffSPH/Foam-Agent metrics supplied by the caller.

## Why you might want this

- **Regression-test control laws** – keep a lightweight plant model handy so agents can sanity-check PID gains.
- **Fuse structural data** – optional diffSPH/Foam-Agent metrics feed into the report, helping cross-discipline reviews.
- **Share reproducible experiments** – request/response payloads double as documentation for how a tuning session was evaluated.

## Features
- Deterministic PID step response analysis (overshoot, settling time, ISE).
- Optional gust detector, adaptive CPG, and MoE router scoring primitives.
- FastAPI app + python-sdk helper ready for MCP deployments.

## Installation
```bash
pip install "git+https://github.com/yevheniikravchuk/ctrltest-mcp.git"
```

## Usage
```python
from ctrltest_mcp import ControlAnalysisInput, ControlPlant, ControlSimulation, PIDGains
from ctrltest_mcp import evaluate_control

inputs = ControlAnalysisInput(
    plant=ControlPlant(natural_frequency_hz=5.0, damping_ratio=0.6, settling_tolerance_rad=0.02, trim_setpoint=0.0),
    simulation=ControlSimulation(duration_s=5.0, sample_points=500),
    gains=PIDGains(kp=0.8, ki=0.05, kd=0.02),
)
metrics = evaluate_control(inputs)
print(metrics["overshoot"])
```

## Development
```bash
uv pip install --system -e .[dev]
uv run ruff check .
uv run pytest
```

The test suite shows both the minimal “PID-only” call and a richer request that merges surrogate data, giving new contributors concrete payloads to copy.

## License
MIT — see [LICENSE](LICENSE).
