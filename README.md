# ctrltest-mcp · A Guided Lab for Flight Control Experiments

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-brightgreen.svg)](pyproject.toml)
[![CI](https://github.com/yevheniikravchuk/ctrltest-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/yevheniikravchuk/ctrltest-mcp/actions/workflows/ci.yml)

`ctrltest-mcp` packages a lightweight control-test bench so that students, hobbyists, and MCP agents can reason about flapping-wing controllers without owning the full hardware stack. When [PteraControls](https://github.com/camUrban/PteraControls) ships a Python interface the MCP automatically upgrades to its high-fidelity routines; until then the built-in analytic surrogate keeps the learning loop quick.

## After reading this guide you will

1. Understand the control plant model used for evaluations.
2. Run a closed-loop test sequence and inspect headline metrics (gust rejection, control energy, etc.).
3. Register the MCP tool so your agent can request “try a higher pitch gain” and immediately see the effect.

## Requirements

- Python 3.10+ with `uv`.
- Optional: `matplotlib` for plotting the returned error/time series.
- For advanced scenarios you can point the tool at real Foam-Agent or diffSPH outputs, but the defaults ship with stubs so you can start immediately.
- Optional: a Python build of PteraControls for high-fidelity evaluation (auto-detected when installed).

## Step 1 – Install the toolkit

```bash
uv pip install "git+https://github.com/yevheniikravchuk/ctrltest-mcp.git"
# optional: enable PteraControls high-fidelity mode when the Python package is available
# uv pip install "git+https://github.com/camUrban/PteraControls.git"
```

## Step 2 – Run a controller evaluation in code

```python
from ctrltest_mcp import ControlRequest, evaluate_controller

request = ControlRequest(
    scenario_name="swift-lite",
    pitch_gain=0.8,
    roll_gain=0.6,
    adaptive_schedule="hover-to-cruise",
)

result = evaluate_controller(request)
print(result.metrics.gust_rejection_pct)
print(result.metrics.energy_integral)
```

The helper loads the embedded plant parameters, simulates a disturbance, and reports summary metrics plus a time history you can plot.

Just like the aerodynamic tool, the response contains a `metadata` payload. Expect `{"solver": "analytic"}` today; once PteraControls publishes Python bindings the adapter automatically upgrades to something like `{"solver": "pteracontrols", "solver_version": "...", "fidelity": "uvlm"}` so downstream scorecards know which engine produced the evaluation.

## Step 3 – Visualise the response

```python
import matplotlib.pyplot as plt

times = [sample.time_s for sample in result.history]
pitch_error = [sample.pitch_error_deg for sample in result.history]

plt.plot(times, pitch_error)
plt.xlabel("Time [s]")
plt.ylabel("Pitch error [deg]")
plt.show()
```

## Step 4 – Make it an MCP service

### FastAPI surface

```python
from ctrltest_mcp.fastapi_app import create_app

app = create_app()
```

Launch locally:

```bash
uv run uvicorn ctrltest_mcp.fastapi_app:create_app --factory --port 8005
```

### python-sdk tool

```python
from mcp.server.fastmcp import FastMCP
from ctrltest_mcp.tool import build_tool

mcp = FastMCP("ctrltest-mcp", "Flapping controller evaluator")
build_tool(mcp)

if __name__ == "__main__":
    mcp.run()
```

In your MCP-aware IDE, call `ctrltest-mcp.evaluate` with different gain sets and review the metrics in the conversation.

## Suggested experiments

- **Gust robustness:** sweep `pitch_gain` and log the resulting `gust_rejection_pct` metric.
- **Energy audits:** contrast adaptive schedules to see which one delivers lower control energy.
- **Integration practice:** combine outputs with `migration-mcp` to see how controller choices affect migration scorecards.

## Developing further

```bash
uv pip install --system -e .[dev]
uv run ruff check .
uv run pytest
```

Tests stub the plant so you can explore input/output formats without waiting for long simulations.

## License

MIT — see [LICENSE](LICENSE).
