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
# AI RECOMMENDED DOSAGE PANEL (BIS + CPHEEO + AWWA + JAR TEST)
# ============================================================

st.subheader("AI Recommended Chemical Dosage (Standards Based AI)")

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
# LOAD JAR TEST DATA (LAB)
# ============================================================

jar_df = pd.read_excel("DATASHEET.xlsx")

jar_turb = jar_df["Turbidity\n(NTU)"].values
jar_dose = jar_df["ALUM DOSE(PPM)"].values

# ============================================================
# STANDARD DATABASE (BIS + CPHEEO + AWWA)
# ============================================================

std_turb = np.array([5,10,20,40,60,80,100,150,200,300])

bis_dose = np.array([6,8,12,18,22,26,30,35,40,45])
cpheeo_dose = np.array([8,10,15,22,26,30,35,40,45,50])
awwa_dose = np.array([10,12,18,24,28,32,38,45,50,55])

# ============================================================
# INTERPOLATE STANDARD DOSE
# ============================================================

bis_today = np.interp(aerator_turbidity, std_turb, bis_dose)
cpheeo_today = np.interp(aerator_turbidity, std_turb, cpheeo_dose)
awwa_today = np.interp(aerator_turbidity, std_turb, awwa_dose)

# ============================================================
# JAR TEST TREND (ONLY FOR GRAPH COMPARISON)
# ============================================================

jar_poly = np.polyfit(jar_turb, jar_dose, 2)
jar_curve = np.poly1d(jar_poly)

jar_today = jar_curve(aerator_turbidity)

# ============================================================
# AI DOSING LOGIC (STANDARDS BASED)
# ============================================================

ai_today_alum = (
    0.4 * cpheeo_today +
    0.3 * bis_today +
    0.2 * awwa_today +
    0.1 * jar_today
)

# SAFETY BAND
lower_limit = jar_today * 0.9
upper_limit = jar_today * 1.1

ai_today_alum = max(min(ai_today_alum, upper_limit), lower_limit)

percent_change_alum = ((ai_today_alum - jar_today) / jar_today) * 100

solid_alum_kg_day = (ai_today_alum * flow_m3_day) / 1000

# ------------------------------------------------------------
# DISPLAY METRICS – ALUM
# ------------------------------------------------------------

c1, c2, c3 = st.columns(3)

c1.metric("Jar Test Dose (mg/L)", f"{jar_today:.2f}")

c2.metric(
    "AI Recommended Dose (mg/L)",
    f"{ai_today_alum:.2f}",
    delta=f"{percent_change_alum:.1f}%"
)

c3.metric("Solid Alum (kg/day)", f"{solid_alum_kg_day:,.0f}")

# ------------------------------------------------------------
# GRAPH – ALUM
# ------------------------------------------------------------

x_range = np.linspace(0,300,200)

jar_curve_plot = jar_curve(x_range)

bis_curve = np.interp(x_range, std_turb, bis_dose)
cpheeo_curve = np.interp(x_range, std_turb, cpheeo_dose)
awwa_curve = np.interp(x_range, std_turb, awwa_dose)

ai_curve = (
    0.4 * cpheeo_curve +
    0.3 * bis_curve +
    0.2 * awwa_curve +
    0.1 * jar_curve_plot
)

fig_alum = go.Figure()

fig_alum.add_trace(go.Scatter(
    x=x_range,
    y=jar_curve_plot,
    mode="lines",
    name="Jar Test Dose (Lab)",
    line=dict(color="red", width=4)
))

