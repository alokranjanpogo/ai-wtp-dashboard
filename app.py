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
# LOAD FILES
# ===============================
plant = pd.read_excel("Book 7.xlsx", engine="openpyxl")
plant.columns = plant.columns.str.strip()

gis = pd.read_excel("Gis Data.xlsx", engine="openpyxl")
gis.columns = gis.columns.str.strip()

# ===============================
# REAL PROCESS CALCULATIONS
# ===============================
turb = plant[plant["Parameter"].str.lower() == "turbidity"]
frc = plant[plant["Parameter"].str.lower() == "frc"]

intake_turb = turb["Intake"].mean()
clarifier_turb = turb["Clarifier"].mean()
clearwater_turb = turb["Clear Water"].mean()

clar_eff = (intake_turb - clarifier_turb) / intake_turb

filter_eff_list = []
for i in range(1,7):
    f_avg = turb[f"Filter {i}"].mean()
    eff = (clarifier_turb - f_avg) / clarifier_turb
    filter_eff_list.append(eff)

avg_filter_eff = sum(filter_eff_list)/len(filter_eff_list)
consumer_frc = frc["Clear Water"].mean()

# ===============================
# ADVANCED ALARM PANEL
# ===============================
st.subheader("🚨 SCADA ALARM PANEL")
alarms = []

if clar_eff < 0.5:
    alarms.append(("CRITICAL","Clarifier Efficiency Below 50%"))
elif clar_eff < 0.7:
    alarms.append(("WARNING","Clarifier Efficiency Moderate"))

for i,eff in enumerate(filter_eff_list):
    if eff < 0.6:
        alarms.append(("CRITICAL",f"Filter {i+1} Efficiency Below 60%"))
    elif eff < 0.8:
        alarms.append(("WARNING",f"Filter {i+1} Efficiency Moderate"))

if consumer_frc < 0.2:
    alarms.append(("CRITICAL","FRC Below 0.2 ppm"))
elif consumer_frc > 1.0:
    alarms.append(("WARNING","FRC Above 1.0 ppm"))

# Bacteria Alarm
total_col = next((c for c in gis.columns if "total" in c.lower()),None)
ecoli_col = next((c for c in gis.columns if "coli" in c.lower()),None)

if total_col:
    if len(gis[gis[total_col].astype(str).str.lower().isin(["present","yes","1"])])>0:
        alarms.append(("CRITICAL","Total Coliform Detected"))
if ecoli_col:
    if len(gis[gis[ecoli_col].astype(str).str.lower().isin(["present","yes","1"])])>0:
        alarms.append(("CRITICAL","E.coli Detected"))

if len(alarms)==0:
    st.success("🟢 All Parameters Within Safe Limits")
else:
    st.metric("Active Alarms",len(alarms))
    for level,msg in alarms:
        if level=="CRITICAL":
            st.markdown(f'<div style="background:#8B0000;color:white;padding:10px;border-radius:5px;">🔴 {msg}</div>',unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background:#FFA500;color:black;padding:10px;border-radius:5px;">🟡 {msg}</div>',unsafe_allow_html=True)

# ===============================
# PRODUCTION
# ===============================
st.subheader("🏭 TOTAL WATER PRODUCTION")
production_mld = 18
production_m3_hr = production_mld*1000/24
production_lps = production_m3_hr*1000/3600

colp = st.columns(3)
colp[0].metric("Production (MLD)",production_mld)
colp[1].metric("Flow (m³/hr)",f"{production_m3_hr:.0f}")
colp[2].metric("Flow (LPS)",f"{production_lps:.1f}")

# ===============================
# GAUGE FUNCTION WITH ZONES
# ===============================
def gauge(title,value,max_val,mode="normal"):
    if mode=="clarifier":
        steps=[{'range':[0,0.5],'color':'red'},
               {'range':[0.5,0.7],'color':'orange'},
               {'range':[0.7,1],'color':'green'}]
    elif mode=="filter":
        steps=[{'range':[0,0.6],'color':'red'},
               {'range':[0.6,0.8],'color':'orange'},
               {'range':[0.8,1],'color':'green'}]
    else:
        steps=[]
    fig=go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text':title},
        gauge={'axis':{'range':[0,max_val]},
               'bar':{'color':"#00F5FF"},
               'steps':steps}
    ))
    fig.update_layout(height=250,paper_bgcolor="#050A18")
    return fig

