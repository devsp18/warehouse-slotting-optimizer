# Warehouse Slotting & Pick-Path Optimization Engine

Assigns part families to storage locations in a distribution center to
minimize total annual pick time - an exact linear assignment optimization
(Hungarian algorithm), driven by real demand-velocity data from the
[service-parts-planning](../service-parts-planning) project.

**Live dashboard:** _[Streamlit link]_

*Facility layout is an illustrative generic distribution-center model - no
public source describes any specific company's actual warehouse geometry.
The optimization method and the demand-velocity data are real; the physical
layout it's applied to is explicitly a demonstration model. See Honest
Limitations below.*

---

## The business problem

Where you put a part in a warehouse determines how long it takes to pick -
put your fastest-moving parts far from the dock and you pay that cost on
every single pick, every day, forever. This project answers the question a
facility planner owns:

**Given real demand patterns, what storage assignment minimizes total
annual pick-and-travel time - and how much better is that than a naive
layout?**

## Data

| Source | What it provides | Role |
|---|---|---|
| service-parts-planning (Project 1) | Real derived monthly demand per part family | SKU pick-frequency / velocity ranking (ABC classification) |
| Generic distribution-center layout model | Aisle/bay/level grid, dock-distance geometry | The facility the optimization is applied to (illustrative, documented in config.yaml) |

## Method

**Linear assignment problem**, solved exactly via the Hungarian algorithm
(`scipy.optimize.linear_sum_assignment`) - not a rule-of-thumb or greedy
heuristic. Minimizes: sum over SKUs of (annual pick frequency x total time
to reach and pick from its assigned slot), where slot time = travel time
(Manhattan distance from dock, at a configured travel speed) + a
level-based pick-time penalty (ground level fastest, top level slowest).

Compared against a **naive alphabetical baseline** - SKUs slotted in name
order into the grid - to produce a clean, defensible "% time reduction"
headline metric.

## Results

_Filled from actual pipeline output - no fabricated numbers._

- Baseline (alphabetical) annual pick time: __ hours
- Optimized (velocity-based) annual pick time: __ hours
- Reduction: __%
- SKUs requiring physical re-slotting to implement: __ (one-time cost $__)

## Stack

Python (pandas, SciPy linear assignment) · SQL (DuckDB) · Streamlit ·
pytest - built as a companion to service-parts-planning, reusing its real
demand output rather than inventing new SKU data.

## Run order

1. Clone [service-parts-planning](../service-parts-planning) as a sibling
   directory - it provides the real demand-velocity data this project reads.
2. `pip install -r requirements.txt`
3. `python src/pipeline/derive_velocity.py`
4. `python src/db_load.py`
5. `python src/layout/build_slots.py`
6. `python src/optimization/slotting.py`
7. `streamlit run app/streamlit_app.py`

**This project requires service-parts-planning cloned as a sibling
directory** for real demand data.

## Honest limitations

- The facility layout (8 aisles x 20 bays x 4 levels, single dock) is an
  illustrative generic model - not any real company's actual warehouse
  geometry, which isn't public.
- SKU granularity is at the part-family level (6 families from Project 1),
  not individual part numbers - a real warehouse slots thousands of
  distinct SKUs; this demonstrates the method at a representative scale.
- Pick-time penalties by level and travel speed are documented estimates,
  not measured from any real facility.
- Re-slotting cost is a flat per-move estimate, not a real labor-cost model.

*Independent portfolio project. Not affiliated with any vehicle
manufacturer.*
