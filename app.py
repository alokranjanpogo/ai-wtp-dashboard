import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime
import time

st.set_page_config(page_title="WTP Moharda SCADA", layout="wide")

# ===============================
# HEADER
# ===============================
st.title("🏭 WTP MOHARDA – SMART SCADA DASHBOARD")
st.markdown(f"### ⏱ {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")

# ===============================
# LOAD CUSTOMER DATA SAFELY
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

data[turb_col] = pd.to_numeric(data[turb_col], errors="coerce")
data[frc_col] = pd.to_numeric(data[frc_col], errors="coerce")
data = data.dropna(subset=[turb_col, frc_col])

consumer_turb = data[turb_col].mean()
consumer_frc = data[frc_col].mean()

# ===============================
# PLANT DESIGN CAPACITY (FROM FIGURE)
# ===============================
INTAKE_CAP = 684
CLARIFIER_CAP = 1200
FILTER_CAP = 200
UGR_CAP = 1000

# ===============================
# ASSUMED PROCESS VALUES
# ===============================
intake_turb = 11
clarifier_turb = intake_turb * 0.35
filter_turb = clarifier_turb * 0.2
sump_turb = filter_turb
sump_frc = 1.0

clar_eff = (intake_turb - clarifier_turb) / intake_turb
filter_eff = (clarifier_turb - filter_turb) / clarifier_turb
frc_loss = sump_frc - consumer_frc

# ===============================
# STATUS LOGIC
# ===============================
def get_status(val, good, warn):
    if val >= good:
        return "GREEN"
    elif val >= warn:
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

# ===============================
# SCADA PROCESS PANEL
# ===============================
st.subheader("🔷 PROCESS OVERVIEW")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("INTAKE", f"{intake_turb:.2f} NTU",
          delta=f"{INTAKE_CAP} m³/hr")

c2.metric("CLARIFIER", f"{clarifier_turb:.2f} NTU",
          delta=f"Eff: {clar_eff:.2f}")

c3.metric("FILTER BED", f"{filter_turb:.2f} NTU",
          delta=f"Eff: {filter_eff:.2f}")

c4.metric("SUMP", f"{sump_turb:.2f} NTU",
          delta=f"Cap: {UGR_CAP} m³")

c5.metric("CUSTOMER FRC", f"{consumer_frc:.2f} ppm",
          delta=f"Loss: {frc_loss:.2f}")

# ===============================
# TURBIDITY FLOW GRAPH (INTAKE → SUMP)
# ===============================
st.subheader("📈 TURBIDITY FLOW (INTAKE TO SUMP)")

stages = ["Intake", "Clarifier", "Filter", "Sump"]
values = [intake_turb, clarifier_turb, filter_turb, sump_turb]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=stages,
    y=values,
    mode="lines+markers",
    line=dict(width=5),
    marker=dict(size=12)
))

fig.update_layout(template="plotly_dark",
                  yaxis_title="Turbidity (NTU)",
                  height=400)

st.plotly_chart(fig, use_container_width=True)

# ===============================
# DATE-WISE CUSTOMER TREND
# ===============================
st.subheader("📊 CUSTOMER TURBIDITY TREND")

date_col = find_col("date")

if date_col:
    data[date_col] = pd.to_datetime(data[date_col], errors="coerce")
    trend = data.groupby(date_col)[turb_col].mean().reset_index()
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=trend[date_col],
                              y=trend[turb_col],
                              mode="lines"))
    fig2.update_layout(template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("No Date column available.")

# ===============================
# ANIMATED WATER INDICATOR
# ===============================
st.subheader("💧 FLOW STATUS")

flow_level = int((filter_eff) * 100)
st.progress(flow_level)

# ===============================
# ALARM PANEL (SCADA STYLE)
# ===============================
st.subheader("🚨 ALARM PANEL")

alarm_triggered = False

if clar_status == "RED":
    st.error("🔴 CLARIFIER PERFORMANCE CRITICAL")
    alarm_triggered = True

if filter_status == "RED":
    st.error("🔴 FILTER BED PERFORMANCE CRITICAL")
    alarm_triggered = True

if dist_status == "RED":
    st.error("🔴 DISTRIBUTION CHLORINE LOSS HIGH")
    alarm_triggered = True

if not alarm_triggered:
    st.success("🟢 ALL SYSTEMS OPERATING NORMALLY")

# ===============================
# GIS CUSTOMER MAP
# ===============================
lat_col = find_col("lat")
lon_col = find_col("lon")
name_col = find_col("cust")

if lat_col and lon_col:
    st.subheader("📍 CUSTOMER RISK MAP")

    def risk(row):
        if row[frc_col] < 0.2 or row[turb_col] > 1.5:
            return "High Risk"
        elif row[frc_col] < 0.3:
            return "Moderate"
        else:
            return "Safe"

    data["Risk"] = data.apply(risk, axis=1)

    import plotly.express as px
    fig3 = px.scatter_mapbox(
        data,
        lat=lat_col,
        lon=lon_col,
        color="Risk",
        hover_name=name_col,
        zoom=12,
        height=500,
        color_discrete_map={
            "Safe": "green",
            "Moderate": "orange",
            "High Risk": "red"
        }
    )

    fig3.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig3, use_container_width=True)
