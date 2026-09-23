import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import datetime
import pytz
import random
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

if "filter_alarm_muted" not in st.session_state:
    st.session_state.filter_alarm_muted = False
if "quality_alarm_list" not in st.session_state:
    st.session_state.quality_alarm_list = []

if "mechanical_alarm_list" not in st.session_state:
    st.session_state.mechanical_alarm_list = []

if "gis_alarm_list" not in st.session_state:
    st.session_state.gis_alarm_list = [] 

# ===============================
# AUTO REFRESH
# ===============================
st.set_page_config(page_title="WTP HMI PANEL", layout="wide")
# ==========================================
# DATA SOURCE SWITCH
# ==========================================

mode = st.sidebar.radio(
    "Select Data Source",
    ["📁 Manual Data", "🟢 Real-Time Data"]
)
if mode == "🟢 Real-Time Data":

    refresh_placeholder = st.empty()

    refresh_placeholder.markdown(
        """
        <script>
        setTimeout(function(){
            window.location.reload();
        }, 10000);
        </script>
        """,
        unsafe_allow_html=True
    )
# ==========================================
# LOAD FILES BASED ON MODE
# ==========================================

if mode == "📁 Manual Data":

    # ======================================
    # MANUAL EXCEL FILES
    # ======================================

    history_df = pd.read_excel(
        "plant_raw_water_history.xlsx"
    )

    df = pd.read_excel(
        "Inlet_outlet_turbidity_dosing_ details.xlsx",
        sheet_name="RawWater"
    )

    trend_df = pd.read_excel(
        "Moharda_WTP_2026_Realistic_Adjusted.xlsx"
    )

    st.sidebar.success("Manual Data Mode Active")

else:

    # ======================================
    # LIVE REAL-TIME DATA ENGINE
    # ======================================
    
    ist = pytz.timezone("Asia/Kolkata")
    
    now = datetime.now(ist)
    
    current_date = now.strftime("%d-%m-%Y")
    
    current_time = now.strftime("%H:%M:%S")
    
    # ======================================
    # DYNAMIC FLOW
    # ======================================
    
    flow_m3hr = round(
        random.uniform(9800, 10000),
        2
    )
    
    flow_lps = round(
        flow_m3hr * 1000 / 3600,
        2
    )
    
    # ======================================
    # RAW WATER
    # ======================================
    
    intake_turbidity = round(
        random.uniform(35, 120),
        2
    )
    
    aerator_turbidity = round(
        intake_turbidity * random.uniform(0.90, 0.97),
        2
    )
    
    conductivity = round(
        random.uniform(280, 420),
        2
    )
    
    # ======================================
    # CLARIFIER LOGIC
    # ======================================
    
    clarifier_p1 = round(aerator_turbidity * 0.78, 2)
    
    clarifier_p2 = round(clarifier_p1 * 0.72, 2)
    
    clarifier_p3 = round(clarifier_p2 * 0.65, 2)
    
    clarifier_p4 = round(clarifier_p3 * 0.50, 2)
    
    clarifier_outlet = round(
        max(clarifier_p4 * 0.40, 0.8),
        2
    )
    
    # ======================================
    # ALUM DOSING
    # ======================================
    
    alum_dose = round(
        intake_turbidity * 0.38,
        2
    )
    
    # ======================================
    # HISTORY DATA
    # ======================================
    
    history_df = pd.DataFrame({
    
        "Date": [current_date],
    
        "Time": [current_time],
    
        "Turbidity (NTU)": [intake_turbidity],
    
        "Conductivity (µS/cm)": [conductivity]
    
    })
    
    # ======================================
    # TURBIDITY DATA
    # ======================================
    
    df = pd.DataFrame({
    
        "Date": [current_date],
    
        "Turbidity (NTU)": [intake_turbidity],
    
        "Outlet Turbidity (NTU)": [clarifier_outlet],
    
        "Alum Dosage (ppm)": [alum_dose]
    
    })
    
    # ======================================
    # TREND DATA
    # ======================================
    
    trend_rows = []
    
    # Clarifier points
    
    clarifier_units = [
    
        ("Clarifier Point 1", aerator_turbidity, clarifier_p1),
    
        ("Clarifier Point 2", clarifier_p1, clarifier_p2),
    
        ("Clarifier Point 3", clarifier_p2, clarifier_p3),
    
        ("Clarifier Point 4", clarifier_p3, clarifier_p4),
    
        ("Clarifier", aerator_turbidity, clarifier_outlet)
    
    ]
    
    for unit, inlet, outlet in clarifier_units:
    
        trend_rows.append({
    
            "Date": current_date,
    
            "Unit": unit,
    
            "Inlet Turbidity": inlet,
    
            "Outlet Turbidity": outlet,
    
            "Conductivity (µS/cm)": conductivity
    
        })
    
    # Filter Beds
    
    for i in range(1,7):

        outlet = round(
            random.uniform(0.08, 1.4),
            2
        )
    
        trend_rows.append({
    
            "Date": current_date,
    
            "Unit": f"Filter Bed {i}",
    
            "Inlet Turbidity": clarifier_outlet,
    
            "Outlet Turbidity": outlet,
    
            "Conductivity (µS/cm)": conductivity
    
        })
    
    trend_df = pd.DataFrame(trend_rows)
    
    st.sidebar.success("Real-Time Data Mode Active")
    
        

# ===============================
# TITLE
# ===============================
st.title("🏭 WTP – LIVE HMI PANEL")
# ======================================
# ACTIVE ALARM CENTER
# ======================================

# ======================================
# ACTIVE ALARM CENTER
# ======================================

st.markdown("### 🚨 Active Alarm Center")

# ======================================
# WATER QUALITY
# ======================================

if st.session_state.quality_alarm_list:

    st.error(
        "🚨 WATER QUALITY : "
        + " | ".join(st.session_state.quality_alarm_list)
    )

    st.button(
        "🌀 Go To Clarifier & Filter Section",
        key="goto_quality"
    )

# ======================================
# MECHANICAL
# ======================================

if st.session_state.mechanical_alarm_list:

    st.warning(
        "⚙️ MECHANICAL : "
        + " | ".join(st.session_state.mechanical_alarm_list)
    )

    st.button(
        "⚙️ Go To Mechanical Section",
        key="goto_mechanical"
    )

# ======================================
# GIS
# ======================================

if st.session_state.gis_alarm_list:

    st.error(
        "📍 GIS : "
        + " | ".join(st.session_state.gis_alarm_list)
    )

    st.button(
        "📍 Go To GIS Section",
        key="goto_gis"
    )

# ======================================
# NO ACTIVE ALARM
# ======================================

if (
    len(st.session_state.quality_alarm_list) == 0
    and
    len(st.session_state.mechanical_alarm_list) == 0
    and
    len(st.session_state.gis_alarm_list) == 0
):

    st.success("✅ No Active Alarms")
ist = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(ist)
st.markdown(f"### 🕒 {current_time.strftime('%d-%m-%Y %H:%M:%S')}")


# ===============================
# PRODUCTION
# ===============================
st.markdown("""
<div style="
background:#F4F8FF;
border-left:8px solid #0A2E6B;
padding:15px;
border-radius:8px;
font-size:24px;
font-weight:bold;
color:#0A2E6B;">
🏭 Total Water Production
</div>
""", unsafe_allow_html=True)

production_mld = 228 # value can vary between 220-235
production_m3_hr = 9500
production_lps = production_m3_hr * 1000 / 3600

colp = st.columns(3)
colp[0].metric("Production (MLD)", production_mld)
colp[1].metric("Flow (m³/hr)", f"{production_m3_hr:.0f}")
colp[2].metric("Flow (LPS)", f"{production_lps:.0f}")

# ============================================================
# RAW WATER QUALITY SECTIOn
# ============================================================

if mode == "📁 Manual Data":

    st.markdown("""
    <div style="
    background:#F4F8FF;
    border-left:8px solid #0A2E6B;
    padding:15px;
    border-radius:8px;
    font-size:24px;
    font-weight:bold;
    color:#0A2E6B;">
    📅 Raw Water Quality Selector
    </div>
    """, unsafe_allow_html=True)
    
    # SAFE DATE CONVERSION
    history_df["Date"] = pd.to_datetime(
        history_df["Date"],
        dayfirst=True,
        errors="coerce"
    )

    # CREATE DATETIME
    if "Time" in history_df.columns:

        history_df["DateTime"] = pd.to_datetime(

            history_df["Date"].astype(str)

            + " "

            + history_df["Time"].astype(str),

            errors="coerce"

        )

    else:

        history_df["DateTime"] = history_df["Date"]

    # REMOVE INVALID
    history_df = history_df.dropna(
        subset=["DateTime"]
    )

    history_df = history_df.sort_values(
        "DateTime"
    )

    # ========================================
    # SAFE SLICER
    # ========================================
    # ========================================
    # SAFE SLICER
    # ========================================
    
    if len(history_df) > 1:
    
        selected_time = st.select_slider(
            "Select Date",
            options=history_df["DateTime"],
            value=history_df[
                history_df["DateTime"].dt.date == datetime.now().date()
            ]["DateTime"].iloc[-1]
        )
    
    else:
    
        selected_time = history_df["DateTime"].iloc[0]
       
    # ========================================
    # FILTER ROW
    # ========================================

    row = history_df[
        history_df["DateTime"] == selected_time
    ]
    
    intake_turb = float(
        row["Turbidity (NTU)"].values[0]
    )
    st.session_state["live_turbidity"] = intake_turb
    
    conductivity_today = float(
        row["Conductivity (µS/cm)"].values[0]
    )

    # ========================================
    # METRICS
    # ========================================

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Date",
        selected_time.strftime("%d-%b-%Y")
    )
    st.session_state["live_turbidity"] = float(intake_turb)
    c2.metric(
        "Raw Turbidity",
        f"{st.session_state['live_turbidity']:.2f}NTU"
    )
   
    c3.metric(
        "Conductivity",
        f"{conductivity_today:.0f} µS/cm"
    )

# ============================================================
# REAL-TIME MODE
# ============================================================

