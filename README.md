# ctrltest-mcp - Flight-control regression lab for MCP agents

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.11%2B-3776AB.svg" alt="Python 3.11 or newer"></a>
  <a href="https://github.com/Three-Little-Birds/ctrltest-mcp/actions/workflows/ci.yml"><img src="https://github.com/Three-Little-Birds/ctrltest-mcp/actions/workflows/ci.yml/badge.svg" alt="CI status"></a>
  <img src="https://img.shields.io/badge/MCP-tooling-blueviolet.svg" alt="MCP tooling badge">
</p>

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
from ctrltest_mcp import PIDRequest, run_pid_analysis

request = PIDRequest(setpoint_rad=0.2)
response = run_pid_analysis(request)
print(response.metrics)
```

Typical metric payload:

```json
{
  "setpoint_rad": 0.2,
  "overshoot_pct": 3.8,
  "settling_time_s": 0.92,
  "energy_j": 1.34,
  "gust_margin_pct": 12.5
}
```

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
- Run `uv run pytest` (tests mock diffSPH/Foam-Agent inputs).
- Keep metric schema changes documented-downstream dashboards rely on them.

## Contributing

1. `uv pip install --system -e .[dev]`
2. `uv run ruff check .` and `uv run pytest`
3. Share sample metrics in PRs so reviewers can sanity-check improvements quickly.

MIT license - see [LICENSE](LICENSE).
