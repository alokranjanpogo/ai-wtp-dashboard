import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import datetime
import time
from streamlit_autorefresh import st_autorefresh

# Auto refresh every 2 seconds
st_autorefresh(interval=2000, key="scada_refresh")

st.set_page_config(page_title="WTP Moharda SCADA", layout="wide")

# ===============================
# CONTROL ROOM STYLE
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
.led-green {color:#00FF00;font-size:22px;}
.led-yellow {color:#FFD700;font-size:22px;}
.led-red {color:#FF0000;font-size:22px;}
</style>
""", unsafe_allow_html=True)

st.title("WTP MOHARDA – LIVE SCADA HMI PANEL")
st.markdown(f"### {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")

# ===============================
# LOAD DATA
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
lat_col = find_col("lat")
lon_col = find_col("lon")

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
# STATUS
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
dist_status = status(1-frc_loss, 0.6, 0.4)

# ===============================
# FLASHING ALARM BANNER
# ===============================
if clar_status == "RED" or filter_status == "RED" or dist_status == "RED":
    st.markdown('<h2 class="blink" style="color:red;">🚨 CRITICAL SYSTEM ALARM 🚨</h2>', unsafe_allow_html=True)
elif clar_status == "YELLOW" or filter_status == "YELLOW" or dist_status == "YELLOW":
    st.markdown('<h3 style="color:gold;">⚠ SYSTEM WARNING</h3>', unsafe_allow_html=True)
else:
    st.markdown('<h3 style="color:lime;">SYSTEM STABLE</h3>', unsafe_allow_html=True)

# ===============================
# NEON GAUGES
# ===============================
cols = st.columns(4)

def gauge(title, value, max_val):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text':title},
        gauge={
            'axis':{'range':[0,max_val]},
            'bar':{'color':"#00F5FF"},
            'bgcolor':"#111111",
        }
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
    st.plotly_chart(gauge("Chlorine Loss", frc_loss, 1), use_container_width=True)

# ===============================
# FLOW PIPE ANIMATION
# ===============================
st.subheader("FLOW VISUALIZATION")

stages = ["Intake","Clarifier","Filter","Sump"]
values = [intake_turb,clarifier_turb,filter_turb,sump_turb]

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=stages,
    y=values,
    mode="lines+markers",
    line=dict(width=8,color="#00F5FF"),
    marker=dict(size=14)
))

# Moving flow particle
index = int((time.time()*3) % 4)
fig.add_trace(go.Scatter(
    x=[stages[index]],
    y=[values[index]],
    mode="markers",
    marker=dict(size=24,color="white"),
    showlegend=False
))

fig.update_layout(template="plotly_dark",
                  height=450,
                  paper_bgcolor="#050A18")

st.plotly_chart(fig, use_container_width=True)

# ===============================
# LED STATUS LIGHTS
# ===============================
st.subheader("SECTION STATUS")

def led(label, stat):
    if stat=="GREEN":
        st.markdown(f'<span class="led-green">●</span> {label}', unsafe_allow_html=True)
    elif stat=="YELLOW":
        st.markdown(f'<span class="led-yellow">●</span> {label}', unsafe_allow_html=True)
    else:
        st.markdown(f'<span class="led-red blink">●</span> {label}', unsafe_allow_html=True)

led("Clarifier", clar_status)
led("Filter Bed", filter_status)
led("Distribution", dist_status)

# ===============================
# MOVING WATER LEVEL BAR
# ===============================
st.subheader("SUMP LEVEL")

level = int((filter_eff + np.sin(time.time())*0.05)*100)
st.progress(level)

# ===============================
# GIS MAP
# ===============================
if lat_col and lon_col:
    st.subheader("CUSTOMER GIS RISK MAP")

    def risk(row):
        if row[frc_col]<0.2 or row[turb_col]>1.5:
            return "High Risk"
        elif row[frc_col]<0.3:
            return "Moderate"
        else:
            return "Safe"

    data["Risk"]=data.apply(risk,axis=1)

    fig_map=px.scatter_mapbox(
        data,
        lat=lat_col,
        lon=lon_col,
        color="Risk",
        zoom=12,
        height=500,
        color_discrete_map={
            "Safe":"green",
            "Moderate":"orange",
            "High Risk":"red"
        }
    )

    fig_map.update_layout(mapbox_style="open-street-map",
                          paper_bgcolor="#050A18")
    st.plotly_chart(fig_map,use_container_width=True)

   

