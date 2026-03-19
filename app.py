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

st.plotly_chart(fig_turb, use_container_width=True)
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
# AI RECOMMENDED DOSAGE PANEL (STANDARDS + LAB VALIDATION)
# ============================================================

st.subheader("AI Recommended Chemical Dosage")

# ------------------------------------------------------------
# INPUTS
# ------------------------------------------------------------

flow_m3_hr = 1100
operating_hours = 16.5
flow_m3_day = flow_m3_hr * operating_hours

aerator_turbidity = float(intake_turb)
current_frc = float(consumer_frc)

conductivity_today = 350

# ============================================================
# LOAD JAR TEST DATA (LAB)
# ============================================================

try:
    jar_df = pd.read_excel("DATASHEET.xlsx")

    jar_df.iloc[:,0] = pd.to_numeric(jar_df.iloc[:,0], errors="coerce")
    jar_df.iloc[:,1] = pd.to_numeric(jar_df.iloc[:,1], errors="coerce")

    jar_df = jar_df.dropna()

    jar_turb = jar_df.iloc[:,0].values
    jar_dose = jar_df.iloc[:,1].values

    sort_idx = np.argsort(jar_turb)
    jar_turb = jar_turb[sort_idx]
    jar_dose = jar_dose[sort_idx]

except:
    jar_turb = np.array([5,10,20,40,80])
    jar_dose = np.array([6,8,12,18,25])
    
# ------------------------------------------------------------
# CREATE JAR CURVE
# ------------------------------------------------------------

if len(jar_turb) >= 3:

    jar_poly = np.polyfit(jar_turb, jar_dose, 2)
    jar_curve = np.poly1d(jar_poly)

else:

    # fallback if jar test data missing
    jar_curve = lambda x: 0.2*x + 8

# ============================================================
# STANDARDS DATABASE
# ============================================================

std_turb = np.array([5,10,20,40,60,80,100,150,200,300])

bis_dose = np.array([6,8,12,18,22,26,30,35,40,45])
cpheeo_dose = np.array([8,10,15,22,26,30,35,40,45,50])
awwa_dose = np.array([10,12,18,24,28,32,38,45,50,55])

# ============================================================
# INTERPOLATION
# ============================================================

bis_today = float(np.interp(aerator_turbidity,std_turb,bis_dose))
cpheeo_today = float(np.interp(aerator_turbidity,std_turb,cpheeo_dose))
awwa_today = float(np.interp(aerator_turbidity,std_turb,awwa_dose))

jar_today = float(jar_curve(aerator_turbidity))

# ============================================================
# AI ALUM DOSING
# ============================================================

ai_today_alum = (
0.4 * cpheeo_today +
0.3 * bis_today +
0.2 * awwa_today +
0.1 * jar_today
)

solid_alum_kg_day = (ai_today_alum * flow_m3_day) / 1000

# ============================================================
# PAC OPTIMIZATION
# ============================================================

pac_dose = 0.6 * ai_today_alum
pac_kg_day = (pac_dose * flow_m3_day) / 1000

# ============================================================
# SLUDGE PRODUCTION ESTIMATION
# ============================================================

sludge_factor = 0.6
sludge_kg_day = sludge_factor * solid_alum_kg_day

# ------------------------------------------------------------
# METRICS
# ------------------------------------------------------------

c1,c2,c3,c4 = st.columns(4)

c1.metric("Jar Test Dose",f"{jar_today:.2f} mg/L")
c2.metric("AI Alum Dose",f"{ai_today_alum:.2f} mg/L")
c3.metric("Alum Required",f"{solid_alum_kg_day:,.0f} kg/day")
c4.metric("Sludge Production",f"{sludge_kg_day:,.0f} kg/day")

# ------------------------------------------------------------
# PAC METRIC
# ------------------------------------------------------------

st.metric("Recommended PAC Dose",f"{pac_dose:.2f} mg/L")

# ============================================================
# ALUM GRAPH
# ============================================================

x_range = np.linspace(0,300,300)
# ============================================================
# EXTEND JAR TEST LINE (LAB)
# ============================================================

# Ensure jar data exists
if len(jar_turb) < 2:

    # fallback assumed data
    jar_turb = np.array([5,10,20,40,80])
    jar_dose = np.array([6,8,12,18,25])
    
# ============================================================
# JAR TEST CURVE EXTENSION
# ============================================================

