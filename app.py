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

sump_turb = clearwater_turb

clar_eff = (intake_turb - clarifier_turb) / intake_turb

filter_eff_list = []
for i in range(1,7):
    f_avg = turb[f"Filter {i}"].mean()
    eff = (clarifier_turb - f_avg) / clarifier_turb
    filter_eff_list.append(eff)

avg_filter_eff = sum(filter_eff_list)/len(filter_eff_list)
consumer_frc = frc["Clear Water"].mean()

filter_turb_list = []
for i in range(1,7):
    f_avg = turb[f"Filter {i}"].mean()
    filter_turb_list.append(f_avg)

# ===============================
# SCADA STYLE ALARM PANEL (SAFE)
# ===============================
st.subheader("🚨 PLANT ALARM STATUS")

alarm_list = []
critical_count = 0
warning_count = 0

# Clarifier
if clar_eff < 0.5:
    alarm_list.append(("CRITICAL", f"Clarifier Efficiency LOW ({clar_eff*100:.1f}%)"))
    critical_count += 1
elif clar_eff < 0.7:
    alarm_list.append(("WARNING", f"Clarifier Efficiency Moderate ({clar_eff*100:.1f}%)"))
    warning_count += 1

# ===============================
# FILTER ALARM LOGIC (CORRECTED)
# ===============================

for i in range(1, 7):

    f_avg = turb[f"Filter {i}"].mean()
    eff = (clarifier_turb - f_avg) / clarifier_turb if clarifier_turb != 0 else 0

    # --- Turbidity Based Alarm ---
    if f_avg > 5:
        alarm_list.append(("CRITICAL", f"Filter {i} Turbidity Above 5 NTU ({f_avg:.2f})"))
        critical_count += 1

    elif f_avg > 1:
        alarm_list.append(("WARNING", f"Filter {i} Turbidity Above 1 NTU ({f_avg:.2f})"))
        warning_count += 1

    # --- Efficiency Based Alarm ---
    if eff < 0.6:
        alarm_list.append(("CRITICAL", f"Filter {i} Efficiency LOW ({eff*100:.1f}%)"))
        critical_count += 1

    elif eff < 0.8:
        alarm_list.append(("WARNING", f"Filter {i} Efficiency Moderate ({eff*100:.1f}%)"))
        warning_count += 1

# FRC
if consumer_frc < 0.2:
    alarm_list.append(("CRITICAL", f"FRC LOW ({consumer_frc:.2f} ppm)"))
    critical_count += 1
elif consumer_frc > 1.0:
    alarm_list.append(("WARNING", f"FRC HIGH ({consumer_frc:.2f} ppm)"))
    warning_count += 1

# Bacteria
total_col = next((c for c in gis.columns if "total" in c.lower()), None)
ecoli_col = next((c for c in gis.columns if "coli" in c.lower()), None)

if total_col:
    if len(gis[gis[total_col].astype(str).str.lower().isin(["present","yes","1"])]) > 0:
        alarm_list.append(("CRITICAL", "Total Coliform Detected"))
        critical_count += 1

if ecoli_col:
    if len(gis[gis[ecoli_col].astype(str).str.lower().isin(["present","yes","1"])]) > 0:
        alarm_list.append(("CRITICAL", "E. Coli Detected"))
        critical_count += 1

# ===============================
# DISPLAY
# ===============================

col1, col2, col3 = st.columns(3)

if critical_count > 0:
    col1.error("🔴 CRITICAL STATUS")
elif warning_count > 0:
    col1.warning("🟡 WARNING STATUS")
else:
    col1.success("🟢 NORMAL STATUS")

col2.metric("Critical Alarms", critical_count)
col3.metric("Warning Alarms", warning_count)

# Alarm List Display
if len(alarm_list) > 0:
    for level, message in alarm_list:
        if level == "CRITICAL":
            st.error(f"🔴 {message}")
        else:
            st.warning(f"🟡 {message}")
else:
    st.success("No Active Alarms")

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
# FILTER BED PERFORMANCE (BIS BASED)
# ===============================
st.subheader("🏗 FILTER BED PERFORMANCE (BIS Standard Based)")

filter_eff_list = []
filter_status_list = []
filter_turb_list = []

for i in range(1,7):
    f_avg = turb[f"Filter {i}"].mean()
    filter_turb_list.append(f_avg)

    # Removal efficiency
    eff = (clarifier_turb - f_avg) / clarifier_turb
    filter_eff_list.append(eff)

    # BIS compliance classification
    if f_avg <= 1:
        filter_status_list.append("Excellent")
    elif f_avg <= 5:
        filter_status_list.append("Acceptable")
    else:
        filter_status_list.append("Failure")

