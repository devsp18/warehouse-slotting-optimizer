"""Generate the warehouse slot grid and each slot's travel distance + pick
time penalty from the dock.

Output: data/processed/slots.csv
Columns: slot_id, aisle, bay, level, distance_ft, travel_time_sec, pick_penalty_sec
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

CONFIG = yaml.safe_load(Path("config.yaml").read_text())
PROC = Path("data/processed")


def build_slots() -> pd.DataFrame:
    lay = CONFIG["layout"]
    dock_x, dock_y = lay["dock_location"]
    rows = []
    for aisle in range(lay["n_aisles"]):
        aisle_x = aisle * lay["aisle_width_ft"]
        for bay in range(lay["bays_per_aisle"]):
            bay_y = bay * lay["bay_depth_ft"]
            for level in range(lay["levels_per_bay"]):
                # Manhattan distance (realistic for aisle-constrained travel)
                dist = abs(aisle_x - dock_x) + abs(bay_y - dock_y)
                travel_time = dist / CONFIG["slotting"]["travel_speed_ft_per_sec"]
                pick_penalty = lay["level_time_penalty_sec"][level]
                rows.append(
                    {
                        "slot_id": f"A{aisle:02d}-B{bay:02d}-L{level}",
                        "aisle": aisle,
                        "bay": bay,
                        "level": level,
                        "distance_ft": round(dist, 1),
                        "travel_time_sec": round(travel_time, 2),
                        "pick_penalty_sec": pick_penalty,
                        "total_time_sec": round(travel_time + pick_penalty, 2),
                    }
                )
    return pd.DataFrame(rows)


def main() -> None:
    PROC.mkdir(parents=True, exist_ok=True)
    slots = build_slots()
    slots.to_csv(PROC / "slots.csv", index=False)
    print(f"Wrote {len(slots):,} slots ({CONFIG['layout']['n_aisles']} aisles x "
          f"{CONFIG['layout']['bays_per_aisle']} bays x "
          f"{CONFIG['layout']['levels_per_bay']} levels)")
    print(f"Round-trip time range: {slots['total_time_sec'].min()}-"
          f"{slots['total_time_sec'].max()} sec")


if __name__ == "__main__":
    main()