jar_interp = np.interp(x_range, jar_turb, jar_dose)

# slope from last two points
slope = (jar_dose[-1] - jar_dose[-2]) / (jar_turb[-1] - jar_turb[-2])

jar_extended = jar_dose[-1] + slope * (x_range - jar_turb[-1])

jar_curve_plot = np.where(
    x_range <= jar_turb[-1],
    jar_interp,
    jar_extended
)

jar_curve_plot = jar_curve(x_range)
bis_curve = np.interp(x_range,std_turb,bis_dose)
cpheeo_curve = np.interp(x_range,std_turb,cpheeo_dose)
awwa_curve = np.interp(x_range,std_turb,awwa_dose)

ai_curve = (
0.4*cpheeo_curve+
0.3*bis_curve+
0.2*awwa_curve+
0.1*jar_curve_plot
)

fig_alum = go.Figure()

fig_alum.add_trace(go.Scatter(
    x=x_range,
    y=jar_curve_plot,
    mode="lines",
    name="Jar Test (Lab)",
    line=dict(color="red", width=4)
))

fig_alum.add_trace(go.Scatter(
    x=x_range,
    y=bis_curve,
    name="BIS Standard",
    line=dict(color="orange", width=3)
))

fig_alum.add_trace(go.Scatter(
    x=x_range,
    y=cpheeo_curve,
    name="CPHEEO Standard",
    line=dict(color="green", width=3)
))

fig_alum.add_trace(go.Scatter(
    x=x_range,
    y=awwa_curve,
    name="AWWA Standard",
    line=dict(color="purple", width=3)
))

fig_alum.add_trace(go.Scatter(
    x=x_range,
    y=ai_curve,
    name="AI Recommended",
    line=dict(color="blue", width=4)
))
fig_alum.add_trace(go.Scatter(
x=[aerator_turbidity],
y=[ai_today_alum],
mode="markers",
marker=dict(size=14,color="yellow"),
name="Current Operating Point"
))

fig_alum.update_layout(
template="plotly_dark",
title="Alum Dosing Recommendation",
xaxis_title="Raw Water Turbidity (NTU)",
yaxis_title="Alum Dose (mg/L)",
height=500
)

st.plotly_chart(fig_alum,use_container_width=True)

st.subheader("AI Recommendation")

if abs(ai_today_alum - jar_today) > 5:

    st.error("🔴 Alum dosing significantly deviates from lab jar test. Adjust dosing.")

elif abs(ai_today_alum - jar_today) > 2:

    st.warning("🟡 Slight deviation from jar test results.")

else:

    st.success("🟢 Alum dosing aligned with lab jar test and standards.")

st.caption(
"Standards referenced: BIS Drinking Water Specification, "
"CPHEEO Manual on Water Supply, and AWWA Water Treatment Practice."
)
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

# ===============================
# 🤖 AI FEEDBACK + LIVE WEATHER + LEARNING SYSTEM
# ===============================

import pandas as pd
import requests
from datetime import datetime
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
from streamlit_autorefresh import st_autorefresh
import streamlit as st

import requests
import streamlit as st

st.subheader("🌦️ Live Weather")

API_KEY = "your_api_key_here" # <-- put your API key
CITY = "Jamshedpur"

try:
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    response = requests.get(url, timeout=5)

    if response.status_code == 200:
        data = response.json()

        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        condition = data["weather"][0]["description"]

        st.success(f"📍 {CITY}")
        st.metric("🌡️ Temperature (°C)", temp)
        st.metric("💧 Humidity (%)", humidity)
        st.write(f"🌥️ Condition: {condition}")

    else:
        st.error("⚠️ Weather API Error")

except:
    st.warning("⚠️ Weather not loading (Check API / Internet)")

# ===============================
# 💾 SAVE FEEDBACK
# ===============================
def save_feedback(dose, raw_ntu, final_ntu, frc, weather, status):
    
    df = pd.DataFrame({
        "Date": [datetime.now()],
        "Dose": [dose],
        "Raw_NTU": [raw_ntu],
        "Final_NTU": [final_ntu],
        "FRC": [frc],
        "Weather": [weather],
        "Status": [status]
    })
    
    try:
        df.to_csv("feedback_data.csv", mode='a', header=False, index=False)
    except:
        df.to_csv("feedback_data.csv", index=False)


