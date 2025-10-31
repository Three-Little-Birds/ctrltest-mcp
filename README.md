# ctrltest-mcp · Flight-control regression lab for MCP agents

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%2B-3776AB.svg" alt="Python 3.10 or newer"></a>
  <a href="https://github.com/Three-Little-Birds/ctrltest-mcp/actions/workflows/ci.yml"><img src="https://github.com/Three-Little-Birds/ctrltest-mcp/actions/workflows/ci.yml/badge.svg" alt="CI status"></a>
  <img src="https://img.shields.io/badge/status-incubating-ff9800.svg" alt="Project status: incubating">
  <img src="https://img.shields.io/badge/MCP-tooling-blueviolet.svg" alt="MCP tooling badge">
</p>

> **TL;DR**: Evaluate PID and bio-inspired controllers against analytic or diffSPH/Foam-Agent data through MCP, logging overshoot, energy, and gust metrics automatically.

## Table of contents

1. [Why agents love it](#why-agents-love-it)
2. [Quickstart](#quickstart)
3. [Run as a service](#run-as-a-service)
4. [Agent playbook](#agent-playbook)
5. [Stretch ideas](#stretch-ideas)
6. [Accessibility & upkeep](#accessibility--upkeep)
7. [Contributing](#contributing)

## Why agents love it

| Persona | Immediate value | Longer-term payoff |
|---------|-----------------|--------------------|
| **New users** | Plug in default plant parameters and observe overshoot/gust KPIs in one call. | Ready-to-run examples mirror the README first, aligning with modern “quick win” documentation advice.【turn0search0】 |
| **Experienced teams** | Fuse metrics from diffSPH and Foam-Agent archives to score adaptive controllers. | Designed for the Continuous Evidence Engine (CEE) – metrics drop straight into nightly scorecards.

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

## Run as a service

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

## Agent playbook

- **Gust rejection** – feed archived diffSPH gradients (`diffsph_metrics`) and Foam-Agent archives to quantify adaptive CPG improvements.
- **Controller comparison** – log analytics for multiple PID gains, export JSONL evidence, and visualise in Grafana.
- **Policy evaluation** – integrate with RL or evolutionary algorithms; metrics are structured for automated scoring.

## Stretch ideas

1. Extend the adapter for PteraControls once upstream bindings land.
2. Drive the MCP from `scripts/fitness` to populate nightly scorecards.
3. Combine with `migration-mcp` to explore route-specific disturbance budgets.

## Accessibility & upkeep

- Hero badges include alt text and stay under five to maintain scanability.【turn0search0】
- Run `uv run pytest` (tests mock diffSPH/Foam-Agent inputs).
- Keep metric schema changes documented—downstream dashboards rely on them.

## Contributing

1. `uv pip install --system -e .[dev]`
2. `uv run ruff check .` and `uv run pytest`
3. Share sample metrics in PRs so reviewers can sanity-check improvements quickly.

MIT license — see [LICENSE](LICENSE).