else:

    st.markdown("""
    <div style="
    background:#F4F8FF;
    border-left:8px solid #0A2E6B;
    padding:15px;
    border-radius:8px;
    font-size:24px;
    font-weight:bold;
    color:#0A2E6B;">
    📡 Live Raw Water Monitoring 
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Time",
        current_time.strftime("%H:%M:%S")
    )
    st.session_state["live_turbidity"] = float(intake_turbidity)
    c2.metric(
        "Raw Turbidity",
        f"{intake_turbidity:.2f} NTU"
    )

    c3.metric(
        "Conductivity",
        f"{conductivity:.0f} µS/cm"
    )


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

st.markdown("""
<div style="
background:#F4F8FF;
border-left:8px solid #0A2E6B;
padding:15px;
border-radius:8px;
font-size:31px;
font-weight:bold;
color:#0A2E6B;">
Turbidity & Alum Dosing Monitoring
</div>
""", unsafe_allow_html=True)

# ==========================================
# REAL-TIME / MANUAL DATA HANDLING
# ==========================================

if mode == "🟢 Real-Time Data":

    # ======================================
    # SESSION STATE STORAGE
    # ======================================

    if "live_trend_df" not in st.session_state:

        st.session_state.live_trend_df = pd.DataFrame({
            "Time": [],
            "Inlet": [],
            "Outlet": [],
            "Alum": []
        })

    live_df = st.session_state.live_trend_df

    # ======================================
    # NEW LIVE VALUES
    # ======================================
    import pytz
    from datetime import datetime
    
    current_time_live = datetime.now(pytz.timezone("Asia/Kolkata")
    ).strftime("%H:%M:%S")

    new_inlet = round(
        random.uniform(35, 120),
        2
    )

    new_outlet = round(
        max(
            new_inlet * random.uniform(0.01, 0.04),
            0.08
        ),
        2
    )

    new_alum = round(
        new_inlet * 0.38,
        2
    )

    # ======================================
    # APPEND NEW ROW
    # ======================================

    new_row = pd.DataFrame({

        "Time": [current_time_live],

        "Inlet": [new_inlet],

        "Outlet": [new_outlet],

        "Alum": [new_alum]

    })

    live_df = pd.concat(
        [live_df, new_row],
        ignore_index=True
    )

    # ======================================
    # KEEP LAST 20 POINTS
    # ======================================

    live_df = live_df.tail(20)

    st.session_state.live_trend_df = live_df

    # ======================================
    # AUTO REFRESH ONLY REAL-TIME PART
    # ======================================

    st_autorefresh(
        interval=10000,
        key="live_only_refresh"
    )

    # ======================================
    # TWO COLUMNS
    # ======================================

    col1, col2 = st.columns(2)

    # ======================================
    # GRAPH 1
    # ======================================

    with col1:

        st.subheader("📊 Live Alum & Turbidity")

        fig1 = go.Figure()

        # ALUM DOSAGE
        fig1.add_trace(

            go.Bar(

                x=live_df["Time"],

                y=live_df["Alum"],

                name="Alum Dosage",

                marker_color="blue",

                opacity=0.8

            )
        )

        # INLET TURBIDITY
        fig1.add_trace(

            go.Scatter(

                x=live_df["Time"],

                y=live_df["Inlet"],

                mode="lines",

                name="Raw Turbidity",

                line=dict(
                    color="red",
                    width=3
                )

            )
        )

        fig1.update_layout(

            height=450,

            hovermode="x unified",

            xaxis_title="Live Time",

            yaxis_title="Value",

            template="plotly_white",

            transition_duration=800,

            uirevision="LIVE_GRAPH_1",

            legend=dict(

                orientation="h",

                yanchor="bottom",

                y=1.02,

                xanchor="right",

                x=1

            )
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

    # ======================================
    # GRAPH 2
    # ======================================

    with col2:

        st.subheader("📈 Live Inlet vs Outlet Trend")

        fig2 = go.Figure()

        # INLET
        fig2.add_trace(

            go.Scatter(

                x=live_df["Time"],

                y=live_df["Inlet"],

                mode="lines",

                name="Inlet Turbidity",

                line=dict(
                    color="red",
                    width=3
                )

            )
        )

        # OUTLET
        fig2.add_trace(

            go.Scatter(

                x=live_df["Time"],

                y=live_df["Outlet"],

                mode="lines",

                name="Outlet Turbidity",

                line=dict(
                    color="blue",
                    width=3
                )

            )
        )

        # ALUM
        fig2.add_trace(

            go.Scatter(

                x=live_df["Time"],

                y=live_df["Alum"],

                mode="lines",

                name="Alum Dosage",

                line=dict(
                    color="green",
                    width=3
                )

            )
        )

        fig2.update_layout(

            height=450,

            hovermode="x unified",

            xaxis_title="Live Time",

            yaxis_title="Value",

            template="plotly_white",

            transition_duration=800,

            uirevision="LIVE_GRAPH_2",

            legend=dict(

                orientation="h",

                yanchor="bottom",

                y=1.02,

                xanchor="right",

                x=1

            )
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

# ==========================================
# MANUAL MODE
# ==========================================

else:

    # ======================================
    # CLEAN DATA
    # ======================================

    df.columns = [str(c).strip() for c in df.columns]

    df["Date"] = pd.to_datetime(
        df["Date"],
        dayfirst=True,
        errors="coerce"
    )

    df = df.dropna(subset=["Date"])

    # ======================================
    # DATE FILTER
    # ======================================

    st.markdown("📅 Select Monitoring Period")

    d1, d2 = st.columns(2)

    with d1:

        start_date = st.date_input(

            "Start Date",

            value=df["Date"].min()

        )

    from datetime import date

    with d2:
    
        end_date = st.date_input(
            "To Date",
            value=date.today(),
            key="monitoring_to_date"
        )
    # ======================================
    # FILTER DATA
    # ======================================

    filtered_df = df[

        (df["Date"] >= pd.to_datetime(start_date)) &

        (df["Date"] <= pd.to_datetime(end_date))

    ]

    # ======================================
    # TWO COLUMNS
    # ======================================

    col1, col2 = st.columns(2)

    # ======================================
    # GRAPH 1
    # ======================================

    with col1:

        st.subheader("📊 Turbidity & Alum Dosing")

        fig1 = go.Figure()

        fig1.add_trace(

            go.Bar(

                x=filtered_df["Date"],

                y=filtered_df["Alum Dosage (ppm)"],

                name="Alum Dosage",

                marker_color="blue",

                opacity=0.8

            )
        )

        fig1.add_trace(

            go.Scatter(

                x=filtered_df["Date"],

                y=filtered_df["Turbidity (NTU)"],

                mode="lines+markers",

                name="Raw Turbidity",

                line=dict(
                    color="red",
                    width=3
                )

            )
        )

        fig1.update_layout(

            height=450,

            hovermode="x unified",

            xaxis_title="Date",

            yaxis_title="Value",

            template="plotly_white",

            legend=dict(

                orientation="h",

                yanchor="bottom",

                y=1.02,

                xanchor="right",

                x=1

            )
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

    # ======================================
    # GRAPH 2
    # ======================================

    with col2:

        st.subheader("📈 Inlet vs Outlet Turbidity")

        fig2 = go.Figure()

        fig2.add_trace(

            go.Scatter(

                x=filtered_df["Date"],

                y=filtered_df["Turbidity (NTU)"],

                mode="lines+markers",

                name="Inlet Turbidity",

                line=dict(
                    color="red",
                    width=3
                )

            )
        )

        fig2.add_trace(

            go.Scatter(

                x=filtered_df["Date"],

                y=filtered_df["Outlet Turbidity (NTU)"],

                mode="lines+markers",

                name="Outlet Turbidity",

                line=dict(
                    color="blue",
                    width=3
                )

            )
        )

        fig2.update_layout(

            height=450,

            hovermode="x unified",

            xaxis_title="Date",

            yaxis_title="Turbidity (NTU)",

            template="plotly_white"

        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )



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
# SMART CLARIFIER + Filter Bed MONITORING SYSTEM
# FINAL STATIC + DYNAMIC VERSION
# ============================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
import pytz
from datetime import datetime
import base64

# ============================================================
# TITLE
# ============================================================

st.markdown("---")
st.markdown("""
<div style="
background:#F4F8FF;
border-left:8px solid #0A2E6B;
padding:15px;
border-radius:8px;
font-size:31px;
font-weight:bold;
color:#0A2E6B;">
📊 Smart Clarifier & Filter House Monitoring
</div>
""", unsafe_allow_html=True)

# ============================================================
# MODE BUTTONS
# ============================================================

monitor_mode = st.radio(

    "Select Monitoring Mode",

    ["📊 Static Monitoring", "🟢 Dynamic Live Monitoring"],

    horizontal=True,

    index=0

)

# ============================================================
# LOAD DATA
# ============================================================

trend_df = pd.read_excel(
    "Moharda_WTP_2026_Realistic_Adjusted.xlsx"
)

trend_df["Date"] = pd.to_datetime(
    trend_df["Date"]
)

# ============================================================
# CLARIFIER / FH SELECTION
# ============================================================

selected_unit = st.sidebar.selectbox(
    "Select Unit",
    [
        "Clarifier Part A",
        "Clarifier Part B",
        "FH3",
        "FH4",
        "FH5",
        "FH6"
    ]
)

# ============================================================
# STATIC DATE FILTER
# ============================================================

from datetime import date

if monitor_mode == "📊 Static Monitoring":

    selected_date = st.date_input(
        "Select Monitoring Date",
        value=date.today(),
        key="clarifier_monitor_date"
    )

    selected_date = pd.to_datetime(
        selected_date
    )

    day_df = trend_df[
        trend_df["Date"] == selected_date
    ]

else:

    day_df = trend_df.tail(20)

# ============================================================
# CLARIFIER SECTION
# ============================================================

st.markdown("---")
st.subheader(f"🌀 {selected_unit} Live Monitoring")

# ============================================================
# VALUES
# ============================================================

if monitor_mode == "🟢 Dynamic Live Monitoring":

    clar_inlet = round(
        random.uniform(25, 120),
        2
    )

    clar_outlet = round(
        random.uniform(0.8, 8.5),
        2
    )

    clar_cond = round(
        random.uniform(280, 420),
        2
    )

else:

    clarifier_data = day_df[
        day_df["Unit"] == "Clarifier"
    ]

    clar_inlet = clarifier_data[
        "Inlet Turbidity"
    ].iloc[0]

    clar_outlet = clarifier_data[
        "Outlet Turbidity"
    ].iloc[0]

    clar_cond = clarifier_data[
        "Conductivity (µS/cm)"
    ].iloc[0]

# ============================================================
# HEALTH STATUS
# ============================================================
if clar_outlet > 5:

    msg = (
        f"Clarifier Outlet High "
        f"({clar_outlet:.2f} NTU)"
    )

    if msg not in st.session_state.quality_alarm_list:

        st.session_state.quality_alarm_list.append(
            msg
        )
if clar_outlet <=3.5:

    clar_health = "🟢 Healthy"

elif clar_outlet <= 5:

    clar_health = "🟡 Moderate"

else:

    clar_health = "🔴 Critical"

# ============================================================
# SPEEDOMETER GAUGE
# ============================================================

fig_clar = go.Figure(go.Indicator(

    mode="gauge+number",

    value=clar_outlet,

    number={
        'suffix': " NTU",
        'font': {
            'size': 42,
            'color': "#0077b6"
        }
    },

    title={
        'text': f"{selected_unit} Outlet Turbidity",
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

    height=420,

    transition={
        'duration': 800,
        'easing': 'cubic-in-out'
    },

    uirevision="clarifier_speedometer"
)

st.plotly_chart(
    fig_clar,
    use_container_width=True
)

# ============================================================
# METRICS
# ============================================================

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

# ============================================================
# ANALYSIS
# ============================================================

st.markdown(
    f"###### Analysis - {selected_unit}"
)


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


# ============================================================
# Filter Bed SECTION
# ============================================================

st.markdown("---")
st.subheader("🧪 Filter House Live Status")

cols = st.columns(6)

filter_summary = []

alarm_triggered = False

for i in range(1,7):

    filter_name = f"Filter Bed {i}"      # Excel lookup
    display_name = f"Filter House {i}"   # Dashboard display

    # ========================================================
    # LIVE / STATIC VALUES
    # ========================================================

    if monitor_mode == "🟢 Dynamic Live Monitoring":

        filter_outlet = round(
            random.uniform(0.08, 1.5),
            2
        )
        
    else:

        filter_data = day_df[
            day_df["Unit"] == filter_name
        ]

        filter_outlet = filter_data[
            "Outlet Turbidity"
        ].iloc[0]

    # ========================================================
    # STATUS
    # ========================================================

    if filter_outlet <= 0.3:

        status = "🟢 Excellent"

    elif filter_outlet <= 0.7:

        status = "🟡 Good"

    elif filter_outlet <= 1:

        status = "🟠 Warning"

    else:

        status = "🔴 Backwash Needed"
    if status == "🔴 Backwash Needed":
        
        alarm_triggered = True
        st.session_state.alarm_active = True
        st.session_state.filter_alarm_muted = False
    filter_summary.append({

        "Filter House": display_name,
    
        "Outlet Turbidity": round(
            filter_outlet,
            2
        ),
    
        "Status": status
    
    })
    if filter_outlet > 1 or status == "🔴 Backwash Needed":

        message = (
            f"{display_name} High Turbidity "
            f"({filter_outlet:.2f} NTU)"
        )
    
        if message not in st.session_state.quality_alarm_list:
    
            st.session_state.quality_alarm_list.append(
                message
            )
        st.error(f"🚨 FILTER ALARM : {display_name}")
    
        col1, col2 = st.columns([4,1])
    
        with col2:
            if st.button(
                "🔕 Stop Filter Alarm",
                key=f"stop_alarm_{filter_name}"
            ):
                st.session_state.filter_alarm_muted = True
                st.session_state.alarm_active = False
                st.rerun()
    
    # ========================================================
    # SMALL SPEEDOMETER GAUGE
    # ========================================================

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
            'text': f"FH-{i}",
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
        ),

        transition={
            'duration': 800,
            'easing': 'cubic-in-out'
        },

        uirevision=f"fb_{i}"
    )

    cols[i-1].plotly_chart(
        fig_small,
        use_container_width=True
    )

# ============================================================
# AUTO ALARM
# ============================================================
if not st.session_state.filter_alarm_muted and alarm_triggered:

    with open("mixkit-sport-start-bleeps-918.wav", "rb") as f:
        audio_bytes = f.read()

    b64 = base64.b64encode(audio_bytes).decode()

    st.components.v1.html(
        f"""
        <audio id="alarm" autoplay loop style="display:none;">
            <source src="data:audio/wav;base64,{b64}" type="audio/wav">
        </audio>

        <script>
            document.getElementById("alarm").play();
        </script>
        """,
        height=0,
    )

else:
    st.components.v1.html(
        """
        <script>
            var audios = document.getElementsByTagName("audio");
            for (var i = 0; i < audios.length; i++) {
                audios[i].pause();
                audios[i].currentTime = 0;
            }
        </script>
        """,
        height=0,
    )
# ============================================================
# FILTER SUMMARY
# ============================================================

st.markdown("---")
st.subheader("📋 Filter House Summary")

for item in filter_summary:

    if "Excellent" in item["Status"]:

        bg = "#d4edda"
        text = "#155724"

    elif "Good" in item["Status"]:

        bg = "#fff3cd"
        text = "#856404"

    elif "Warning" in item["Status"]:

        bg = "#ffe5b4"
        text = "#9c5700"

    else:

        bg = "#f8d7da"
        text = "#721c24"

    st.markdown(
        f"""
        <div style="
            background-color:{bg};
            padding:12px;
            border-radius:12px;
            margin-bottom:10px;
            border-left:8px solid {text};
        ">

        <h4 style="margin:0;color:{text};">
            {item['Filter House']}
        </h4>

        <p style="
            font-size:18px;
            font-weight:bold;
            color:{text};
            margin:4px 0;
        ">
            {item['Status']}
        </p>

        <p style="color:{text}; margin:0;">
            Outlet Turbidity:
            {item['Outlet Turbidity']} NTU
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# OUTPUT TURBIDITY TREND
# ============================================================

st.markdown("---")
st.subheader("📈 Output Turbidity Trend")

units = [
    "Clarifier",
    "Filter House 1",
    "Filter House 2",
    "Filter House 3",
    "Filter House 4",
    "Filter House 5",
    "Filter House 6"
]

# ============================================================
# DYNAMIC MODE
# ============================================================

if monitor_mode == "🟢 Dynamic Live Monitoring":

    selected_unit = st.selectbox(
        "Select Unit",
        units,
        key="dynamic_output_unit"
    )

    if "hist_trend" not in st.session_state:

        st.session_state.hist_trend = pd.DataFrame({
            "Time": [],
            "Output": []
        })

    hist_df = st.session_state.hist_trend

    current_time = datetime.now(
        pytz.timezone("Asia/Kolkata")
    ).strftime("%H:%M:%S")

    new_output = round(
        random.uniform(0.08, 1.5),
        2
    )

    new_row = pd.DataFrame({
        "Time": [current_time],
        "Output": [new_output]
    })

    hist_df = pd.concat(
        [hist_df, new_row],
        ignore_index=True
    )

    hist_df = hist_df.tail(25)

    st.session_state.hist_trend = hist_df

    fig_hist = go.Figure()

    fig_hist.add_trace(
        go.Scatter(
            x=hist_df["Time"],
            y=hist_df["Output"],
            mode="lines+markers",
            line=dict(
                color="#0077b6",
                width=4
            ),
            fill="tozeroy",
            name="Outlet Turbidity"
        )
    )

    fig_hist.update_layout(
        height=400,
        template="plotly_white",
        xaxis_title="Live Time",
        yaxis_title="Outlet Turbidity (NTU)",
        uirevision="live_hist"
    )

    st.plotly_chart(
        fig_hist,
        use_container_width=True
    )

# ============================================================
# STATIC MODE
# ============================================================

else:

    # Ensure Date column is datetime
    trend_df["Date"] = pd.to_datetime(trend_df["Date"])

    # -------------------------
    # Date Range Selection
    # -------------------------

    col1, col2 = st.columns(2)

    with col1:
        from_date = st.date_input(
            "From Date",
            value=pd.Timestamp("2026-01-01").date(),
            min_value=pd.Timestamp("2026-01-01").date(),
            max_value=pd.Timestamp("2035-12-31").date(),
            key="output_trend_from_date"
        )

    from datetime import date

    with col2:
        to_date = st.date_input(
            "To Date",
            value=date.today(),
            min_value=pd.Timestamp("2026-01-01").date(),
            max_value=pd.Timestamp("2035-12-31").date(),
            key="output_trend_to_date"
        )

    # -------------------------
    # Unit Selection
    # -------------------------

    selected_unit = st.selectbox(
        "Select Unit",
        [
            "Clarifier",
            "Filter House 1",
            "Filter House 2",
            "Filter House 3",
            "Filter House 4",
            "Filter House 5",
            "Filter House 6"
        ],
        key="output_trend_unit"
    )

    # -------------------------
    # Apply Filters
    # -------------------------

    unit_df = trend_df[
        (trend_df["Unit"] == selected_unit)
        &
        (trend_df["Date"] >= pd.Timestamp(from_date))
        &
        (trend_df["Date"] <= pd.Timestamp(to_date))
    ].copy()

    unit_df = unit_df.sort_values("Date")

    # -------------------------
    # Graph
    # -------------------------

    fig_hist = go.Figure()

    fig_hist.add_trace(
        go.Scatter(
            x=unit_df["Date"],
            y=unit_df["Outlet Turbidity"],
            mode="lines+markers",
            line=dict(
                color="#0077b6",
                width=4
            ),
            fill="tozeroy",
            name="Outlet Turbidity"
        )
    )

    fig_hist.update_layout(
        height=400,
        template="plotly_white",
        xaxis_title="Date",
        yaxis_title="Outlet Turbidity (NTU)"
    )

    st.plotly_chart(
        fig_hist,
        use_container_width=True
    )



# ============================================================
# MANUAL DATA MODE → LAST 4 DAYS TREND
# ============================================================

if mode == "📁 Manual Data":

    st.markdown("""
    <div style="
    background:#F4F8FF;
    border-left:8px solid #0A2E6B;
    padding:31px;
    border-radius:8px;
    font-size:24px;
    font-weight:bold;
    color:#0A2E6B;">
    Raw Water Turbidity Trend (Last 4 Days)
    
    </div>
    """, unsafe_allow_html=True)
    
    history_df["Date"] = pd.to_datetime(
        history_df["Date"],
        dayfirst=True,
        errors="coerce"
    )

    from datetime import date

    selected_date = st.date_input(
        "Select Date",
        value=date.today(),
        key="raw_water_trend_date"
    )

    selected_date = pd.to_datetime(selected_date)

    trend_df = history_df[
        (history_df["Date"] <= selected_date)
        &
        (
            history_df["Date"] >=
            selected_date - pd.Timedelta(days=4)
        )
    ]

    fig_turb = go.Figure()

    fig_turb.add_trace(
        go.Scatter(
            x=trend_df["Date"],
            y=trend_df["Turbidity (NTU)"],
            mode="lines+markers",
            line=dict(color="cyan", width=3),
            marker=dict(size=8),
            name="Raw Turbidity (Intake)"
        )
    )

    fig_turb.update_layout(
        template="plotly_dark",
        title="Intake Turbidity Trend (Last 4 Days)",
        xaxis_title="Date",
        yaxis_title="Turbidity (NTU)",
        height=400
    )

    st.plotly_chart(
        fig_turb,
        use_container_width=True
    )

# ============================================================
# REAL-TIME MODE → PLANT HEALTH GAUGE
# ============================================================

else:

    st.subheader("🏭 Real-Time Plant Health Monitor")

    # Latest outlet turbidity from live graph data
    plant_outlet_turbidity = float(
        live_df["Outlet"].iloc[-1]
    )

    # --------------------------------------------------------
    # HEALTH SCORE CALCULATION
    # --------------------------------------------------------

    if plant_outlet_turbidity <= 0.30:

        health_score = 95
        status = "🟢 Excellent"

    elif plant_outlet_turbidity <= 0.50:

        health_score = 75
        status = "🟡 Good"

    elif plant_outlet_turbidity <= 1.00:

        health_score = 45
        status = "🟠 Warning"

    else:

        health_score = 15
        status = "🔴 Critical"

    # --------------------------------------------------------
    # SPEEDOMETER GAUGE
    # --------------------------------------------------------

    fig_health = go.Figure(
        go.Indicator(
            mode="gauge+number",

            value=health_score,

            number={
                "suffix": "%",
                "font": {"size": 40}
            },

            title={
                "text": "🏭 Plant Health Index"
            },

            gauge={

                "axis": {
                    "range": [0, 100]
                },

                "bar": {
                    "thickness": 0.35
                },

                "steps": [

                    {
                        "range": [0, 30],
                        "color": "#ff4b4b"
                    },

                    {
                        "range": [30, 60],
                        "color": "#ff9800"
                    },

                    {
                        "range": [60, 85],
                        "color": "#ffd54f"
                    },

                    {
                        "range": [85, 100],
                        "color": "#4caf50"
                    }

                ]
            }
        )
    )

    fig_health.update_layout(
        template="plotly_white",
        height=450
    )

    st.plotly_chart(
        fig_health,
        use_container_width=True
    )

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Outlet Turbidity",
        f"{plant_outlet_turbidity:.2f} NTU"
    )

    c2.metric(
        "Plant Health",
        f"{health_score}%"
    )

    c3.metric(
        "Status",
        status
    )

    # --------------------------------------------------------
    # STATUS MESSAGE
    # --------------------------------------------------------

    if health_score >= 85:

        st.success(
            "🟢 Plant operating at excellent performance."
        )

    elif health_score >= 60:

        st.info(
            "🟡 Plant operating within normal limits."
        )

    elif health_score >= 30:

        st.warning(
            "🟠 Filtration efficiency reducing. Monitor closely."
        )

    else:

        st.error(
            "🔴 Immediate operator attention required."
        )