# ===============================
# 🧠 MODEL TRAINING (ADVANCED)
# ===============================
def train_model():
    try:
        df = pd.read_csv("feedback_data.csv")

        if len(df) < 10:
            return None, None, None

        le = LabelEncoder()
        df['Weather_encoded'] = le.fit_transform(df['Weather'])

        df['Weight'] = df['Status'].apply(lambda x: 2 if x=="Achieved" else 1)

        X = df[['Dose', 'Raw_NTU', 'FRC', 'Weather_encoded']]
        y = df['Final_NTU']

        model = GradientBoostingRegressor()
        model.fit(X, y, sample_weight=df['Weight'])

        return model, le, df

    except:
        return None, None, None


# ===============================
# 🤖 AI DECISION
# ===============================
def generate_remark(dose, raw_ntu, frc, weather, model, le):

    if model is None:
        return "⚠️ Learning in progress (need more data)"

    weather_encoded = le.transform([weather])[0]

    predicted_ntu = model.predict([[dose, raw_ntu, frc, weather_encoded]])[0]

    if predicted_ntu < 1 and frc >= 0.2:
        return f"✅ Predicted NTU: {round(predicted_ntu,2)} → Optimal dosing"

    elif predicted_ntu >= 1 and weather == "Rainy":
        new_dose = dose * 1.2
        return f"🌧 Rain impact → Increase dose to ~{round(new_dose,2)} mg/L"

    elif predicted_ntu >= 1:
        new_dose = dose * 1.1
        return f"⚠️ Underdosing → Increase to ~{round(new_dose,2)} mg/L"

    elif frc < 0.2:
        return "⚠️ Low FRC → Increase chlorine dosing"

    else:
        return "✔️ Stable condition"


# ===============================
# 🔄 AUTO REFRESH
# ===============================
st_autorefresh(interval=30000, key="weather_refresh")


# ===============================
# 🎛 UI SECTION
# ===============================
st.markdown("## 🤖 AI Feedback & Learning System")

left_col, right_col = st.columns([2,1])

# LEFT SIDE → INPUT
with left_col:
    col1, col2 = st.columns(2)

    with col1:
        dose = st.slider("Dose Applied (mg/L)", 0.0, 100.0, 10.0)
        final_turbidity = st.number_input("Final Turbidity (NTU)", 0.0, 50.0, 1.0)
        frc = st.number_input("Final Residual Chlorine (mg/L)", 0.0, 5.0, 0.5)

    with col2:
        raw_turbidity = st.number_input("Raw Water Turbidity (NTU)", 0.0, 500.0, 50.0)

    submit = st.button("Submit Feedback")

# RIGHT SIDE → WEATHER
with right_col:
    st.markdown("### 🌦 Live Weather")

    condition, temp = get_weather()

    if condition in ["Error", "API Error", "No Data"]:
        st.error("⚠️ Weather not loading (Check API / Internet)")
    else:
        st.metric("🌡 Temp (°C)", f"{round(temp,1)}")

        if condition == "Rainy":
            st.error("🌧 Rainy → High turbidity expected")
        elif condition == "Cloudy":
            st.warning("☁️ Cloudy → Moderate condition")
        elif condition == "Clear":
            st.success("☀️ Clear → Stable condition")
        else:
            st.info(condition)


# ===============================
# 🚀 MAIN EXECUTION
# ===============================
if submit:

    weather, _ = get_weather()

    if final_turbidity < 1 and frc >= 0.2:
        status = "Achieved"
    else:
        status = "Not Achieved"

    save_feedback(dose, raw_turbidity, final_turbidity, frc, weather, status)

    model, le, df = train_model()

    remark = generate_remark(dose, raw_turbidity, frc, weather, model, le)

    st.markdown("### 📊 AI Analysis Result")

    col3, col4, col5 = st.columns(3)

    col3.metric("Status", status)
    col4.metric("Weather", weather)
    col5.metric("Final NTU", round(final_turbidity,2))

    st.info(f"💧 FRC: {frc} mg/L")
    st.warning(remark)

    if df is not None:
        X = df[['Dose','Raw_NTU','FRC','Weather_encoded']]
        y = df['Final_NTU']
        confidence = model.score(X,y)
        st.success(f"🧠 Model Confidence: {round(confidence*100,1)}%")

    if df is None or len(df) < 10:
        st.info("📚 System is learning... Add more feedback")
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
