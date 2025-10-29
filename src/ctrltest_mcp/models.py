"""Typed models for control analysis."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PIDGains(BaseModel):
    kp: float = Field(..., ge=0.0)
    ki: float = Field(0.0, ge=0.0)
    kd: float = Field(0.0, ge=0.0)


class ControlPlant(BaseModel):
    natural_frequency_hz: float = Field(..., gt=0.0)
    damping_ratio: float = Field(..., ge=0.0)
    settling_tolerance_rad: float = Field(0.02, gt=0.0)
    trim_setpoint: float = Field(0.0)


class ControlSimulation(BaseModel):
    duration_s: float = Field(5.0, gt=0.0)
    sample_points: int = Field(500, ge=50, le=5000)


class GustDetectorConfig(BaseModel):
    latency_ms: float = Field(0.8, ge=0.1)
    bandwidth_hz: float = Field(1200.0, ge=10.0)
    sensitivity: float = Field(0.88, ge=0.0, le=1.0)


class AdaptiveCPGConfig(BaseModel):
    target_rejection_pct: float = Field(0.45, ge=0.0, le=0.95)
    energy_baseline_j: float = Field(12.0, gt=0.0)
    energy_reduction_pct: float = Field(0.35, ge=0.0, le=0.95)
    lyapunov_margin: float = Field(0.12, ge=0.0)


class MoERouterConfig(BaseModel):
    switch_events: int = Field(3, ge=0)
    switch_cost_weight: float = Field(0.045, ge=0.0)
    latency_budget_ms: float = Field(12.0, gt=0.0)
    energy_budget_j: float = Field(6.0, gt=0.0)


class ControlAnalysisInput(BaseModel):
    plant: ControlPlant
    gains: PIDGains
    simulation: ControlSimulation = Field(default_factory=ControlSimulation)
    setpoint: float = Field(0.0)
    gust_detector: GustDetectorConfig = Field(default_factory=GustDetectorConfig)
    adaptive_cpg: AdaptiveCPGConfig = Field(default_factory=AdaptiveCPGConfig)
    moe_router: MoERouterConfig = Field(default_factory=MoERouterConfig)
    diffsph_metrics: dict[str, Any] | None = None
    foam_metrics: dict[str, Any] | None = None
    prefer_high_fidelity: bool = Field(
        default=True,
        description="Attempt to use PteraControls when available before falling back to the analytic surrogate.",
    )


class ControlAnalysisOutput(BaseModel):
    overshoot: float
    ise: float
    settling_time: float
    gust_detection_latency_ms: float
    gust_detection_bandwidth_hz: float
    gust_rejection_pct: float
    cpg_energy_baseline_j: float
    cpg_energy_consumed_j: float
    cpg_energy_reduction_pct: float
    lyapunov_margin: float
    moe_switch_penalty: float
    moe_latency_ms: float
    moe_energy_j: float
    multi_modal_score: float | None = None
    extra_metrics: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
