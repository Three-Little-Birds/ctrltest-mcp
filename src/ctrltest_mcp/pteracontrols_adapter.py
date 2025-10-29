"""Optional bridge to the PteraControls toolbox."""

from __future__ import annotations

from typing import Any, Optional

from .models import ControlAnalysisInput, ControlAnalysisOutput

try:  # pragma: no cover - optional dependency
    import pteracontrols as pc  # type: ignore
except Exception:  # pragma: no cover
    pc = None  # type: ignore


def is_available() -> bool:
    return pc is not None  # type: ignore[return-value]


def run_high_fidelity(inputs: ControlAnalysisInput) -> Optional[ControlAnalysisOutput]:
    if pc is None:  # pragma: no cover - guarded import
        return None

    try:
        payload = {
            "plant": inputs.plant.model_dump(),
            "gains": inputs.gains.model_dump(),
            "simulation": inputs.simulation.model_dump(),
            "setpoint": inputs.setpoint,
            "gust_detector": inputs.gust_detector.model_dump(),
            "adaptive_cpg": inputs.adaptive_cpg.model_dump(),
            "moe_router": inputs.moe_router.model_dump(),
            "diffsph_metrics": inputs.diffsph_metrics or {},
            "foam_metrics": inputs.foam_metrics or {},
        }
        result: Any = None
        if hasattr(pc, "evaluate_controller"):
            result = pc.evaluate_controller(payload)  # type: ignore[attr-defined]
        elif hasattr(pc, "api") and hasattr(pc.api, "evaluate_controller"):
            result = pc.api.evaluate_controller(payload)  # type: ignore[attr-defined]
        if not isinstance(result, dict):
            return None

        metadata = {
            "solver": "pteracontrols",
            "source": result.get("source", "unknown"),
        }

        return ControlAnalysisOutput(
            overshoot=float(result.get("overshoot", 0.0)),
            ise=float(result.get("ise", 0.0)),
            settling_time=float(result.get("settling_time", inputs.simulation.duration_s)),
            gust_detection_latency_ms=float(result.get("gust_detection_latency_ms", inputs.gust_detector.latency_ms)),
            gust_detection_bandwidth_hz=float(result.get("gust_detection_bandwidth_hz", inputs.gust_detector.bandwidth_hz)),
            gust_rejection_pct=float(result.get("gust_rejection_pct", inputs.adaptive_cpg.target_rejection_pct)),
            cpg_energy_baseline_j=float(result.get("cpg_energy_baseline_j", inputs.adaptive_cpg.energy_baseline_j)),
            cpg_energy_consumed_j=float(result.get("cpg_energy_consumed_j", inputs.adaptive_cpg.energy_baseline_j)),
            cpg_energy_reduction_pct=float(result.get("cpg_energy_reduction_pct", inputs.adaptive_cpg.energy_reduction_pct)),
            lyapunov_margin=float(result.get("lyapunov_margin", inputs.adaptive_cpg.lyapunov_margin)),
            moe_switch_penalty=float(result.get("moe_switch_penalty", 0.0)),
            moe_latency_ms=float(result.get("moe_latency_ms", inputs.moe_router.latency_budget_ms)),
            moe_energy_j=float(result.get("moe_energy_j", inputs.moe_router.energy_budget_j)),
            multi_modal_score=result.get("multi_modal_score"),
            extra_metrics=result.get("extra_metrics"),
            metadata=metadata,
        )
    except Exception as exc:  # pragma: no cover - safety
        raise RuntimeError(f"PteraControls evaluation failed: {exc}") from exc


__all__ = ["is_available", "run_high_fidelity"]
