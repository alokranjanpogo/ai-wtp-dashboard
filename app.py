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

# ===============================
# STYLE
# ===============================
st.markdown("""
<style>
body {background-color:#050A18;}
h1,h2,h3 {color:#00F5FF;}
.blink {animation: blinker 1s linear infinite;}
@keyframes blinker {50% {opacity:0;}}
</style>
""", unsafe_allow_html=True)

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
date_col = find_col("date")
name_col = find_col("cust")
ph_col = find_col("ph")
cond_col = find_col("cond")
total_coliform_col = find_col("total")
ecoli_col = find_col("coli")

if turb_col is None or frc_col is None:
    st.error("Required columns not found.")
    st.stop()

data[turb_col] = pd.to_numeric(data[turb_col], errors="coerce")
data[frc_col] = pd.to_numeric(data[frc_col], errors="coerce")
data = data.dropna(subset=[turb_col, frc_col])

# ===============================
# PROCESS VALUES
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
# FRC STATUS
# ===============================
st.subheader("🧪 FREE RESIDUAL CHLORINE STATUS")

if consumer_frc < 0.2:
    st.error(f"FRC: {consumer_frc:.2f} ppm → BELOW 0.2 ppm")
elif 0.2 <= consumer_frc <= 1.0:
    st.success(f"FRC: {consumer_frc:.2f} ppm → UNDER CONTROL")
else:
    st.warning(f"FRC: {consumer_frc:.2f} ppm → ABOVE 1.0 ppm")

# ===============================
# TURBIDITY PROFILE
# ===============================
st.subheader("🌊 TURBIDITY REDUCTION PROFILE")

stages = ["Intake", "Clarifier", "Filter", "Sump"]
values = [intake_turb, clarifier_turb, filter_turb, sump_turb]

fig_flow = go.Figure()
fig_flow.add_trace(go.Scatter(
    x=stages,
    y=values,
    mode="lines+markers",
    line=dict(width=6, color="#00F5FF"),
    marker=dict(size=10),
    fill='tozeroy'
))
fig_flow.update_layout(template="plotly_dark", height=400)
st.plotly_chart(fig_flow, use_container_width=True)

# ===============================
# FILTER BED SECTION (6 DIVISIONS)
# ===============================
st.subheader("🏗 FILTER BED SECTION")

filter_efficiencies = []
for i in range(6):
    eff = filter_eff + np.sin(time.time() + i) * 0.01
    filter_efficiencies.append(eff)

filter_html = """
<div style="background-color:#111111;
padding:25px;border-radius:10px;
border:2px solid #00F5FF;">
<h3 style='color:#00F5FF;text-align:center;'>FILTER BED SYSTEM</h3>
<div style="display:flex;justify-content:space-between;margin-top:20px;">
"""

for i in range(6):
    filter_html += f"""
    <div style="width:14%;
    padding:15px;
    border:1px solid #00F5FF;
    border-radius:6px;
    text-align:center;
    color:white;">
    <h4>Filter {i+1}</h4>
    <p style='font-size:20px;'>{filter_efficiencies[i]:.2f}</p>
    </div>
    """

filter_html += "</div></div>"
st.markdown(filter_html, unsafe_allow_html=True)

# ===============================
# WATER TOWERS SECTION (6 TOWERS)
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

tower_html = """
<div style="background-color:#111111;
padding:25px;border-radius:10px;
border:2px solid #00F5FF;">
<h3 style='color:#00F5FF;text-align:center;'>DISTRIBUTION STORAGE SYSTEM</h3>
<div style="display:flex;justify-content:space-between;margin-top:20px;">
"""

for i in range(6):
    level = 75 + np.sin(time.time() + i) * 5

    tower_html += f"""
    <div style="width:14%;
    padding:15px;
    border:1px solid #00F5FF;
    border-radius:6px;
    text-align:center;
    color:white;">
    <h4 style='font-size:14px;'>{tower_names[i]}</h4>
    <p style='font-size:20px;'>{level:.1f}%</p>
    </div>
    """

tower_html += "</div></div>"
st.markdown(tower_html, unsafe_allow_html=True)

# ===============================
# GIS MAP
# ===============================
if lat_col and lon_col:
    st.subheader("📍 CUSTOMER END QUALITY MAP")

    def classify(row):
        if total_coliform_col and str(row[total_coliform_col]).lower() in ["present","yes","1"]:
            return "Bacteria Present"
        if ecoli_col and str(row[ecoli_col]).lower() in ["present","yes","1"]:
            return "Bacteria Present"
        if row[frc_col] < 0.2:
            return "Low Chlorine"
        if row[frc_col] > 1.0:
            return "Over Chlorinated"
        if row[turb_col] > 1.5:
            return "High Turbidity"
        return "Safe"

    data["Quality_Status"] = data.apply(classify, axis=1)

    fig_map = px.scatter_mapbox(
        data,
        lat=lat_col,
        lon=lon_col,
        color="Quality_Status",
        zoom=12,
        height=600,
        color_discrete_map={
            "Safe": "green",
            "Low Chlorine": "orange",
            "Over Chlorinated": "yellow",
            "High Turbidity": "orange",
            "Bacteria Present": "red"
        }
    )

    fig_map.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig_map, use_container_width=True)