fc = st.columns(6)

for i in range(6):

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=filter_turb_list[i],
        title={'text': f"Filter {i+1} (NTU)"},
        gauge={
            'axis': {'range': [0, 6]},
            'steps': [
                {'range': [0, 1], 'color': 'green'},
                {'range': [1, 5], 'color': 'orange'},
                {'range': [5, 6], 'color': 'red'}
            ],
            'bar': {'color': "#00F5FF"}
        }
    ))

    fig.update_layout(height=250, paper_bgcolor="#050A18")
    fc[i].plotly_chart(fig, use_container_width=True)

    fc[i].write(f"Removal Efficiency: {filter_eff_list[i]*100:.1f}%")
    fc[i].write(f"Status: {filter_status_list[i]}")

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
# INTAKE TURBIDITY TREND (SAFE)
# ===============================
st.subheader("📈 Intake Turbidity Trend")

date_col_plant = next((c for c in plant.columns if "date" in c.lower()), None)

if date_col_plant is not None and "Intake" in turb.columns:
    try:
        turb[date_col_plant] = pd.to_datetime(turb[date_col_plant], errors='coerce')
        intake_trend = turb[[date_col_plant, "Intake"]].dropna()

        fig_intake = px.line(
            intake_trend,
            x=date_col_plant,
            y="Intake",
            markers=True,
            template="plotly_dark"
        )

        fig_intake.update_layout(
            xaxis_title="Date",
            yaxis_title="Turbidity (NTU)",
            height=400
        )

        st.plotly_chart(fig_intake, use_container_width=True)

    except Exception as e:
        st.warning("Intake trend could not be generated. Check Date column format.")

else:
    st.info("No Date column found in plant file. Showing sample trend instead.")

    fig_intake = px.line(
        y=turb["Intake"],
        template="plotly_dark"
    )
    st.plotly_chart(fig_intake, use_container_width=True)

# ===============================
# CHEMICAL DOSAGE
# ===============================
st.subheader("🧪 Recommended Dosage")
alum=max(10,min(8+1.2*intake_turb,70))
chlorine=1.5+1.2*intake_turb
c1,c2=st.columns(2)
c1.metric("Recommended Alum Dose (mg/L)",f"{alum:.1f}")
c2.metric("Recommended Chlorine Dose (mg/L)",f"{chlorine:.2f}")

# ============================================================
# AI RECOMMENDED DOSAGE PANEL (STANDARD BASED – FINAL CLEAN)
# ============================================================

st.subheader("AI Recommended Chemical Dosage (As per Standards)")

# ------------------------------------------------------------
# PLANT INPUTS
# ------------------------------------------------------------
flow_m3_hr = 1100
operating_hours = 16.5
flow_m3_day = flow_m3_hr * operating_hours

aerator_turbidity = intake_turb
current_frc = consumer_frc
conductivity_today = 283

# ============================================================
# 1️⃣ ALUM DOSING – CPHEEO JAR TEST PRACTICE
# ============================================================

alum_df = pd.read_excel("Standard_Based_Dosing_Template.xlsx",
                        sheet_name="Alum_Dosing_Standard")

turb_values = alum_df["Turbidity (NTU)"].values
std_alum = alum_df["Standard Alum Dose (mg/L)"].values
plant_alum = alum_df["Plant Current Dose (mg/L)"].values

# Interpolate standard dose at current turbidity
std_today_alum = np.interp(aerator_turbidity, turb_values, std_alum)

# AI Recommendation Logic (Standard + Performance Feedback)
ai_today_alum = std_today_alum

if clearwater_turb > 1:
    ai_today_alum *= 1.05

if not (0.2 <= current_frc <= 1):
    ai_today_alum *= 1.03

# ±10% Safety Band
lower_limit = std_today_alum * 0.9
upper_limit = std_today_alum * 1.1
ai_today_alum = max(min(ai_today_alum, upper_limit), lower_limit)

percent_change_alum = 0
if std_today_alum != 0:
    percent_change_alum = ((ai_today_alum - std_today_alum) / std_today_alum) * 100

solid_alum_kg_day = (ai_today_alum * flow_m3_day) / 1000

# ------------------------------------------------------------
# DISPLAY METRICS – ALUM
# ------------------------------------------------------------

c1, c2, c3 = st.columns(3)

c1.metric("Standard Alum Dose (mg/L)", f"{std_today_alum:.2f}")
c2.metric("AI Recommended Dose (mg/L)", f"{ai_today_alum:.2f}",
          delta=f"{percent_change_alum:.1f}%")
