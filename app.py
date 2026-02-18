import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import datetime
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
# LOAD PLANT DATA
# ===============================
plant = pd.read_excel("Book 7.xlsx", engine="openpyxl")
plant.columns = plant.columns.str.strip()

# ===============================
# LOAD GIS DATA
# ===============================
data = pd.read_excel("Gis Data.xlsx", engine="openpyxl")
data.columns = data.columns.str.strip()

# ===============================
# REAL PROCESS CALCULATION
# ===============================
turb_data = plant[plant["Parameter"].str.lower() == "turbidity"]
frc_data = plant[plant["Parameter"].str.lower() == "frc"]

intake_turb = turb_data["Intake"].mean()
clarifier_turb = turb_data["Clarifier"].mean()
clearwater_turb = turb_data["Clear Water"].mean()

clar_eff = (intake_turb - clarifier_turb) / intake_turb

filter_eff_list = []
for i in range(1, 7):
    f_avg = turb_data[f"Filter {i}"].mean()
    eff = (clarifier_turb - f_avg) / clarifier_turb
    filter_eff_list.append(eff)

avg_filter_eff = sum(filter_eff_list)/len(filter_eff_list)

consumer_frc = frc_data["Clear Water"].mean()

# ===============================
# ALARM SECTION
# ===============================
st.subheader("🚨 ALARM PANEL")

if clar_eff < 0.5:
    st.markdown('<h3 class="blink" style="color:red;">Clarifier Efficiency Poor (<50%)</h3>', unsafe_allow_html=True)

for i, eff in enumerate(filter_eff_list):
    if eff < 0.6:
        st.markdown(f'<h4 class="blink" style="color:red;">Filter {i+1} Efficiency Poor (<60%)</h4>', unsafe_allow_html=True)

if consumer_frc < 0.2:
    st.markdown('<h4 class="blink" style="color:red;">FRC Below 0.2 ppm</h4>', unsafe_allow_html=True)

if consumer_frc > 1.0:
    st.markdown('<h4 class="blink" style="color:red;">FRC Above 1.0 ppm</h4>', unsafe_allow_html=True)

# Bacterial alarm
total_coliform_col = next((c for c in data.columns if "total" in c.lower()), None)
ecoli_col = next((c for c in data.columns if "coli" in c.lower()), None)

bacteria_count = 0
if total_coliform_col:
    bacteria_count += len(data[data[total_coliform_col].astype(str).str.lower().isin(["present","yes","1"])])
if ecoli_col:
    bacteria_count += len(data[data[ecoli_col].astype(str).str.lower().isin(["present","yes","1"])])

if bacteria_count > 0:
    st.markdown(f'<h3 class="blink" style="color:red;">{bacteria_count} Bacterial Contamination Points Detected</h3>', unsafe_allow_html=True)

# ===============================
# PRODUCTION
# ===============================
st.subheader("🏭 TOTAL WATER PRODUCTION")

production_mld = 18
production_m3_hr = production_mld * 1000 / 24
production_lps = production_m3_hr * 1000 / 3600

colp = st.columns(3)
colp[0].metric("Production (MLD)", production_mld)
colp[1].metric("Flow (m³/hr)", f"{production_m3_hr:.0f}")
colp[2].metric("Flow (LPS)", f"{production_lps:.1f}")

# ===============================
# GAUGE FUNCTION
# ===============================
def gauge(title, value, max_val):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        gauge={'axis': {'range':[0,max_val]},
               'bar': {'color':"#00F5FF"}}
    ))
    fig.update_layout(height=250, paper_bgcolor="#050A18")
    return fig

# ===============================
# LIVE GAUGES
# ===============================
st.subheader("📊 LIVE PERFORMANCE")

cols = st.columns(4)
cols[0].plotly_chart(gauge("Intake Turbidity", intake_turb, 20), use_container_width=True)
cols[1].plotly_chart(gauge("Clarifier Efficiency", clar_eff, 1), use_container_width=True)
cols[2].plotly_chart(gauge("Average Filter Efficiency", avg_filter_eff, 1), use_container_width=True)
cols[3].plotly_chart(gauge("Clear Water FRC", consumer_frc, 2), use_container_width=True)

# ===============================
# FILTER GAUGES
# ===============================
st.subheader("🏗 Filter Bed Efficiency")
fc = st.columns(6)
for i in range(6):
    fc[i].plotly_chart(gauge(f"Filter {i+1}", filter_eff_list[i], 1), use_container_width=True)

# ===============================
# TURBIDITY PROFILE
# ===============================
st.subheader("🌊 Turbidity Reduction Profile")
fig_profile = go.Figure()
fig_profile.add_trace(go.Scatter(
    x=["Intake","Clarifier","Clear Water"],
    y=[intake_turb, clarifier_turb, clearwater_turb],
    mode="lines+markers"
))
fig_profile.update_layout(template="plotly_dark", height=400)
st.plotly_chart(fig_profile, use_container_width=True)

# ===============================
# INTAKE TREND
# ===============================
st.subheader("📈 Intake Turbidity Trend")
fig_intake = px.line(turb_data, y="Intake", template="plotly_dark")
st.plotly_chart(fig_intake, use_container_width=True)

# ===============================
# CHEMICAL DOSAGE
# ===============================
st.subheader("🧪 Recommended Dosage")

alum_dose = max(10, min(8 + 1.2 * intake_turb, 70))
chlorine_dose = 1.5 + 1.2 * intake_turb

cd = st.columns(2)
cd[0].metric("Recommended Alum Dose (mg/L)", f"{alum_dose:.1f}")
cd[1].metric("Recommended Chlorine Dose (mg/L)", f"{chlorine_dose:.2f}")

# ===============================
# WATER TOWERS
# ===============================
st.subheader("🗼 Water Towers")
names = ["Moharda WT","Zone 9 WT","Zone 3 WT","Zone 1 GSR outlet","Bagunhatu WT","Bagunnagar WT"]
tc = st.columns(3)
for i in range(6):
    tc[i%3].plotly_chart(gauge(names[i],75,100), use_container_width=True)

# ===============================
# CUSTOMER END GIS MAP
# ===============================
st.subheader("📍 Customer End GIS Map")

lat_col = next((c for c in data.columns if "lat" in c.lower()), None)
lon_col = next((c for c in data.columns if "lon" in c.lower()), None)
name_col = next((c for c in data.columns if "name" in c.lower() or "cust" in c.lower()), None)

if lat_col and lon_col:
    fig_map = px.scatter_mapbox(
        data,
        lat=lat_col,
        lon=lon_col,
        hover_name=name_col,
        hover_data=True,
        zoom=12,
        height=600
    )
    fig_map.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig_map, use_container_width=True)

