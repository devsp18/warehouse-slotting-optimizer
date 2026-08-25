# Recommendation Memo - Warehouse Slotting
**To:** Supply Chain Planning | **From:** Satyam | **Date:** ___

## Recommendation
Re-slotting to velocity-based assignment cuts annual pick time __% (___ ->
___ hours), for a one-time re-slotting cost of $___ covering __ SKU moves.

## Method
Linear assignment (Hungarian algorithm) minimizing pick-frequency-weighted
travel+pick time, using real demand velocity from the service parts
planning model.

## Assumptions (each one challengeable)
Facility layout is illustrative, not a real warehouse | Pick penalty by
level: estimated | SKU granularity: part-family level (6 families)