import streamlit as st
import pandas as pd

# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data
def load_data():
    df = pd.read_excel("LRD_Pc.xlsx")
    return df

df = load_data()

# Rename columns for easy handling
df.columns = [
    "Raw_Turbidity_NTU",
    "Raw_pH",
    "S_Alum",
    "L_Alum",
    "P_PAC",
    "L_PAC",
    "Polymer"
]

df = df.sort_values("Raw_Turbidity_NTU")


# =====================================================
# HEADER
# =====================================================

st.markdown("""
<div style="
background:#F4F8FF;
border-left:8px solid #0A2E6B;
padding:15px;
border-radius:8px;
font-size:30px;
font-weight:bold;
color:#0A2E6B;">
Coagulant Dosing Decision Support System
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
font-size:18px;
font-weight:600;
color:#3B4A6B;
margin-top:8px;
margin-bottom:15px;">
Based on Historical Jar Test Data & Plant Performance Records
</div>
""", unsafe_allow_html=True)
# =====================================================
# INPUT SECTION
# =====================================================

# =====================================================
# INPUT SECTION
# =====================================================

col1, col2 = st.columns(2)

with col1:

    t1, t2 = st.columns([4, 1])

    with t1:
        turbidity = st.number_input(
            "Raw Water Turbidity",
            min_value=0.0,
            value=10.0,
            step=0.1,
            format="%.1f"
        )

    with t2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            "<h3 style='color:#0A2E6B;'>NTU</h3>",
            unsafe_allow_html=True
        )

