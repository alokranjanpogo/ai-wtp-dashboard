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
st_autorefresh(interval=3000, key="scada_refresh")

st.set_page_config(page_title="WTP Moharda SCADA", layout="wide")

st.markdown("""
<style>
body {background-color:#050A18;}
h1,h2,h3 {color:#00F5FF;}
.blink {animation: blinker 1s linear infinite;}
@keyframes blinker {50% {opacity:0;}}
</style>
""", unsafe_allow_html=True)

st.title("🏭 WTP MOHARDA – LIVE SCADA HMI PANEL")
st.markdown(f"### ⏱ {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")

# ===============================
# LOAD DATA
# ===============================
try:
    data = pd.read_excel("Gis Data.xlsx", engine="openpyxl")
    data.columns = data.columns.str.strip()
except Exception as e:
    st.error(f"Excel Load Error: {e}")
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
total_coliform_col = find_col("total")
ecoli_col = find_col("coli")

if turb_col is None or frc_col is None:
    st.error("Required Turbidity or FRC column not found.")
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
# TOTAL PRODUCTION
# ===============================
st.subheader("🏭 TOTAL WATER PRODUCTION")

production_mld = 18
production_m3_hr = production_mld * 1000 / 24
production_lps = production_m3_hr * 1000 / 3600

prod_cols = st.columns(3)
prod_cols[0].metric("Production (MLD)", f"{production_mld}")
prod_cols[1].metric("Flow (m³/hr)", f"{production_m3_hr:.0f}")
prod_cols[2].metric("Flow (LPS)", f"{production_lps:.1f}")

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
# BACTERIA CHECK
# ===============================
bacteria_present_count = 0

if total_coliform_col:
    bacteria_present_count += len(
        data[data[total_coliform_col].astype(str).str.lower().isin(["present","yes","1"])]
    )

if ecoli_col:
    bacteria_present_count += len(
        data[data[ecoli_col].astype(str).str.lower().isin(["present","yes","1"])]
    )

if bacteria_present_count > 0:
    st.markdown(
        f'<h2 class="blink" style="color:red;">🚨 {bacteria_present_count} BACTERIAL CONTAMINATION POINTS DETECTED</h2>',
        unsafe_allow_html=True
    )

# ===============================
# LIVE GAUGES
# ===============================
st.subheader("📊 LIVE PERFORMANCE GAUGES")

cols = st.columns(4)

def gauge(title, value, max_val):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        gauge={'axis': {'range': [0, max_val]},
               'bar': {'color': "#00F5FF"}}
    ))
    fig.update_layout(height=250, paper_bgcolor="#050A18")
    return fig

with cols[0]:
    st.plotly_chart(gauge("Intake Turbidity", intake_turb, 20), use_container_width=True)
with cols[1]:
    st.plotly_chart(gauge("Clarifier Efficiency", clar_eff, 1), use_container_width=True)
with cols[2]:
    st.plotly_chart(gauge("Filter Efficiency", filter_eff, 1), use_container_width=True)
with cols[3]:
    st.plotly_chart(gauge("Consumer FRC", consumer_frc, 2), use_container_width=True)

# ===============================
# 6 FILTER BED GAUGES
# ===============================
st.subheader("🏗 FILTER BED PERFORMANCE")

filter_cols = st.columns(6)

for i in range(6):
    eff = filter_eff + np.sin(time.time() + i) * 0.01
    with filter_cols[i]:
        st.plotly_chart(gauge(f"Filter {i+1}", eff, 1), use_container_width=True)

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
    line=dict(width=6),
    marker=dict(size=12),
    fill='tozeroy'
))
fig_flow.update_layout(template="plotly_dark", height=450)
st.plotly_chart(fig_flow, use_container_width=True)

# ===============================
# CHEMICAL DOSE RECOMMENDATION
# ===============================
st.subheader("🧪 CHEMICAL DOSE RECOMMENDATION")

alum_dose = max(10, min(8 + 1.2 * intake_turb, 70))
chlorine_dose = 1.5 + 1.2 * intake_turb

chem_cols = st.columns(2)
chem_cols[0].metric("Recommended Alum Dose (mg/L)", f"{alum_dose:.1f}")
chem_cols[1].metric("Recommended Chlorine Dose (mg/L)", f"{chlorine_dose:.2f}")

dose_range = np.linspace(10, 70, 30)
eff_response = 0.5 + 0.005 * dose_range - 0.00003 * (dose_range - 40)**2

fig_dose = go.Figure()
fig_dose.add_trace(go.Scatter(
    x=dose_range,
    y=eff_response,
    mode="lines"
))
fig_dose.update_layout(template="plotly_dark",
                       xaxis_title="Alum Dose (mg/L)",
                       yaxis_title="Clarifier Efficiency",
                       height=400)
st.plotly_chart(fig_dose, use_container_width=True)

# ===============================
# 6 WATER TOWERS
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

tower_cols = st.columns(3)

for i in range(6):
    level = 75 + np.sin(time.time() + i) * 5
    with tower_cols[i % 3]:
        fig_tower = go.Figure(go.Indicator(
            mode="gauge+number",
            value=level,
            title={'text': tower_names[i]},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "#00F5FF"}}
        ))
        fig_tower.update_layout(height=300, paper_bgcolor="#050A18")
        st.plotly_chart(fig_tower, use_container_width=True)

# ===============================
# INTAKE TURBIDITY TREND
# ===============================
st.subheader("📈 Intake Turbidity Trend")

intake_trend = 10 + np.sin(np.linspace(0, 5, 30)) * 2

fig_intake = go.Figure()
fig_intake.add_trace(go.Scatter(y=intake_trend, mode="lines"))
fig_intake.update_layout(template="plotly_dark", height=400)
st.plotly_chart(fig_intake, use_container_width=True)

# ===============================
# CUSTOMER TURBIDITY TREND
# ===============================
if date_col:
    st.subheader("📅 Customer Turbidity Trend")
    data[date_col] = pd.to_datetime(data[date_col], errors="coerce")
    trend = data.groupby(date_col)[turb_col].mean().reset_index()

    fig_trend = px.line(trend, x=date_col, y=turb_col, markers=True)
    fig_trend.update_layout(template="plotly_dark", height=450)
    st.plotly_chart(fig_trend, use_container_width=True)

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
        height=650,
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


