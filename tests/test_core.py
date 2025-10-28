from __future__ import annotations

import math

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


def test_evaluate_control_with_extra_metrics() -> None:
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