with col2:

    ph = st.slider(
        "pH",
        min_value=0.0,
        max_value=14.0,
        value=7.0,
        step=0.1
    )
# =====================================================
# RANGE CHECK
# =====================================================

min_turb = df["Raw_Turbidity_NTU"].min()
max_turb = df["Raw_Turbidity_NTU"].max()

if turbidity < min_turb or turbidity > max_turb:

    st.error(
        f"❌ Value Not Available. Historical data available from "
        f"{min_turb:.1f} NTU to {max_turb:.1f} NTU"
    )

else:

    # =================================================
    # NEAREST TURBIDITY MATCH
    # =================================================

    idx = (
        df["Raw_Turbidity_NTU"]
        .sub(turbidity)
        .abs()
        .idxmin()
    )

    result = df.loc[idx]

    nearest_turbidity = result["Raw_Turbidity_NTU"]

    # =================================================
    # MATCH STATUS
    # =================================================

    if abs(nearest_turbidity - turbidity) < 0.01:

        st.success(
            f"✅ Exact Match Found : {nearest_turbidity:.1f} NTU"
        )

    else:

        st.info(
            f"ℹ Entered Turbidity : {turbidity:.1f} NTU | "
            f"Nearest Historical Value Used : {nearest_turbidity:.1f} NTU"
        )

    st.markdown("---")

    # =================================================
    # DOSING DISPLAY
    # =================================================

    st.markdown("##  Recommended Chemical Doses")

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric(
            "Solid Alum",
            result["S_Alum"]
        )

    with c2:
        st.metric(
            "Liquid Alum",
            result["L_Alum"]
        )

    with c3:
        st.metric(
            "Powder PAC",
            result["P_PAC"]
        )

    with c4:
        st.metric(
            "Liquid PAC",
            result["L_PAC"]
        )

    with c5:
        st.metric(
            "Polymer",
            result["Polymer"]
        )

    st.markdown("---")

    # =================================================
    # SUMMARY TABLE
    # =================================================

    st.markdown("### 📋 Dosing Record Used")

    summary = pd.DataFrame({

        "Parameter": [
            "Entered Turbidity",
            "Historical Turbidity Used",
            "Historical pH"
        ],

        "Value": [
            f"{turbidity:.1f} NTU",
            f"{nearest_turbidity:.1f} NTU",
            f"{result['Raw_pH']}"
        ]

    })

    st.table(summary)

    st.markdown("### 📊 Chemical Recommendation")

    chemical_df = pd.DataFrame({

        "Chemical": [
            "Solid Alum",
            "Liquid Alum",
            "Powder PAC",
            "Liquid PAC",
            "Polymer"
        ],

        "Recommended Dose": [
            result["S_Alum"],
            result["L_Alum"],
            result["P_PAC"],
            result["L_PAC"],
            result["Polymer"]
        ]

    })

    st.dataframe(
        chemical_df,
        use_container_width=True,
        hide_index=True
    )
# ============================================================
# CORRECT DYNAMIC HYPOCHLORITE DOSING MODEL
# ============================================================

st.markdown("""
<div style="
background:#F4F8FF;
border-left:8px solid #0A2E6B;
padding:15px;
border-radius:8px;
font-size:31px;
font-weight:bold;
color:#0A2E6B;">
Smart Dynamic Hypochlorite Dosing Model
</div>
""", unsafe_allow_html=True)
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

temperature = st.slider(
    "Water Temperature (°C)",
    0.0, 70.0, 25.0, 0.5
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
# REGRESSION-BASED CHLORINE DEMAND MODEL
# -----------------------------

chlorine_demand = (
    -1.60
    + 1.40 * nitrite
    + 0.0020 * conductivity
    + 0.35 * pH
    + 0.05 * temperature
)

chlorine_demand = max(chlorine_demand, 0.1)

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
    title="Regression-Based Sodium Hypochlorite Dosing Model",
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
st.markdown("""
<div style="
background:#F4F8FF;
border-left:8px solid #0A2E6B;
padding:15px;
border-radius:8px;
font-size:24px;
font-weight:bold;
color:#0A2E6B;">



🗼 Distribution Water Towers
</div>
""", unsafe_allow_html=True)

names=["Central WT","Kadma WT","Sidgorah 3 WT","Sakchi WT","Tatanagar WT","Tatanagarr WT"]
tc=st.columns(3)
for i in range(6):
    tc[i%3].plotly_chart(gauge(names[i],75,100),use_container_width=True)

# ===============================
# SUMP LEVEL MONITORING
# ===============================

st.markdown("""
<div style="
background:#F4F8FF;
border-left:8px solid #0A2E6B;
padding:15px;
border-radius:8px;
font-size:24px;
font-weight:bold;
color:#0A2E6B;">
💧 Sump Level Monitoring
</div>
""", unsafe_allow_html=True)

names = [
    "Sonari Sump",
    "Kadma Sump",
    "Sakchi Sump",
    "Tatanagar Sump",
    "Central Sump",
    "Sidgorah Sump"
]

levels = [82, 65, 91, 73, 88, 57]

tc = st.columns(3)

for i in range(6):
    tc[i % 3].plotly_chart(
        gauge(names[i], levels[i], 100),
        use_container_width=True
    )
import streamlit as st
import smtplib
import pandas as pd
import os
import numpy as np
import requests
import base64

from datetime import datetime, timedelta
import pytz
# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(layout="wide")

st.markdown("""
<div style="
background:#F4F8FF;
border-left:8px solid #0A2E6B;
padding:15px;
border-radius:8px;
font-size:31px;
font-weight:bold;
color:#0A2E6B;">
Smart Feedback System
</div>
""", unsafe_allow_html=True)

left_col, right_col = st.columns([2,1])

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# =========================================================
# EMAIL ALERT
# =========================================================

def send_email_alert(message):

    sender = "alokranjanjha18april@gmail.com"
    password = "ocnthywxvljtqbgt"

    receiver = "alok.ranjan6@tatasteel.com"

    try:

        msg = MIMEMultipart()

        msg["From"] = sender

        msg["To"] = receiver

        msg["Subject"] = "🚨 WATER QUALITY ALERT 🚨"

        body = message

        msg.attach(
            MIMEText(body, "plain", "utf-8")
        )

        server = smtplib.SMTP(
            "smtp.gmail.com",
            587
        )

        server.starttls()

        server.login(sender, password)

        server.sendmail(
            sender,
            receiver,
            msg.as_string()
        )

        server.quit()

        st.success("📧 Alert Email Sent")

    except Exception as e:

        st.error(f"Email Error: {e}")
       

# =========================================================
# SESSION STATES
# =========================================================

if "alarm" not in st.session_state:
    st.session_state.alarm = False

if "sound_enabled" not in st.session_state:
    st.session_state.sound_enabled = False

# =========================================================
# WEATHER DATA
# =========================================================

temperature = 30
humidity = 60

try:

    API_KEY = "f899db331049be78181d1afddbc92935"

    CITY = "Jamshedpur"

    url = (
        f"http://api.openweathermap.org/data/2.5/weather?"
        f"q={CITY}&appid={API_KEY}&units=metric"
    )

    data = requests.get(url).json()

    temperature = data["main"]["temp"]

    humidity = data["main"]["humidity"]

except:
    pass

# =========================================================
# DATA STORAGE
# =========================================================

FILE = "feedback_data.csv"

required_columns = [

    "timestamp",
    "date",
    "time",
    "temperature",
    "humidity",
    "raw_turbidity",
    "alum_dose",
    "pac_dose",
    "hypo_dose",
    "outlet_turbidity",
    "final_turbidity",
    "frc",
    "status",
    "operator_feedback"


]
if not os.path.exists(FILE):

   empty_df = pd.DataFrame(
       columns=required_columns
   )
   empty_df.to_csv(FILE, index=False)

# =========================================================
# LOAD DATA
# =========================================================


try:

    df = pd.read_csv(FILE)

except Exception as e:

    st.error(f"File Load Error: {e}")

    df = pd.DataFrame(
        columns=required_columns
    )
st.info(
    f"📂 Records Loaded At Startup: {len(df)}"
)
# =========================================================
# ENSURE COLUMNS EXIST
# =========================================================

for col in required_columns:

    if col not in df.columns:

        df[col] = None

# =========================================================
# CONVERT TIMESTAMP
# =========================================================

if len(df) > 0:

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

# =========================================================
# INPUT SECTION
# =========================================================

with left_col:

    st.markdown("Plant Feedback Entry")

    c1, c2 = st.columns(2)

    with c1:

        raw_turbidity = st.number_input(
            "Raw Water Turbidity",
            0.0,
            1000.0,
            50.0,
            0.1
        )

        alum_dose = st.slider(
            "Alum Dose (mg/L)",
            min_value=0.00,
            max_value=100.00,
            value=15.00,
            step=0.10
        )

        st.write(f"Selected Alum Dose: {alum_dose:.2f} mg/L")

        pac_dose = st.slider(
            "PAC Dose (mg/L)",
            min_value=0.00,
            max_value=100.00,
            value=10.00,
            step=0.10
        )

        st.write(f"Selected PAC Dose: {pac_dose:.2f} mg/L")
        
        hypo_dose = st.slider(
            "Hypo Dose (ppm)",
            0.0,
            10.0,
            1.0
        )

    with c2:

        outlet_turbidity = st.number_input(
            "Clarifier Outlet Turbidity",
            0.0,
            100.0,
            5.0
        )

        final_turbidity = st.number_input(
            "Final Water Turbidity",
            0.0,
            50.0,
            0.5
        )

        frc = st.number_input(
            "FRC",
            0.0,
            5.0,
            0.5
        )
    operator_feedback = st.text_area(
    "📝 Operator Remarks / Feedback"
)
    submit = st.button("✅ Submit Feedback")

# =========================================================
# SUBMIT DATA
# =========================================================

if submit:

    now = datetime.now(pytz.timezone("Asia/Kolkata"))

    # =====================================================
    # HEALTH STATUS
    # =====================================================

    if final_turbidity <= 1 and 0.2 <= frc <= 1:

        status = "GOOD"

    elif final_turbidity <= 2:

        status = "MODERATE"

    else:

        status = "CRITICAL"

    # =====================================================
    # NEW ENTRY
    # =====================================================

    new_data = pd.DataFrame([{

        "timestamp": now,
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),

        "temperature": temperature,
        "humidity": humidity,

        "raw_turbidity": raw_turbidity,

        "alum_dose": alum_dose,
        "pac_dose": pac_dose,
        "hypo_dose": hypo_dose,

        "outlet_turbidity": outlet_turbidity,

        "final_turbidity": final_turbidity,

        "frc": frc,

        "status": status,

        "operator_feedback": operator_feedback

    }])

    # =====================================================
    # APPEND DATA
    # =====================================================

    df = pd.concat([df, new_data], ignore_index=True)
    if len(df) > 1000:
        df = df.tail(1000).reset_index(drop=True)

    # =====================================================
    # SAVE CSV
    # =====================================================

    
    df.to_csv(
        FILE,
        index=False,
        encoding="utf-8-sig"
    )
    
    # Verify data actually saved
    saved_df = pd.read_csv(FILE)
    
    st.success("✅ Feedback Stored Successfully")
    
    st.info(
        f"📦 Total Samples In Memory: {len(df)}"
    )
    
    st.info(
        f"💾 Total Samples Saved In CSV: {len(saved_df)}"
    )
    
    st.dataframe(
        saved_df.tail(5),
        use_container_width=True
    )
    # =====================================================
    # AI RECOMMENDATION
    # =====================================================

    if len(df) >= 30:

        st.markdown("## Smart Recommendation")

        good_data = df[
            (df["final_turbidity"] <= 1)
            &
            (df["frc"] >= 0.2)
            &
            (df["frc"] <= 1)
        ]

        if len(good_data) >= 10:

            good_data = good_data.copy()

            good_data["difference"] = abs(
                good_data["raw_turbidity"]
                -
                raw_turbidity
            )

            similar = good_data.sort_values(
                by="difference"
            ).head(10)

            recommended_alum = similar[
                "alum_dose"
            ].mean()

            recommended_hypo = similar[
                "hypo_dose"
            ].mean()

            st.success(
                f"✅ Recommended Alum Dose: "
                f"{recommended_alum:.2f} mg/L"
            )

            st.success(
                f"✅ Recommended Hypo Dose: "
                f"{recommended_hypo:.2f} ppm"
            )

            if raw_turbidity > 150:

                st.warning(
                    "⚠️ High raw turbidity detected."
                )

            if temperature > 35:

                st.warning(
                    "🌡 High temperature may increase chlorine decay."
                )

            if frc < 0.2:

                st.error(
                    "🚨 Low FRC detected."
                )

            if outlet_turbidity > 10:

                st.warning(
                    "⚠️ Clarifier performance issue suspected."
                )

        else:

            st.warning(
                "Not enough good quality samples available."
            )

    else:

        remaining = 30 - len(df)

        st.info(
            f"AI Recommendation activates after "
            f"30 samples.\n"
            f"Remaining samples: {remaining}"
        )

    # =====================================================
    # ALARM CONDITIONS
    # =====================================================
    # =====================================================
    # ALARM CONDITIONS
    # =====================================================
    
    if (
        final_turbidity > 1
        or frc < 0.2
        or outlet_turbidity > 10
    ):
    
        if final_turbidity > 1:
    
            msg = (
                f"Final Turbidity High "
                f"({final_turbidity:.2f} NTU)"
            )
    
            if msg not in st.session_state.quality_alarm_list:

                st.session_state.quality_alarm_list.append(msg)
                
        if frc < 0.2:
    
            msg = (
                f"Low FRC "
                f"({frc:.2f})"
            )
    
            if msg not in st.session_state.quality_alarm_list:

                st.session_state.quality_alarm_list.append(msg)
        st.session_state.alarm = True
    
        # =================================================
        # EMAIL MESSAGE
        # =================================================
    
        msg = f"""
    🚨 WATER QUALITY ALERT 🚨
    
    Time: {now}
    
    Raw Turbidity: {raw_turbidity}
    
    Clarifier Outlet Turbidity: {outlet_turbidity}
    
    Final Turbidity: {final_turbidity}
    
    FRC: {frc}
    
    Alum Dose: {alum_dose}
    Pac Dose: {pac_dose}
    Hypo Dose: {hypo_dose}
    
    Immediate operator action required.
    """
    
        send_email_alert(msg)
        
