import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import datetime

st.set_page_config(page_title="WTP Moharda SCADA", layout="wide")

st.title("🏭 WTP MOHARDA – AI POWERED SCADA CONTROL")

# ==============================
# LOAD DATA
# ==============================
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

data[turb_col] = pd.to_numeric(data[turb_col], errors="coerce")
data[frc_col] = pd.to_numeric(data[frc_col], errors="coerce")
data = data.dropna(subset=[turb_col, frc_col])

consumer_turb = data[turb_col].mean()
consumer_frc = data[frc_col].mean()

# ==============================
# PROCESS VALUES
# ==============================
intake_turb = 11
clarifier_turb = intake_turb * 0.35
filter_turb = clarifier_turb * 0.2
sump_turb = filter_turb
sump_frc = 1.0

clar_eff = (intake_turb - clarifier_turb) / intake_turb
filter_eff = (clarifier_turb - filter_turb) / clarifier_turb
frc_loss = sump_frc - consumer_frc

# ==============================
# STATUS
# ==============================
def status(val, good, warn):
    if val >= good:
        return "GREEN"
    elif val >= warn:
        return "YELLOW"
    else:
        return "RED"

clar_status = status(clar_eff, 0.65, 0.60)
filter_status = status(filter_eff, 0.80, 0.75)
dist_status = status(1-frc_loss, 0.6, 0.4)

# ==============================
# 🔴 ALARM STRIP
# ==============================
if clar_status == "RED" or filter_status == "RED" or dist_status == "RED":
    st.error("🚨 CRITICAL PLANT CONDITION – IMMEDIATE ACTION REQUIRED")
elif clar_status == "YELLOW" or filter_status == "YELLOW" or dist_status == "YELLOW":
    st.warning("⚠ MINOR DEVIATION DETECTED")
else:
    st.success("🟢 ALL SYSTEMS NORMAL")

# ==============================
# GAUGE ROW
# ==============================
st.subheader("📊 LIVE PERFORMANCE GAUGES")

g1, g2, g3, g4 = st.columns(4)

def gauge(title, value, max_val):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        gauge={
            'axis': {'range': [0, max_val]},
            'bar': {'thickness': 0.6}
        }
    ))
    fig.update_layout(height=250)
    return fig

with g1:
    st.plotly_chart(gauge("Intake Turbidity", intake_turb, 20), use_container_width=True)

with g2:
    st.plotly_chart(gauge("Clarifier Efficiency", clar_eff, 1), use_container_width=True)

with g3:
    st.plotly_chart(gauge("Filter Efficiency", filter_eff, 1), use_container_width=True)

with g4:
    st.plotly_chart(gauge("Chlorine Loss", frc_loss, 1), use_container_width=True)

# ==============================
# TURBIDITY FLOW
# ==============================
st.subheader("🌊 TURBIDITY REDUCTION PROFILE")

stages = ["Intake", "Clarifier", "Filter", "Sump"]
values = [intake_turb, clarifier_turb, filter_turb, sump_turb]

fig_flow = go.Figure()
fig_flow.add_trace(go.Scatter(
    x=stages,
    y=values,
    mode="lines+markers",
    line=dict(width=6)
))
fig_flow.update_layout(template="plotly_dark",
                       yaxis_title="Turbidity (NTU)",
                       height=400)

st.plotly_chart(fig_flow, use_container_width=True)

# ==============================
# LOWER PANEL
# ==============================
col_left, col_right = st.columns(2)

# DATE TREND
with col_left:
    st.subheader("📅 Customer Turbidity Trend")
    if date_col:
        data[date_col] = pd.to_datetime(data[date_col], errors="coerce")
        trend = data.groupby(date_col)[turb_col].mean().reset_index()
        fig_trend = px.line(trend, x=date_col, y=turb_col)
        fig_trend.update_layout(template="plotly_dark")
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("No Date column detected.")

# GIS
with col_right:
    if lat_col and lon_col:
        st.subheader("📍 GIS Risk Map")

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
            zoom=12,
            height=400,
            color_discrete_map={
                "Safe": "green",
                "Moderate": "orange",
                "High Risk": "red"
            }
        )

        fig_map.update_layout(mapbox_style="open-street-map")
        st.plotly_chart(fig_map, use_container_width=True)





    
                             

     
