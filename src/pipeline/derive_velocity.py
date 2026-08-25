"""Derive SKU (part family) pick velocity from Project 1's real demand
output. This is the honesty-critical link: velocity must come from actual
derived demand data, not an invented ranking.

Output: data/processed/sku_velocity.csv
Columns: sku, annual_picks, velocity_rank (A/B/C)
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

CONFIG = yaml.safe_load(Path("config.yaml").read_text())
PROC = Path("data/processed")


def load_demand() -> pd.DataFrame:
    primary = Path(CONFIG["data"]["demand_source"])
    if primary.exists():
        print(f"Using real demand data from {primary}")
        return pd.read_csv(primary)
    fallback = Path("data/raw/demand_fallback.csv")
    print(
        f"WARNING: {primary} not found (Project 1 repo not alongside this one?). "
        f"Falling back to {fallback} - velocity ranking will NOT reflect real demand. "
        "This must be disclosed if used in any published results."
    )
    if not fallback.exists():
        raise FileNotFoundError(
            "Neither the Project 1 demand file nor a fallback exists. "
            "Place service-parts-planning alongside this repo, or supply "
            "data/raw/demand_fallback.csv manually."
        )
    return pd.read_csv(fallback)


def classify_abc(annual_picks: pd.Series) -> pd.Series:
    """Standard 80/15/5 ABC classification by cumulative demand share."""
    sorted_desc = annual_picks.sort_values(ascending=False)
    cum_share = sorted_desc.cumsum() / sorted_desc.sum()
    rank = pd.Series(index=sorted_desc.index, dtype="object")
    rank[cum_share <= 0.80] = "A"
    rank[(cum_share > 0.80) & (cum_share <= 0.95)] = "B"
    rank[cum_share > 0.95] = "C"
    return rank.reindex(annual_picks.index)


def main() -> None:
    PROC.mkdir(parents=True, exist_ok=True)
    demand = load_demand()
    # Project 1's demand is (region, part_family, month, units) - collapse
    # to a single national SKU-level annual pick count per part_family.
    annual = (
        demand.groupby("part_family")["units"]
        .sum()
        .reset_index()
        .rename(columns={"part_family": "sku", "units": "annual_picks"})
    )
    annual["annual_picks"] = (
        annual["annual_picks"] * CONFIG["slotting"]["picks_per_unit_demand"]
    ).round(0)
    annual["velocity_rank"] = classify_abc(annual["annual_picks"])
    annual = annual.sort_values("annual_picks", ascending=False).reset_index(drop=True)
    annual.to_csv(PROC / "sku_velocity.csv", index=False)
    print(annual.to_string(index=False))


if __name__ == "__main__":
    main()