# =========================================================
# ACTIVE ALARM DISPLAY
# =========================================================

if st.session_state.alarm:

    st.session_state.sound_enabled = True

    st.error("🚨 ACTIVE WATER QUALITY ALARM")

    st.markdown("""
    <style>

    @keyframes blink {
        0% { background-color: red; }
        50% { background-color: white; }
        100% { background-color: red; }
    }

    .alarm-box {
        animation: blink 1s infinite;
        padding: 25px;
        font-size: 30px;
        text-align: center;
        font-weight: bold;
        color: black;
        border-radius: 10px;
        margin-top: 10px;
    }

    </style>

    <div class="alarm-box">
        🚨 CRITICAL WATER QUALITY ISSUE 🚨
    </div>

    """, unsafe_allow_html=True)

# =====================================================
# AUTO PLAY ALARM SOUND
# =====================================================

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
        <audio autoplay loop id="alarm-audio">
            <source
            src="data:audio/wav;base64,{b64}"
            type="audio/wav">
        </audio>

        <script>

        var audio = document.getElementById("alarm-audio");

        audio.volume = 1.0;

        audio.play();

        </script>
        """

        st.components.v1.html(
            audio_html,
            height=0
        )

        st.error("🔊 ALARM SOUND ACTIVE")

    except Exception as e:

        st.warning(f"Alarm sound issue: {e}")

# =====================================================
# STOP BUTTON
# =====================================================

if st.button("🛑 Stop Alarm"):

    st.session_state.alarm = False
    st.session_state.sound_enabled = False

    st.success("Alarm Stopped")

# =========================================================
# ANALYTICS DASHBOARD
# =========================================================

st.markdown("---")

st.markdown("""
<div style="
background:#F4F8FF;
border-left:8px solid #0A2E6B;
padding:15px;
border-radius:8px;
font-size:24px;
font-weight:bold;
color:#0A2E6B;">
Analytics Dashboard
</div>
""", unsafe_allow_html=True)

if len(df) > 0:

    m1, m2, m3, m4, m5 = st.columns(5)

    with m1:
        st.metric(
            "Total Samples",
            len(df)
        )

    with m2:
        st.metric(
            "Avg Alum Dose",
            f"{df['alum_dose'].mean():.2f} mg/L"
        )

    with m3:
        st.metric(
            "Avg PAC Dose",
            f"{df['pac_dose'].mean():.2f} mg/L"
        )

    with m4:
        st.metric(
            "Avg Final Turbidity",
            f"{df['final_turbidity'].mean():.2f}"
        )

    with m5:

        efficiency = (
            len(
                df[
                    df["final_turbidity"] <= 1
                ]
            )
            / len(df)
        ) * 100

        st.metric(
            "Treatment Efficiency",
            f"{efficiency:.1f}%"
        )

    if efficiency >= 90:

        st.success("🟢 Plant Health Excellent")

    elif efficiency >= 70:

        st.warning("🟡 Plant Health Moderate")

    else:

        st.error("🔴 Plant Requires Attention")

# =========================================================
# TREND CHART
# =========================================================

st.subheader("## 📈 Treatment Trend")

import plotly.graph_objects as go

chart_df = df.copy()

chart_df["timestamp"] = pd.to_datetime(
    chart_df["timestamp"],
    errors="coerce"
)

chart_df = chart_df.dropna(
    subset=["timestamp"]
)

chart_df = chart_df.sort_values(
    by="timestamp"
)

fig = go.Figure()

# =====================================================
# ADD PARAMETERS
# =====================================================

fig.add_trace(go.Scatter(
    x=chart_df["timestamp"],
    y=chart_df["raw_turbidity"],
    mode='lines+markers',
    name='Raw Turbidity'
))

fig.add_trace(go.Scatter(
    x=chart_df["timestamp"],
    y=chart_df["alum_dose"],
    mode='lines+markers',
    name='Alum Dose'
))

fig.add_trace(go.Scatter(
    x=chart_df["timestamp"],
    y=chart_df["hypo_dose"],
    mode='lines+markers',
    name='Hypo Dose'
))

fig.add_trace(go.Scatter(
    x=chart_df["timestamp"],
    y=chart_df["outlet_turbidity"],
    mode='lines+markers',
    name='Outlet Turbidity'
))

fig.add_trace(go.Scatter(
    x=chart_df["timestamp"],
    y=chart_df["final_turbidity"],
    mode='lines+markers',
    name='Final Turbidity'
))

fig.add_trace(go.Scatter(
    x=chart_df["timestamp"],
    y=chart_df["frc"],
    mode='lines+markers',
    name='FRC'
))
fig.add_trace(go.Scatter(
    x=chart_df["timestamp"],
    y=chart_df["pac_dose"],
    mode='lines+markers',
    name='PAC Dose'
))

# =====================================================
# GRAPH SETTINGS
# =====================================================

fig.update_layout(

    title="Water Treatment Plant Trend Analysis",

    xaxis_title="Time",

    yaxis_title="Values",

    hovermode="x unified",

    height=600,

    legend_title="Parameters"
)

# =====================================================
# DISPLAY GRAPH
# =====================================================

st.plotly_chart(
    fig,
    use_container_width=True
)
# =========================================================
# STORED DATA
# =========================================================

st.markdown("---")

st.subheader("📂 Complete Feedback Database")

latest_df = pd.read_csv(FILE)

st.write(f"Total Records: {len(latest_df)}")

st.dataframe(
    latest_df.sort_values(
        by="timestamp",
        ascending=False
    ),
    use_container_width=True,
    height=500
)
   # =========================================================
# DELETE ROW OPTION
# =========================================================

st.markdown("🗑 Delete Stored Row")

if len(df) > 0:

    display_df = df.sort_values(
        by="timestamp",
        ascending=False
    ).reset_index()

    selected_row = st.selectbox(

        "Select Row To Delete",

        display_df.index,

        format_func=lambda x:
        f"Row {x} | "
        f"Time: {display_df.loc[x, 'time']} | "
        f"Raw Turbidity: {display_df.loc[x, 'raw_turbidity']} | "
        f"Final Turbidity: {display_df.loc[x, 'final_turbidity']}"

    )

    if st.button("🗑 Delete Selected Row"):

        try:

            original_index = display_df.loc[
                selected_row,
                "index"
            ]

            df = df.drop(original_index)

            df = df.reset_index(drop=True)

            df.to_csv(FILE, index=False)

            st.success(
                "Selected row deleted successfully"
            )

            st.rerun()

        except Exception as e:

            st.error(f"Delete Error: {e}") 

# =========================================================
# WEATHER PANEL
# =========================================================

with right_col:

    st.subheader("🌤 Live Weather")

    st.metric(
        "Temperature",
        f"{temperature} °C"
    )

    st.metric(
        "Humidity",
        f"{humidity}%"
    )

    if temperature > 35:

        st.warning(
            "High temperature may increase chlorine consumption."
        )

    elif temperature < 20:

        st.info(
            "Low temperature may slow coagulation."
        )

    else:

        st.success(
            "Weather conditions normal."
        )
# ============================================================
# WEATHER FORECAST
# ============================================================

# ============================================================
# 🌦️ WEATHER FORECAST
# ============================================================

import requests
import pandas as pd
import streamlit as st

# ============================================================
# TITLE
# ============================================================

st.markdown("""
<div style="
background:#F4F8FF;
border-left:8px solid #0A2E6B;
padding:15px;
border-radius:8px;
font-size:31px;
font-weight:bold;
color:#0A2E6B;">
🌦️ Weather Forecast
</div>
""", unsafe_allow_html=True)

# ============================================================
# CSS
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

</style>
""", unsafe_allow_html=True)

