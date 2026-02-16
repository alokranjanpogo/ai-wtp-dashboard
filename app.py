import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import datetime

st.set_page_config(page_title="WTP Moharda SCADA", layout="wide")

st.title("🏭 WTP Moharda – AI Smart SCADA Control System")
st.markdown(f"### ⏱ {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")

# =====================================================
# LOAD CUSTOMER DATA
# =====================================================
data = pd.read_excel("Gis Data.xlsx", engine="openpyxl")
data.columns = data.columns.str.strip()

def find_col(keyword):
    for col in data.columns:
        if keyword.lower() in col.lower():
            return col
    return None

turb_col = find_col("turb")
frc_col = find_col("frc")
lat_col = find_col("lat")
lon_col = find_col("lon")
name_col = find_col("cust")

data[turb_col] = pd.to_numeric(data[turb_col], errors="coerce")
data[frc_col] = pd.to_numeric(data[frc_col], errors="coerce")
data = data.dropna(subset=[turb_col, frc_col])

consumer_turb = data[turb_col].mean()
consumer_frc = data[frc_col].mean()

# =====================================================
# PLANT VALUES
# =====================================================
intake_turb = 10.5
clarifier_turb = intake_turb * 0.35
filter_turb = clarifier_turb * 0.2
sump_frc = 1.0

clar_eff = (intake_turb - clarifier_turb) / intake_turb
filter_eff = (clarifier_turb - filter_turb) / clarifier_turb
frc_loss = sump_frc - consumer_frc

# =====================================================
# STATUS LOGIC
# =====================================================
def get_status(value, good, warn):
    if value >= good:
        return "GREEN"
    elif value >= warn:
        return "YELLOW"
    else:
        return "RED"

clar_status = get_status(clar_eff, 0.65, 0.60)
filter_status = get_status(filter_eff, 0.80, 0.75)

if frc_loss <= 0.4:
    dist_status = "GREEN"
elif frc_loss <= 0.6:
    dist_status = "YELLOW"
else:
    dist_status = "RED"

# =====================================================
# BLINKING CSS
# =====================================================
st.markdown("""
<style>
.blink {
  animation: blinker 1s linear infinite;
}
@keyframes blinker {
  50% { opacity: 0; }
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# PLANT IMAGE WITH OVERLAY CIRCLES
# =====================================================
st.subheader("📍 Plant Process Overview")

fig = go.Figure()

fig.add_layout_image(
    dict(
        source="plant_flow.png",
        xref="paper",
        yref="paper",
        x=0,
        y=1,
        sizex=1,
        sizey=1,
        sizing="stretch",
        opacity=0.9,
        layer="below"
    )
)

# Add colored indicators
def add_indicator(x, y, status):
    color_map = {"GREEN": "green", "YELLOW": "orange", "RED": "red"}
    fig.add_trace(go.Scatter(
        x=[x], y=[y],
        mode="markers",
        marker=dict(size=20, color=color_map[status]),
        showlegend=False
    ))

# Approximate positions on image
add_indicator(0.3, 0.6, clar_status) # Clarifier
add_indicator(0.4, 0.45, filter_status) # Filter
add_indicator(0.75, 0.35, dist_status) # Distribution

fig.update_xaxes(visible=False)
fig.update_yaxes(visible=False)
fig.update_layout(height=500)

st.plotly_chart(fig, use_container_width=True)

# =====================================================
# STATUS PANELS
# =====================================================
st.subheader("🚦 Section Status")

col1, col2, col3 = st.columns(3)

def show_status(label, status):
    if status == "GREEN":
        st.success(f"🟢 {label}")
    elif status == "YELLOW":
        st.warning(f"🟡 {label}")
    else:
        st.markdown(f'<p class="blink">🔴 {label} - CRITICAL</p>', unsafe_allow_html=True)

with col1:
    show_status("Clarifier", clar_status)

with col2:
    show_status("Filter", filter_status)

with col3:
    show_status("Distribution", dist_status)

# =====================================================
# TURBIDITY FLOW GRAPH
# =====================================================
st.subheader("📈 Turbidity Flow")

stages = ["Intake", "Clarifier", "Filter", "Customer"]
values = [intake_turb, clarifier_turb, filter_turb, consumer_turb]

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=stages, y=values,
                          mode='lines+markers',
                          line=dict(width=4)))
fig2.update_layout(template="plotly_dark",
                   yaxis_title="Turbidity (NTU)")

st.plotly_chart(fig2, use_container_width=True)

# =====================================================
# GIS CUSTOMER MAP
# =====================================================
st.subheader("📍 Customer-End Risk Map")

def risk(row):
    if row[frc_col] < 0.2 or row[turb_col] > 1.5:
        return "High Risk"
    elif row[frc_col] < 0.3:
        return "Moderate"
    else:
        return "Safe"

data["Risk"] = data.apply(risk, axis=1)

color_map = {
    "Safe": "green",
    "Moderate": "orange",
    "High Risk": "red"
}

fig3 = px.scatter_mapbox(
    data,
    lat=lat_col,
    lon=lon_col,
    color="Risk",
    hover_name=name_col,
    zoom=12,
    height=500,
    color_discrete_map=color_map
)

fig3.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig3, use_container_width=True)

# =====================================================
# ALARM PANEL
# =====================================================
st.subheader("🚨 Alarm Panel")

if clar_status == "RED":
    st.markdown('<p class="blink">Clarifier Efficiency Critical</p>', unsafe_allow_html=True)
if filter_status == "RED":
    st.markdown('<p class="blink">Filter Efficiency Critical</p>', unsafe_allow_html=True)
if dist_status == "RED":
    st.markdown('<p class="blink">Distribution Chlorine Loss High</p>', unsafe_allow_html=True)
if clar_status == filter_status == dist_status == "GREEN":
    st.success("No Active Critical Alarms")




