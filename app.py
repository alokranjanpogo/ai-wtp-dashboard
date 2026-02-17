import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import datetime
import time
from streamlit_autorefresh import st_autorefresh

# ===============================
# AUTO REFRESH
# ===============================
st_autorefresh(interval=3000, key="refresh")

st.set_page_config(page_title="WTP Moharda SCADA", layout="wide")

st.title("🏭 WTP MOHARDA – LIVE SCADA PANEL")
st.markdown(f"### {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")

# ===============================
# LOAD DATA
# ===============================
try:
    data = pd.read_excel("Gis Data.xlsx", engine="openpyxl")
    data.columns = data.columns.str.strip()
except:
    st.error("Excel file not found.")
    st.stop()

def find_col(keyword):
    for col in data.columns:
        if keyword.lower() in col.lower():
            return col
    return None

turb_col = find_col("turb")
frc_col = find_col("frc")
lat_col = find_col("lat")
lon_col = find_col("lon")

if turb_col is None or frc_col is None:
    st.error("Required columns not found.")
    st.stop()

data[turb_col] = pd.to_numeric(data[turb_col], errors="coerce")
data[frc_col] = pd.to_numeric(data[frc_col], errors="coerce")
data = data.dropna(subset=[turb_col, frc_col])

# ===============================
# PROCESS VALUES (Same as Before)
# ===============================
wave = np.sin(time.time())
intake_turb = 10 + wave * 0.5
clarifier_turb = intake_turb * 0.35
filter_turb = clarifier_turb * 0.2
sump_turb = filter_turb

clar_eff = (intake_turb - clarifier_turb) / intake_turb
filter_eff = (clarifier_turb - filter_turb) / clarifier_turb
consumer_frc = data[frc_col].mean()

# ===============================
# SUMP LEVEL (UNCHANGED)
# ===============================
st.subheader("💧 SUMP LEVEL")

sump_level = int((filter_eff + np.sin(time.time()) * 0.05) * 100)
st.progress(sump_level)

# ===============================
# TURBIDITY PROFILE (UNCHANGED)
# ===============================
st.subheader("🌊 TURBIDITY REDUCTION PROFILE")

stages = ["Intake", "Clarifier", "Filter", "Sump"]
values = [intake_turb, clarifier_turb, filter_turb, sump_turb]

fig_flow = go.Figure()
fig_flow.add_trace(go.Scatter(
    x=stages,
    y=values,
    mode="lines+markers",
    line=dict(width=6),
    marker=dict(size=10),
    fill='tozeroy'
))
fig_flow.update_layout(template="plotly_dark", height=400)
st.plotly_chart(fig_flow, use_container_width=True)

# ===============================
# 6 FILTER BEDS (ONLY ADDED)
# ===============================
st.subheader("🏗 FILTER BED SECTION")

filter_cols = st.columns(6)

for i in range(6):
    eff = filter_eff + np.sin(time.time() + i) * 0.01
    with filter_cols[i]:
        st.markdown(f"**Filter {i+1}**")
        st.metric(label="Efficiency", value=f"{eff:.2f}")

# ===============================
# 6 WATER TOWERS (ONLY ADDED)
# ===============================
st.subheader("🗼 DISTRIBUTION WATER TOWERS")

tower_names = [
    "Moharda WT",
    "Zone 9 WT",
    "Zone 3 WT",
    "Zone 1 GSR outlet",
    "Bagunhatu WT",
    "Bagunnagar WT"
]

tower_cols = st.columns(6)

for i in range(6):
    level = 75 + np.sin(time.time() + i) * 5
    with tower_cols[i]:
        st.markdown(f"**{tower_names[i]}**")
        st.metric(label="Level (%)", value=f"{level:.1f}")

# ===============================
# GIS MAP (UNCHANGED)
# ===============================
if lat_col and lon_col:
    st.subheader("📍 CUSTOMER END MAP")

    fig_map = px.scatter_mapbox(
        data,
        lat=lat_col,
        lon=lon_col,
        zoom=12,
        height=500
    )

    fig_map.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig_map, use_container_width=True)