# ============================================================
# WEATHER API
# ============================================================

API_KEY = "f899db331049be78181d1afddbc92935"

CITY = "Jamshedpur"

url = (
    f"https://api.openweathermap.org/data/2.5/forecast"
    f"?q={CITY}"
    f"&appid={API_KEY}"
    f"&units=metric"
)

try:

    response = requests.get(url, timeout=10)

    if response.status_code == 200:

        data = response.json()

        weather_data = []

        for item in data["list"][:6]:

            weather_data.append({

                "Time": item["dt_txt"][11:16],

                "Temp": item["main"]["temp"],

                "Humidity": item["main"]["humidity"],

                "Rain": item.get("rain", {}).get("3h", 0)

            })

        weather_df = pd.DataFrame(weather_data)

        st.markdown("### ⏰ Hourly Weather Forecast")

        cols = st.columns(6)

        for i in range(6):

            row = weather_df.iloc[i]

            with cols[i]:

                st.markdown(f"""
                <div class='small-weather'>

                <b>{row['Time']}</      Temp: {row['Temp']:.1f}°C<br>

                Humidity: {row['Humidity']}%<br>

                Rain: {row['Rain']} mm

                </div>
                """, unsafe_allow_html=True)

    else:

        st.error(f"Weather API Error : {response.status_code}")

except Exception as e:

    st.error(f"Unable to fetch weather data : {e}")
  
# =======================================
# CUSTOMER END GIS MAP
# ==========================================================

st.markdown("""
<div style="
background:#F4F8FF;
border-left:8px solid #0A2E6B;
padding:15px;
border-radius:8px;
font-size:31px;
font-weight:bold;
color:#0A2E6B;">
📍 Customer End GIS Map
</div>
""", unsafe_allow_html=True)

try:

    # ======================================================
    # READ GIS FILE
    # ======================================================
    gis = pd.read_excel("Moharda_GIS_Cleaned.xlsx")

    # ======================================================
    # NUMERIC CONVERSION
    # ======================================================
    gis["Latitude"] = pd.to_numeric(
        gis["Latitude"],
        errors="coerce"
    )

    gis["Longitude"] = pd.to_numeric(
        gis["Longitude"],
        errors="coerce"
    )

    gis["Turbidity"] = pd.to_numeric(
        gis["Turbidity"],
        errors="coerce"
    )

    gis["FRC_PPM"] = pd.to_numeric(
        gis["FRC_PPM"],
        errors="coerce"
    )

    # ======================================================
    # STATUS FILTER
    # ======================================================
    # ======================================================
    # STATUS FILTER
    # ======================================================
    
    selected_status = st.multiselect(
        "Select Water Quality Status",
        [
            "Safe",
            "Slight Deviation",
            "Critical"
        ],
        default=[
            "Safe",
            "Slight Deviation",
            "Critical"
        ]
    )
    
    gis_filtered = gis[
        gis["Status"].isin(selected_status)
    ]
    
    # ======================================================
    # GIS ALARM COUNT
    # ======================================================
    
    total_coliform_count = len(
        gis[
            gis["Total_Coli"]
            .astype(str)
            .str.strip()
            .str.lower()
            == "present"
        ]
    )
    
    faecal_coliform_count = len(
        gis[
            gis["Faecal_Col"]
            .astype(str)
            .str.strip()
            .str.lower()
            == "present"
        ]
    )
    
    gis_alarms = []
    
    if total_coliform_count > 0:
    
        gis_alarms.append(
            f"Total Coliform Present : {total_coliform_count}"
        )
    
    if faecal_coliform_count > 0:
    
        gis_alarms.append(
            f"Faecal Coliform Present : {faecal_coliform_count}"
        )
    
    st.session_state.gis_alarm_list = gis_alarms
    
    # ======================================================
    # NO DATA CHECK
    # ======================================================
    
    if gis_filtered.empty:
    
        st.warning(
            "No locations found for selected status."
        )
    
    else:
    
        # REST OF GIS MAP CODE HERE
        # ==================================================
        # SUMMARY CARDS
        # ==================================================
        col1, col2, col3 = st.columns(3)

        with col1:

            st.success(
                f"🟢 Safe Locations : "
                f"{len(gis[gis['Status']=='Safe'])}"
            )

        with col2:

            st.warning(
                f"🟡 Slight Deviation : "
                f"{len(gis[gis['Status']=='Slight Deviation'])}"
            )

        with col3:

            st.error(
                f"🔴 Critical Locations : "
                f"{len(gis[gis['Status']=='Critical'])}"
            )

        # ==================================================
        # FIXED MAP CENTER
        # ==================================================
        center_lat = 22.804
        center_lon = 86.230

        # ==================================================
        # MAP
        # ==================================================
        fig_map = px.scatter_map(
            gis_filtered,
            lat="Latitude",
            lon="Longitude",
            color="Status",
            hover_name="Cust_Name_",
            hover_data={
                "Turbidity": True,
                "FRC_PPM": True,
                "Total_Coli": True,
                "Faecal_Col": True,
                "Status": True,
                "Latitude": False,
                "Longitude": False
            },
            color_discrete_map={
                "Safe": "green",
                "Slight Deviation": "yellow",
                "Critical": "red"
            },
            zoom=12,
            height=700
        )

        fig_map.update_traces(
            marker=dict(
                size=13,
                opacity=0.95
            )
        )

        fig_map.update_layout(
            map_style="open-street-map",
            map=dict(
                center=dict(
                    lat=center_lat,
                    lon=center_lon
                ),
                zoom=12
            ),
            legend=dict(
                title="Water Quality Status",
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
            margin=dict(
                l=0,
                r=0,
                t=0,
                b=0
            )
        )

        st.plotly_chart(
            fig_map,
            use_container_width=True
        )

        # ==================================================
        # STATUS DISTRIBUTION
        # ==================================================
        st.markdown("### 📊 Status Distribution")

        status_count = (
            gis["Status"]
            .value_counts()
            .reset_index()
        )

        status_count.columns = [
            "Status",
            "Count"
        ]

        fig_status = px.pie(
            status_count,
            names="Status",
            values="Count",
            hole=0.5
        )

        st.plotly_chart(
            fig_status,
            use_container_width=True
        )

except Exception as e:

    st.error(
        f"GIS Map Error : {e}"
    )
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# ============================================================
# TITLE
# ============================================================

# ============================================================
# 📍 Washout GIS Map
# ============================================================

st.markdown("""
<div style="
background:#F4F8FF;
border-left:8px solid #0A2E6B;
padding:15px;
border-radius:8px;
font-size:31px;
font-weight:bold;
color:#0A2E6B;">
📍 Washout GIS Map
</div>
""", unsafe_allow_html=True)

# ============================================================
# LOAD DATA
# ============================================================

washout = pd.read_excel("Wahout_pointss.xlsx")

# ============================================================
# DATE CONVERSION
# ============================================================

washout["Prv_Washout Date"] = pd.to_datetime(
    washout["Prv_Washout Date"],
    errors="coerce"
)

washout["Due_Washout Date"] = pd.to_datetime(
    washout["Due_Washout Date"],
    errors="coerce"
)

# ============================================================
# LAT LONG CLEANING
# ============================================================

washout["Lattitude"] = pd.to_numeric(
    washout["Lattitude"],
    errors="coerce"
)

washout["Longitude"] = pd.to_numeric(
    washout["Longitude"],
    errors="coerce"
)

washout = washout.dropna(
    subset=["Lattitude", "Longitude"]
)

# ============================================================
# RANDOMIZE FOR COLOR DISTRIBUTION
# ============================================================

washout = washout.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)

# ============================================================
# MAP CENTER
# ============================================================

center_lat = washout["Lattitude"].mean()
center_lon = washout["Longitude"].mean()

# ============================================================
# CREATE MAP
# ============================================================

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=12,
    tiles="OpenStreetMap"
)

# ============================================================
# MARKERS
# ============================================================

for i, row in washout.iterrows():

    if i < 4:
        color = "red"

    elif i < 7:
        color = "orange"

    else:
        color = "green"


    folium.CircleMarker(
        location=[
            row["Lattitude"],
            row["Longitude"]
        ],
        radius=8,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.9,
        tooltip=str(row["Location"])
    ).add_to(m)

# ============================================================
# DISPLAY MAP
# ============================================================

st_folium(
    m,
    width=None,
    height=650
)
# ==========================================================
# WATER QUALITY EXECUTIVE DASHBOARD - PART 1
# HEADER + KPI + WQI GAUGE
# ==========================================================

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import plotly.express as px

st.markdown("---")

st.markdown("""
<div style="
background:linear-gradient(90deg,#0f172a,#1e3a8a);
padding:15px;
border-radius:12px;
text-align:center;
margin-bottom:15px;">
<h2 style="color:white;margin:0;">
📊 WATER QUALITY EXECUTIVE DASHBOARD
</h2>
<p style="color:#cbd5e1;margin:0;">
Water Supply Monitoring System
</p>
</div>
""", unsafe_allow_html=True)

# ==========================================================
# LOAD DATA
# ==========================================================

wq = pd.read_excel("mohardawaterQuality.xlsx")
# ==========================================================
# GLOBAL MONTH & YEAR FILTER
# ==========================================================

wq["created_da"] = pd.to_datetime(
    wq["created_da"],
    errors="coerce"
)

wq["Year"] = wq["created_da"].dt.year
wq["Month"] = wq["created_da"].dt.month_name()

all_months = [
    "January","February","March","April",
    "May","June","July","August",
    "September","October","November","December"
]

all_years = list(range(2026, 2036))

st.markdown("### 📅 Dashboard Time Filter")

f1, f2 = st.columns(2)

with f1:

    selected_year = st.selectbox(
        "Select Year",
        all_years,
        index=0
    )

with f2:

    selected_month = st.selectbox(
        "Select Month",
        all_months,
        index=1
    )

filtered_wq = wq[
    (wq["Year"] == selected_year)
    &
    (wq["Month"] == selected_month)
]

if filtered_wq.empty:

    st.warning(
        f"⚠️ Data Not Available for {selected_month} {selected_year}"
    )

    st.stop()

st.success(
    f"Showing Dashboard Data for {selected_month} {selected_year}"
)

# Use filtered data for entire dashboard

wq = filtered_wq.copy()
# Remove blank coordinates
wq = wq[
    (wq["Latitude"] != 0) &
    (wq["Longitude"] != 0)
].copy()