# ===============================
# LIVE GAUGES
# ===============================
st.subheader("📊 LIVE PERFORMANCE")
cols=st.columns(4)
cols[0].plotly_chart(gauge("Intake Turbidity",intake_turb,20),use_container_width=True)
cols[1].plotly_chart(gauge("Clarifier Efficiency",clar_eff,1,"clarifier"),use_container_width=True)
cols[2].plotly_chart(gauge("Average Filter Efficiency",avg_filter_eff,1,"filter"),use_container_width=True)
cols[3].plotly_chart(gauge("Clear Water FRC",consumer_frc,2),use_container_width=True)

# ===============================
# FILTER BED GAUGES
# ===============================
st.subheader("🏗 FILTER BED PERFORMANCE")
fc=st.columns(6)
for i in range(6):
    fc[i].plotly_chart(gauge(f"Filter {i+1}",filter_eff_list[i],1,"filter"),use_container_width=True)

# ===============================
# TURBIDITY PROFILE
# ===============================
st.subheader("🌊 Turbidity Reduction Profile")
fig_prof=go.Figure()
fig_prof.add_trace(go.Scatter(
    x=["Intake","Clarifier","Clear Water"],
    y=[intake_turb,clarifier_turb,clearwater_turb],
    mode="lines+markers"))
fig_prof.update_layout(template="plotly_dark",height=400)
st.plotly_chart(fig_prof,use_container_width=True)

# ===============================
# INTAKE TREND
# ===============================
st.subheader("📈 Intake Turbidity Trend")
fig_int=px.line(turb,y="Intake",template="plotly_dark")
st.plotly_chart(fig_int,use_container_width=True)

# ===============================
# CUSTOMER TURBIDITY TREND
# ===============================
date_col=next((c for c in gis.columns if "date" in c.lower()),None)
turb_col=next((c for c in gis.columns if "turb" in c.lower()),None)
if date_col and turb_col:
    gis[date_col]=pd.to_datetime(gis[date_col],errors='coerce')
    trend=gis.groupby(date_col)[turb_col].mean().reset_index()
    fig_ct=px.line(trend,x=date_col,y=turb_col,template="plotly_dark")
    st.plotly_chart(fig_ct,use_container_width=True)

# ===============================
# CHEMICAL DOSAGE
# ===============================
st.subheader("🧪 Recommended Dosage")
alum=max(10,min(8+1.2*intake_turb,70))
chlorine=1.5+1.2*intake_turb
c1,c2=st.columns(2)
c1.metric("Recommended Alum Dose (mg/L)",f"{alum:.1f}")
c2.metric("Recommended Chlorine Dose (mg/L)",f"{chlorine:.2f}")

# ===============================
# WATER TOWERS
# ===============================
st.subheader("🗼 Distribution Water Towers")
names=["Moharda WT","Zone 9 WT","Zone 3 WT","Zone 1 GSR outlet","Bagunhatu WT","Bagunnagar WT"]
tc=st.columns(3)
for i in range(6):
    tc[i%3].plotly_chart(gauge(names[i],75,100),use_container_width=True)

# ===============================
# CUSTOMER END GIS MAP
# ===============================
st.subheader("📍 Customer End GIS Map")

lat=next((c for c in gis.columns if "lat" in c.lower()),None)
lon=next((c for c in gis.columns if "lon" in c.lower()),None)
name=next((c for c in gis.columns if "name" in c.lower() or "cust" in c.lower()),None)

if turb_col:
    gis[turb_col]=pd.to_numeric(gis[turb_col],errors='coerce')
if lat and lon:
    gis["Status"]=np.where(gis[turb_col]>1.5,"High Turbidity","Safe")
    fig_map=px.scatter_mapbox(
        gis,
        lat=lat,
        lon=lon,
        hover_name=name,
        hover_data=gis.columns,
        color="Status",
        color_discrete_map={"Safe":"green","High Turbidity":"red"},
        zoom=12,
        height=600)
    fig_map.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig_map,use_container_width=True)


