# ============================================================
# SMART CLARIFIER + Filter Bed MONITORING SYSTEM
# FINAL STATIC + DYNAMIC VERSION
# ============================================================
import streamlit as st

st.title("Clarifier Loaded")

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
