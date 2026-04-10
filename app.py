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
st_autorefresh(interval=9000, key="scada_refresh")
st.set_page_config(page_title="WTP Moharda SCADA", layout="wide")

import datetime
import pandas as pd
import streamlit as st

# ===============================
# STYLING (UPGRADED UI)
# ===============================
st.markdown("""
<style>
body {background-color:#050A18;}
h1,h2,h3 {color:#00F5FF;}

.blink {animation: blinker 1s linear infinite;}
@keyframes blinker {50% {opacity:0;}}

button[kind="secondary"] {
    background-color:#001F3F;
    color:#00F5FF;
    border-radius:10px;
    height:45px;
    font-weight:bold;
}
button[kind="secondary"]:hover {
    background-color:#003366;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# TITLE
# ===============================
st.title("🏭 WTP MOHARDA – LIVE HMI PANEL")
st.markdown(f"### ⏱ {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")

# ===============================
# LOAD FILES
# ===============================
plant = pd.read_excel("Book 7.xlsx", engine="openpyxl")
plant.columns = plant.columns.str.strip()

gis = pd.read_excel("Gis Data.xlsx", engine="openpyxl")
gis.columns = gis.columns.str.strip()

# ===============================
# CALCULATIONS
# ===============================
turb = plant[plant["Parameter"].str.lower() == "turbidity"]
frc = plant[plant["Parameter"].str.lower() == "frc"]

intake_turb = turb["Intake"].mean()
clarifier_turb = turb["Clarifier"].mean()
clearwater_turb = turb["Clear Water"].mean()

clar_eff = (intake_turb - clarifier_turb) / intake_turb if intake_turb != 0 else 0

filter_eff_list = []
filter_turb_list = []

for i in range(1,7):
    f_avg = turb[f"Filter {i}"].mean()
    filter_turb_list.append(f_avg)

    eff = (clarifier_turb - f_avg) / clarifier_turb if clarifier_turb != 0 else 0
    filter_eff_list.append(eff)

avg_filter_eff = sum(filter_eff_list)/len(filter_eff_list)
consumer_frc = frc["Clear Water"].mean()

# ===============================
# ALARM LOGIC
# ===============================
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

# Filters
for i in range(1, 7):

    f_avg = turb[f"Filter {i}"].mean()
    eff = (clarifier_turb - f_avg) / clarifier_turb if clarifier_turb != 0 else 0

    if f_avg > 5:
        alarm_list.append(("CRITICAL", f"Filter {i} Turbidity Above 5 NTU ({f_avg:.2f})"))
        critical_count += 1
    elif f_avg > 1:
        alarm_list.append(("WARNING", f"Filter {i} Turbidity Above 1 NTU ({f_avg:.2f})"))
        warning_count += 1

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
# TOGGLE BUTTON
# ===============================
if "show_alarm" not in st.session_state:
    st.session_state.show_alarm = False

def toggle_alarm():
    st.session_state.show_alarm = not st.session_state.show_alarm

st.button("🚨 Plant Alarm Status", on_click=toggle_alarm)

# ===============================
# SUMMARY PANEL
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

# ===============================
# ALARM DISPLAY (TOGGLE)
# ===============================
if st.session_state.show_alarm:

    st.markdown("### 🚨 Active Alarm Details")

    if len(alarm_list) > 0:

        for level, message in alarm_list:

            if level == "CRITICAL":
                st.markdown(f"""
                <div style='
                    background-color:#2b0000;
                    padding:12px;
                    border-left:6px solid red;
                    border-radius:10px;
                    margin-bottom:10px;
                    color:white;
                    font-size:16px;
                '>🔴 {message}</div>
                """, unsafe_allow_html=True)

            else:
                st.markdown(f"""
                <div style='
                    background-color:#2b2b00;
                    padding:12px;
                    border-left:6px solid yellow;
                    border-radius:10px;
                    margin-bottom:10px;
                    color:white;
                    font-size:16px;
                '>🟡 {message}</div>
                """, unsafe_allow_html=True)

    else:
        st.success("✅ No Active Alarms")
# ===============================
# PRODUCTION
# ===============================
st.subheader("🏭 TOTAL WATER PRODUCTION")

production_mld = 18 # value can vary between 18–23
production_m3_hr = 1100
production_lps = production_m3_hr * 1000 / 3600

colp = st.columns(3)
colp[0].metric("Production (MLD)", production_mld)
colp[1].metric("Flow (m³/hr)", f"{production_m3_hr:.0f}")
colp[2].metric("Flow (LPS)", f"{production_lps:.0f}")

# ============================================================
# RAW WATER QUALITY SLICER (ERROR SAFE)
# ============================================================

st.subheader("📅 Raw Water Quality Selector")

# Load Excel
history_df = pd.read_excel("plant_raw_water_history.xlsx")

# Convert date safely
history_df["Date"] = pd.to_datetime(history_df["Date"], dayfirst=True)

# If time column exists combine it
if "Time" in history_df.columns:

    history_df["DateTime"] = pd.to_datetime(
        history_df["Date"].astype(str) + " " + history_df["Time"].astype(str),
        errors="coerce"
    )

else:

    history_df["DateTime"] = history_df["Date"]

# Drop invalid rows
history_df = history_df.dropna(subset=["DateTime"])

# Sort
history_df = history_df.sort_values("DateTime")

# ------------------------------------------------------------
# SLICER
# ------------------------------------------------------------

selected_time = st.select_slider(
    "Select Date",
    options=history_df["DateTime"],
    value=history_df["DateTime"].iloc[-1]
)

# Extract row
row = history_df[history_df["DateTime"] == selected_time]

intake_turb = float(row["Turbidity (NTU)"].values[0])
conductivity_today = float(row["Conductivity (µS/cm)"].values[0])

# Display
c1,c2,c3 = st.columns(3)

c1.metric("Date", selected_time.strftime("%d-%b-%Y"))
c2.metric("Raw Turbidity", f"{intake_turb:.2f} NTU")
c3.metric("Conductivity", f"{conductivity_today:.0f} µS/cm")
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

import streamlit as st

# ===============================
# FUNCTIONS
# ===============================

def calculate_efficiency(t_in, t_out):
    if t_in == 0:
        return 0
    return ((t_in - t_out) / t_in) * 100


def get_limit(unit_type):
    return 15 if unit_type == "Clarifier" else 1


def performance_index(t_out, limit):
    if t_out == 0:
        return float('inf')
    return limit / t_out


def performance_status(t_out, limit):
    return "OK" if t_out <= limit else "NOT OK"


def performance_grade(pi):
    if pi >= 1.5:
        return "Excellent"
    elif pi >= 1.0:
        return "Good"
    elif pi >= 0.7:
        return "Average"
    else:
        return "Poor"


def get_color(status, pi):
    if status == "NOT OK":
        return "red"
    elif pi >= 1.5:
        return "green"
    elif pi >= 1.0:
        return "orange"
    else:
        return "red"


# ===============================
# STREAMLIT UI
# ===============================

st.set_page_config(page_title="Water Treatment Performance", layout="wide")

st.subheader("💧 Water Treatment Performance Dashboard")

st.subheader("### 🏭 Unit Selection")

unit_type = st.selectbox("Select Unit", ["Clarifier", "Filter Bed"])

# Inputs
st.subheader("### 📥 Input Parameters")

col1, col2 = st.columns(2)

with col1:
    t_in = st.number_input("Inlet Turbidity (NTU)", min_value=0.0, value=100.0)

with col2:
    t_out = st.number_input("Outlet Turbidity (NTU)", min_value=0.0, value=10.0)

# ===============================
# CALCULATIONS
# ===============================

limit = get_limit(unit_type)

eff = calculate_efficiency(t_in, t_out)
pi = performance_index(t_out, limit)
status = performance_status(t_out, limit)
grade = performance_grade(pi)
color = get_color(status, pi)

# ===============================
# DISPLAY METRICS
# ===============================

st.subheader("### 📊 Performance Results")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Efficiency (%)", f"{eff:.2f}")
col2.metric("Performance Index", f"{pi:.2f}")
col3.metric("Status", status)
col4.metric("Grade", grade)

# ===============================
# VISUAL INDICATOR
# ===============================

st.subheader("### 🚦 Performance Indicator")

if color == "green":
    st.success("Excellent Performance ✅")
elif color == "orange":
    st.warning("Moderate Performance ⚠️")
else:
    st.error("Poor Performance ❌")

# ===============================
# INTERPRETATION BOX
# ===============================

st.subheader("### Interpretation")

st.info(f"""
- **Unit Selected:** {unit_type}  
- **Standard Limit:** {limit} NTU  
- **Performance Index (PI):** {pi:.2f}  

👉 PI > 1 → Within standard  
👉 PI < 1 → Exceeds standard  

👉 Efficiency shows removal performance,  
👉 Status confirms compliance with water quality standard.
""")


# ============================================================
# PREVIOUS 4 DAYS TURBIDITY TREND
# ============================================================

st.subheader("Raw Water Turbidity Trend (Last 4 Days)")

# ensure date column is datetime
history_df["Date"] = pd.to_datetime(history_df["Date"], dayfirst=True)

# selected date from slicer
selected_date = selected_time.normalize()

# filter last 4 days including today
trend_df = history_df[
    (history_df["Date"] <= selected_date) &
    (history_df["Date"] >= selected_date - pd.Timedelta(days=4))
]

# ------------------------------------------------------------
# GRAPH
# ------------------------------------------------------------

fig_turb = go.Figure()

fig_turb.add_trace(go.Scatter(
    x=trend_df["Date"],
    y=trend_df["Turbidity (NTU)"],
    mode="lines+markers",
    line=dict(color="cyan", width=3),
    marker=dict(size=8),
    name="Raw Turbidity (Intake)"
))

fig_turb.update_layout(
    template="plotly_dark",
    title="Intake Turbidity Trend (Last 4 Days)",
    xaxis_title="Date",
    yaxis_title="Turbidity (NTU)",
    height=400
)

# ============================================================
# IMPORTS (VERY IMPORTANT)
# ============================================================

import streamlit as st
import numpy as np
import plotly.graph_objects as go

# ============================================================
# TITLE
# ============================================================

st.subheader(" Intelligent Alum Dosing Decision System")

# ============================================================
# INPUTS
# ============================================================

flow_mld = 18
flow_m3_day = flow_mld * 1000

turbidity = float(intake_turb) # from your existing slider

ph = st.slider("pH", 4.5, 9.0, 7.0, 0.1)

industrial = st.toggle("⚠️ Industrial Discharge Present")

# ============================================================
# 🧪 JAR TEST INPUT (MANUAL)
# ============================================================

st.markdown("### 🧪 Jar Test Input")

jar_available = st.toggle("Use Jar Test")

if jar_available:
    jar_dose = st.number_input("Enter Jar Test Dose (mg/L)", value=25.0)
else:
    jar_dose = None

# ============================================================
# STANDARD MODELS (REALISTIC ENGINEERING)
# ============================================================

def cpheeo_model(t):
    return 0.35*t + 5

def awwa_model(t):
    return 0.40*t + 8

def bis_model(t):
    return 0.30*t + 6

cpheeo = cpheeo_model(turbidity)
awwa = awwa_model(turbidity)
bis = bis_model(turbidity)

# ============================================================
# CORRECTIONS
# ============================================================

# pH correction
if ph < 5.5:
    ph_factor = 1.2
elif ph > 7.5:
    ph_factor = 1.1
else:
    ph_factor = 1.0

# industrial load
industrial_factor = 1.25 if industrial else 1.0

# turbidity boost
if turbidity > 300:
    turb_factor = 1.35
elif turbidity > 150:
    turb_factor = 1.2
else:
    turb_factor = 1.0

# ============================================================
# AI DOSING LOGIC (SAFE + COMPLETE)
# ============================================================

if jar_available:
    ai_dose = (
        0.6 * jar_dose +
        0.2 * cpheeo +
        0.1 * awwa +
        0.1 * bis
    )
else:
    ai_dose = (
        0.4 * cpheeo +
        0.35 * awwa +
        0.25 * bis
    )

ai_dose = ai_dose * ph_factor * industrial_factor * turb_factor
ai_dose = float(np.clip(ai_dose, 5, 150)) # ALWAYS defined

# ============================================================
# CHEMICAL REQUIREMENT
# ============================================================

alum_kg_day = (ai_dose * flow_m3_day) / 1000
pac_dose = 0.6 * ai_dose

# ============================================================
# STATUS BAND
# ============================================================

if ai_dose > 80:
    st.error("🔴 High Chemical Demand")
elif ai_dose > 40:
    st.warning("🟡 Moderate Condition")
else:
    st.success("🟢 Normal Operation")

# ============================================================
# LAYOUT
# ============================================================

left, right = st.columns([1.1,1.4])

# ============================================================
# 📊 LEFT → CLEAN GRAPH
# ============================================================

with left:

    st.markdown("### 📊 Dosing Decision Curve")

    x = np.linspace(0, 300, 100)
    y_ai = 0.3*x + 8 + 0.0005*(x**2)

    fig = go.Figure()

    # Optimal zone
    fig.add_hrect(
        y0=20, y1=30,
        fillcolor="green", opacity=0.15,
        line_width=0
    )

    # Warning zone
    fig.add_hrect(
        y0=30, y1=60,
        fillcolor="yellow", opacity=0.1,
        line_width=0
    )

    # Critical zone
    fig.add_hrect(
        y0=60, y1=120,
        fillcolor="red", opacity=0.08,
        line_width=0
    )

    # AI curve
    fig.add_trace(go.Scatter(
        x=x,
        y=y_ai,
        line=dict(color="cyan", width=4),
        name="AI Curve"
    ))

    # Operating point (SAFE)
    fig.add_trace(go.Scatter(
        x=[turbidity],
        y=[ai_dose],
        mode="markers+text",
        marker=dict(size=14, color="yellow"),
        text=["Operating"],
        textposition="top center"
    ))

    fig.update_layout(
        template="plotly_dark",
        height=350,
        margin=dict(l=10,r=10,t=40,b=10),
        xaxis_title="Turbidity (NTU)",
        yaxis_title="Alum Dose (mg/L)",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    st.metric("Dose", f"{ai_dose:.1f} mg/L")
    st.metric("Alum Required", f"{alum_kg_day:,.0f} kg/day")

# ============================================================
# 📘 RIGHT → DECISION PANEL
# ============================================================

with right:

    st.markdown("### 📘 Recommendation Logic")

    st.markdown(f"""
**Input Conditions**
- Turbidity: **{turbidity} NTU**
- pH: **{ph}**
- Industrial Load: **{"Yes" if industrial else "No"}**
""")

    st.markdown("---")

    st.markdown(f"""
**Standard Estimates**
- CPHEEO: {cpheeo:.1f} mg/L  
- AWWA: {awwa:.1f} mg/L  
- BIS: {bis:.1f} mg/L  
""")

    if jar_available:
        st.success(f"Jar Test Used: {jar_dose:.1f} mg/L")
    else:
        st.warning("Jar Test not used")

    st.markdown("---")

    st.markdown(f"""
###  Final Decision

👉 **{ai_dose:.1f} mg/L Alum**

✔ Adjusted for:
- pH factor: {ph_factor}
- Industrial load: {industrial_factor}
- Turbidity factor: {turb_factor}

✔ Ensures:
- Effective coagulation  
- Controlled sludge  
- Stable filtration  

📦 Alum Required: **{alum_kg_day:,.0f} kg/day**  
⚡ PAC Dose: **{pac_dose:.1f} mg/L**
""")

# ============================================================
# ALERT SYSTEM
# ============================================================

if ai_dose > 80:
    st.error("🔴 Consider PAC or Pre-treatment")

elif jar_available and abs(ai_dose - jar_dose) > 5:
    st.warning("🟡 Deviation from Jar Test")

else:
    st.success("🟢 Optimal dosing")
# ============================================================
# CORRECT DYNAMIC HYPOCHLORITE DOSING MODEL
# ============================================================

st.subheader("Dynamic Hypochlorite Dose vs Residual Chlorine")

import numpy as np
import plotly.graph_objects as go

# -----------------------------
# FIXED PARAMETERS
# -----------------------------
operation_hours = 16.5
hypo_strength = 0.12

# -----------------------------
# SLICERS
# -----------------------------

flow_m3_hr = st.slider(
    "Flow Rate (m³/hr)",
    500,1500,1100,50
)

flow_m3_day = flow_m3_hr * operation_hours

frc_selected = st.slider(
    "Free Residual Chlorine (ppm)",
    0.2,1.0,0.5,0.05
)

nitrite = st.slider(
    "Nitrite Level (mg/L)",
    0.0,1.0,0.2,0.05
)

conductivity = st.slider(
    "Conductivity (µS/cm)",
    200,600,350,10
)

pH = st.slider(
    "pH",
    6.0,9.0,7.2,0.1
)

# -----------------------------
# STANDARD SELECTION
# -----------------------------

standards = st.multiselect(
    "Select Standards to Display",
    ["BIS", "WHO", "AWWA"],
    default=["WHO","BIS"]
)

# -----------------------------
# CHLORINE DEMAND MODEL (REALISTIC)
# -----------------------------

base_demand = 2.5

nitrite_effect = nitrite * 1.5
conductivity_effect = (conductivity - 300)/250
ph_effect = (pH - 7.0) * 0.8

chlorine_demand = base_demand + nitrite_effect + conductivity_effect + ph_effect

# -----------------------------
# SINGLE CURVE (CORRECT)
# -----------------------------

frc_range = np.linspace(0.2,1.0,100)

dose_curve = ((chlorine_demand + frc_range) * flow_m3_day) / (hypo_strength*1000)

# -----------------------------
# GRAPH
# -----------------------------

fig_hypo = go.Figure()

# MAIN SINGLE CURVE
fig_hypo.add_trace(go.Scatter(
    x=frc_range,
    y=dose_curve,
    name="Dose Curve (Demand + Residual)",
    line=dict(color="cyan", width=4)
))

# -----------------------------
# STANDARD LINES (CORRECT WAY)
# -----------------------------

if "BIS" in standards:
    fig_hypo.add_vline(x=0.5, line_dash="dash", line_color="orange",
                       annotation_text="BIS (0.5 mg/L)")

if "WHO" in standards:
    fig_hypo.add_vline(x=0.5, line_dash="dot", line_color="green",
                       annotation_text="WHO (0.2–0.5 mg/L)")

if "AWWA" in standards:
    fig_hypo.add_vline(x=0.6, line_dash="dashdot", line_color="purple",
                       annotation_text="AWWA (0.6 mg/L)")

# -----------------------------
# CURRENT OPERATING POINT
# -----------------------------

dose_selected = ((chlorine_demand + frc_selected) * flow_m3_day) / (hypo_strength*1000)

fig_hypo.add_trace(go.Scatter(
    x=[frc_selected],
    y=[dose_selected],
    mode="markers",
    marker=dict(size=14, color="yellow"),
    name="Selected Condition"
))

# -----------------------------
# GRAPH LAYOUT
# -----------------------------

fig_hypo.update_layout(
    template="plotly_dark",
    title="Hypochlorite Dose vs Residual Chlorine (Correct Model)",
    xaxis_title="Free Residual Chlorine (ppm)",
    yaxis_title="NaOCl Dose (kg/day)",
    height=500
)

st.plotly_chart(fig_hypo, use_container_width=True)

# -----------------------------
# RECOMMENDATION
# -----------------------------

st.subheader("Chlorination Recommendation")

if frc_selected < 0.2:
    st.error("🔴 Below safe limit (WHO/BIS). Increase dosing.")

elif frc_selected > 0.8:
    st.warning("🟡 Too high. Risk of taste/odor issues.")

else:
    st.success("🟢 Within acceptable disinfection range.")

# -----------------------------
# OUTPUT METRICS
# -----------------------------

st.metric("Required Hypo Dose", f"{dose_selected:,.0f} kg/day")
st.metric("Chlorine Demand", f"{chlorine_demand:.2f} mg/L")
# WATER TOWERS
# ===============================
st.subheader("🗼 Distribution Water Towers")
names=["Moharda WT","Zone 9 WT","Zone 3 WT","Zone 1 GSR outlet","Bagunhatu WT","Bagunnagar WT"]
tc=st.columns(3)
for i in range(6):
    tc[i%3].plotly_chart(gauge(names[i],75,100),use_container_width=True)

import streamlit as st
import smtplib
import pandas as pd
import os
import numpy as np
import requests
from datetime import datetime
from sklearn.linear_model import LinearRegression

# ===============================
# PAGE
# ===============================
st.set_page_config(layout="wide")
st.markdown("## AI Water Treatment Feedback System")

left_col, right_col = st.columns([2,1])

# ===============================
# EMAIL FUNCTION (FINAL FIXED)
# ===============================
def send_email_alert(message):

    sender = "alokranjan18april@gmail.com"
    password = "wpnrabqfbtkhsqpe"
    receiver = "alok.ranjan6@tatasteel.com"

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, message.encode("utf-8"))
        server.quit()

        st.success("📧 Email Sent")

    except Exception as e:
        st.error(f"Email error: {e}")

# ===============================
# ALARM STATE
# ===============================
if "alarm" not in st.session_state:
    st.session_state.alarm = False

# ===============================
# DATA
# ===============================
FILE = "feedback_data.csv"

if os.path.exists(FILE):
    df = pd.read_csv(FILE)
else:
    df = pd.DataFrame(columns=[
        "timestamp","raw_turbidity","dose","final_turbidity","frc"
    ])

# ===============================
# INPUT
# ===============================
with left_col:

    c1, c2 = st.columns(2)

    with c1:
        dose = st.slider("Dose (mg/L)", 0.0, 100.0, 10.0)
        final_turbidity = st.number_input("Final Turbidity", 0.0, 50.0, 1.0)
        frc = st.number_input("FRC", 0.0, 5.0, 0.5)

    with c2:
        raw_turbidity = st.number_input("Raw Turbidity", 0.0, 500.0, 50.0)

    submit = st.button("Submit Feedback", key="submit_btn")

# ===============================
# MAIN
# ===============================
if submit:

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new = pd.DataFrame([{
        "timestamp": now,
        "raw_turbidity": raw_turbidity,
        "dose": dose,
        "final_turbidity": final_turbidity,
        "frc": frc
    }])

    df = pd.concat([df, new], ignore_index=True)
    df.to_csv(FILE, index=False)

    st.success(f"Saved at {now}")
    st.info(f"Total Samples: {len(df)}")

    # ===============================
    # AI LOGIC
    # ===============================
    if len(df) >= 30:

        st.markdown("### AI Smart Recommendation")

        good = df[
            (df["final_turbidity"] <= 1) &
            (df["frc"] >= 0.2) &
            (df["frc"] <= 1)
        ]

        if len(good) > 10:

            good = good.copy()
            good["diff"] = abs(good["raw_turbidity"] - raw_turbidity)

            similar = good.sort_values(by="diff").head(10)
            best = similar["dose"].mean()

            st.success(f"Recommended Dose: {best:.2f} mg/L")

        else:
            st.warning("Collect more good data")

    else:
        st.info(f"AI activates after 30 samples (Current: {len(df)})")

    # ===============================
    # 🚨 ALERT + EMAIL
    # ===============================
    if final_turbidity > 1 or frc < 0.2:

        st.session_state.alarm = True

        msg = f"""Subject: 🚨 WATER QUALITY ALERT

Time: {now}
Final Turbidity: {final_turbidity}
FRC: {frc}

Immediate action required.
"""

        send_email_alert(msg)

    else:
        st.success("Quality Achieved")

# ===============================
# 🔊 FINAL WORKING ALARM (EMBEDDED SOUND)
# ===============================

import base64

# One-time enable
if "sound_enabled" not in st.session_state:
    st.session_state.sound_enabled = False

if not st.session_state.sound_enabled:
    if st.button("🔊 Enable Alarm Sound", key="enable_sound"):
        st.session_state.sound_enabled = True
        st.success("Sound Enabled ✅")

# Alarm
if st.session_state.alarm:

    st.error("🚨 CONTINUOUS ALARM ACTIVE")

    # 🔴 Flashing UI
    st.markdown("""
    <style>
    @keyframes blink {
        0% { background-color: red; }
        50% { background-color: transparent; }
        100% { background-color: red; }
    }
    .alarm-box {
        animation: blink 1s infinite;
        padding: 20px;
        text-align: center;
        font-size: 26px;
        color: white;
        font-weight: bold;
    }
    </style>
    <div class="alarm-box">🚨 CRITICAL WATER QUALITY ALERT 🚨</div>
    """, unsafe_allow_html=True)

    # 🔊 SOUND (EMBEDDED + LOOP)
    if st.session_state.sound_enabled:
        try:
            with open("mixkit-sport-start-bleeps-918.wav", "rb") as f:
                data = f.read()
                b64 = base64.b64encode(data).decode()

            st.markdown(f"""
            <audio autoplay loop>
                <source src="data:audio/wav;base64,{b64}" type="audio/wav">
            </audio>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.warning(f"⚠️ Sound issue: {e}")

    else:
        st.warning("🔊 Enable sound once")

    # Stop
    if st.button("🔴 Stop Alarm", key="stop_alarm_btn"):
        st.session_state.alarm = False
        st.success("Alarm Stopped")
# ===============================
# 📂 DATA TABLE + DELETE
# ===============================
st.markdown("### 📂 Stored Data")

if st.checkbox("Show Data Table"):

    if len(df) > 0:

        st.dataframe(df.sort_values(by="timestamp", ascending=False))

        selected_index = st.selectbox("Select row to delete", df.index)

        if st.button("🗑 Delete Selected Row", key="delete_btn"):

            df = df.drop(selected_index).reset_index(drop=True)
            df.to_csv(FILE, index=False)

            st.success("Row deleted!")
            st.rerun()

# ===============================
# WEATHER
# ===============================
with right_col:

    st.markdown("### 🌤 Weather")

    API_KEY = "f899db331049be78181d1afddbc92935"
    CITY = "Jamshedpur"

    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
        data = requests.get(url).json()

        st.metric("Temp", f"{data['main']['temp']} °C")
        st.metric("Humidity", f"{data['main']['humidity']} %")
        st.write(data['weather'][0]['description'])

    except:
        st.error("Weather error")

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
# ==============================
# 🌊 AI INTAKE DEBRIS MODULE
# ==============================

from ultralytics import YOLO
from PIL import Image
import numpy as np
import streamlit as st

@st.cache_resource
def load_model():
    return YOLO("best.pt")

debris_model = load_model()

st.markdown("---")
st.header("🌊 AI Intake Monitoring System")

uploaded_img = st.file_uploader("Upload Intake Image", type=["jpg","png","jpeg"], key="intake")

if uploaded_img:
    img = Image.open(uploaded_img)
    st.image(img, caption="Intake Image", use_container_width=True)

    if st.button("🔍 Run AI Analysis"):

        # Convert image to numpy (important for YOLO stability)
        img_np = np.array(img)

        results = debris_model(img_np)

        detected = []
        total_area = 0.0 # ensure float

        for r in results:
            if r.boxes is not None:
                for box in r.boxes:

                    label = r.names[int(box.cls[0])]
                    detected.append(label)

                    # Convert tensor → float
                    x1, y1, x2, y2 = box.xyxy[0].tolist()

                    area = (x2 - x1) * (y2 - y1)
                    total_area += float(area)

        # ==========================
        # 📊 INTELLIGENT ANALYSIS
        # ==========================
        st.subheader("📊 AI Detection Summary")
        st.write("Detected Objects:", detected)

        debris_count = len(detected)

        # Avoid division by zero
        img_area = img.size[0] * img.size[1]

        if img_area > 0:
            density = total_area / img_area
        else:
            density = 0

        st.write(f"Debris Density: {round(float(density),3)}")

        # ==========================
        #  AI DECISION ENGINE
        # ==========================
        st.subheader("⚠️ AI Identified Issues")

        issues = []
        actions = []

        # --- Plastic detection ---
        if any(x in detected for x in ["plastic", "bottle", "bag"]):
            issues.append("Plastic accumulation → Intake blockage risk")
            actions.append("Install / clean trash racks immediately")

        # --- Organic load ---
        if any(x in detected for x in ["leaf", "plant"]):
            issues.append("High organic load → Increased coagulant demand")
            actions.append("Increase alum/PAC dosing temporarily")

        # --- High density ---
        if density > 0.15:
            issues.append("High debris density → Clarifier overload risk")
            actions.append("Reduce intake flow rate")

        # --- Extreme condition ---
        if density > 0.25 or debris_count > 8:
            issues.append("Extreme debris condition → Filter choking risk")
            actions.append("Prepare for frequent backwashing")

        # --- No detection ---
        if debris_count == 0:
            issues.append("No visible debris → System stable")
            actions.append("Maintain normal operation")

        # ==========================
        # OUTPUT
        # ==========================
        for i in issues:
            st.write("•", i)

        st.subheader("🛠 Recommended Actions")

        for a in actions:
            st.write("•", a)

        # ==========================
        # IMAGE OUTPUT
        # ==========================
        st.subheader("📦 Detection Output")

        for r in results:
            st.image(r.plot(), use_container_width=True)

# ==========================================
# 🖥️ WATER QUALITY AI - ADVANCED PRACTICAL VERSION
# Added: Pre-Chlorination + Oily Water Logic
# ==========================================

import streamlit as st

st.subheader("🖥️ Water Treatment AI Assistant")

# ===============================
# STEP 1: COMPLAINT
# ===============================
st.markdown("Step 1: Customer Complaint")

complaint = st.text_input("Enter issue (muddy, smell, worms, yellow, green layer)")

# ===============================
# STEP 2: WATER PARAMETERS
# ===============================
if complaint:

    st.markdown("Step 2: Plant Data")

    col1, col2 = st.columns(2)

    with col1:
        raw_turbidity = st.number_input("Raw Water Turbidity (NTU)", value=80.0)
        treated_turbidity = st.number_input("Treated Water Turbidity (NTU)", value=1.2)

    with col2:
        chlorine = st.number_input("Residual Chlorine (ppm)", value=0.3)
        sunlight = st.selectbox("Is storage exposed to sunlight?", ["Yes", "No"])

# ===============================
# STEP 3: DOSING + CONDITIONS
# ===============================
    st.markdown("Step 3: Chemical Dosing")

    col3, col4 = st.columns(2)

    with col3:
        alum = st.number_input("Alum Dose (ppm)", value=25.0)
        pre_chlorine = st.number_input("Pre-Chlorination Dose (ppm)", value=0.5)

    with col4:
        hypo = st.number_input("Post-Chlorination (Hypo) Dose (ppm)", value=1.0)
        oily = st.selectbox("Is oily layer observed in raw water?", ["No", "Yes"])

# ===============================
# FINAL ANALYSIS
# ===============================
    if st.button("Run Diagnosis"):

        st.markdown("Diagnosis & Action")

        text = complaint.lower()

        # -------------------------------
        # 🧪 PRE-CHLORINATION CHECK
        # -------------------------------
        st.markdown("### 🧪 Pre-Chlorination Status")

        if pre_chlorine < 0.3:
            st.warning("⚠️ Low Pre-Chlorination")

            st.write("Impact:")
            st.write("- Poor algae control")
            st.write("- Biological load entering clarifier")

            st.write("Action:")
            st.write("- Increase pre-chlorine (0.5–1 ppm typical)")
            st.write("- Reduces coagulant demand")

        elif pre_chlorine > 2:
            st.warning("⚠️ Excess Pre-Chlorination")

            st.write("Impact:")
            st.write("- Formation of chlorinated organics")
            st.write("- Taste & odor problems")

            st.write("Action:")
            st.write("- Optimize dosing (jar test / breakpoint chlorination)")

        else:
            st.success("Pre-chlorination is in optimal range")

        # -------------------------------
        # 🛢️ OILY WATER CHECK
        # -------------------------------
        if oily == "Yes":

            st.error("🛢️ Issue: Oil/Grease contamination")

            st.write("Cause:")
            st.write("- Industrial discharge / runoff")

            st.write("Impact:")
            st.write("- Poor coagulation")
            st.write("- Filter choking")
            st.write("- Odor issues")

            st.write("Action:")
            st.write("- Use oil skimmer / trap before treatment")
            st.write("- Increase coagulant dose slightly")
            st.write("- Use PAC/polymer")
            st.write("- Avoid direct chlorination before oil removal")

        # -------------------------------
        # 🟤 MUDDY / SEDIMENT
        # -------------------------------
        if "muddy" in text or "sediment" in text:

            if treated_turbidity > 1:
                st.error("Issue: Poor clarification / filtration")

                st.write("Possible reasons:")
                if raw_turbidity > 100:
                    st.write("- High river turbidity (seasonal load)")
                if alum < 20:
                    st.write("- Insufficient alum dosing")
                if oily == "Yes":
                    st.write("- Oil interfering with coagulation")

                st.write("Action:")
                st.write("- Increase alum dose (jar test)")
                st.write("- Check floc formation")
                st.write("- Backwash filter")

        # -------------------------------
        # 🪱 WORMS
        # -------------------------------
        elif "worm" in text:

            st.error("Issue: Biological growth in filter/sump")

            st.write("Cause:")
            st.write("- Organic sludge accumulation")
            st.write("- Infrequent backwashing")

            st.write("Action:")
            st.write("- Increase backwash frequency")
            st.write("- Shock chlorination")
            st.write("- Cover tanks")

        # -------------------------------
        # 🌫️ SMELL
        # -------------------------------
        elif "smell" in text or "fish" in text:

            if chlorine > 0.5:
                st.warning("Likely Cause: Over chlorination")

                st.write("Action:")
                st.write("- Reduce hypo dose")

            elif chlorine < 0.2:
                st.warning("Likely Cause: Organic contamination")

                st.write("Action:")
                st.write("- Increase chlorination")
                st.write("- Improve aeration")

            else:
                st.warning("Likely Cause: Chloramines / algae")

                st.write("Action:")
                st.write("- Improve clarification")
                st.write("- Consider PAC dosing")

        # -------------------------------
        # 🟢 GREEN LAYER
        # -------------------------------
        elif "green" in text:

            st.error("Issue: Algae growth")

            if sunlight == "Yes":
                st.write("- Sunlight exposure present")
            if chlorine < 0.2:
                st.write("- Low chlorine")

            st.write("Action:")
            st.write("- Cover tank")
            st.write("- Maintain chlorine 0.2–0.5 ppm")

        # -------------------------------
        # 🟡 YELLOW
        # -------------------------------
        elif "yellow" in text:

            if chlorine > 0.5:
                st.error("Cause: Excess chlorine")

                st.write("Action:")
                st.write("- Reduce dosing")

            elif chlorine < 0.2:
                st.warning("Cause: Biological activity")

                st.write("Action:")
                st.write("- Increase chlorine")

            else:
                st.info("Possible iron presence")

                st.write("Action:")
                st.write("- Improve aeration & filtration")

        # -------------------------------
        # DEFAULT
        # -------------------------------
        else:
            st.info("No clear issue. Check full parameters.")

        # ===============================
        # 📊 STANDARD CHECK
        # ===============================
        st.markdown("---")
        st.subheader("Standards Check (BIS/WHO)")

        if treated_turbidity <= 1:
            st.success("Turbidity OK")
        else:
            st.error("Turbidity High")

        if 0.2 <= chlorine <= 0.5:
            st.success("Chlorine OK")
        else:
            st.error("Chlorine Out of Range")
