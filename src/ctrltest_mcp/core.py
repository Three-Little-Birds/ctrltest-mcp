"""Control analysis routines."""

from __future__ import annotations

import logging
import math
from typing import Any

import numpy as np
from control import feedback, forced_response, tf

from .models import ControlAnalysisInput, ControlAnalysisOutput
from .pteracontrols_adapter import is_available, run_high_fidelity

LOGGER = logging.getLogger(__name__)


def evaluate_control(inputs: ControlAnalysisInput) -> ControlAnalysisOutput:
    if inputs.prefer_high_fidelity and is_available():
        try:
            high_fidelity = run_high_fidelity(inputs)
            if high_fidelity is not None:
                return high_fidelity
        except Exception as exc:  # pragma: no cover - fallback safety
            LOGGER.warning("PteraControls evaluation failed, using surrogate results: %s", exc)

    plant = inputs.plant
    gains = inputs.gains
    simulation = inputs.simulation

    omega_n = 2.0 * math.pi * plant.natural_frequency_hz
    zeta = plant.damping_ratio
    plant_tf = tf([omega_n**2], [1, 2 * zeta * omega_n, omega_n**2])
    pid_tf = tf([gains.kd, gains.kp, gains.ki], [1, 0])
    closed_loop = feedback(pid_tf * plant_tf, 1)

    t = np.linspace(0, simulation.duration_s, simulation.sample_points)
    setpoint = inputs.setpoint
    u = np.full_like(t, setpoint)
    _, y = forced_response(closed_loop, T=t, U=u)
    error = setpoint - y

    overshoot = float(np.max(y) - setpoint)
    tolerance = plant.settling_tolerance_rad
    try:
        settling_idx = np.argmax(np.abs(error) < tolerance)
        settling_time = (
            float(t[settling_idx])
            if np.abs(error[settling_idx]) < tolerance
            else simulation.duration_s
        )
    except ValueError:  # pragma: no cover
        settling_time = simulation.duration_s
    ise = float(np.trapezoid(error**2, t))

    gust_detector = inputs.gust_detector
    adaptive_cpg = inputs.adaptive_cpg
    moe_router = inputs.moe_router

    detection_latency = float(max(gust_detector.latency_ms, 0.1))
    detector_gain = min(gust_detector.sensitivity * (gust_detector.bandwidth_hz / 1200.0), 1.1)
    gust_rejection_pct = min(adaptive_cpg.target_rejection_pct * detector_gain, 0.95)
    energy_baseline = float(adaptive_cpg.energy_baseline_j)
    energy_reduction = min(max(adaptive_cpg.energy_reduction_pct, 0.0), 0.95)
    energy_consumed = energy_baseline * (1.0 - energy_reduction)
    lyapunov_margin = float(adaptive_cpg.lyapunov_margin)
    moe_switch_penalty = moe_router.switch_cost_weight * moe_router.switch_events
    moe_latency = min(
        moe_router.latency_budget_ms * (1.0 + 0.02 * moe_router.switch_events),
        moe_router.latency_budget_ms * 1.5,
    )
    moe_energy = moe_router.energy_budget_j * (1.0 - energy_reduction)

    diffsph_metrics = _coerce_metrics(inputs.diffsph_metrics)
    foam_metrics = _coerce_metrics(inputs.foam_metrics)

    extra_metrics: dict[str, Any] | None = None
    multi_modal_score: float | None = None

    if diffsph_metrics:
        extra_metrics = (extra_metrics or {}) | diffsph_metrics
    if foam_metrics:
        extra_metrics = (extra_metrics or {}) | foam_metrics
    if diffsph_metrics and foam_metrics:
        ratio = float(foam_metrics.get("lift_drag_ratio", 0.0))
        denom = max(abs(ratio), 1e-6)
        force_norm = float(diffsph_metrics.get("force_gradient_norm", 0.0))
        multi_modal_score = round(force_norm / denom, 6)

    return ControlAnalysisOutput(
        overshoot=float(overshoot),
        ise=float(ise),
        settling_time=float(settling_time),
        gust_detection_latency_ms=round(detection_latency, 6),
        gust_detection_bandwidth_hz=round(gust_detector.bandwidth_hz, 6),
        gust_rejection_pct=round(gust_rejection_pct, 6),
        cpg_energy_baseline_j=round(energy_baseline, 6),
        cpg_energy_consumed_j=round(energy_consumed, 6),
        cpg_energy_reduction_pct=round(energy_reduction, 6),
        lyapunov_margin=round(lyapunov_margin, 6),
        moe_switch_penalty=round(moe_switch_penalty, 6),
        moe_latency_ms=round(moe_latency, 6),
        moe_energy_j=round(moe_energy, 6),
        multi_modal_score=multi_modal_score,
        extra_metrics=extra_metrics,
        metadata={"solver": "analytic"},
    )


def _coerce_metrics(metrics: dict[str, Any] | None) -> dict[str, float] | None:
    if not metrics:
        return None
    coerced: dict[str, float] = {}
    for key, value in metrics.items():
        try:
            coerced[key] = float(value)
        except (TypeError, ValueError):  # pragma: no cover
            continue
    return coerced


__all__ = ["evaluate_control"]
