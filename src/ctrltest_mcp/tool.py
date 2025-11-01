"""python-sdk integration for ctrltest."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .core import evaluate_control
from .models import ControlAnalysisInput, ControlAnalysisOutput


def build_tool(app: FastMCP) -> None:
    """Register ctrltest analysis tooling on an MCP server."""

    @app.tool(
        name="ctrltest.analyze_pid",
        description=(
            "Score PID gains for a flapping-wing plant. "
            "Provide plant dynamics and optional gradients/metadata. "
            "Returns key control metrics plus provenance. "
            "Example input: "
            '{"plant":{"natural_frequency_hz":4.2,"damping_ratio":0.45},'
            '"gains":{"kp":1.1,"ki":0.2,"kd":0.08},'
            '"diffsph_metrics":{"force_gradient_norm":1.9}}'
        ),
        meta={"version": "0.1.0", "categories": ["control", "analysis"]},
    )
    def analyze(request: ControlAnalysisInput) -> ControlAnalysisOutput:
        return evaluate_control(request)


__all__ = ["build_tool"]
