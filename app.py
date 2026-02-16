import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import datetime
import time
from streamlit_autorefresh import st_autorefresh

# Auto refresh every 3 seconds
st_autorefresh(interval=3000, key="scada_refresh")

st.set_page_config(page_title="WTP Moharda SCADA", layout="wide")

# ===============================
# INDUSTRIAL STYLE
# ===============================
st.markdown("""
<style>
body {background-color:#050A18;}
h1,h2,h3 {color:#00F5FF;}
.blink {
    animation: blinker 1s linear infinite;
}
@keyframes blinker {
    50% {opacity:0;}
}
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

if turb_col is None or frc_col is None:
    st.error("Turbidity or FRC column not found.")
    st.write("Available Columns:", data.columns)
    st.stop()

data[turb_col] = pd.to_numeric(data[turb_col], errors="coerce")
data[frc_col] = pd.to_numeric(data[frc_col], errors="coerce")
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
frc_loss = sump_frc - consumer_frc

# ===============================
# STATUS LOGIC
# ===============================
def status(val, good, warn):
    if val >= good:
        return "GREEN"
    elif val >= warn:
        return "YELLOW"
    else:
        return "RED"

clar_status = status(clar_eff, 0.65, 0.60)
filter_status = status(filter_eff, 0.80, 0.75)

if frc_loss <= 0.4:
    dist_status = "GREEN"
elif frc_loss <= 0.6:
    dist_status = "YELLOW"
else:
    dist_status = "RED"

# ===============================
# ALARM BANNER
# ===============================
if clar_status == "RED" or filter_status == "RED" or dist_status == "RED":
    st.markdown('<h2 class="blink" style="color:red;">🚨 CRITICAL SYSTEM ALARM</h2>', unsafe_allow_html=True)
elif clar_status == "YELLOW" or filter_status == "YELLOW" or dist_status == "YELLOW":
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
        gauge={
            'axis': {'range': [0, max_val]},
            'bar': {'color': "#00F5FF"},
            'bgcolor': "#111111"
        }
    ))
    fig.update_layout(height=260, paper_bgcolor="#050A18")
    return fig

with cols[0]:
    st.plotly_chart(gauge("Intake Turbidity (NTU)", intake_turb, 20), use_container_width=True)

with cols[1]:
    st.plotly_chart(gauge("Clarifier Efficiency", clar_eff, 1), use_container_width=True)

with cols[2]:
    st.plotly_chart(gauge("Filter Efficiency", filter_eff, 1), use_container_width=True)

with cols[3]:
    st.plotly_chart(gauge("Chlorine Loss", frc_loss, 1), use_container_width=True)

# ===============================
# FLOW ANIMATION
# ===============================
st.subheader("🌊 FLOW VISUALIZATION")

stages = ["Intake", "Clarifier", "Filter", "Sump"]
values = [intake_turb, clarifier_turb, filter_turb, sump_turb]

fig_flow = go.Figure()

fig_flow.add_trace(go.Scatter(
    x=stages,
    y=values,
    mode="lines+markers",
    line=dict(width=8, color="#00F5FF"),
    marker=dict(size=14)
))

index = int((time.time()*3) % 4)

fig_flow.add_trace(go.Scatter(
    x=[stages[index]],
    y=[values[index]],
    mode="markers",
    marker=dict(size=24, color="white"),
    showlegend=False
))

fig_flow.update_layout(template="plotly_dark",
                       height=450,
                       paper_bgcolor="#050A18")

st.plotly_chart(fig_flow, use_container_width=True)

# ===============================
# SUMP LEVEL
# ===============================
st.subheader("💧 SUMP LEVEL")

sump_level = int((filter_eff + np.sin(time.time())*0.05) * 100)
st.progress(sump_level)

# ===============================
# WATER TOWER LEVEL
# ===============================
st.subheader("🗼 WATER TOWER LEVEL")

tower_level = 75 + np.sin(time.time()) * 5

fig_tower = go.Figure(go.Indicator(
    mode="gauge+number",
    value=tower_level,
    title={'text': "Tower Level (%)"},
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': "#00F5FF"},
        'steps': [
            {'range': [0, 30], 'color': "red"},
            {'range': [30, 60], 'color': "orange"},
            {'range': [60, 100], 'color': "green"}
        ]
    }
))
fig_tower.update_layout(height=300, paper_bgcolor="#050A18")
st.plotly_chart(fig_tower, use_container_width=True)

# ===============================
# PARAMETER CONTROL PANEL
# ===============================
st.subheader("⚙ TREATMENT PARAMETER STATUS")

def parameter_status(name, value, low, high):
    if low <= value <= high:
        st.success(f"{name}: {value:.2f} → UNDER CONTROL")
    elif (value < low and value > low*0.8) or (value > high and value < high*1.2):
        st.warning(f"{name}: {value:.2f} → MINOR DEVIATION")
    else:
        st.error(f"{name}: {value:.2f} → OUT OF RANGE")

parameter_status("Intake Turbidity", intake_turb, 0, 15)
parameter_status("Clarifier Efficiency", clar_eff, 0.60, 1.0)
parameter_status("Filter Efficiency", filter_eff, 0.75, 1.0)
parameter_status("Chlorine Loss", frc_loss, 0.0, 0.5)

# ===============================
# DATE-WISE TURBIDITY TREND
# ===============================
if date_col:
    st.subheader("📅 CUSTOMER TURBIDITY TREND")
    data[date_col] = pd.to_datetime(data[date_col], errors="coerce")
    trend = data.groupby(date_col)[turb_col].mean().reset_index()

    fig_trend = px.line(trend, x=date_col, y=turb_col, markers=True)
    fig_trend.update_layout(template="plotly_dark",
                            height=450,
                            paper_bgcolor="#050A18")
    st.plotly_chart(fig_trend, use_container_width=True)

# ===============================
# GIS MAP
# ===============================
if lat_col and lon_col:
    st.subheader("📍 CUSTOMER GIS RISK MAP")

    def risk(row):
        if row[frc_col] < 0.2 or row[turb_col] > 1.5:
            return "High Risk"
        elif row[frc_col] < 0.3:
            return "Moderate"
        else:
            return "Safe"

    data["Risk"] = data.apply(risk, axis=1)

    fig_map = px.scatter_mapbox(
        data,
        lat=lat_col,
        lon=lon_col,
        color="Risk",
        hover_name=name_col,
        zoom=12,
        height=600,
        color_discrete_map={
            "Safe": "green",
            "Moderate": "orange",
            "High Risk": "red"
        }
    )

    fig_map.update_layout(mapbox_style="open-street-map",
                          paper_bgcolor="#050A18")
    st.plotly_chart(fig_map, use_container_width=True)

