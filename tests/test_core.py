from __future__ import annotations

import math

from unittest import mock

from ctrltest_mcp.core import evaluate_control
from ctrltest_mcp.models import (
    AdaptiveCPGConfig,
    ControlAnalysisInput,
    ControlPlant,
    ControlSimulation,
    GustDetectorConfig,
    MoERouterConfig,
    PIDGains,
)


def test_evaluate_control_returns_metrics() -> None:
    """Smoke-test the default PID analysis so learners can see the basics."""
    request = ControlAnalysisInput(
        plant=ControlPlant(
            natural_frequency_hz=5.0,
            damping_ratio=0.6,
            settling_tolerance_rad=0.02,
            trim_setpoint=0.0,
        ),
        gains=PIDGains(kp=0.8, ki=0.05, kd=0.02),
        simulation=ControlSimulation(duration_s=2.0, sample_points=200),
        setpoint=0.3,
        gust_detector=GustDetectorConfig(),
        adaptive_cpg=AdaptiveCPGConfig(),
        moe_router=MoERouterConfig(),
    )

    output = evaluate_control(request)

    assert math.isfinite(output.overshoot)
    assert output.settling_time <= request.simulation.duration_s
    assert output.extra_metrics is None
    assert output.multi_modal_score is None
    assert output.metadata == {"solver": "analytic"}


def test_evaluate_control_with_extra_metrics() -> None:
    """Show how diffSPH/Foam-Agent outputs can be injected into the report."""
    request = ControlAnalysisInput(
        plant=ControlPlant(
            natural_frequency_hz=4.0,
            damping_ratio=0.5,
            settling_tolerance_rad=0.02,
            trim_setpoint=0.0,
        ),
        gains=PIDGains(kp=1.0, ki=0.2, kd=0.1),
        diffsph_metrics={"force_gradient_norm": 2.0},
        foam_metrics={"lift_drag_ratio": 0.5},
    )

    output = evaluate_control(request)
    assert output.extra_metrics is not None
    assert output.multi_modal_score is not None


def test_evaluate_control_uses_pteracontrols_when_available() -> None:
    request = ControlAnalysisInput(
        plant=ControlPlant(natural_frequency_hz=3.5, damping_ratio=0.4),
        gains=PIDGains(kp=0.6, ki=0.1, kd=0.05),
    )

    high_fidelity = ControlAnalysisOutput(
        overshoot=0.01,
        ise=0.02,
        settling_time=1.0,
        gust_detection_latency_ms=0.9,
        gust_detection_bandwidth_hz=1200.0,
        gust_rejection_pct=0.6,
        cpg_energy_baseline_j=12.0,
        cpg_energy_consumed_j=6.0,
        cpg_energy_reduction_pct=0.5,
        lyapunov_margin=0.1,
        moe_switch_penalty=0.2,
        moe_latency_ms=10.0,
        moe_energy_j=5.0,
        metadata={"solver": "pteracontrols"},
    )

    with mock.patch("ctrltest_mcp.core.is_available", return_value=True), mock.patch(
        "ctrltest_mcp.core.run_high_fidelity", return_value=high_fidelity
    ):
        output = evaluate_control(request)

    assert output.metadata == {"solver": "pteracontrols"}