# ==========================================================
# WATER QUALITY STATUS
# ==========================================================

def classify(row):

    if str(row["Total_Coli"]).strip().lower() == "present":
        return "Critical"

    if str(row["Faecal_Col"]).strip().lower() == "present":
        return "Critical"

    if row["Turbidity"] > 1:
        return "Observation"

    if row["FRC_PPM"] < 0.2:
        return "Observation"

    return "Safe"

wq["Status"] = wq.apply(classify, axis=1)

# ==========================================================
# KPI CALCULATIONS
# ==========================================================

total_samples = len(wq)
if total_samples == 0:
    st.warning("⚠ No data available for the selected month.")
    st.stop()
safe_samples = len(
    wq[wq["Status"] == "Safe"]
)

critical_samples = len(
    wq[wq["Status"] == "Critical"]
)

safe_percent = round(
    (safe_samples / total_samples) * 100,
    1
)

avg_rating = round(
    pd.to_numeric(
        wq["Rating"],
        errors="coerce"
    ).mean(),
    1
)

turb_fail = len(
    wq[wq["Turbidity"] > 1]
)

frc_fail = len(
    wq[wq["FRC_PPM"] < 0.2]
)

coli_fail = len(
    wq[
        wq["Total_Coli"]
        .astype(str)
        .str.lower()
        == "present"
    ]
)

faecal_fail = len(
    wq[
        wq["Faecal_Col"]
        .astype(str)
        .str.lower()
        == "present"
    ]
)

failure_dict = {
    "Turbidity": turb_fail,
    "Low FRC": frc_fail,
    "Total Coliform": coli_fail,
    "Faecal Coliform": faecal_fail
}

top_failure = max(
    failure_dict,
    key=failure_dict.get
)

# ==========================================================
# SIMPLE WQI
# ==========================================================

wqi_score = max(
    0,
    round(
        100 -
        (
            critical_samples * 2
            +
            turb_fail * 0.5
        ),
        1
    )
)

# ==========================================================
# KPI ROW
# ==========================================================

k1,k2,k3,k4,k5,k6 = st.columns(6)

k1.metric(
    "Total Samples",
    total_samples
)

k2.metric(
    "Safe %",
    f"{safe_percent}%"
)

k3.metric(
    "Critical",
    critical_samples
)

k4.metric(
    "Avg Rating",
    avg_rating
)

k5.metric(
    "Top Failure",
    top_failure
)

# ==========================================================
# WQI GAUGE
# ==========================================================

fig_wqi = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=wqi_score,
        title={
            "text":"Water Quality Index"
        },
        gauge={
            "axis":{
                "range":[0,100]
            },
            "bar":{
                "color":"#00B4D8"
            },
            "steps":[

                {
                    "range":[0,50],
                    "color":"#FF6B6B"
                },

                {
                    "range":[50,80],
                    "color":"#FFD166"
                },

                {
                    "range":[80,100],
                    "color":"#06D6A0"
                }
            ]
        }
    )
)

fig_wqi.update_layout(
    height=180,
    margin=dict(
        l=10,
        r=10,
        t=40,
        b=10
    )
)

k6.plotly_chart(
    fig_wqi,
    use_container_width=True
)

st.markdown("<br>", unsafe_allow_html=True)
# ==========================================================
# WATER QUALITY EXECUTIVE DASHBOARD - PART 2
# AREA WISE COMPARISON
# ==========================================================

st.markdown("### 📊 Area-wise Water Quality Comparison")

# ==========================================================
# AREA SUMMARY
# ==========================================================

zone_summary = (
    wq.groupby("Cust_Name_")
    .agg({
        "Turbidity":"mean",
        "FRC_PPM":"mean",
        "PH":"mean",
        "Rating":"mean"
    })
    .reset_index()
)

zone_summary["Rating"] = (
    pd.to_numeric(
        zone_summary["Rating"],
        errors="coerce"
    )
)

# ==========================================================
# CHART TABS
# ==========================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "Turbidity",
    "FRC",
    "pH",
    "Rating"
])

# ==========================================================
# TURBIDITY
# ==========================================================

with tab1:

    fig_turb = go.Figure()

    fig_turb.add_trace(
        go.Bar(
            x=zone_summary["Cust_Name_"],
            y=zone_summary["Turbidity"],
            name="Turbidity",
            marker_color="#EF4444"
        )
    )

    fig_turb.add_hline(
        y=1,
        line_dash="dash",
        line_color="green"
    )

    fig_turb.update_layout(
        title="Average Turbidity by Area",
        height=350,
        xaxis_tickangle=-45,
        template="plotly_white",
        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20
        )
    )

    st.plotly_chart(
        fig_turb,
        use_container_width=True
    )

# ==========================================================
# FRC
# ==========================================================

with tab2:

    fig_frc = go.Figure()

    fig_frc.add_trace(
        go.Bar(
            x=zone_summary["Cust_Name_"],
            y=zone_summary["FRC_PPM"],
            name="FRC",
            marker_color="#00B4D8"
        )
    )

    fig_frc.add_hline(
        y=0.2,
        line_dash="dash",
        line_color="red"
    )

    fig_frc.update_layout(
        title="Average Free Residual Chlorine",
        height=350,
        xaxis_tickangle=-45,
        template="plotly_white",
        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20
        )
    )

    st.plotly_chart(
        fig_frc,
        use_container_width=True
    )

# ==========================================================
# PH
# ==========================================================

with tab3:

    fig_ph = go.Figure()

    fig_ph.add_trace(
        go.Bar(
            x=zone_summary["Cust_Name_"],
            y=zone_summary["PH"],
            name="pH",
            marker_color="#22C55E"
        )
    )

    fig_ph.add_hline(
        y=6.5,
        line_dash="dash",
        line_color="red"
    )

    fig_ph.add_hline(
        y=8.5,
        line_dash="dash",
        line_color="red"
    )

    fig_ph.update_layout(
        title="Average pH by Area",
        height=350,
        xaxis_tickangle=-45,
        template="plotly_white",
        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20
        )
    )

    st.plotly_chart(
        fig_ph,
        use_container_width=True
    )

# ==========================================================
# CUSTOMER RATING
# ==========================================================

