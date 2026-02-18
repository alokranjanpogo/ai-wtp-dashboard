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
    data = pd.read_excel("Book 7.xlsx", engine="openpyxl")
    data.columns = data.columns.str.strip()
except Exception as e:
    st.error(f"Excel Load Error: {e}")
    st.stop()

# ===============================
# REAL CALCULATIONS
# ===============================
turb_data = data[data["Parameter"].str.lower() == "turbidity"]
frc_data = data[data["Parameter"].str.lower() == "frc"]

intake_avg = turb_data["Intake"].mean()
clarifier_avg = turb_data["Clarifier"].mean()
clearwater_avg = turb_data["Clear Water"].mean()

clar_eff = (intake_avg - clarifier_avg) / intake_avg

filter_eff_list = []
for i in range(1, 7):
    col = f"Filter {i}"
    filter_avg = turb_data[col].mean()
    eff = (clarifier_avg - filter_avg) / clarifier_avg
    filter_eff_list.append(eff)

consumer_frc = frc_data["Clear Water"].mean()

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
    st.plotly_chart(gauge("Intake Turbidity", intake_avg, 20), use_container_width=True)
with cols[1]:
    st.plotly_chart(gauge("Clarifier Efficiency", clar_eff, 1), use_container_width=True)
with cols[2]:
    st.plotly_chart(gauge("Clear Water Turbidity", clearwater_avg, 10), use_container_width=True)
with cols[3]:
    st.plotly_chart(gauge("Clear Water FRC", consumer_frc, 2), use_container_width=True)

# ===============================
# 6 FILTER BED GAUGES
# ===============================
st.subheader("🏗 FILTER BED PERFORMANCE")

filter_cols = st.columns(6)

for i in range(6):
    with filter_cols[i]:
        st.plotly_chart(gauge(f"Filter {i+1}", filter_eff_list[i], 1), use_container_width=True)

# ===============================
# TURBIDITY PROFILE (REAL)
# ===============================
st.subheader("🌊 TURBIDITY REDUCTION PROFILE")

stages = ["Intake", "Clarifier", "Clear Water"]
values = [intake_avg, clarifier_avg, clearwater_avg]

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
