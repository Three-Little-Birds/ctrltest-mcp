"""FastAPI application for control analysis."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from .core import evaluate_control
from .models import ControlAnalysisInput, ControlAnalysisOutput


def create_app() -> FastAPI:
    app = FastAPI(
        title="CtrlTest MCP Service",
        version="0.1.0",
        description="Evaluate PID control metrics for flapping-wing plants.",
    )

    @app.post("/analyze", response_model=ControlAnalysisOutput)
    def analyze(request: ControlAnalysisInput) -> ControlAnalysisOutput:
        try:
            return evaluate_control(request)
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    return app


app = create_app()

__all__ = ["create_app", "app"]