with tab4:

    fig_rate = go.Figure()

    fig_rate.add_trace(
        go.Bar(
            x=zone_summary["Cust_Name_"],
            y=zone_summary["Rating"],
            name="Rating",
            marker_color="#F59E0B"
        )
    )

    fig_rate.update_layout(
        title="Customer Rating by Area",
        height=350,
        xaxis_tickangle=-45,
        template="plotly_white",
        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20
        )
    )

    st.plotly_chart(
        fig_rate,
        use_container_width=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================================
# WATER QUALITY EXECUTIVE DASHBOARD - PART 9
# EXECUTIVE HEATMAP ANALYSIS
# ==========================================================

st.markdown("### 🔥 Executive Heatmap Dashboard")

# ==========================================================
# PREPARE DATA
# ==========================================================

heat_df = wq.copy()

st.success(
    f"Showing Executive Heatmap for {selected_month} {selected_year}"
)
heat_df["UpdatedOn"] = pd.to_datetime(
    heat_df["UpdatedOn"],
    errors="coerce"
)

heat_df["Rating"] = pd.to_numeric(
    heat_df["Rating"],
    errors="coerce"
)

# Latest record from each area
zone_heat = (
    heat_df
    .sort_values("UpdatedOn")
    .groupby("Cust_Name_", as_index=True)
    .last()
)

# ==========================================================
# COMPLIANCE SCORING
# ==========================================================

def turbidity_score(x):

    if pd.isna(x):
        return 1

    elif x <= 1:
        return 5

    elif x <= 5:
        return 3

    else:
        return 1


def frc_score(x):

    if pd.isna(x):
        return 1

    elif 0.2 <= x <= 1.0:
        return 5

    elif (0.1 <= x < 0.2) or (1.0 < x <= 1.5):
        return 3

    else:
        return 1


def ph_score(x):

    if pd.isna(x):
        return 1

    elif 6.6 <= x <= 8.5:
        return 5

    elif (6.0 <= x < 6.6) or (8.5 < x <= 9.0):
        return 3

    else:
        return 1


def rating_score(x):

    if pd.isna(x):
        return 1

    elif x >= 4.5:
        return 5

    elif x >= 3:
        return 3

    else:
        return 1


def coliform_score(x):

    if str(x).strip().lower() == "absent":
        return 5

    return 1


# ==========================================================
# SCORE MATRIX
# ==========================================================

score_matrix = pd.DataFrame(
    index=zone_heat.index
)

score_matrix["Turbidity"] = (
    zone_heat["Turbidity"]
    .apply(turbidity_score)
)

score_matrix["FRC"] = (
    zone_heat["FRC_PPM"]
    .apply(frc_score)
)

score_matrix["pH"] = (
    zone_heat["PH"]
    .apply(ph_score)
)

score_matrix["Rating"] = (
    zone_heat["Rating"]
    .apply(rating_score)
)

score_matrix["Total Coliform"] = (
    zone_heat["Total_Coli"]
    .apply(coliform_score)
)

score_matrix["Faecal Coliform"] = (
    zone_heat["Faecal_Col"]
    .apply(coliform_score)
)

# ==========================================================
# TEXT DISPLAY MATRIX
# ==========================================================

text_matrix = []

for _, row in zone_heat.iterrows():

    text_matrix.append([

        f"{row['Turbidity']:.2f}",

        f"{row['FRC_PPM']:.2f}",

        f"{row['PH']:.2f}",

        f"{row['Rating']:.1f}",

        str(row["Total_Coli"]),

        str(row["Faecal_Col"])

    ])

# ==========================================================
# HEATMAP FIGURE
# ==========================================================

fig_heat = go.Figure(

    data=go.Heatmap(

        z=score_matrix.values,

        x=[
            "Turbidity",
            "FRC",
            "pH",
            "Rating",
            "Total Coliform",
            "Faecal Coliform"
        ],

        y=score_matrix.index,

        colorscale=[
            [0.0, "#EF4444"],
            [0.5, "#FACC15"],
            [1.0, "#22C55E"]
        ],

        zmin=1,
        zmax=5,

        text=text_matrix,

        texttemplate="%{text}",

        textfont=dict(
            size=9,
            color="black"
        ),

        hoverongaps=False

    )

)

fig_heat.update_layout(

    title="Zone-wise Water Quality Compliance Heatmap",

    height=max(
        700,
        len(score_matrix.index) * 35
    ),

    margin=dict(
        l=10,
        r=10,
        t=60,
        b=10
    )

)

st.plotly_chart(
    fig_heat,
    use_container_width=True
)

# ==========================================================
# HEATMAP LEGEND
# ==========================================================

with st.expander(
    "📘 Executive Heatmap Standards (Click to View)",
    expanded=False
):

    st.markdown(
        """
### Turbidity (NTU)
- 🟢 ≤ 1 : Desirable
- 🟡 > 1 to 5 : Acceptable / Permissible
- 🔴 > 5 : Non-Compliant

### pH
- 🟢 6.6 – 8.5 : Acceptable Range
- 🟡 6.0 – 6.5 or 8.5 – 9.0 : Observation
- 🔴 < 6.0 or > 9.0 : Non-Compliant

### Free Residual Chlorine (FRC)
- 🟢 0.2 – 1.0 ppm : Adequate Residual Chlorine
- 🟡 0.1 – 0.2 ppm or 1.0 – 1.5 ppm : Observation
- 🔴 < 0.1 ppm or > 1.5 ppm : Non-Compliant

### Customer Rating
- 🟢 5 : Excellent
- 🟡 3 – 4 : Average / Satisfactory
- 🔴 1 – 2 : Poor

### Total Coliform
- 🟢 Absent
- 🔴 Present

### Faecal Coliform
- 🟢 Absent
- 🔴 Present

### Heatmap Interpretation
- 🟢 Green = Within Standard
- 🟡 Yellow = Acceptable / Observation
- 🔴 Red = Requires Immediate Attention
"""
    )
st.markdown("<br>", unsafe_allow_html=True)
# ==========================================================
# WATER QUALITY EXECUTIVE DASHBOARD - PART 10
# FILTERS + EXECUTIVE SUMMARY
# ==========================================================



# ==========================================================
# FINAL STATUS
# ==========================================================

st.markdown("### 🎯 Overall System Status")

if wqi_score >= 80:

    st.markdown(
        """
        <div style="
        background:#d1e7dd;
        color:#0f5132;
        padding:20px;
        border-radius:12px;
        text-align:center;
        font-size:24px;
        font-weight:bold;
        ">
        ✅ GOOD WATER QUALITY
        </div>
        """,
        unsafe_allow_html=True
    )

elif wqi_score >= 60:

    st.markdown(
        """
        <div style="
        background:#fff3cd;
        color:#664d03;
        padding:20px;
        border-radius:12px;
        text-align:center;
        font-size:24px;
        font-weight:bold;
        ">
        ⚠ MODERATE ATTENTION REQUIRED
        </div>
        """,
        unsafe_allow_html=True
    )

else:

    st.markdown(
        """
        <div style="
        background:#f8d7da;
        color:#842029;
        padding:20px;
        border-radius:12px;
        text-align:center;
        font-size:24px;
        font-weight:bold;
        ">
        🚨 IMMEDIATE ACTION REQUIRED
        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================================================
# DASHBOARD FOOTER
# ==========================================================

st.markdown("---")

st.markdown(
    """
    <div style="
    text-align:center;
    padding:18px;
    background:linear-gradient(90deg,#0d6efd,#20c997);
    color:white;
    border-radius:12px;
    font-size:16px;
    font-weight:bold;
    ">
    GIS Based Water Quality Executive Dashboard<br>
    Moharda Water Supply System Monitoring
    </div>
    """,
    unsafe_allow_html=True
)


# SUMP LEVEL MONITORING
# ===============================
st.markdown("""
<div style="
background:#F4F8FF;
border-left:8px solid #0A2E6B;
padding:15px;
border-radius:8px;
font-size:28px;
font-weight:bold;
color:#0A2E6B;">
💧 Clear Water Sump Status
</div>
""", unsafe_allow_html=True)
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
from ultralytics import YOLO
import streamlit as st
import cv2
import numpy as np
from PIL import Image
st.markdown("""
<div style="
background:#F4F8FF;
border-left:8px solid #0A2E6B;
padding:15px;
border-radius:8px;
font-size:28px;
font-weight:bold;
color:#0A2E6B;">
Intake Monitoring System
</div>
""", unsafe_allow_html=True)

st.caption("Real-time monitoring of floating debris and plastic load at Moharda Intake")
model = YOLO("best.pt")
def cleaning_frequency(load_percent):

    if load_percent < 5:
        return "Weekly Cleaning", "Low"

    elif load_percent < 15:
        return "Twice a Week", "Moderate"

    elif load_percent < 30:
        return "Every Alternate Day", "Medium"

    elif load_percent < 50:
        return "Daily Cleaning", "High"

    else:
        return "Immediate Cleaning Required", "Critical"
uploaded_file = st.file_uploader(
    "Upload Intake Image",
    type=["jpg","jpeg","png"]
)

if uploaded_file:

    image = Image.open(uploaded_file)

    st.image(
        image,
        caption="Uploaded Intake Image",
        use_container_width=True
    )

    if st.button("🚀 Run Diagnosis"):

        with st.spinner(
            "AI Model Analyzing Plastic Accumulation..."
        ):

            frame = np.array(image)

            if len(frame.shape) == 2:
                frame = cv2.cvtColor(
                    frame,
                    cv2.COLOR_GRAY2RGB
                )

            frame_bgr = cv2.cvtColor(
                frame,
                cv2.COLOR_RGB2BGR
            )

            h, w = frame_bgr.shape[:2]

            results = model.predict(
                frame_bgr,
                conf=0.25,
                verbose=False
            )

            # ==========================
            # DISPLAY SEGMENTATION
            # ==========================

            plotted = results[0].plot()

            # ==========================
            # AREA CALCULATION
            # ==========================

            plastic_pixels = 0

            for result in results:

                if result.masks is not None:

                    masks = result.masks.data.cpu().numpy()

                    for mask in masks:

                        mask = cv2.resize(
                            mask,
                            (w, h)
                        )

                        binary_mask = (
                            mask > 0.5
                        ).astype(np.uint8)

                        plastic_pixels += np.sum(
                            binary_mask
                        )

            total_pixels = h * w

            load_percent = (
                plastic_pixels /
                total_pixels
            ) * 100

            recommendation, risk = cleaning_frequency(
                load_percent
            )

        st.success(
            "Diagnosis Completed Successfully"
        )

        st.image(
            plotted,
            caption="AI Segmentation Result",
            use_container_width=True
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Plastic Load (%)",
                f"{load_percent:.2f}"
            )

        with col2:
            st.metric(
                "Risk Level",
                risk
            )

        with col3:
            st.metric(
                "Plastic Pixels",
                f"{plastic_pixels:,}"
            )

        st.subheader(
            "🧹 Cleaning Recommendation"
        )

        st.success(
            f"Recommended Frequency: {recommendation}"
        )

        if load_percent > 50:

            st.error(
                "🚨 Critical Plastic Accumulation Detected. Immediate Cleaning Recommended."
            )

        elif load_percent > 30:

            st.warning(
                "⚠ High Plastic Accumulation Detected."
            )

        elif load_percent > 15:

            st.info(
                "🔍 Moderate Plastic Accumulation Detected."
            )

        else:

            st.success(
                "✅ Plastic Load Within Acceptable Range."
            )

        with st.expander(
            "Technical Details"
        ):

            st.write(
                "Image Resolution:",
                f"{w} x {h}"
            )

            st.write(
                "Plastic Pixels:",
                plastic_pixels
            )

            st.write(
                "Total Pixels:",
                total_pixels
            )

            st.write(
                "Load Percentage:",
                round(load_percent, 2)
            )

            st.write(
                "Model Classes:",
                model.names
            )


# 🖥️ WATER QUALITY - ADVANCED PRACTICAL VERSION
# Added: Pre-Chlorination + Oily Water Logic
# ==========================================

import streamlit as st
st.markdown("""
<div style="
background:#F4F8FF;
border-left:8px solid #0A2E6B;
padding:15px;
border-radius:8px;
font-size:24px;
font-weight:bold;
color:#0A2E6B;">
Water Treatment Assistant
</div>
""", unsafe_allow_html=True)
st.caption("Complaint analysis and troubleshooting support")

# ===============================
# STEP 1: COMPLAINT
# ===============================

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
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Clariflocculator SCADA",
    layout="wide"
)

# ==========================
# LOAD EXCEL
# ==========================

df = pd.read_excel(
    "Clariflocculator Running Status.xlsx"
)

# ==========================
# LIGHT SCADA THEME
# ==========================

st.markdown("""
<style>

.stApp{
    background:#f4f6f8;
}

.block-container{
    padding-top:1rem;
}

.scada-card{
    background:white;
    border-radius:15px;
    padding:20px;
    box-shadow:0px 2px 8px rgba(0,0,0,0.15);
}

.tank{
    width:280px;
    height:280px;
    border:10px solid #2F80ED;
    border-radius:50%;
    position:relative;
    margin:auto;
    background:#dceeff;
}

.bridge{
    position:absolute;
    top:50%;
    left:50%;
    width:200px;
    height:8px;
    background:#444;
}

.running{
    animation:rotate 8s linear infinite;
    transform-origin:center center;
    transform:translate(-50%,-50%);
}

.stopped{
    transform:translate(-50%,-50%);
}

.green-light{
    width:24px;
    height:24px;
    border-radius:50%;
    background:#00C853;
    margin:auto;
    box-shadow:0 0 20px #00C853;
}

.red-light{
    width:24px;
    height:24px;
    border-radius:50%;
    background:#D50000;
    margin:auto;
    box-shadow:0 0 20px #D50000;
}

@keyframes rotate{
    from{
        transform:translate(-50%,-50%) rotate(0deg);
    }
    to{
        transform:translate(-50%,-50%) rotate(360deg);
    }
}

</style>
""", unsafe_allow_html=True)

# ==========================
# TITLE
# ==========================

st.markdown("""
<div style="
background:#F4F8FF;
border-left:8px solid #0A2E6B;
padding:15px;
border-radius:8px;
font-size:24px;
font-weight:bold;
color:#0A2E6B;">
💧 Clariflocculator Running Status
</div>
""", unsafe_allow_html=True)

# ==========================
# SIDEBAR
# ==========================

st.sidebar.header("Control Panel")

mode = st.sidebar.radio(
    "View",
    [
        "Single Location",
        "Multiple Locations"
    ],
    index=1
)

locations = sorted(df["Location"].unique())

# ==========================
# UNIT DRAW
# ==========================

def draw_unit(location):

    row = df[df["Location"] == location].iloc[0]

    bridge_status = str(
        row["Bridge Running Status"]
    ).strip()

    blowdown_status = str(
        row["Blowdown Valve Status"]
    ).strip()

    running = (
        bridge_status == "OK"
        and blowdown_status == "OK"
    )

    if not running:

        mech_msg = (
            f"{location} Clariflocculator Not Running"
        )

        if mech_msg not in st.session_state.mechanical_alarm_list:

            st.session_state.mechanical_alarm_list.append(
                mech_msg
            )

    if running:

        bridge_class = "bridge running"
        light = "green-light"
        text = "🟢 RUNNING"

    else:

        bridge_class = "bridge stopped"
        light = "red-light"
        text = "🔴 NOT RUNNING"

    problem = "-"

    if "Problem" in df.columns:
        problem = row["Problem"]

    st.markdown(
        f"""
        <div class="scada-card">

        <h2 style="text-align:center">
        {location}
        </h2>

        <div class="tank">
            <div class="{bridge_class}">
            </div>
        </div>

        <br>

        <div class="{light}"></div>

        <h3 style="text-align:center">
        {text}
        </h3>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.write(
        "**Bridge Status:**",
        bridge_status
    )

    st.write(
        "**Blowdown Valve Status:**",
        blowdown_status
    )

    st.write(
        "**Problem:**",
        problem
    )

# ==========================
# SINGLE LOCATION
# ==========================

if mode == "Single Location":

    selected_location = st.sidebar.selectbox(
        "Select Location",
        locations
    )

    draw_unit(selected_location)

# ==========================
# MULTIPLE LOCATION
# ==========================

else:

    selected_locations = st.sidebar.multiselect(
        "Select Locations",
        locations,
        default=locations
    )

    cols = st.columns(2)

    for i, loc in enumerate(selected_locations):

        with cols[i % 2]:

            draw_unit(loc)