c3.metric("Solid Alum (kg/day)", f"{solid_alum_kg_day:,.0f}")

# ------------------------------------------------------------
# GRAPH – ALUM
# ------------------------------------------------------------

fig_alum = go.Figure()

fig_alum.add_trace(go.Scatter(
    x=turb_values,
    y=std_alum,
    mode="lines",
    name="Standard Dose (CPHEEO)",
    line=dict(color="red", width=4)
))

fig_alum.add_trace(go.Scatter(
    x=turb_values,
    y=std_alum * (ai_today_alum / std_today_alum),
    mode="lines",
    name="AI Recommended Dose",
    line=dict(color="blue", width=4)
))

fig_alum.add_trace(go.Scatter(
    x=[aerator_turbidity],
    y=[ai_today_alum],
    mode="markers",
    marker=dict(size=12, color="yellow"),
    name="Current Operating Point"
))

fig_alum.update_layout(
    template="plotly_dark",
    title="Alum Dose vs Aerator Outlet Turbidity",
    xaxis_title="Aerator Outlet Turbidity (NTU)",
    yaxis_title="Alum Dose (mg/L)",
    height=450
)

st.plotly_chart(fig_alum, use_container_width=True)

st.caption("*Alum dosing derived as per CPHEEO Manual – Jar Test Based Coagulant Optimization Practice.*")

# ------------------------------------------------------------
# ALUM REMARK
# ------------------------------------------------------------

if clearwater_turb > 1:
    st.warning("AI Suggestion: Increase alum slightly to maintain <1 NTU desirable limit.")
else:
    st.success("Alum dosing aligned with CPHEEO jar test practice.")

# ============================================================
# 2️⃣ HYPOCHLORITE DOSING – CPHEEO + AWWA
# ============================================================

hypo_df = pd.read_excel("Standard_Based_Dosing_Template.xlsx",
                        sheet_name="NaOCl_Dosing_Standard")

frc_values = hypo_df["Target FRC (mg/L)"].values
std_hypo = hypo_df["Standard NaOCl (kg/day)"].values
plant_hypo = hypo_df["Plant Current (kg/day)"].values

target_frc = 0.6

std_today_hypo = np.interp(target_frc, frc_values, std_hypo)

ai_today_hypo = std_today_hypo

if current_frc < 0.2:
    ai_today_hypo *= 1.05
elif current_frc > 1:
    ai_today_hypo *= 0.95

# ±10% Safety Band
lower_limit = std_today_hypo * 0.9
upper_limit = std_today_hypo * 1.1
ai_today_hypo = max(min(ai_today_hypo, upper_limit), lower_limit)

percent_change_hypo = 0
if std_today_hypo != 0:
    percent_change_hypo = ((ai_today_hypo - std_today_hypo) / std_today_hypo) * 100

# ------------------------------------------------------------
# DISPLAY METRICS – HYPO
# ------------------------------------------------------------

c1, c2, c3 = st.columns(3)

c1.metric("Standard NaOCl (kg/day)", f"{std_today_hypo:.0f}")
c2.metric("AI Recommended (kg/day)", f"{ai_today_hypo:.0f}",
          delta=f"{percent_change_hypo:.1f}%")
c3.metric("Current FRC (mg/L)", f"{current_frc:.2f}")

# ------------------------------------------------------------
# GRAPH – HYPO
# ------------------------------------------------------------

fig_hypo = go.Figure()

fig_hypo.add_trace(go.Scatter(
    x=frc_values,
    y=std_hypo,
    mode="lines",
    name="Standard Dose (CPHEEO/AWWA)",
    line=dict(color="red", width=4)
))

fig_hypo.add_trace(go.Scatter(
    x=frc_values,
    y=std_hypo * (ai_today_hypo / std_today_hypo),
    mode="lines",
    name="AI Recommended Dose",
    line=dict(color="blue", width=4)
))

fig_hypo.add_trace(go.Scatter(
    x=[target_frc],
    y=[ai_today_hypo],
    mode="markers",
    marker=dict(size=12, color="yellow"),
    name="Recommended Operating Point"
))

fig_hypo.update_layout(
    template="plotly_dark",
    title="NaOCl Dose vs Target FRC",
    xaxis_title="Target FRC (mg/L)",
    yaxis_title="NaOCl Dose (kg/day)",
    height=450
)

st.plotly_chart(fig_hypo, use_container_width=True)

st.caption("*Chlorination requirement calculated using CPHEEO Manual & AWWA Chlorine Mass Balance Method.*")

# ------------------------------------------------------------
# HYPO REMARK
# ------------------------------------------------------------

