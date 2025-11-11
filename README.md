# ctrltest-mcp - Flight-control regression lab for MCP agents

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.11%2B-3776AB.svg" alt="Python 3.11 or newer"></a>
  <a href="https://github.com/Three-Little-Birds/ctrltest-mcp/actions/workflows/ci.yml"><img src="https://github.com/Three-Little-Birds/ctrltest-mcp/actions/workflows/ci.yml/badge.svg" alt="CI status"></a>
  <img src="https://img.shields.io/badge/MCP-tooling-blueviolet.svg" alt="MCP tooling badge">
</p>

<a href="https://glama.ai/mcp/servers/@yevheniikravchuk/ctrltest-mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@yevheniikravchuk/ctrltest-mcp/badge" alt="CtrlTest Server MCP server" />
</a>

> **TL;DR**: Evaluate PID and bio-inspired controllers against analytic or diffSPH/Foam-Agent data through MCP, logging overshoot, energy, and gust metrics automatically.

## Table of contents

1. [What it provides](#what-it-provides)
2. [Quickstart](#quickstart)
3. [Run as a service](#run-as-a-service)
4. [Agent playbook](#agent-playbook)
5. [Stretch ideas](#stretch-ideas)
6. [Accessibility & upkeep](#accessibility--upkeep)
7. [Contributing](#contributing)

## What it provides

| Scenario | Value |
|----------|-------|
| Analytic PID benchmarking | Run closed-form plant models and produce overshoot/settling/energy metrics without manual scripting. |
| High-fidelity scoring | Ingest logged data from [Foam-Agent](https://github.com/csml-rpi/Foam-Agent) or diffSPH runs and fuse it into controller evaluations. |
| MCP integration | Expose the scoring API via STDIO/HTTP so ToolHive or other clients can automate gain tuning and generate continuous performance scorecards. |

## Quickstart

```bash
uv pip install "git+https://github.com/Three-Little-Birds/ctrltest-mcp.git"
```

Run a PID evaluation:

```python
from ctrltest_mcp import (
    ControlAnalysisInput,
    ControlPlant,
    ControlSimulation,
    PIDGains,
    evaluate_control,
)

request = ControlAnalysisInput(
    plant=ControlPlant(natural_frequency_hz=3.2, damping_ratio=0.35),
    gains=PIDGains(kp=2.0, ki=0.5, kd=0.12),
    simulation=ControlSimulation(duration_s=3.0, sample_points=400),
    setpoint=0.2,
)
response = evaluate_control(request)
print(response.model_dump())
```

Typical outputs (analytic only):

```json
{
  "overshoot": -0.034024863556091134,
  "ise": 0.008612387509182674,
  "settling_time": 3.0,
  "gust_detection_latency_ms": 0.8,
  "gust_detection_bandwidth_hz": 1200.0,
  "gust_rejection_pct": 0.396,
  "cpg_energy_baseline_j": 12.0,
  "cpg_energy_consumed_j": 7.8,
  "cpg_energy_reduction_pct": 0.35,
  "lyapunov_margin": 0.12,
  "moe_switch_penalty": 0.135,
  "moe_latency_ms": 12.72,
  "moe_energy_j": 3.9,
  "multi_modal_score": null,
  "extra_metrics": null,
  "metadata": {"solver": "analytic"}
}
```

> The analytic plant example above clips `settling_time` at the requested simulation duration (`duration_s=3.0`). Increase the horizon if you need the loop to settle fully before computing that metric.

## Run as a service

### CLI (STDIO transport)

```bash
uvx ctrltest-mcp  # runs the MCP over stdio
# or just python -m ctrltest_mcp
```

Use `python -m ctrltest_mcp --describe` to print basic metadata without starting the server.

### FastAPI (REST)

```bash
uv run uvicorn ctrltest_mcp.fastapi_app:create_app --factory --port 8005
```

### python-sdk tool (STDIO / MCP)

```python
from mcp.server.fastmcp import FastMCP
from ctrltest_mcp.tool import build_tool

mcp = FastMCP("ctrltest-mcp", "Flapping-wing control regression")
build_tool(mcp)

if __name__ == "__main__":
    mcp.run()
```

### ToolHive smoke test

Run the integration script from your workspace root:

```bash
uvx --with 'mcp==1.20.0' python scripts/integration/run_ctrltest.py
```

The smoke test runs the analytic path by default. To exercise high-fidelity scoring, stage Foam-Agent archives under `logs/foam_agent/` and diffSPH gradients under `logs/diffsph/` before launching the script.

## Agent playbook

- **Gust rejection** - feed archived diffSPH gradients (`diffsph_metrics`) and Foam-Agent archives (paths returned by those services) to quantify adaptive CPG improvements.
- **Controller comparison** - log analytics for multiple PID gains, export JSONL evidence, and visualise in Grafana.
- **Policy evaluation** - integrate with RL or evolutionary algorithms; metrics are structured for automated scoring.

## Stretch ideas

1. Extend the adapter for PteraControls (planned once upstream Python bindings are published).
2. Drive the MCP from `scripts/fitness` to populate nightly scorecards.
3. Combine with `migration-mcp` to explore route-specific disturbance budgets.

## Accessibility & upkeep

- Hero badges include alt text and stay under five to maintain scanability.
- Run `uv run pytest` (tests mock diffSPH/Foam-Agent inputs and assert deterministic analytic results).
- Keep metric schema changes documented—downstream dashboards rely on them.

### Metric schema at a glance

| Field | Units | Notes |
|-------|-------|-------|
| `overshoot` | radians | peak response minus setpoint |
| `ise` | rad²·s | integral squared error |
| `settling_time` | seconds | first time error stays within tolerance |
| `gust_detection_latency_ms` | milliseconds | detector latency |
| `gust_detection_bandwidth_hz` | hertz | detector bandwidth |
| `gust_rejection_pct` | 0–1 | fraction of disturbance rejected |
| `cpg_energy_baseline_j` | joules | energy pre-adaptation |
| `cpg_energy_consumed_j` | joules | energy post-adaptation |
| `cpg_energy_reduction_pct` | 0–1 | energy reduction ratio |
| `lyapunov_margin` | unitless | stability margin |
| `moe_switch_penalty` | unitless | cost weight × switches |
| `moe_latency_ms` | milliseconds | latency budget after switching |
| `moe_energy_j` | joules | mix-of-experts energy draw |
| `multi_modal_score` | unitless | only when both diffSPH & Foam metrics are present |
| `extra_metrics` | varies | raw diffSPH/Foam metrics merged in |

Example of fused high-fidelity metrics:

```json
{
  "extra_metrics": {
    "force_gradient_norm": 0.87,
    "lift_drag_ratio": 18.4
  },
  "multi_modal_score": 0.047,
  "metadata": {"solver": "analytic"}
}
```

## Contributing

1. `uv pip install --system -e .[dev]`
2. `uv run ruff check .` and `uv run pytest`
3. Share sample metrics in PRs so reviewers can sanity-check improvements quickly.

MIT license - see [LICENSE](LICENSE).