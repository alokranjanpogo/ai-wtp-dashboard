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

# ===============================
# INDUSTRIAL STYLE
# ===============================
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
# LOAD DATA SAFELY
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
ph_col = find_col("ph")
cond_col = find_col("cond")
bacteria_col = find_col("bact")

if turb_col is None or frc_col is None:
    st.error("Turbidity or FRC column not found in Excel.")
    st.write("Available Columns:", data.columns)
    st.stop()

# Convert safely
data[turb_col] = pd.to_numeric(data[turb_col], errors="coerce")
data[frc_col] = pd.to_numeric(data[frc_col], errors="coerce")
if ph_col:
    data[ph_col] = pd.to_numeric(data[ph_col], errors="coerce")
if cond_col:
    data[cond_col] = pd.to_numeric(data[cond_col], errors="coerce")

data = data.dropna(subset=[turb_col, frc_col])

# ===============================
# DYNAMIC PROCESS VALUES
# ===============================
wave = np.sin(time.time())

intake_turb = 10 + wave * 0.5
clarifier_turb = intake_turb * 0.35
filter_turb = clarifier_turb * 0.2
sump_turb = filter_turb
sump_frc = 1.0
consumer_frc = data[frc_col].mean()

clar_eff = (intake_turb - clarifier_turb) / intake_turb
filter_eff = (clarifier_turb - filter_turb) / clarifier_turb

# ===============================
# FRC STATUS (0.2–1.0 ppm)
# ===============================
st.subheader("🧪 FREE RESIDUAL CHLORINE STATUS")

if consumer_frc < 0.2:
    st.error(f"FRC: {consumer_frc:.2f} ppm → BELOW DESIRABLE LIMIT (0.2 ppm)")
elif 0.2 <= consumer_frc <= 1.0:
    st.success(f"FRC: {consumer_frc:.2f} ppm → UNDER CONTROL")
else:
    st.warning(f"FRC: {consumer_frc:.2f} ppm → ABOVE PERMISSIBLE LIMIT (1.0 ppm)")

# ===============================
# ALARM LOGIC
# ===============================
if clar_eff < 0.60 or filter_eff < 0.75 or consumer_frc < 0.2:
    st.markdown('<h2 class="blink" style="color:red;">🚨 CRITICAL SYSTEM ALARM</h2>', unsafe_allow_html=True)
elif clar_eff < 0.65 or filter_eff < 0.80:
    st.warning("⚠ MINOR DEVIATION DETECTED")
else:
    st.success("🟢 ALL SYSTEMS OPERATING NORMALLY")

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
# TURBIDITY PROFILE GRAPH
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
    marker=dict(size=12),
    fill='tozeroy'
))
fig_flow.update_layout(template="plotly_dark",
                       height=450,
                       yaxis_title="Turbidity (NTU)")
st.plotly_chart(fig_flow, use_container_width=True)

# ===============================
# WATER TOWER LEVEL
# ===============================
st.subheader("🗼 WATER TOWER LEVEL")

tower_level = 75 + np.sin(time.time()) * 5

fig_tower = go.Figure(go.Indicator(
    mode="gauge+number",
    value=tower_level,
    title={'text': "Tower Level (%)"},
    gauge={'axis': {'range': [0, 100]},
           'steps': [
               {'range': [0, 30], 'color': "red"},
               {'range': [30, 60], 'color': "orange"},
               {'range': [60, 100], 'color': "green"}
           ]}
))
fig_tower.update_layout(height=300, paper_bgcolor="#050A18")
st.plotly_chart(fig_tower, use_container_width=True)

# ===============================
# DATE-WISE TREND
# ===============================
if date_col:
    st.subheader("📅 CUSTOMER TURBIDITY TREND")
    data[date_col] = pd.to_datetime(data[date_col], errors="coerce")
    trend = data.groupby(date_col)[turb_col].mean().reset_index()

    fig_trend = px.line(trend, x=date_col, y=turb_col, markers=True)
    fig_trend.update_layout(template="plotly_dark", height=450)
    st.plotly_chart(fig_trend, use_container_width=True)

# ===============================
# GIS MAP WITH BACTERIA
# ===============================
if lat_col and lon_col:
    st.subheader("📍 CUSTOMER END QUALITY MAP")

    def classify(row):
        if bacteria_col and str(row[bacteria_col]).lower() in ["yes", "present", "1"]:
            return "Bacteria Present"
        elif row[frc_col] < 0.2 or row[turb_col] > 1.5:
            return "High Risk"
        elif row[frc_col] > 1.0:
            return "Over Chlorinated"
        else:
            return "Safe"

    data["Quality_Status"] = data.apply(classify, axis=1)

    hover_dict = {turb_col: True, frc_col: True}
    if ph_col: hover_dict[ph_col] = True
    if cond_col: hover_dict[cond_col] = True

    fig_map = px.scatter_mapbox(
        data,
        lat=lat_col,
        lon=lon_col,
        color="Quality_Status",
        hover_name=name_col,
        hover_data=hover_dict,
        zoom=12,
        height=600,
        color_discrete_map={
            "Safe": "green",
            "High Risk": "orange",
            "Over Chlorinated": "yellow",
            "Bacteria Present": "red"
        }
    )

    fig_map.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig_map, use_container_width=True)


       
