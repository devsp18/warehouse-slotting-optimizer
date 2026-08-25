"""Warehouse Slotting & Pick-Path Optimizer - Streamlit app."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

PROC = Path("data/processed")

st.set_page_config(page_title="Warehouse Slotting Optimizer", layout="wide")
st.title("Warehouse Slotting & Pick-Path Optimization")
st.caption(
    "Assigns part families to warehouse storage locations minimizing total "
    "annual pick time, using real demand velocity from the service-parts "
    "planning project. Facility layout is an illustrative generic "
    "distribution-center model - see Honest Limitations in the README."
)


@st.cache_data
def load(name: str) -> pd.DataFrame:
    path = PROC / f"{name}.csv"
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


optimal = load("optimal_assignment")
baseline = load("baseline_assignment")
velocity = load("sku_velocity")

if optimal.empty:
    st.warning("No processed data found. Run the pipeline first (see README).")
    st.stop()

opt_hours = optimal["annual_time_sec"].sum() / 3600
base_hours = baseline["annual_time_sec"].sum() / 3600
reduction = 100 * (base_hours - opt_hours) / base_hours

c1, c2, c3 = st.columns(3)
c1.metric("Baseline annual pick time", f"{base_hours:,.0f} hrs")
c2.metric("Optimized annual pick time", f"{opt_hours:,.0f} hrs")
c3.metric("Reduction", f"{reduction:.1f}%")

tab1, tab2 = st.tabs(["Optimal Slotting", "SKU Velocity (ABC)"])

with tab1:
    st.subheader("Optimal SKU -> slot assignment")
    st.dataframe(
        optimal[["sku", "velocity_rank", "annual_picks", "slot_id", "total_time_sec"]]
        .sort_values("annual_picks", ascending=False),
        hide_index=True,
    )
    st.caption(
        "Fastest-moving SKUs are assigned the closest, ground-level slots "
        "to the dock - the golden-zone principle, applied via optimal "
        "assignment rather than manual rule-of-thumb."
    )

with tab2:
    st.subheader("SKU velocity classification (from real demand data)")
    st.bar_chart(velocity.set_index("sku")["annual_picks"])
    st.dataframe(velocity, hide_index=True)
