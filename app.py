import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime
import time

st.set_page_config(page_title="WTP Moharda SCADA", layout="wide")

# ===============================
# REAL TIME CLOCK
# ===============================
st.markdown(f"### ⏱ {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")

st.title("🏭 WTP Moharda – AI Smart SCADA Control Panel")

# ===============================
# LOAD CUSTOMER DATA
# ===============================
data = pd.read_excel("Gis Data.xlsx", engine="openpyxl")
data.columns = data.columns.str.strip()

def find_col(keyword):
    for col in data.columns:
        if keyword.lower() in col.lower():
            return col
    return None

turb_col = find_col("turb")
frc_col = find_col("frc")

data[turb_col] = pd.to_numeric(data[turb_col], errors="coerce")
data[frc_col] = pd.to_numeric(data[frc_col], errors="coerce")
data = data.dropna(subset=[turb_col, frc_col])

consumer_turb = data[turb_col].mean()
consumer_frc = data[frc_col].mean()

# ===============================
# PLANT VALUES
# ===============================
intake_turb = 10.5
clarifier_turb = intake_turb * 0.35
filter_turb = clarifier_turb * 0.2
sump_frc = 1.0

clar_eff = (intake_turb - clarifier_turb) / intake_turb
filter_eff = (clarifier_turb - filter_turb) / clarifier_turb
frc_loss = sump_frc - consumer_frc

# ===============================
# STATUS LOGIC
# ===============================
def status_logic(value, good, warn):
    if value >= good:
        return "GREEN"
    elif value >= warn:
        return "YELLOW"
    else:
        return "RED"

clar_status = status_logic(clar_eff, 0.65, 0.60)
filter_status = status_logic(filter_eff, 0.80, 0.75)

if frc_loss <= 0.4:
    dist_status = "GREEN"
elif frc_loss <= 0.6:
    dist_status = "YELLOW"
else:
    dist_status = "RED"

# ===============================
# SCADA IMAGE BACKGROUND
# ===============================
st.subheader("📍 Plant Live Overview")

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
        opacity=0.8,
        layer="below"
    )
)

fig.update_xaxes(visible=False)
fig.update_yaxes(visible=False)
fig.update_layout(height=500)

st.plotly_chart(fig, use_container_width=True)

# ===============================
# STATUS PANELS
# ===============================
st.subheader("🚦 Live Section Status")

col1, col2, col3 = st.columns(3)

def show_alarm(label, status):
    if status == "GREEN":
        st.success(f"🟢 {label}")
    elif status == "YELLOW":
        st.warning(f"🟡 {label} – Minor Deviation")
    else:
        st.error(f"🔴 {label} – CRITICAL")

with col1:
    show_alarm("Clarifier", clar_status)

with col2:
    show_alarm("Filter Bed", filter_status)

with col3:
    show_alarm("Distribution", dist_status)

# ===============================
# TURBIDITY FLOW GRAPH
# ===============================
st.subheader("📈 Turbidity Flow")

stages = ["Intake", "Clarifier", "Filter", "Customer"]
values = [intake_turb, clarifier_turb, filter_turb, consumer_turb]

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=stages, y=values, mode='lines+markers'))
fig2.update_layout(template="plotly_dark",
                   yaxis_title="Turbidity (NTU)")

st.plotly_chart(fig2, use_container_width=True)

# ===============================
# CHLORINE DECAY GRAPH
# ===============================
st.subheader("🧪 Chlorine Monitoring")

frc_stages = ["Sump", "Customer"]
frc_values = [sump_frc, consumer_frc]

fig3 = go.Figure()
fig3.add_trace(go.Bar(x=frc_stages, y=frc_values))
fig3.update_layout(template="plotly_dark",
                   yaxis_title="FRC (ppm)")

st.plotly_chart(fig3, use_container_width=True)

# ===============================
# ALARM HISTORY
# ===============================
st.subheader("🚨 Alarm Log")

alarms = []

if clar_status == "RED":
    alarms.append("Clarifier Efficiency Critical")
if filter_status == "RED":
    alarms.append("Filter Efficiency Critical")
if dist_status == "RED":
    alarms.append("Distribution Chlorine Loss High")

if alarms:
    for a in alarms:
        st.error(a)
else:
    st.success("No Active Critical Alarms")

