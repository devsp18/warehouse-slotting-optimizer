"""Smoke tests on synthetic data - verify the assignment optimization
correctly beats the baseline, with no dependency on Project 1's files."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.layout.build_slots import build_slots
from src.optimization.slotting import baseline_alphabetical, optimize


def _synthetic_velocity() -> pd.DataFrame:
    # 5 SKUs with sharply different demand - fast mover should get the
    # closest slot in the optimal solution.
    return pd.DataFrame(
        {
            "sku": ["Zeta", "Alpha", "Mu", "Beta", "Omega"],
            "annual_picks": [10000, 500, 200, 8000, 100],
            "velocity_rank": ["A", "C", "C", "A", "C"],
        }
    )


def test_optimal_beats_baseline():
    slots = build_slots()
    velocity = _synthetic_velocity()
    opt = optimize(slots, velocity)
    base = baseline_alphabetical(slots, velocity)
    assert opt["annual_time_sec"].sum() < base["annual_time_sec"].sum()


def test_fastest_mover_gets_closest_slot():
    slots = build_slots()
    velocity = _synthetic_velocity()
    opt = optimize(slots, velocity)
    fastest_sku = velocity.loc[velocity["annual_picks"].idxmax(), "sku"]
    fastest_slot_time = opt.loc[opt["sku"] == fastest_sku, "total_time_sec"].iloc[0]
    assert fastest_slot_time == opt["total_time_sec"].min()


def test_assignment_is_one_to_one():
    slots = build_slots()
    velocity = _synthetic_velocity()
    opt = optimize(slots, velocity)
    assert opt["slot_id"].nunique() == len(velocity)
    assert opt["sku"].nunique() == len(velocity)


if __name__ == "__main__":
    test_optimal_beats_baseline()
    test_fastest_mover_gets_closest_slot()
    test_assignment_is_one_to_one()
    print("All smoke tests passed.")