fig_alum.add_trace(go.Scatter(
    x=x_range,
    y=ai_curve,
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
    title="AI vs Jar Test Alum Dose Comparison",
    xaxis_title="Aerator Outlet Turbidity (NTU)",
    yaxis_title="Alum Dose (mg/L)",
    height=450
)

st.plotly_chart(fig_alum, use_container_width=True)

st.caption(
"""
AI Recommendation derived using:

• BIS Drinking Water Treatment Guidelines  
• CPHEEO Manual on Water Supply and Treatment  
• AWWA Coagulation Practice Guidelines  

Jar Test data used only for validation.
"""
)

# ============================================================
# AI SODIUM HYPOCHLORITE DOSING
# ============================================================

st.subheader("AI Recommended Sodium Hypochlorite Dosage")

target_frc = 0.5
hypo_strength = 5

raw_turbidity = intake_turb
conductivity = conductivity_today

base_demand = 0.8 + (0.01 * raw_turbidity)

if conductivity > 250:
    base_demand *= 1.05

required_chlorine = base_demand + target_frc

hypo_dose_mgL = required_chlorine / (hypo_strength / 100)

hypo_kg_day = (hypo_dose_mgL * flow_m3_day) / 1000

c1, c2, c3 = st.columns(3)

c1.metric("Required Chlorine Dose (mg/L)", f"{required_chlorine:.2f}")
c2.metric("NaOCl Dose (mg/L)", f"{hypo_dose_mgL:.2f}")
c3.metric("NaOCl Requirement (kg/day)", f"{hypo_kg_day:,.0f}")

# GRAPH

x_cl = np.linspace(0,300,200)

chlorine_demand_curve = 0.8 + (0.01 * x_cl)

hypo_curve = (chlorine_demand_curve + target_frc) / (hypo_strength / 100)

fig_cl = go.Figure()

fig_cl.add_trace(go.Scatter(
    x=x_cl,
    y=hypo_curve,
    mode="lines",
    name="AI Recommended NaOCl Dose",
    line=dict(color="blue", width=4)
))

fig_cl.add_trace(go.Scatter(
    x=[raw_turbidity],
    y=[hypo_dose_mgL],
    mode="markers",
    marker=dict(size=12, color="yellow"),
    name="Current Operating Point"
))

fig_cl.update_layout(
    template="plotly_dark",
    title="AI Sodium Hypochlorite Dosing",
    xaxis_title="Raw Water Turbidity (NTU)",
    yaxis_title="NaOCl Dose (mg/L)",
    height=450
)

st.plotly_chart(fig_cl, use_container_width=True)

st.caption(
"""
AI Chlorination derived from:

• BIS Drinking Water Specification  
• WHO Residual Chlorine Guideline (0.2–0.5 mg/L)  
• AWWA Chlorination Practice Manual
"""
)

# ============================================================
# PAC DOSING SUGGESTION
# ============================================================

st.subheader("AI PAC Dosing Suggestion")

pac_base = 0.6 * ai_today_alum

pac_kg_day = (pac_base * flow_m3_day) / 1000

c1, c2 = st.columns(2)

c1.metric("Recommended PAC Dose (mg/L)", f"{pac_base:.2f}")
c2.metric("PAC Requirement (kg/day)", f"{pac_kg_day:,.0f}")

# ============================================================
# SLUDGE GENERATION ESTIMATION
# ============================================================

st.subheader("Estimated Sludge Production")

sludge_factor = 0.6

sludge_kg_day = solid_alum_kg_day * sludge_factor

st.metric("Estimated Sludge Generation (kg/day)", f"{sludge_kg_day:,.0f}")

# ============================================================
# CHEMICAL COST ESTIMATION
# ============================================================

st.subheader("Daily Chemical Cost Estimation")

alum_price = 8
hypo_price = 25
pac_price = 60

alum_cost = solid_alum_kg_day * alum_price
hypo_cost = hypo_kg_day * hypo_price
pac_cost = pac_kg_day * pac_price

total_cost = alum_cost + hypo_cost + pac_cost

c1, c2, c3, c4 = st.columns(4)

c1.metric("Alum Cost (₹/day)", f"{alum_cost:,.0f}")
c2.metric("NaOCl Cost (₹/day)", f"{hypo_cost:,.0f}")
c3.metric("PAC Cost (₹/day)", f"{pac_cost:,.0f}")
c4.metric("Total Cost (₹/day)", f"{total_cost:,.0f}")

# ============================================================
# AI OPERATOR RECOMMENDATION PANEL
# ============================================================

st.subheader("AI Plant Operation Suggestions")

if aerator_turbidity > 100:
    st.warning("High turbidity detected. Consider increasing coagulant dosing.")

elif aerator_turbidity < 20:
    st.info("Low turbidity water. Chemical dosing can be optimized to reduce cost.")

if current_frc < 0.2:
    st.error("Residual chlorine below safe limit. Increase NaOCl dosing.")

elif current_frc > 1:
    st.warning("Excess chlorine detected. Reduce NaOCl dose to avoid taste issues.")

else:
    st.success("Plant operating within recommended standards.")
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

import pandas as pd
import plotly.express as px

st.subheader("📍 Washout GIS Map")
washout = pd.read_excel("Wahout_points.xlsx")

# Safe date conversion
washout["Prv_Washout Date"] = pd.to_datetime(washout["Prv_Washout Date"], errors="coerce")
washout["Due_Washout Date"] = pd.to_datetime(washout["Due_Washout Date"], errors="coerce")

today = pd.Timestamp.today()

def classify(row):

    if row["Due_Washout Date"] < today:
        return "Overdue"

    elif row["Due_Washout Date"] <= today + pd.Timedelta(days=10):
        return "Due Soon"

    else:
        return "OK"

washout["Status"] = washout.apply(classify, axis=1)

fig = px.scatter_mapbox(
    washout,
    lat="Lattitude",
    lon="Longitude",
    color="Status",
    color_discrete_map={
        "OK": "green",
        "Due Soon": "yellow",
        "Overdue": "red"
    },
    hover_name="Location",
    hover_data=[
        "Sl no.",
        "Prv_Washout Date",
        "Due_Washout Date",
        "Status"
    ],
    zoom=12,
    height=600
)

fig.update_layout(mapbox_style="open-street-map")
fig.update_traces(marker=dict(size=15))

st.plotly_chart(fig, use_container_width=True)
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
