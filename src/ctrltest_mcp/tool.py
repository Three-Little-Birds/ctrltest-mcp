"""python-sdk integration for ctrltest."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .core import evaluate_control
from .models import ControlAnalysisInput, ControlAnalysisOutput


def build_tool(app: FastMCP) -> None:
    @app.tool()
    def analyze(request: ControlAnalysisInput) -> ControlAnalysisOutput:  # type: ignore[valid-type]
        return evaluate_control(request)


__all__ = ["build_tool"]