if current_frc < 0.2:
    st.error("AI Suggestion: Increase NaOCl dosing to maintain minimum 0.2 mg/L residual.")
elif current_frc > 1:
    st.warning("AI Suggestion: Reduce NaOCl dosing to avoid excess chlorine complaints.")
else:
    st.success("Chlorination within BIS limit (0.2–1.0 mg/L). Maintain dosing.")
# WATER TOWERS
# ===============================
st.subheader("🗼 Distribution Water Towers")
names=["Moharda WT","Zone 9 WT","Zone 3 WT","Zone 1 GSR outlet","Bagunhatu WT","Bagunnagar WT"]
tc=st.columns(3)
for i in range(6):
    tc[i%3].plotly_chart(gauge(names[i],75,100),use_container_width=True)

# ===============================
# CUSTOMER END GIS MAP (FIXED)
# ===============================
st.subheader("📍 Customer End GIS Map")

lat_col = next((c for c in gis.columns if "lat" in c.lower()), None)
lon_col = next((c for c in gis.columns if "lon" in c.lower()), None)
name_col = next((c for c in gis.columns if "name" in c.lower() or "cust" in c.lower()), None)
turb_col = next((c for c in gis.columns if "turb" in c.lower()), None)
frc_col = next((c for c in gis.columns if "frc" in c.lower()), None)
date_col = next((c for c in gis.columns if "date" in c.lower()), None)

total_col = next((c for c in gis.columns if "total" in c.lower()), None)
ecoli_col = next((c for c in gis.columns if "coli" in c.lower()), None)

# Convert numeric safely
if turb_col:
    gis[turb_col] = pd.to_numeric(gis[turb_col], errors='coerce')
if frc_col:
    gis[frc_col] = pd.to_numeric(gis[frc_col], errors='coerce')

def classify(row):
    # Bacteria priority (RED)
    if total_col and str(row[total_col]).lower() in ["present","yes","1"]:
        return "Bacteria Present"
    if ecoli_col and str(row[ecoli_col]).lower() in ["present","yes","1"]:
        return "Bacteria Present"

    # Chemical/physical deviation (YELLOW)
    if turb_col and row[turb_col] > 1.5:
        return "High Turbidity"
    if frc_col and (row[frc_col] < 0.2 or row[frc_col] > 1.0):
        return "Chlorine Deviation"

    # Safe (GREEN)
    return "Safe"

gis["Status"] = gis.apply(classify, axis=1)

if lat_col and lon_col:
    fig_map = px.scatter_mapbox(
        gis,
        lat=lat_col,
        lon=lon_col,
        hover_name=name_col,
        hover_data={
            turb_col: True,
            frc_col: True,
            total_col: True,
            ecoli_col: True
        },
        color="Status",
        color_discrete_map={
            "Safe": "green",
            "High Turbidity": "yellow",
            "Chlorine Deviation": "yellow",
            "Bacteria Present": "red"
        },
        zoom=12,
        height=600
    )

    fig_map.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig_map, use_container_width=True)


# ===============================
# SUMP LEVEL MONITORING
# ===============================
st.subheader("💧 Clear Water Sump Status")

# Given values
sump_capacity = 1500000 # litres
production_mld = 18
flow_per_hour = (production_mld * 1000000) / 24 # L/hr

# Theoretical operating level based on 1 hr residence time
sump_volume_required = flow_per_hour # 1 hr storage
sump_level_percent = (sump_volume_required / sump_capacity) * 100

# Ensure it doesn't exceed 100%
sump_level_percent = min(sump_level_percent, 100)

col1, col2, col3 = st.columns(3)

col1.metric("Sump Capacity (L)", f"{sump_capacity:,}")
col2.metric("Flow per Hour (L/hr)", f"{flow_per_hour:,.0f}")
col3.metric("Operating Level (%)", f"{sump_level_percent:.1f}%")

# Gauge representation
fig_sump = go.Figure(go.Indicator(
    mode="gauge+number",
    value=sump_level_percent,
    title={'text': "Sump Level (%)"},
    gauge={
        'axis': {'range': [0, 100]},
        'steps': [
            {'range': [0, 30], 'color': "red"},
            {'range': [30, 60], 'color': "orange"},
            {'range': [60, 100], 'color': "green"}
        ],
        'bar': {'color': "#00F5FF"}
    }
))

fig_sump.update_layout(height=350, paper_bgcolor="#050A18")
st.plotly_chart(fig_sump, use_container_width=True)

st.info("Design Residence Time: 1 Hour | Current Storage Based on 18 MLD Production")
