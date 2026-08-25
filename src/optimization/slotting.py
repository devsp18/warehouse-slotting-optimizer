"""Assign SKUs to warehouse slots minimizing total expected annual pick time.

This is a linear assignment problem: minimize sum(picks_i * time_ij) over
all SKU-to-slot assignments, one slot per SKU. Solved exactly with the
Hungarian algorithm (scipy.optimize.linear_sum_assignment) - optimal, not
a heuristic.

When there are more slots than SKUs (the realistic case), each SKU still
gets exactly one slot; unused slots are simply not assigned to any SKU.
This is handled by only optimizing over the top-N candidate slots (N = SKU
count) with lowest total_time, since assigning to a farther unused slot is
never optimal for any SKU under a monotonic cost structure - proven by
construction, not assumed.

Output: data/processed/optimal_assignment.csv, data/processed/baseline_assignment.csv
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy.optimize import linear_sum_assignment

CONFIG = yaml.safe_load(Path("config.yaml").read_text())
PROC = Path("data/processed")


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    slots = pd.read_csv(PROC / "slots.csv")
    velocity = pd.read_csv(PROC / "sku_velocity.csv")
    return slots, velocity


def optimize(slots: pd.DataFrame, velocity: pd.DataFrame) -> pd.DataFrame:
    n_sku = len(velocity)
    # candidate pool: the n_sku cheapest slots (sufficient - see module docstring)
    candidates = slots.nsmallest(n_sku, "total_time_sec").reset_index(drop=True)
    cost_matrix = np.outer(
        velocity["annual_picks"].values, candidates["total_time_sec"].values
    )
    sku_idx, slot_idx = linear_sum_assignment(cost_matrix)

    rows = []
    for si, ti in zip(sku_idx, slot_idx):
        rows.append(
            {
                "sku": velocity.iloc[si]["sku"],
                "annual_picks": velocity.iloc[si]["annual_picks"],
                "velocity_rank": velocity.iloc[si]["velocity_rank"],
                "slot_id": candidates.iloc[ti]["slot_id"],
                "total_time_sec": candidates.iloc[ti]["total_time_sec"],
                "annual_time_sec": velocity.iloc[si]["annual_picks"]
                * candidates.iloc[ti]["total_time_sec"],
            }
        )
    return pd.DataFrame(rows)


def baseline_alphabetical(slots: pd.DataFrame, velocity: pd.DataFrame) -> pd.DataFrame:
    """Naive baseline: SKUs slotted alphabetically into slots in grid order
    (aisle, bay, level) - mimics a warehouse with no velocity-based slotting."""
    n_sku = len(velocity)
    sku_sorted = velocity.sort_values("sku").reset_index(drop=True)
    slot_sorted = slots.sort_values(["aisle", "bay", "level"]).head(n_sku).reset_index(drop=True)
    rows = []
    for i in range(n_sku):
        rows.append(
            {
                "sku": sku_sorted.iloc[i]["sku"],
                "annual_picks": sku_sorted.iloc[i]["annual_picks"],
                "velocity_rank": sku_sorted.iloc[i]["velocity_rank"],
                "slot_id": slot_sorted.iloc[i]["slot_id"],
                "total_time_sec": slot_sorted.iloc[i]["total_time_sec"],
                "annual_time_sec": sku_sorted.iloc[i]["annual_picks"]
                * slot_sorted.iloc[i]["total_time_sec"],
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    slots, velocity = load_inputs()
    optimal = optimize(slots, velocity)
    baseline = baseline_alphabetical(slots, velocity)

    optimal.to_csv(PROC / "optimal_assignment.csv", index=False)
    baseline.to_csv(PROC / "baseline_assignment.csv", index=False)

    opt_total = optimal["annual_time_sec"].sum()
    base_total = baseline["annual_time_sec"].sum()
    reduction_pct = 100 * (base_total - opt_total) / base_total

    print(f"Baseline (alphabetical) total annual pick time: {base_total / 3600:,.1f} hours")
    print(f"Optimal (velocity-slotted) total annual pick time: {opt_total / 3600:,.1f} hours")
    print(f"Reduction: {reduction_pct:.1f}%")

    moves = (
        optimal[["sku", "slot_id"]]
        .merge(baseline[["sku", "slot_id"]], on="sku", suffixes=("_optimal", "_baseline"))
    )
    n_moves = (moves["slot_id_optimal"] != moves["slot_id_baseline"]).sum()
    reslot_cost = n_moves * CONFIG["slotting"]["reslotting_cost_per_move_usd"]
    print(f"SKUs requiring re-slotting: {n_moves} (one-time cost ${reslot_cost:,.0f})")


if __name__ == "__main__":
    main()
