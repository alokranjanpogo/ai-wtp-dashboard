import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import datetime
import pytz
from streamlit_autorefresh import st_autorefresh
# ===============================
# AUTO REFRESH
# ===============================
st_autorefresh(interval=19000, key="scada_refresh")
st.set_page_config(page_title="WTP Moharda SCADA", layout="wide")

# ===============================
# TITLE
# ===============================
st.title("🏭 WTP MOHARDA – LIVE HMI PANEL")
ist = pytz.timezone('Asia/Kolkata')
current_time = datetime.datetime.now(ist)
st.markdown(f"### 🕒 {current_time.strftime('%d-%m-%Y %H:%M:%S')}")


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

import plotly.graph_objects as go
# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="WTP Dashboard",
    layout="wide"
)


# ==========================================
# LOAD EXCEL FILE
# ==========================================

file_name = "Inlet_outlet_turbidity_dosing_ details.xlsx"

try:

    df = pd.read_excel(file_name, sheet_name="RawWater")

    # Clean column names
    df.columns = [str(c).strip() for c in df.columns]

    # Convert Date column properly
    df["Date"] = pd.to_datetime(
        df["Date"],
        dayfirst=True,
        errors="coerce"
    )

    # Remove invalid dates if any
    df = df.dropna(subset=["Date"])

    

    # ==========================================
    # DASHBOARD HEADING
    # ==========================================

    st.subheader("Turbidity & Alum Dosing Monitoring")

    # ==========================================
    # DATE FILTER BUTTONS
    # ==========================================

    st.markdown("📅 Select Monitoring Period")

    d1, d2 = st.columns(2)

    with d1:
        start_date = st.date_input(
            "Start Date",
            value=df["Date"].min()
        )

    with d2:
        end_date = st.date_input(
            "End Date",
            value=df["Date"].max()
        )

    # Filter dataframe
    filtered_df = df[
        (df["Date"] >= pd.to_datetime(start_date)) &
        (df["Date"] <= pd.to_datetime(end_date))
    ]

    # ==========================================
    # SIDE BY SIDE GRAPHS
    # ==========================================

    col1, col2 = st.columns(2)

    # ==========================================
    # GRAPH 1
    # ==========================================

    with col1:
    
        st.subheader("📊 Turbidity & Alum Dosing")
    
        fig1 = go.Figure()
    
        # BLUE BAR FOR ALUM DOSAGE
        fig1.add_trace(
            go.Bar(
                x=filtered_df["Date"],
                y=filtered_df["Alum Dosage (ppm)"],
                name="Alum Dosage",
                marker_color="blue",
                opacity=0.8
            )
        )
    
        # RED LINE FOR TURBIDITY
        fig1.add_trace(
            go.Scatter(
                x=filtered_df["Date"],
                y=filtered_df["Turbidity (NTU)"],
                mode="lines+markers",
                name="Raw Turbidity",
                line=dict(color="red", width=3)
            )
        )
    
        fig1.update_layout(
            height=450,
            hovermode="x unified",
            xaxis_title="Date",
            yaxis_title="Value",
            barmode="group",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
    
        st.plotly_chart(fig1, use_container_width=True)
        # ==========================================
    # GRAPH 2
    # ==========================================

    with col2:

        st.subheader("📈 Inlet vs Outlet Turbidity")

        fig2 = go.Figure()

        # RED LINE
        fig2.add_trace(
            go.Scatter(
                x=filtered_df["Date"],
                y=filtered_df["Turbidity (NTU)"],
                mode="lines+markers",
                name="Inlet Turbidity",
                line=dict(color="red", width=3)
            )
        )

        # BLUE LINE
        fig2.add_trace(
            go.Scatter(
                x=filtered_df["Date"],
                y=filtered_df["Outlet Turbidity (NTU)"],
                mode="lines+markers",
                name="Outlet Turbidity",
                line=dict(color="blue", width=3)
            )
        )

        fig2.update_layout(
            height=450,
            hovermode="x unified",
            xaxis_title="Date",
            yaxis_title="Turbidity (NTU)"
        )

        st.plotly_chart(fig2, use_container_width=True)

except FileNotFoundError:

    st.error(
        "Excel file not found. "
        "Make sure 'Inlet_outlet_turbidity_dosing_details.xlsx' "
        "is uploaded in your GitHub repository."
    )

except Exception as e:

    st.error(f"Error: {e}")
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

# ============================================================
# SMART CLARIFIER + FILTER BED MONITORING SYSTEM
# REALISTIC WTP MONITORING VERSION
# ============================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ============================================================
# LIGHT CLEAN UI
# ============================================================

st.markdown("""
<style>

.stApp {
    background-color: #f5f7fa;
}

[data-testid="stMetric"] {
    background-color: white;
    border-radius: 12px;
    padding: 12px;
    border: 1px solid #dbe4ee;
    box-shadow: 0px 1px 4px rgba(0,0,0,0.08);
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# LOAD EXCEL
# ============================================================

trend_df = pd.read_excel("Moharda_WTP_2026_Realistic_Adjusted.xlsx")

trend_df["Date"] = pd.to_datetime(trend_df["Date"])

# ============================================================
# TITLE
# ============================================================

st.markdown("---")
st.subheader("📊 Smart Clarifier & Filter Bed Monitoring")

# ============================================================
# DATE FILTER
# ============================================================

selected_date = st.date_input(
    "Select Monitoring Date",
    value=trend_df["Date"].max()
)

selected_date = pd.to_datetime(selected_date)

# ============================================================
# FILTER DATA
# ============================================================

day_df = trend_df[
    trend_df["Date"] == selected_date
]

# ============================================================
# SAFETY CHECK
# ============================================================

if day_df.empty:

    st.error("No monitoring data available for selected date.")

else:

    # ========================================================
    # CLARIFIER DATA
    # ========================================================

    clarifier_data = day_df[
        day_df["Unit"] == "Clarifier"
    ]

    if clarifier_data.empty:

        st.error("Clarifier data not found.")

    else:

        clar_inlet = clarifier_data["Inlet Turbidity"].iloc[0]

        clar_outlet = clarifier_data["Outlet Turbidity"].iloc[0]

        clar_cond = clarifier_data["Conductivity (µS/cm)"].iloc[0]

        # ====================================================
        # CLARIFIER HEALTH
        # ====================================================

        if clar_outlet <= 5:
            clar_health = "Healthy"

        elif clar_outlet <= 10:
            clar_health = "Moderate"

        else:
            clar_health = "Critical"

        # ====================================================
        # BIG CLARIFIER GAUGE
        # ====================================================

        st.markdown("🌀 Clarifier Live Monitoring")

        fig_clar = go.Figure(go.Indicator(

            mode="gauge+number",

            value=clar_outlet,

            number={
                'suffix': " NTU",
                'font': {
                    'size': 44,
                    'color': "#0077b6"
                }
            },

            title={
                'text': "Clarifier Outlet Turbidity",
                'font': {
                    'size': 24
                }
            },

            gauge={

                'axis': {
                    'range': [0,20]
                },

                'bar': {
                    'color': "#0077b6",
                    'thickness': 0.35
                },

                'bgcolor': "#edf2f7",

                'borderwidth': 2,

                'bordercolor': "#0077b6",

                'steps': [

                    {
                        'range':[0,5],
                        'color': "#d4edda"
                    },

                    {
                        'range':[5,10],
                        'color': "#fff3cd"
                    },

                    {
                        'range':[10,20],
                        'color': "#f8d7da"
                    }
                ]
            }
        ))

        fig_clar.update_layout(

            paper_bgcolor="#f5f7fa",

            height=420
        )

        st.plotly_chart(
            fig_clar,
            use_container_width=True
        )

        # ====================================================
        # METRICS
        # ====================================================

        m1,m2,m3,m4 = st.columns(4)

        m1.metric(
            "Inlet Turbidity",
            f"{clar_inlet:.1f} NTU"
        )

        m2.metric(
            "Outlet Turbidity",
            f"{clar_outlet:.1f} NTU"
        )

        m3.metric(
            "Clarifier Health",
            clar_health
        )

        m4.metric(
            "Conductivity",
            f"{clar_cond:.0f} µS/cm"
        )

        # ====================================================
        # AI ANALYSIS
        # ====================================================

        st.markdown("Analysis")

        if clar_outlet <= 5:

            st.success(
                "Clarifier performance stable. Turbidity under control."
            )

        elif clar_outlet <= 10:

            st.warning(
                "Clarifier operating under moderate load."
            )

        else:

            st.error(
                "High clarifier outlet turbidity detected. Check coagulant dosing and sludge blanket."
            )

    # ========================================================
    # FILTER BED SECTION
    # ========================================================

    st.markdown("---")
    st.markdown("🧪 Filter Bed Live Status")

    cols = st.columns(6)

    filter_summary = []

    for i in range(1,7):

        filter_name = f"Filter Bed {i}"

        filter_data = day_df[
            day_df["Unit"] == filter_name
        ]

        if filter_data.empty:
            continue

        filter_outlet = filter_data["Outlet Turbidity"].iloc[0]

        # ====================================================
        # FILTER HEALTH
        # ====================================================

        if filter_outlet <= 0.3:

            status = "Excellent"

        elif filter_outlet <= 0.7:

            status = "Good"

        elif filter_outlet <= 1:

            status = "Warning"

        else:

            status = "Backwash Needed"

        filter_summary.append({

            "Filter Bed": filter_name,

            "Outlet Turbidity": round(filter_outlet,2),

            "Status": status
        })

        # ====================================================
        # SMALL FILTER GAUGES
        # ====================================================

        fig_small = go.Figure(go.Indicator(

            mode="gauge+number",

            value=filter_outlet,

            number={
                'suffix': " NTU",
                'font': {
                    'size': 15,
                    'color': "#0077b6"
                }
            },

            title={
                'text': f"FB-{i}",
                'font': {
                    'size': 13
                }
            },

            gauge={

                'axis': {
                    'range':[0,2]
                },

                'bar': {
                    'color': "#0077b6",
                    'thickness': 0.22
                },

                'bgcolor': "#edf2f7",

                'borderwidth': 1,

                'bordercolor': "#0077b6",

                'steps':[

                    {
                        'range':[0,0.3],
                        'color': "#d4edda"
                    },

                    {
                        'range':[0.3,0.7],
                        'color': "#cfe2ff"
                    },

                    {
                        'range':[0.7,1],
                        'color': "#fff3cd"
                    },

                    {
                        'range':[1,2],
                        'color': "#f8d7da"
                    }
                ]
            }
        ))

        fig_small.update_layout(

            paper_bgcolor="#f5f7fa",

            height=135,

            margin=dict(
                l=5,
                r=5,
                t=28,
                b=5
            )
        )

        cols[i-1].plotly_chart(
            fig_small,
            use_container_width=True
        )

    # ========================================================
    # FILTER SUMMARY
    # ========================================================

    st.markdown("---")
    st.markdown("📋 Filter Bed Summary")

    filter_summary_df = pd.DataFrame(filter_summary)

    st.dataframe(
        filter_summary_df,
        use_container_width=True
    )

    # ========================================================
    # TREND SECTION
    # ========================================================

    st.markdown("---")
    st.subheader("📈 Historical Output Turbidity Trend")

    selected_unit = st.selectbox(
        "Select Unit",
        trend_df["Unit"].unique()
    )

    unit_df = trend_df[
        trend_df["Unit"] == selected_unit
    ]

    previous_df = unit_df[
        unit_df["Date"] <= selected_date
    ].sort_values("Date")

    if previous_df.empty:

        st.warning("No trend data available.")

    else:

        current_turbidity = previous_df[
            previous_df["Date"] == selected_date
        ]["Outlet Turbidity"].iloc[0]

        # ====================================================
        # TREND GRAPH
        # ====================================================

        fig_trend = go.Figure()

        fig_trend.add_trace(go.Scatter(

            x=previous_df["Date"],

            y=previous_df["Outlet Turbidity"],

            mode="lines+markers",

            line=dict(
                color="#0077b6",
                width=3
            ),

            marker=dict(
                size=6
            ),

            name="Outlet Turbidity"
        ))

        fig_trend.update_layout(

            template="simple_white",

            title=f"{selected_unit} Output Turbidity Trend",

            xaxis_title="Date",

            yaxis_title="Outlet Turbidity (NTU)",

            height=450
        )

        st.plotly_chart(
            fig_trend,
            use_container_width=True
        )

        # ====================================================
        # TREND ANALYSIS
        # ====================================================

        st.markdown("Historical Analysis")

        if current_turbidity <= 0.5:

            st.success(
                f"{selected_unit} operating with excellent water quality."
            )

        elif current_turbidity <= 1:

            st.warning(
                f"{selected_unit} performance acceptable."
            )

        else:

            st.error(
                f"{selected_unit} turbidity rising. Maintenance or backwash recommended."
            )
# ===============================
# STREAMLIT UI
# ===============================

st.set_page_config(page_title="Water Treatment Performance", layout="wide")

st.header("💧 Water Treatment Performance Dashboard")

st.subheader("🏭 Unit Selection")

unit_type = st.selectbox("Select Unit", ["Clarifier", "Filter Bed"])

# Inputs
st.subheader("📥 Input Parameters")

col1, col2 = st.columns(2)

with col1:
    t_in = st.number_input("Inlet Turbidity (NTU)", min_value=0.0, value=100.0)

with col2:
    t_out = st.number_input("Outlet Turbidity (NTU)", min_value=0.0, value=10.0)

# ============================================================
# LIMIT FUNCTION
# ============================================================

def get_limit(unit_type):

    limits = {

        "Clarifier": 5,

        "Filter Bed 1": 1,

        "Filter Bed 2": 1,

        "Filter Bed 3": 1,

        "Filter Bed 4": 1,

        "Filter Bed 5": 1,

        "Filter Bed 6": 1
    }

    return limits.get(unit_type, 1)
# ===============================
# CALCULATIONS
# ===============================
# ============================================================
# PERFORMANCE FUNCTIONS
# ============================================================

def calculate_efficiency(t_in, t_out):

    if t_in == 0:
        return 0

    return ((t_in - t_out) / t_in) * 100


def performance_index(t_out, limit):

    if limit == 0:
        return 0

    return t_out / limit


def performance_status(t_out, limit):

    if t_out <= limit:
        return "Safe"

    elif t_out <= limit * 1.5:
        return "Warning"

    else:
        return "Critical"


def performance_grade(pi):

    if pi <= 1:
        return "A"

    elif pi <= 1.5:
        return "B"

    else:
        return "C"


def get_color(status, pi):

    if status == "Safe":
        return "green"

    elif status == "Warning":
        return "orange"

    else:
        return "red"

limit = get_limit(unit_type)

eff = calculate_efficiency(t_in, t_out)
pi = performance_index(t_out, limit)
status = performance_status(t_out, limit)
grade = performance_grade(pi)
color = get_color(status, pi)

# ===============================
# DISPLAY METRICS
# ===============================

st.subheader("📊 Performance Results")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Efficiency (%)", f"{eff:.2f}")
col2.metric("Performance Index", f"{pi:.2f}")
col3.metric("Status", status)
col4.metric("Grade", grade)

# ===============================
# VISUAL INDICATOR
# ===============================

st.subheader("Performance Indicator")

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

st.plotly_chart(fig_turb, use_container_width=True)
# ============================================================
# IMPORTS (VERY IMPORTANT)
# ============================================================

import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.subheader(" Intelligent Alum Dosing Decision System")

import numpy as np
import plotly.graph_objects as go

# ============================================================
# INPUTS
# ============================================================

flow_mld = 18
flow_m3_day = flow_mld * 1000

turbidity = float(intake_turb) # from existing slider/input

ph = st.slider("pH", 4.5, 9.0, 7.0, 0.1)

# ============================================================
# INDUSTRIAL DISCHARGE INPUT
# ============================================================

industrial = st.toggle("⚠️ Industrial Discharge Present")

industrial_type = "None"
discharge_level = 1
conductivity = 350
odor_detected = False
water_color = "Normal"

if industrial:

    industrial_type = st.selectbox(
        "Industrial Discharge Type",
        [
            "Textile/Dye",
            "Steel/Metal",
            "Organic/Food",
            "Chemical",
            "Mixed Effluent"
        ]
    )

    # ========================================================
    # INDUSTRIAL WATER QUALITY INDICATORS
    # ========================================================

    st.markdown("🧪 Industrial Impact Indicators")

    conductivity = st.slider(
        "Conductivity (µS/cm)",
        100,
        3000,
        700
    )

    odor_detected = st.toggle(
        "Chemical / Oily Odor Detected"
    )

    water_color = st.selectbox(
        "Raw Water Appearance",
        [
            "Normal",
            "Slightly Colored",
            "Highly Colored"
        ]
    )

    # ========================================================
    # AUTOMATIC SEVERITY ESTIMATION
    # ========================================================

    severity_score = 0

    # Conductivity effect
    if conductivity > 1200:
        severity_score += 2

    elif conductivity > 800:
        severity_score += 1

    # pH abnormality
    if ph < 6 or ph > 8.5:
        severity_score += 1

    # Turbidity effect
    if turbidity > 250:
        severity_score += 2

    elif turbidity > 120:
        severity_score += 1

    # Odor effect
    if odor_detected:
        severity_score += 1

    # Color effect
    if water_color == "Highly Colored":
        severity_score += 2

    elif water_color == "Slightly Colored":
        severity_score += 1

    # ========================================================
    # FINAL SEVERITY CLASSIFICATION
    # ========================================================

    if severity_score <= 1:
        discharge_level = 1
        severity_label = "Very Mild"

    elif severity_score == 2:
        discharge_level = 2
        severity_label = "Mild"

    elif severity_score == 3:
        discharge_level = 3
        severity_label = "Moderate"

    elif severity_score == 4:
        discharge_level = 4
        severity_label = "High"

    else:
        discharge_level = 5
        severity_label = "Severe"

    # ========================================================
    # DISPLAY INDUSTRIAL SEVERITY
    # ========================================================

    if discharge_level >= 5:
        st.error(
            f"🔴 Industrial Severity: {severity_label}"
        )

    elif discharge_level >= 3:
        st.warning(
            f"🟠 Industrial Severity: {severity_label}"
        )

    else:
        st.success(
            f"🟢 Industrial Severity: {severity_label}"
        )

# ============================================================
# 🧪 JAR TEST INPUT
# ============================================================

st.markdown("🧪 Jar Test Input")

jar_available = st.toggle("Use Jar Test")

if jar_available:

    jar_dose = st.number_input(
        "Enter Jar Test Dose (mg/L)",
        min_value=1.0,
        max_value=200.0,
        value=25.0,
        step=1.0
    )

else:
    jar_dose = None

# ============================================================
# STANDARD MODELS
# ============================================================

def cpheeo_model(t):
    return 0.35 * t + 5

def awwa_model(t):
    return 0.40 * t + 8

def bis_model(t):
    return 0.30 * t + 6

cpheeo = cpheeo_model(turbidity)
awwa = awwa_model(turbidity)
bis = bis_model(turbidity)

# ============================================================
# pH EFFECT ON COAGULATION
# ============================================================

if ph < 5.5:
    ph_factor = 1.25

elif 5.5 <= ph < 6.0:
    ph_factor = 1.10

elif 6.0 <= ph <= 7.2:
    ph_factor = 1.0

elif 7.2 < ph <= 8.0:
    ph_factor = 1.08

else:
    ph_factor = 1.18

# ============================================================
# INDUSTRIAL IMPACT ENGINEERING LOGIC
# ============================================================

industrial_factor = 1.0

if industrial:

    if industrial_type == "Textile/Dye":
        industrial_factor = 1.10 + (0.05 * discharge_level)

    elif industrial_type == "Steel/Metal":
        industrial_factor = 1.08 + (0.04 * discharge_level)

    elif industrial_type == "Organic/Food":
        industrial_factor = 1.05 + (0.03 * discharge_level)

    elif industrial_type == "Chemical":
        industrial_factor = 1.12 + (0.06 * discharge_level)

    elif industrial_type == "Mixed Effluent":
        industrial_factor = 1.15 + (0.05 * discharge_level)

# ============================================================
# TURBIDITY BOOST FACTOR
# ============================================================

if turbidity > 300:
    turb_factor = 1.35

elif turbidity > 150:
    turb_factor = 1.20

else:
    turb_factor = 1.0

# ============================================================
# AI DOSING LOGIC
# ============================================================

if jar_available:

    deviation = abs(jar_dose - cpheeo)

    if deviation > 25:
        st.warning(
            "⚠️ Jar Test significantly differs from theoretical estimate"
        )

    ai_dose = (
        0.75 * jar_dose +
        0.15 * cpheeo +
        0.05 * awwa +
        0.05 * bis
    )

else:

    ai_dose = (
        0.40 * cpheeo +
        0.35 * awwa +
        0.25 * bis
    )

# ============================================================
# FINAL CORRECTIONS
# ============================================================

ai_dose = ai_dose * ph_factor * industrial_factor * turb_factor

# Safety limit
ai_dose = float(np.clip(ai_dose, 5, 150))

# ============================================================
# CHEMICAL REQUIREMENT
# ============================================================

alum_kg_day = (ai_dose * flow_m3_day) / 1000

# PAC generally requires lower dose than alum
pac_dose = ai_dose * 0.45

# ============================================================
# RAW WATER RISK CLASSIFICATION
# ============================================================

if turbidity < 50:
    raw_risk = "Low"

elif turbidity < 150:
    raw_risk = "Moderate"

elif turbidity < 300:
    raw_risk = "High"

else:
    raw_risk = "Critical"

# ============================================================
# CONFIDENCE SCORE
# ============================================================

confidence = 92

if not jar_available:
    confidence -= 15

if industrial:
    confidence -= 8

if turbidity > 300:
    confidence -= 10

confidence = max(confidence, 60)

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

left, right = st.columns([1.1, 1.4])

# ============================================================
# 📊 LEFT → GRAPH + METRICS
# ============================================================

with left:

    st.markdown("📊 Dosing Decision Curve")

    x = np.linspace(0, 400, 150)

    # More realistic nonlinear curve
    y_ai = (
        8 +
        0.22 * x +
        12 * np.log1p(x / 40)
    )

    fig = go.Figure()

    # ========================================================
    # OPTIMAL ZONE
    # ========================================================

    fig.add_hrect(
        y0=20,
        y1=30,
        fillcolor="green",
        opacity=0.15,
        line_width=0
    )

    # ========================================================
    # WARNING ZONE
    # ========================================================

    fig.add_hrect(
        y0=30,
        y1=60,
        fillcolor="yellow",
        opacity=0.10,
        line_width=0
    )

    # ========================================================
    # CRITICAL ZONE
    # ========================================================

    fig.add_hrect(
        y0=60,
        y1=120,
        fillcolor="red",
        opacity=0.08,
        line_width=0
    )

    # ========================================================
    # AI CURVE
    # ========================================================

    fig.add_trace(go.Scatter(
        x=x,
        y=y_ai,
        line=dict(
            color="cyan",
            width=4
        ),
        name="Curve"
    ))

    # ========================================================
    # OPERATING POINT
    # ========================================================

    fig.add_trace(go.Scatter(
        x=[turbidity],
        y=[ai_dose],
        mode="markers+text",
        marker=dict(
            size=14,
            color="yellow"
        ),
        text=["Operating"],
        textposition="top center"
    ))

    # ========================================================
    # GRAPH LAYOUT
    # ========================================================

    fig.update_layout(
        template="plotly_dark",
        height=350,
        margin=dict(
            l=10,
            r=10,
            t=40,
            b=10
        ),
        xaxis_title="Turbidity (NTU)",
        yaxis_title="Alum Dose (mg/L)",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # ========================================================
    # METRICS
    # ========================================================

    st.metric("Recommended Alum Dose", f"{ai_dose:.1f} mg/L")

    st.metric(
        "Alum Required",
        f"{alum_kg_day:,.0f} kg/day"
    )

    st.metric("Raw Water Risk", raw_risk)

    st.metric(
        "Prediction Confidence",
        f"{confidence}%"
    )

# ============================================================
# 📘 RIGHT → DECISION PANEL
# ============================================================

with right:

    st.markdown("📘 Recommendation Logic")

    st.markdown(f"""
### Input Conditions

- Turbidity: **{turbidity:.1f} NTU**
- pH: **{ph:.1f}**
- Industrial Discharge: **{"Yes" if industrial else "No"}**
- Risk Category: **{raw_risk}**
""")

    if industrial:

        st.markdown(f"""
### Industrial Impact

- Discharge Type: **{industrial_type}**
- Conductivity: **{conductivity} µS/cm**
- Water Appearance: **{water_color}**
- Odor Detected: **{"Yes" if odor_detected else "No"}**
- Severity Level: **{discharge_level}/5**
- Severity Category: **{severity_label}**
- Industrial Correction Factor: **{industrial_factor:.2f}**
""")

    st.markdown("---")

    st.markdown(f"""
### Standard Engineering Estimates

- CPHEEO Model: **{cpheeo:.1f} mg/L**
- AWWA Model: **{awwa:.1f} mg/L**
- BIS Estimate: **{bis:.1f} mg/L**
""")

    st.markdown("---")

    if jar_available:

        st.success(
            f"🧪 Jar Test Integrated: {jar_dose:.1f} mg/L"
        )

    else:

        st.warning(
            "⚠️ Jar Test not used — relying on theoretical models"
        )

    st.markdown("---")

    st.markdown(f"""
# ✅ Final AI Recommendation

👉 **{ai_dose:.1f} mg/L Alum Dose Recommended**

### Applied Engineering Corrections

✔ pH Factor: **{ph_factor:.2f}**  
✔ Industrial Factor: **{industrial_factor:.2f}**  
✔ Turbidity Factor: **{turb_factor:.2f}**

### Expected Outcomes

✔ Effective coagulation  
✔ Stable sludge blanket  
✔ Reduced filter loading  
✔ Improved settling efficiency  
✔ Better filtration stability

### Chemical Requirement

 Alum Requirement: **{alum_kg_day:,.0f} kg/day**  
 PAC Equivalent Dose: **{pac_dose:.1f} mg/L**

### AI Confidence

🎯 Confidence Level: **{confidence}%**
""")

# ============================================================
# ALERT SYSTEM
# ============================================================

st.markdown("---")
st.markdown("### 🚨 Intelligent Alert System")

if ai_dose > 80:

    st.error(
        "🔴 Extremely high chemical demand detected. "
        "Consider PAC optimization or pre-treatment."
    )

elif turbidity > 300:

    st.warning(
        "🟠 Severe raw water turbidity detected. "
        "Closely monitor sludge blanket and filter loading."
    )

elif jar_available and abs(ai_dose - jar_dose) > 5:

    st.warning(
        "🟡 AI recommendation deviates from Jar Test. "
        "Verify coagulation conditions."
    )

else:

    st.success(
        "🟢 System operating within optimal dosing conditions."
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
import streamlit as st
import smtplib
import pandas as pd
import numpy as np
import requests
import base64
import sqlite3
import plotly.graph_objects as go

from datetime import datetime
from sklearn.ensemble import RandomForestRegressor

# ===============================
# PAGE
# ===============================

st.set_page_config(layout="wide")

st.markdown("## Water Treatment Feedback System")

left_col, right_col = st.columns([2,1])

# ===============================
# EMAIL FUNCTION
# ===============================

def send_email_alert(message):

    sender = "alokranjan18april@gmail.com"
    password = "wpnrabqfbtkhsqpe"
    receiver = "alok.ranjan6@tatasteel.com"

    try:

        server = smtplib.SMTP("smtp.gmail.com", 587)

        server.starttls()

        server.login(sender, password)

        server.sendmail(
            sender,
            receiver,
            message.encode("utf-8")
        )

        server.quit()

        st.success("📧 Email Sent")

    except Exception as e:

        st.error(f"Email error: {e}")

# ===============================
# SESSION STATES
# ===============================

if "alarm" not in st.session_state:
    st.session_state.alarm = False

if "mail_sent" not in st.session_state:
    st.session_state.mail_sent = False

if "sound_enabled" not in st.session_state:
    st.session_state.sound_enabled = False

# ===============================
# DATABASE
# ===============================

conn = sqlite3.connect(
    "feedback_data.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""

CREATE TABLE IF NOT EXISTS feedback (

    timestamp TEXT,

    raw_turbidity REAL,

    alum_dose REAL,

    hypo_dose REAL,

    outlet_turbidity REAL,

    frc REAL,

    ph REAL,

    conductivity REAL,

    temperature REAL,

    humidity REAL,

    rainfall REAL
)

""")

conn.commit()

# ===============================
# WEATHER API
# ===============================

def get_weather_data():

    try:

        API_KEY = "f899db331049be78181d1afddbc92935"

        CITY = "Jamshedpur"

        url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

        data = requests.get(url).json()

        temperature = data["main"]["temp"]

        humidity = data["main"]["humidity"]

        rainfall = data.get("rain", {}).get("1h", 0)

        return temperature, humidity, rainfall

    except:

        return 30,70,0

# ===============================
# LOAD DATA
# ===============================

df = pd.read_sql(
    "SELECT rowid,* FROM feedback",
    conn
)

# ===============================
# INPUT SECTION
# ===============================

with left_col:

    c1, c2 = st.columns(2)

    with c1:

        alum_dose = st.slider(
            "Alum Dose (mg/L)",
            0.0,
            100.0,
            10.0
        )

        hypo_dose = st.slider(
            "Hypo Dose (mg/L)",
            0.0,
            20.0,
            3.0
        )

        outlet_turbidity = st.number_input(
            "Outlet Turbidity",
            0.0,
            50.0,
            1.0
        )

        frc = st.number_input(
            "FRC",
            0.0,
            5.0,
            0.5
        )

    with c2:

        raw_turbidity = st.number_input(
            "Raw Turbidity",
            0.0,
            500.0,
            50.0
        )

        ph = st.number_input(
            "pH",
            0.0,
            14.0,
            7.0
        )

        conductivity = st.number_input(
            "Conductivity",
            0.0,
            5000.0,
            350.0
        )

    submit = st.button(
        "💾 Save Operational Data",
        key="submit_btn"
    )

# ===============================
# SAVE DATA
# ===============================

if submit:

    now = datetime.now()

    temperature, humidity, rainfall = get_weather_data()

    cursor.execute("""

    INSERT INTO feedback VALUES (
        ?,?,?,?,?,?,?,?,?,?,?
    )

    """, (

        now.strftime("%Y-%m-%d %H:%M:%S"),

        raw_turbidity,

        alum_dose,

        hypo_dose,

        outlet_turbidity,

        frc,

        ph,

        conductivity,

        temperature,

        humidity,

        rainfall

    ))

    conn.commit()

    st.success(
        f"Saved at {now.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    st.rerun()

# ===============================
# RELOAD DATA
# ===============================

df = pd.read_sql(
    "SELECT rowid,* FROM feedback",
    conn
)

# ===============================
# EXPORT EXCEL
# ===============================

excel_file = "feedback_export.xlsx"

export_df = df.drop(columns=["rowid"])

export_df.to_excel(
    excel_file,
    index=False
)

# ===============================
# KPIs
# ===============================

st.markdown("## 📊 Learning Statistics")

good_data = df[
    (df["outlet_turbidity"] <= 1)
    &
    (df["frc"] >= 0.2)
    &
    (df["frc"] <= 1)
]

k1,k2,k3,k4 = st.columns(4)

k1.metric(
    "Total Samples",
    len(df)
)

k2.metric(
    "Successful Records",
    len(good_data)
)

if len(df) > 0:

    k3.metric(
        "Average Alum",
        f"{df['alum_dose'].mean():.1f} mg/L"
    )

    k4.metric(
        "Average Hypo",
        f"{df['hypo_dose'].mean():.2f} mg/L"
    )

# ===============================
# AI MODEL
# ===============================

if len(good_data) >= 30:

    st.markdown("## 🤖 Smart AI Recommendation")

    X = good_data[[

        "raw_turbidity",
        "ph",
        "conductivity",
        "temperature",
        "humidity",
        "rainfall"

    ]]

    y_alum = good_data["alum_dose"]

    y_hypo = good_data["hypo_dose"]

    alum_model = RandomForestRegressor(
        n_estimators=300,
        random_state=42
    )

    hypo_model = RandomForestRegressor(
        n_estimators=300,
        random_state=42
    )

    alum_model.fit(X, y_alum)

    hypo_model.fit(X, y_hypo)

    temperature, humidity, rainfall = get_weather_data()

    input_data = np.array([[

        raw_turbidity,

        ph,

        conductivity,

        temperature,

        humidity,

        rainfall

    ]])

    predicted_alum = alum_model.predict(input_data)[0]

    predicted_hypo = hypo_model.predict(input_data)[0]

    confidence = min(
        95,
        60 + (len(good_data) * 0.7)
    )

    a1,a2,a3 = st.columns(3)

    a1.metric(
        "Recommended Alum Dose",
        f"{predicted_alum:.1f} mg/L"
    )

    a2.metric(
        "Recommended Hypo Dose",
        f"{predicted_hypo:.2f} mg/L"
    )

    a3.metric(
        "AI Confidence",
        f"{confidence:.0f}%"
    )

else:

    remaining = 30 - len(good_data)

    st.info(
        f"AI activates after {remaining} more successful records."
    )

# ===============================
# ALERT + EMAIL
# ===============================

if outlet_turbidity > 1 or frc < 0.2:

    st.session_state.alarm = True

    if not st.session_state.mail_sent:

        msg = f"""Subject: 🚨 WATER QUALITY ALERT

Time: {datetime.now()}

Outlet Turbidity: {outlet_turbidity}

FRC: {frc}

Immediate action required.
"""

        send_email_alert(msg)

        st.session_state.mail_sent = True

else:

    st.session_state.mail_sent = False

# ===============================
# ENABLE SOUND
# ===============================

if not st.session_state.sound_enabled:

    if st.button(
        "🔊 Enable Alarm Sound",
        key="enable_sound"
    ):

        st.session_state.sound_enabled = True

        st.success("Sound Enabled ✅")

# ===============================
# ACTIVE ALARM
# ===============================

if st.session_state.alarm:

    st.error("🚨 CONTINUOUS ALARM ACTIVE")

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

    <div class="alarm-box">

    🚨 CRITICAL WATER QUALITY ALERT 🚨

    </div>

    """, unsafe_allow_html=True)

    # ===============================
    # SOUND
    # ===============================

    if st.session_state.sound_enabled:

        try:

            with open(
                "mixkit-sport-start-bleeps-918.wav",
                "rb"
            ) as f:

                audio_bytes = f.read()

                b64 = base64.b64encode(
                    audio_bytes
                ).decode()

            audio_html = f"""

            <audio autoplay loop controls>

                <source
                src="data:audio/wav;base64,{b64}"
                type="audio/wav">

            </audio>

            """

            st.markdown(
                audio_html,
                unsafe_allow_html=True
            )

        except Exception as e:

            st.warning(f"⚠️ Sound issue: {e}")

    else:

        st.warning("🔊 Enable sound once")

    # ===============================
    # STOP BUTTON
    # ===============================

    if st.button(
        "🔴 Stop Alarm",
        key="stop_alarm_btn"
    ):

        st.session_state.alarm = False

        st.session_state.mail_sent = False

        st.rerun()

# ===============================
# DATA TABLE
# ===============================

st.markdown("## 📂 Stored Operational Data")

if len(df) > 0:

    display_df = df.sort_values(
        by="timestamp",
        ascending=False
    )

    st.dataframe(
        display_df.drop(columns=["rowid"]),
        use_container_width=True
    )

# ===============================
# DELETE ROW
# ===============================

if len(df) > 0:

    selected_rowid = st.selectbox(
        "Select Row to Delete",
        display_df["rowid"]
    )

    if st.button("🗑 Delete Selected Row"):

        cursor.execute(
            "DELETE FROM feedback WHERE rowid=?",
            (int(selected_rowid),)
        )

        conn.commit()

        st.success("Row Deleted")

        st.rerun()

# ===============================
# TREND GRAPH
# ===============================

if len(df) > 0:

    st.markdown("## 📈 Operational Trends")

    fig = go.Figure()

    fig.add_trace(go.Scatter(

        x=df["timestamp"],

        y=df["alum_dose"],

        mode="lines+markers",

        name="Alum Dose"

    ))

    fig.add_trace(go.Scatter(

        x=df["timestamp"],

        y=df["hypo_dose"],

        mode="lines+markers",

        name="Hypo Dose"

    ))

    fig.update_layout(

        template="plotly_dark",

        height=450,

        xaxis_title="Timestamp",

        yaxis_title="Dose (mg/L)"

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ===============================
# DOWNLOAD EXCEL
# ===============================

with open(excel_file, "rb") as f:

    st.download_button(

        "📥 Download Excel Data",

        f,

        file_name="feedback_export.xlsx"
    )

# ============================================================
# 📊 AI ANALYTICS DASHBOARD
# ============================================================

st.markdown("---")
st.markdown("📊 Performance Analytics")

if len(df) > 0:

    a1, a2, a3, a4 = st.columns(4)

    with a1:

        st.metric(
            "Total Samples",
            len(df)
        )

    with a2:

        st.metric(
            "Average Dose",
            f"{df['dose'].mean():.1f} mg/L"
        )

    with a3:

        st.metric(
            "Avg Outlet Turbidity",
            f"{df['Outlet_turbidity'].mean():.2f}"
        )

    with a4:

        good_quality = len(
            df[
                (df["Outlet_turbidity"] <= 1)
            ]
        )

        efficiency = (
            good_quality / len(df)
        ) * 100

        st.metric(
            "Treatment Efficiency",
            f"{efficiency:.1f}%"
        )

    # ========================================================
    # TREND CHART
    # ========================================================

    st.markdown("📈 Treatment Trend")

    chart_df = df.copy()

    chart_df["timestamp"] = pd.to_datetime(
        chart_df["timestamp"]
    )

    chart_df = chart_df.sort_values(
        by="timestamp"
    )

    st.line_chart(
        chart_df.set_index("timestamp")[
            ["raw_turbidity", "dose"]
        ]
    )

    # ========================================================
    # AI INSIGHT
    # ========================================================

    latest = chart_df.iloc[-1]

    if latest["final_turbidity"] <= 1:

        st.success(
            "✅ Latest treatment cycle achieved "
            "desired water quality."
        )

    else:

        st.warning(
            "⚠️ Latest cycle indicates possible "
            "coagulation or filtration issue."
        )
# ===============================
# WEATHER
# ===============================

with right_col:

    st.markdown("🌤 Weather")

    API_KEY = "f899db331049be78181d1afddbc92935"

    CITY = "Jamshedpur"

    try:

        url = (
            f"http://api.openweathermap.org/data/2.5/weather?"
            f"q={CITY}&appid={API_KEY}&units=metric"
        )

        data = requests.get(url).json()

        temperature = data['main']['temp']

        humidity = data['main']['humidity']

        weather_desc = data['weather'][0]['description']

        st.metric(
            "Temp",
            f"{temperature} °C"
        )

        st.metric(
            "Humidity",
            f"{humidity} %"
        )

        st.write(weather_desc)
        
        # ====================================================
        # RECOMMENDED ACTIONS
        # ====================================================
        
        st.markdown("""
        ### Suggested Actions
        
        ✔ Monitor intake turbidity  
        ✔ Keep additional alum ready  
        ✔ Observe filter loading  
        ✔ Monitor sludge blanket  
        ✔ Verify residual chlorine
        """)

    except Exception as e:

        st.error(f"Weather error: {e}")
# ============================================================
# 🌦️ WEATHER BASED DOSING PREDICTION CENTER
# ============================================================

import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# SECTION TITLE
# ============================================================

st.subheader("🌦️ Weather Based Prediction System")

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.small-weather{
    background: linear-gradient(135deg,#0f172a,#1e293b);
    padding:8px;
    border-radius:10px;
    text-align:center;
    color:white;
    border:1px solid rgba(255,255,255,0.06);
    font-size:13px;
}

.ai-alert{
    background:#111827;
    padding:10px;
    border-radius:10px;
    border-left:4px solid cyan;
    margin-bottom:8px;
    color:white;
    font-size:14px;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# WEATHER API
# ============================================================

API_KEY = "f899db331049be78181d1afddbc92935"

CITY = "Jamshedpur"

url = f"https://api.openweathermap.org/data/2.5/forecast?q={CITY}&appid={API_KEY}&units=metric"

response = requests.get(url)

# ============================================================
# WEATHER DATA
# ============================================================

if response.status_code == 200:

    data = response.json()

    weather_data = []

    for item in data["list"][:12]:

        weather_data.append({

            "Time": item["dt_txt"][11:16],

            "Temp": item["main"]["temp"],

            "Humidity": item["main"]["humidity"],

            "Rain": item.get("rain", {}).get("3h", 0),

            "Condition": item["weather"][0]["main"]

        })

    weather_df = pd.DataFrame(weather_data)

    # ========================================================
    # SMALL WEATHER FORECAST CARDS
    # ========================================================

    st.markdown("⏰ Hourly Weather Forecast")

    cols = st.columns(6)

    for i in range(6):

        row = weather_df.iloc[i]

        with cols[i]:

            st.markdown(f"""
            <div class='small-weather'>

            <b>{row['Time']}</b><br>

            🌡️ {row['Temp']:.1f}°C<br>

            💧 {row['Humidity']}%<br>

            🌧️ {row['Rain']} mm

            </div>
            """, unsafe_allow_html=True)

    # ========================================================
    # WEATHER IMPACT ENGINE
    # ========================================================

    predicted_alum = []
    predicted_chlorine = []

    ai_messages = []

    for _, row in weather_df.iterrows():

        # ====================================================
        # TEMPERATURE FACTOR
        # ====================================================

        temp_factor = 1.0

        if row["Temp"] > 35:
            temp_factor += 0.12

        elif row["Temp"] > 30:
            temp_factor += 0.06

        # ====================================================
        # RAIN FACTOR
        # ====================================================

        rain_factor = 1.0

        if row["Rain"] > 8:
            rain_factor += 0.30

        elif row["Rain"] > 3:
            rain_factor += 0.15

        # ====================================================
        # HUMIDITY FACTOR
        # ====================================================

        humidity_factor = 1.0

        if row["Humidity"] > 85:
            humidity_factor += 0.05

        # ====================================================
        # INDUSTRIAL FACTOR
        # ====================================================

        weather_industrial_factor = 1.0

        if industrial:

            if conductivity > 1200:
                weather_industrial_factor += 0.15

            elif conductivity > 800:
                weather_industrial_factor += 0.08

        # ====================================================
        # FUTURE ALUM PREDICTION
        # ====================================================

        future_alum = (

            ai_dose *

            temp_factor *

            rain_factor *

            humidity_factor *

            weather_industrial_factor

        )

        predicted_alum.append(future_alum)

        # ====================================================
        # FUTURE CHLORINE DEMAND PREDICTION
        # ====================================================

        base_chlorine_dose = frc_selected * 4.5

        temp_chlorine_factor = (
            1 + ((row["Temp"] - 25) * 0.02)
        )

        rain_chlorine_factor = (
            1 + (row["Rain"] * 0.035)
        )

        humidity_chlorine_factor = 1.0

        if row["Humidity"] > 85:
            humidity_chlorine_factor += 0.03

        future_chlorine_dose = (

            base_chlorine_dose *

            temp_chlorine_factor *

            rain_chlorine_factor *

            humidity_chlorine_factor

        )

        predicted_chlorine.append(
            future_chlorine_dose
        )

    weather_df["Pred Alum"] = predicted_alum

    weather_df["Pred Chlorine"] = predicted_chlorine

    # ========================================================
    # RECOMMENDATION SYSTEM
    # ========================================================

    st.markdown("Operational Recommendations")

    avg_temp = weather_df["Temp"].mean()

    avg_rain = weather_df["Rain"].sum()

    avg_humidity = weather_df["Humidity"].mean()

    # ========================================================
    # HIGH TEMPERATURE
    # ========================================================

    if avg_temp > 35:

        ai_messages.append(
            "🔥 High temperature detected → Increase chlorine dosing gradually due to faster chlorine decay."
        )

        ai_messages.append(
            "🧪 Conduct frequent jar testing to optimize alum consumption."
        )

        ai_messages.append(
            "💨 Increase aeration rates to maintain dissolved oxygen stability."
        )

    # ========================================================
    # HEAVY RAIN
    # ========================================================

    if avg_rain > 10:

        ai_messages.append(
            "🌧️ Heavy rainfall expected → Raw water turbidity may increase sharply."
        )

        ai_messages.append(
            "⚠️ Increase Alum/PAC dose gradually for stable coagulation."
        )

        ai_messages.append(
            "🚨 Monitor sludge blanket and filter loading carefully."
        )

        ai_messages.append(
            "🧫 Increase chlorine monitoring frequency during rainfall period."
        )

    # ========================================================
    # HIGH HUMIDITY
    # ========================================================

    if avg_humidity > 85:

        ai_messages.append(
            "💧 High humidity may affect powder chemical storage and handling."
        )

        ai_messages.append(
            "🔌 Inspect electrical and SCADA panels for moisture condensation."
        )

    # ========================================================
    # INDUSTRIAL IMPACT
    # ========================================================

    if industrial:

        ai_messages.append(
            f"🏭 Industrial discharge impact active → Conductivity: {conductivity} µS/cm"
        )

    # ========================================================
    # DISPLAY ALERTS
    # ========================================================

    for msg in ai_messages:

        st.markdown(f"""
        <div class='ai-alert'>
        {msg}
        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # WEATHER RISK INDEX
    # ========================================================

    risk_score = 0

    if avg_temp > 35:
        risk_score += 30

    if avg_rain > 10:
        risk_score += 45

    if avg_humidity > 85:
        risk_score += 15

    if industrial:
        risk_score += 10

    # ========================================================
    # LAYOUT
    # ========================================================

    left, right = st.columns([5,1])

    # ========================================================
    # FUTURE DOSING TREND
    # ========================================================

    with left:

        st.markdown("📈 Future Dosing Trend")

        fig = go.Figure()

        # ====================================================
        # ALUM TREND
        # ====================================================

        fig.add_trace(go.Scatter(

            x=weather_df["Time"],

            y=weather_df["Pred Alum"],

            mode='lines+markers',

            name='Predicted Alum Dose',

            line=dict(width=3)

        ))

        # ====================================================
        # CHLORINE TREND
        # ====================================================

        fig.add_trace(go.Scatter(

            x=weather_df["Time"],

            y=weather_df["Pred Chlorine"],

            mode='lines+markers',

            name='Predicted Chlorine Dose',

            line=dict(width=3)

        ))

        # ====================================================
        # RAINFALL OVERLAY
        # ====================================================

        fig.add_trace(go.Bar(

            x=weather_df["Time"],

            y=weather_df["Rain"],

            name='Rainfall',

            opacity=0.25

        ))

        fig.update_layout(

            height=300,

            template="plotly_dark",

            margin=dict(
                l=5,
                r=5,
                t=25,
                b=5
            ),

            legend_orientation="h",

            xaxis_title="Time",

            yaxis_title="Predicted Dose (mg/L)"

        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ========================================================
    # SMALL WEATHER RISK GAUGE
    # ========================================================

    with right:

        fig2 = go.Figure(go.Indicator(

            mode="gauge+number",

            value=risk_score,

            title={'text':"Weather Risk"},

            gauge={

                'axis': {'range':[0,100]},

                'bar': {'color':"cyan"}

            }

        ))

        fig2.update_layout(

            height=220,

            margin=dict(
                l=5,
                r=5,
                t=35,
                b=5
            )

        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    # ========================================================
    # FINAL AI DECISION SUMMARY
    # ========================================================

    st.markdown("✅Smart Decision Summary")

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Peak Alum Dose",
            f"{max(predicted_alum):.1f} mg/L"
        )

    with c2:

        st.metric(
            "Peak Chlorine Dose",
            f"{max(predicted_chlorine):.1f} mg/L"
        )

    with c3:

        if risk_score > 60:

            st.error("High Impact")

        elif risk_score > 30:

            st.warning("Moderate")

        else:

            st.success("Stable")

else:

    st.error("Weather API Connection Failed")

# ===============================
# CUSTOMER END GIS MAP (FIXED)
# ===============================

st.subheader("📍 Customer End GIS Map")

# Read GIS Sheet
gis = pd.read_excel("Gis Data.xlsx")

if gis.empty:
    st.warning("No GIS data found.")

else:

    # ===============================
    # COLUMN DETECTION
    # ===============================
    lat_col = next((c for c in gis.columns if "lat" in c.lower()), None)

    lon_col = next(
        (c for c in gis.columns
         if "lon" in c.lower() or "lng" in c.lower()),
        None
    )

    name_col = next(
        (c for c in gis.columns
         if "name" in c.lower()
         or "cust" in c.lower()
         or "consumer" in c.lower()),
        None
    )

    turb_col = next((c for c in gis.columns if "turb" in c.lower()), None)

    frc_col = next(
        (c for c in gis.columns
         if "frc" in c.lower()
         or "chlor" in c.lower()),
        None
    )

    total_col = next(
        (c for c in gis.columns
         if "total" in c.lower() and "coli" in c.lower()),
        None
    )

    ecoli_col = next(
        (c for c in gis.columns
         if "ecoli" in c.lower()
         or "e coli" in c.lower()),
        None
    )

    # ===============================
    # SAFE NUMERIC CONVERSION
    # ===============================
    if lat_col:
        gis[lat_col] = pd.to_numeric(gis[lat_col], errors="coerce")

    if lon_col:
        gis[lon_col] = pd.to_numeric(gis[lon_col], errors="coerce")

    if turb_col:
        gis[turb_col] = pd.to_numeric(gis[turb_col], errors="coerce")

    if frc_col:
        gis[frc_col] = pd.to_numeric(gis[frc_col], errors="coerce")

    # Remove rows with missing coordinates
    gis = gis.dropna(subset=[lat_col, lon_col])

    # ===============================
    # STATUS CLASSIFICATION
    # ===============================
    def classify(row):

        # RED → Bacteria Present
        if total_col:
            val = str(row[total_col]).strip().lower()

            if val in ["present", "yes", "1", "positive"]:
                return "Bacteria Present"

        if ecoli_col:
            val = str(row[ecoli_col]).strip().lower()

            if val in ["present", "yes", "1", "positive"]:
                return "Bacteria Present"

        # YELLOW → High Turbidity
        if turb_col and pd.notnull(row[turb_col]):

            if row[turb_col] > 1.5:
                return "High Turbidity"

        # ORANGE → Chlorine Deviation
        if frc_col and pd.notnull(row[frc_col]):

            if row[frc_col] < 0.2 or row[frc_col] > 1.0:
                return "Chlorine Deviation"

        # GREEN → Safe
        return "Safe"

    gis["Status"] = gis.apply(classify, axis=1)

    # ===============================
    # MAP
    # ===============================
    if lat_col and lon_col:

        hover_dict = {}

        if turb_col:
            hover_dict[turb_col] = True

        if frc_col:
            hover_dict[frc_col] = True

        if total_col:
            hover_dict[total_col] = True

        if ecoli_col:
            hover_dict[ecoli_col] = True

        fig_map = px.scatter_mapbox(
            gis,
            lat=lat_col,
            lon=lon_col,
            hover_name=name_col,
            hover_data=hover_dict,
            color="Status",
            color_discrete_map={
                "Safe": "green",
                "High Turbidity": "yellow",
                "Chlorine Deviation": "orange",
                "Bacteria Present": "red"
            },
            zoom=11,
            height=650
        )

        fig_map.update_layout(
            mapbox_style="open-street-map",
            margin={"r": 0, "t": 0, "l": 0, "b": 0}
        )

        st.plotly_chart(fig_map, use_container_width=True)

    else:
        st.error("Latitude or Longitude column not found.")

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
# 🌊 INTAKE DEBRIS MODULE
# ==============================

# ==============================
# 🌊 INTAKE DEBRIS MODULE
# ==============================

import streamlit as st
import onnxruntime as ort
import numpy as np
from PIL import Image

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Intake Monitoring",
    layout="wide"
)

st.header("🌊Intake Monitoring System")

# =========================
# CLASS NAMES
# =========================
# CHANGE ACCORDING TO YOUR TRAINED MODEL
CLASS_NAMES = [
    "Plastic",
    "Bottle",
    "Bag",
    "Leaf",
    "Plant",
    "Wood"
]

# =========================
# LOAD ONNX MODEL
# =========================
@st.cache_resource
def load_model():

    session = ort.InferenceSession("best.onnx")

    return session

session = load_model()

# =========================
# IMAGE UPLOAD
# =========================
uploaded_img = st.file_uploader(
    "Upload Intake Image",
    type=["jpg", "jpeg", "png"],
    key="intake"
)

# =========================
# IMAGE PREPROCESS
# =========================
def preprocess(img):

    img = img.resize((640, 640))

    img_np = np.array(img).astype(np.float32)

    img_np = img_np / 255.0

    img_np = np.transpose(img_np, (2, 0, 1))

    img_np = np.expand_dims(img_np, axis=0)

    return img_np

# =========================
# RUN
# =========================
if uploaded_img:

    img = Image.open(uploaded_img).convert("RGB")

    st.image(
        img,
        caption="Uploaded Intake Image",
        use_container_width=True
    )

    if st.button("🔍 Run Analysis"):

        try:

            # =========================
            # MODEL INFERENCE
            # =========================
            input_tensor = preprocess(img)

            input_name = session.get_inputs()[0].name

            outputs = session.run(
                None,
                {input_name: input_tensor}
            )

            # =========================
            # EXTRACT OUTPUT
            # =========================
            output = outputs[0][0]

            confidence_threshold = 0.40

            detected = []

            plastic_count = 0
            organic_count = 0
            total_detection = 0

            # =========================
            # DETECTION LOOP
            # =========================
            for detection in output.T:

                scores = detection[4:]

                class_id = np.argmax(scores)

                confidence = scores[class_id]

                if confidence > confidence_threshold:

                    total_detection += 1

                    if class_id < len(CLASS_NAMES):

                        label = CLASS_NAMES[class_id]

                    else:

                        label = f"Class {class_id}"

                    detected.append(label)

                    # =========================
                    # PLASTIC LOAD
                    # =========================
                    if label in ["Plastic", "Bottle", "Bag"]:

                        plastic_count += 1

                    # =========================
                    # ORGANIC LOAD
                    # =========================
                    if label in ["Leaf", "Plant", "Wood"]:

                        organic_count += 1

            # =========================
            # LOAD CALCULATION
            # =========================
            if total_detection > 0:

                plastic_load = round(
                    (plastic_count / total_detection) * 100,
                    1
                )

                organic_load = round(
                    (organic_count / total_detection) * 100,
                    1
                )

            else:

                plastic_load = 0
                organic_load = 0

            # =========================
            # BLOCKAGE RISK
            # =========================
            if plastic_load > 60:

                blockage_risk = "HIGH"

            elif plastic_load > 30:

                blockage_risk = "MODERATE"

            else:

                blockage_risk = "LOW"

            # =========================
            # INTAKE HEALTH
            # =========================
            if total_detection == 0:

                intake_health = "EXCELLENT"

            elif plastic_load > 60 or total_detection > 10:

                intake_health = "CRITICAL"

            elif plastic_load > 30:

                intake_health = "WARNING"

            else:

                intake_health = "NORMAL"

            # =========================
            # DASHBOARD OUTPUT
            # =========================
            st.subheader("📊 Intake Monitoring Summary")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Plastic Load %",
                plastic_load
            )

            col2.metric(
                "Organic Load %",
                organic_load
            )

            col3.metric(
                "Total Debris Objects",
                total_detection
            )

            # =========================
            # DETECTED MATERIALS
            # =========================
            st.subheader("🧾 Detected Materials")

            if len(detected) > 0:

                unique_detected = list(set(detected))

                for item in unique_detected:

                    st.success(item)

            else:

                st.info("No significant debris detected")

            # =========================
            # RISK ASSESSMENT
            # =========================
            st.subheader("⚠️ Intake Risk Assessment")

            st.warning(
                f"Trash Rack Blockage Risk: {blockage_risk}"
            )

            st.warning(
                f"Overall Intake Health: {intake_health}"
            )

            # =========================
            # PROCESS IMPACT
            # =========================
            st.subheader("🏭 Process Impact Analysis")

            if plastic_load > 50:

                st.error(
                    "High plastic accumulation may choke intake screens and filters"
                )

            if organic_load > 40:

                st.warning(
                    "High organic load may increase alum/PAC dosing"
                )

            if total_detection > 10:

                st.error(
                    "Heavy debris condition may overload clarifier"
                )

            if total_detection == 0:

                st.success(
                    "Raw water intake condition stable"
                )

            # =========================
            # RECOMMENDED ACTIONS
            # =========================
            st.subheader("🛠 Recommended Actions")

            if blockage_risk == "HIGH":

                st.error(
                    "Immediate trash rack cleaning required"
                )

                st.error(
                    "Reduce intake flow temporarily"
                )

            elif blockage_risk == "MODERATE":

                st.warning(
                    "Schedule preventive intake cleaning"
                )

            else:

                st.success(
                    "Maintain normal operation"
                )

            if organic_load > 40:

                st.warning(
                    "Increase alum/PAC dosing temporarily"
                )

            # =========================
            # AI STATUS
            # =========================
            st.subheader(" Monitoring Status")

            st.success(
                "Industrial Intake Monitoring Active"
            )

        except Exception as e:

            st.error(f"Analysis Failed: {e}")
# ==========================================
# 🖥️ WATER QUALITY - ADVANCED PRACTICAL VERSION
# Added: Pre-Chlorination + Oily Water Logic
# ==========================================

import streamlit as st

st.header("🖥️ Water Treatment Assistant")

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
        st.markdown("🧪 Pre-Chlorination Status")

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
        #  WORMS
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

