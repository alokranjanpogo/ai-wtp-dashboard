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
# ===============================
# AUTO REFRESH
# ===============================
st.set_page_config(page_title="WTP Moharda SCADA", layout="wide")
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
        random.uniform(1088, 1112),
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
    
    # Filter beds
    
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
st.title("🏭 WTP MOHARDA – LIVE HMI PANEL")
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

production_mld = 18 # value can vary between 18–23
production_m3_hr = 1100
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

    if len(history_df) > 1:

        selected_time = st.select_slider(

            "Select Date",

            options=history_df["DateTime"],

            value=history_df["DateTime"].iloc[-1]

        )

    else:

        selected_time = history_df[
            "DateTime"
        ].iloc[0]

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

    with d2:

        end_date = st.date_input(

            "End Date",

            value=df["Date"].max()

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
# SMART CLARIFIER + FILTER BED MONITORING SYSTEM
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
📊 Smart Clarifier & Filter Bed Monitoring
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
# STATIC DATE FILTER
# ============================================================

if monitor_mode == "📊 Static Monitoring":

    selected_date = st.date_input(

        "Select Monitoring Date",

        value=trend_df["Date"].max()

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
st.subheader("🌀 Clarifier Live Monitoring")

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

if clar_outlet <= 5:

    clar_health = "🟢 Healthy"

elif clar_outlet <= 10:

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

st.markdown("###### Analysis")

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
# FILTER BED SECTION
# ============================================================

st.markdown("---")
st.subheader("🧪 Filter Bed Live Status")

cols = st.columns(6)

filter_summary = []

alarm_triggered = False

for i in range(1,7):

    filter_name = f"Filter Bed {i}"

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
    filter_summary.append({

        "Filter Bed": filter_name,

        "Outlet Turbidity": round(
            filter_outlet,
            2
        ),

        "Status": status

    })
    if filter_outlet > 4.5 or status == "🔴 Backwash Needed":

        st.error(f"🚨 FILTER ALARM : {filter_name}")
    
        col1, col2 = st.columns([4,1])
    
        with col2:
            if st.button(
                "🔕 Stop Filter Alarm",
                key=f"stop_alarm_{filter_name}"
            ):
                st.session_state.filter_alarm_muted = True

    if not st.session_state.filter_alarm_muted:

        with open(
            "mixkit-sport-start-bleeps-918.wav",
            "rb"
        ) as f:

            audio_bytes = f.read()

        b64 = base64.b64encode(audio_bytes).decode()

        st.markdown(
            f"""
            <audio autoplay loop>
                <source src="data:audio/wav;base64,{b64}"
                        type="audio/wav">
            </audio>
            """,
            unsafe_allow_html=True
        )
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

if alarm_triggered:

    audio_file = open(
        "mixkit-sport-start-bleeps-918.wav",
        "rb"
    )

    audio_bytes = audio_file.read()

    b64 = base64.b64encode(
        audio_bytes
    ).decode()

    audio_html = f"""
    <audio autoplay>
    <source src="data:audio/wav;base64,{b64}" type="audio/wav">
    </audio>
    """

    st.markdown(
        audio_html,
        unsafe_allow_html=True
    )

# ============================================================
# FILTER SUMMARY
# ============================================================

st.markdown("---")
st.subheader("📋 Filter Bed Summary")

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
            {item['Filter Bed']}
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
    "Filter Bed 1",
    "Filter Bed 2",
    "Filter Bed 3",
    "Filter Bed 4",
    "Filter Bed 5",
    "Filter Bed 6"
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

    with col2:
        to_date = st.date_input(
            "To Date",
            value=trend_df["Date"].max().date(),
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
            "Filter Bed 1",
            "Filter Bed 2",
            "Filter Bed 3",
            "Filter Bed 4",
            "Filter Bed 5",
            "Filter Bed 6"
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
# ===============================
# STREAMLIT UI
# ===============================

st.set_page_config(page_title="Water Treatment Performance", layout="wide")

st.markdown("""
<div style="
background:#F4F8FF;
border-left:8px solid #0A2E6B;
padding:15px;
border-radius:8px;
font-size:31px;
font-weight:bold;
color:#0A2E6B;">
💧 Water Treatment Performance Dashboard
</div>
""", unsafe_allow_html=True)

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

st.subheader("Interpretation")

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

    selected_date = st.date_input(
        "Select Date",
        value=history_df["Date"].max()
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
# ============================================================
# Intelligent alum dosing section
# ============================================================

import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.markdown("""
<div style="
background:#F4F8FF;
border-left:8px solid #0A2E6B;
padding:15px;
border-radius:8px;
font-size:31px;
font-weight:bold;
color:#0A2E6B;">
Smart Alum Dosing Decision System
</div>
""", unsafe_allow_html=True)

# ============================================================
# INPUTS
# ============================================================

flow_mld = 18
flow_m3_day = flow_mld * 1000

turbidity = float(st.session_state.get("live_turbidity",0))

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

    if conductivity > 1200:
        severity_score += 2

    elif conductivity > 800:
        severity_score += 1

    if ph < 6 or ph > 8.5:
        severity_score += 1

    if turbidity > 250:
        severity_score += 2

    elif turbidity > 120:
        severity_score += 1

    if odor_detected:
        severity_score += 1

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
        value=5.0,
        step=1.0
    )

else:
    jar_dose = None

# ============================================================
# ALKALINITY INPUT
# ============================================================

alkalinity = st.slider(
    "Alkalinity (mg/L as CaCO3)",
    20,
    250,
    100
)

# ============================================================
# MULTIVARIABLE REGRESSION MODEL
# ============================================================

predicted_dose = (
    -1.88
    + 0.219 * turbidity
    + 1.269 * ph
    + 0.00593 * conductivity
    - 0.0301 * alkalinity
)

predicted_dose = max(predicted_dose, 5)

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
# INDUSTRIAL RISK ADJUSTMENT
# ============================================================

risk_adjustment = 0

if conductivity > 1200:
    risk_adjustment += 5

elif conductivity > 800:
    risk_adjustment += 3

if odor_detected:
    risk_adjustment += 3

if water_color == "Highly Colored":
    risk_adjustment += 5

elif water_color == "Slightly Colored":
    risk_adjustment += 2

predicted_dose += risk_adjustment

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

# ============================================================
# JAR TEST + REGRESSION HYBRID
# ============================================================

if jar_available:

    ai_dose = (
        0.80 * jar_dose
        + 0.20 * predicted_dose
    )

    if abs(jar_dose - predicted_dose) > 20:

        st.warning(
            "⚠️ Significant deviation between Jar Test and Model Prediction"
        )

else:

    ai_dose = predicted_dose
# ============================================================
# FINAL CORRECTIONS
# ============================================================

ai_dose = ai_dose * ph_factor 

ai_dose = float(np.clip(ai_dose, 5, 150))

# ============================================================
# CHEMICAL REQUIREMENT
# ============================================================

alum_kg_day = (ai_dose * flow_m3_day) / 1000

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

# ============================================================
# EXECUTIVE KPI ROW
# ============================================================

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric("Turbidity", f"{turbidity:.1f} NTU")

with k2:
    st.metric("pH", f"{ph:.1f}")

with k3:
    st.metric("Conductivity", f"{conductivity:.0f} µS/cm")

with k4:
    st.metric("Alkalinity", f"{alkalinity:.0f} mg/L")

st.markdown("---")

left, right = st.columns([1.3, 1], gap="large")
# ============================================================
# 📊 LEFT → GRAPH + METRICS
# ============================================================

with left:

    st.markdown("""
    <div style="
    background:#F4F8FF;
    border-left:8px solid #0A2E6B;
    padding:15px;
    border-radius:8px;
    font-size:24px;
    font-weight:bold;
    color:#0A2E6B;">
    🧪 Alum Dosing Recommendation System
    </div>
    """, unsafe_allow_html=True)
        
    st.markdown("")

    x = np.linspace(0, 400, 150)

    y_ai = (
    -1.88
    + 0.219 * x
    + 1.269 * ph
    + 0.00593 * conductivity
    - 0.0301 * alkalinity
)

y_ai = np.clip(y_ai, 5, 150)

fig = go.Figure()

fig.add_hrect(
    y0=0,
    y1=20,
    fillcolor="green",
    opacity=0.10,
    line_width=0
)

fig.add_hrect(
    y0=20,
    y1=40,
    fillcolor="yellow",
    opacity=0.08,
    line_width=0
)

fig.add_hrect(
    y0=40,
    y1=80,
    fillcolor="orange",
    opacity=0.08,
    line_width=0
)

fig.add_hrect(
    y0=80,
    y1=150,
    fillcolor="red",
    opacity=0.06,
    line_width=0
)    
# ========================================================
# AI CURVE
# ========================================================

fig.add_trace(go.Scatter(
    x=x,
    y=y_ai,
    line=dict(
        color="#0A66C2",
        width=5
    ),
    name="Regression Model"
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
    template="plotly_white",
    height=500,

    margin=dict(
        l=10,
        r=10,
        t=35,
        b=10
    ),

    xaxis_title="Turbidity (NTU)",
    yaxis_title="Alum Dose (mg/L)",
    showlegend=False
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={"displayModeBar": False}
)

st.markdown("### 📌 Decision Indicators")

d1,d2,d3,d4 = st.columns(4)

with d1:
    st.metric(
        "Recommended Dose",
        f"{ai_dose:.1f} mg/L"
    )

with d2:
    st.metric(
        "Alum Required",
        f"{alum_kg_day:,.0f} kg/day"
    )

with d3:
    st.metric(
        "Confidence",
        f"{confidence}%"
    )

with d4:
    st.metric(
        "Risk Level",
        raw_risk
    )

    summary_df = pd.DataFrame({
    "Parameter":[
        "Turbidity",
        "pH",
        "Conductivity",
        "Alkalinity"
    ],
    "Value":[
        f"{turbidity:.1f} NTU",
        f"{ph:.1f}",
        f"{conductivity:.0f} µS/cm",
        f"{alkalinity:.0f} mg/L"
    ]
})

st.table(summary_df)
# ========================================================
# INDUSTRIAL SUMMARY
# ========================================================

if industrial:

    st.markdown(f"""
### 🏭 Industrial Assessment

| Parameter | Status |
|---|---|
| Discharge Type | **{industrial_type}** |
| Conductivity | **{conductivity} µS/cm** |
| Water Appearance | **{water_color}** |
| Odor Detected | **{"Yes" if odor_detected else "No"}** |
| Severity | **{severity_label} ({discharge_level}/5)** |
| Risk Adjustment | **{risk_adjustment:.1f} mg/L** |
""")
st.markdown(f"""
### 📐 Multivariable Regression Prediction

| Parameter | Value |
|---|---|
| Turbidity | **{turbidity:.1f} NTU** |
| pH | **{ph:.2f}** |
| Conductivity | **{conductivity:.0f} µS/cm** |
| Alkalinity | **{alkalinity:.0f} mg/L** |

### Predicted Dose

## {predicted_dose:.1f} mg/L
""")


# ========================================================
# JAR TEST STATUS
# ========================================================

if jar_available:

    st.success(
        f"🧪 Jar Test Integrated: {jar_dose:.1f} mg/L"
    )

else:

    st.warning(
        "⚠️ Jar Test not used — relying on regression prediction"
    )

# ========================================================
# FINAL RECOMMENDATION
# ========================================================

st.markdown(f"""
<div style="
background:#F8FAFC;
border-left:6px solid #22C55E;
padding:18px;
border-radius:10px;
margin-top:15px;">

<h3 style="
margin:0;
color:#166534;
font-size:24px;
font-weight:700;">
✅ Final Recommendation
</h3>

<p style="
font-size:30px;
font-weight:700;
color:#0A2E6B;
margin-top:10px;
margin-bottom:10px;">
{predicted_dose:.1f} mg/L Alum Dose
</p>

<p style="
font-size:15px;
color:#666;
margin:0;">
pH Factor: 1.00 &nbsp;&nbsp;|&nbsp;&nbsp;
Risk Adjustment: 0.0 mg/L &nbsp;&nbsp;|&nbsp;&nbsp;
Source: Regression Model
</p>

</div>
""", unsafe_allow_html=True)
st.markdown(f"""
### Expected Outcomes

- Optimized coagulant utilization
- Improved floc formation
- Better sedimentation performance
- Reduced filter loading
- Enhanced treated water quality

### Chemical Requirement

- Alum Requirement:

**{alum_kg_day:,.0f} kg/day**

- PAC Equivalent Dose:

**{pac_dose:.1f} mg/L**

### AI Confidence

🎯 **{confidence}%**

""")
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

    sender = "alokranjan18april@gmail.com"
    password = "wpnrabqfbtkhsqpe"

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
    "hypo_dose",
    "outlet_turbidity",
    "final_turbidity",
    "frc",
    "status"


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
            50.0
        )

        alum_dose = st.slider(
            "Alum Dose (mg/L)",
            0.0,
            100.0,
            15.0
        )

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
        "hypo_dose": hypo_dose,

        "outlet_turbidity": outlet_turbidity,

        "final_turbidity": final_turbidity,

        "frc": frc,

        "status": status

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

    df.to_csv(FILE, index=False, encoding='utf-8-sig')

    st.success("✅ Feedback Stored Successfully")

    st.info(f"📦 Total Samples Stored: {len(df)}")

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

    if (

        final_turbidity > 1

        or

        frc < 0.2

        or

        outlet_turbidity > 10

    ):

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

    m1, m2, m3, m4 = st.columns(4)

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
            "Avg Final Turbidity",
            f"{df['final_turbidity'].mean():.2f}"
        )

    with m4:

        efficiency = (

            len(
                df[
                    df["final_turbidity"] <= 1
                ]
            )

            /

            len(df)

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

st.subheader("📂 Stored Feedback Data")

if st.checkbox("Show Stored Data"):

    st.dataframe(

        df.sort_values(
            by="timestamp",
            ascending=False
        ),

        use_container_width=True

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

st.markdown("""
<div style="
background:#F4F8FF;
border-left:8px solid #0A2E6B;
padding:15px;
border-radius:8px;
font-size:31px;
font-weight:bold;
color:#0A2E6B;">
🌦️ Weather Based Prediction System
</div>
""", unsafe_allow_html=True)

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
# FUTURE DOSING PREDICTION ENGINE (FULLY CORRECTED)
# ========================================================

import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ========================================================
# SAFETY CHECKS
# ========================================================

required_columns = ["Rain", "Humidity", "Temp"]

for col in required_columns:

    if col not in weather_df.columns:

        weather_df[col] = 0

# ========================================================
# RAW TURBIDITY SAFETY
# ========================================================

try:
    raw_turbidity
except NameError:
    raw_turbidity = 50

# ========================================================
# RESET INDEX
# ========================================================

weather_df = weather_df.reset_index(drop=True)

# ========================================================
# TIME SERIES GENERATION
# ========================================================

weather_df["DateTime"] = pd.date_range(
    start=datetime.now(),
    periods=int(len(weather_df)),
    freq="3h"
)

# ========================================================
# SCIENTIFIC HYPOCHLORITE FORECAST
# ========================================================

# Baseline dose from Dynamic Hypochlorite Dosing System

current_hypo_dose = dose_selected

# Current live temperature from weather panel

current_temp = temperature

# Temperature coefficient for chlorine decay

theta = 1.04

# ========================================================
# FUTURE HYP OCHLORITE REQUIREMENT
# ========================================================

weather_df["Pred Chlorine"] = (

    current_hypo_dose *

    (

        theta ** (

            weather_df["Temp"] - current_temp

        )

    )

)

# ========================================================
# LIMIT EXTREME VALUES
# ========================================================

weather_df["Pred Chlorine"] = weather_df[
    "Pred Chlorine"
].clip(

    lower=current_hypo_dose * 0.70,

    upper=current_hypo_dose * 1.50

)
# ========================================================
# WEATHER RISK SCORE
# ========================================================

risk_score = int(

    (

        weather_df["Rain"].mean() * 3

        +

        weather_df["Humidity"].mean() * 0.4

        +

        weather_df["Temp"].mean() * 0.8

    )

)

risk_score = max(0, min(risk_score, 100))

# ========================================================
# FUTURE DOSING TREND
# ========================================================

with left:

   st.markdown("""
    <div style="
    background:#F4F8FF;
    border-left:8px solid #0A2E6B;
    padding:15px;
    border-radius:8px;
    font-size:24px;
    font-weight:bold;
    color:#0A2E6B;">
    📈 Weather-Adjusted Hypochlorite Requirement
    </div>
    """, unsafe_allow_html=True)
    
fig = go.Figure()

    
    # ====================================================
    # CHLORINE TREND
    # ====================================================

fig.add_trace(go.Scatter(

    x=weather_df["DateTime"],

    y=weather_df["Pred Chlorine"],

    mode='lines+markers',

    name='Weather Adjusted Hypochlorite Requirement',

    line=dict(
        width=4,
        color="red"
    ),

    marker=dict(
        size=8,
        color="red"
    )

))
# ====================================================
# RAINFALL OVERLAY
# ====================================================

fig.add_trace(go.Bar(

    x=weather_df["DateTime"],

    y=weather_df["Rain"],

    name='Rainfall',

    opacity=0.20

))
              

# ====================================================
# GRAPH SETTINGS
# ====================================================

fig.update_layout(

    height=350,

    template="plotly_white",

    hovermode="x unified",

    margin=dict(
        l=5,
        r=5,
        t=40,
        b=5
    ),

    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),

    xaxis_title="Forecast Time",

    yaxis_title="Predicted Chemical Dose",

    xaxis=dict(
        tickformat="%H:%M",
        tickmode="linear",
        dtick=10800000,
        tickangle=-45
    )

)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ========================================================
# WEATHER RISK GAUGE
# ========================================================

with right:

    fig2 = go.Figure(go.Indicator(

        mode="gauge+number",

        value=risk_score,

        title={'text': "Weather Risk"},

        gauge={

            'axis': {'range': [0, 100]},

            'bar': {'color': "cyan"},

            'steps': [

                {'range': [0, 30], 'color': "lightgreen"},

                {'range': [30, 70], 'color': "yellow"},

                {'range': [70, 100], 'color': "red"}

            ]

        }

    ))

    fig2.update_layout(

        height=230,

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

st.subheader("✅ Smart Decision Summary")

c1, c2, c3 = st.columns(3)

# ========================================================
# CURRENT DOSE
# ========================================================

with c1:

    st.metric(
        "Current Hypochlorite Dose",
        f"{dose_selected:.1f} kg/day"
    )

# ========================================================
# PEAK FORECAST REQUIREMENT
# ========================================================

with c2:

    st.metric(
        "Peak Forecast Requirement",
        f"{weather_df['Pred Chlorine'].max():.1f} kg/day"
    )

# ========================================================
# WEATHER RISK STATUS
# ========================================================

with c3:

    if risk_score > 60:

        st.error("🔴 High Impact")

    elif risk_score > 30:

        st.warning("🟡 Moderate")

    else:

        st.success("🟢 Stable")

# ========================================================
# SYSTEM INTERPRETATION
# ========================================================

if risk_score > 60:

    st.error(

        "⚠️ Severe weather instability detected. "
        "High probability of turbidity fluctuation "
        "and increased chemical demand."

    )

elif risk_score > 30:

    st.warning(

        "⚠️ Moderate weather influence detected. "
        "Operator monitoring and dosing adjustments "
        "may be required."

    )

else:

    st.success(

        "✅ Weather conditions are operationally stable. "
        "Normal treatment performance expected."

    )

# ==========================================================
# CUSTOMER END GIS MAP
# ==========================================================

st.markdown("---")
st.subheader("📍 Customer End GIS Map")

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

    if gis_filtered.empty:

        st.warning(
            "No locations found for selected status."
        )

    else:

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
        fig_map = px.scatter_mapbox(
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
            mapbox_style="open-street-map",
            mapbox=dict(
                center=dict(
                    lat=center_lat,
                    lon=center_lon
                )
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
# ==========================================================
# WATER QUALITY EXECUTIVE DASHBOARD - PART 1
# HEADER + KPI + WQI GAUGE
# ==========================================================

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

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
Moharda Water Supply Monitoring System
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
        index=0
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
# WATER QUALITY EXECUTIVE DASHBOARD - PART 3
# ALERTS & NOTIFICATIONS
# ==========================================================

st.markdown("### 🚨 Alerts & Notifications")

# ==========================================================
# ALERT CALCULATIONS
# ==========================================================

high_turb_df = wq[
    wq["Turbidity"] > 1
]

low_frc_df = wq[
    wq["FRC_PPM"] < 0.2
]

total_coli_df = wq[
    wq["Total_Coli"]
    .astype(str)
    .str.lower()
    == "present"
]

faecal_coli_df = wq[
    wq["Faecal_Col"]
    .astype(str)
    .str.lower()
    == "present"
]

poor_rating_df = wq[
    pd.to_numeric(
        wq["Rating"],
        errors="coerce"
    ) < 2
]

# ==========================================================
# ALERT COUNTERS
# ==========================================================

a1,a2,a3,a4,a5 = st.columns(5)

a1.metric(
    "High Turbidity",
    len(high_turb_df)
)

a2.metric(
    "Low FRC",
    len(low_frc_df)
)

a3.metric(
    "Total Coliform",
    len(total_coli_df)
)

a4.metric(
    "Faecal Coliform",
    len(faecal_coli_df)
)

a5.metric(
    "Poor Rating",
    len(poor_rating_df)
)

st.markdown("---")

# ==========================================================
# ALERT PANELS
# ==========================================================

left_alert,right_alert = st.columns(2)

# ==========================================================
# CRITICAL ALERTS
# ==========================================================

with left_alert:

    st.markdown(
        "#### 🔴 Critical Alerts"
    )

    if len(total_coli_df) > 0:

        for _,row in total_coli_df.head(10).iterrows():

            st.error(
                f"""
                Total Coliform Present

                📍 {row['Cust_Name_']}
                """
            )

    if len(faecal_coli_df) > 0:

        for _,row in faecal_coli_df.head(10).iterrows():

            st.error(
                f"""
                Faecal Coliform Present

                📍 {row['Cust_Name_']}
                """
            )

# ==========================================================
# OBSERVATION ALERTS
# ==========================================================

with right_alert:

    st.markdown(
        "#### 🟡 Observation Alerts"
    )

    if len(high_turb_df) > 0:

        for _,row in high_turb_df.head(5).iterrows():

            st.warning(
                f"""
                High Turbidity
                ({row['Turbidity']})

                📍 {row['Cust_Name_']}
                """
            )

    if len(low_frc_df) > 0:

        for _,row in low_frc_df.head(5).iterrows():

            st.warning(
                f"""
                Low FRC
                ({row['FRC_PPM']})

                📍 {row['Cust_Name_']}
                """
            )

# ==========================================================
# SYSTEM STATUS
# ==========================================================

critical_count = (
    len(total_coli_df)
    +
    len(faecal_coli_df)
)

if critical_count == 0:

    st.success(
        "✅ System Status : Healthy"
    )

elif critical_count <= 5:

    st.warning(
        "⚠️ System Status : Moderate Risk"
    )

else:

    st.error(
        "🚨 System Status : Critical"
    )

st.markdown("<br>", unsafe_allow_html=True)
# ==========================================================
# WATER QUALITY EXECUTIVE DASHBOARD - PART 4
# FAILURE CONTRIBUTION ANALYSIS
# ==========================================================

st.markdown("### 🥧 Failure Contribution Analysis")

# ==========================================================
# FAILURE COUNTS
# ==========================================================

turb_fail = len(
    wq[wq["Turbidity"] > 1]
)

frc_fail = len(
    wq[wq["FRC_PPM"] < 0.2]
)

total_coli_fail = len(
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

ph_fail = len(
    wq[
        (wq["PH"] < 6.5)
        |
        (wq["PH"] > 8.5)
    ]
)

# ==========================================================
# DONUT + SUMMARY
# ==========================================================

left_donut,right_donut = st.columns([2,1])

with left_donut:

    fig_donut = go.Figure(
        data=[
            go.Pie(
                labels=[
                    "Turbidity",
                    "Low FRC",
                    "Total Coliform",
                    "Faecal Coliform",
                    "pH"
                ],
                values=[
                    turb_fail,
                    frc_fail,
                    total_coli_fail,
                    faecal_fail,
                    ph_fail
                ],
                hole=0.60,
                textinfo="label+percent"
            )
        ]
    )

    fig_donut.update_layout(
        height=420,
        title="Failure Contribution Distribution",
        margin=dict(
            l=10,
            r=10,
            t=50,
            b=10
        )
    )

    st.plotly_chart(
        fig_donut,
        use_container_width=True
    )

with right_donut:

    st.markdown("#### Failure Summary")

    st.metric(
        "Turbidity Failures",
        turb_fail
    )

    st.metric(
        "Low FRC Cases",
        frc_fail
    )

    st.metric(
        "Total Coliform",
        total_coli_fail
    )

    st.metric(
        "Faecal Coliform",
        faecal_fail
    )

    st.metric(
        "pH Deviation",
        ph_fail
    )

    failure_dict = {
        "Turbidity": turb_fail,
        "Low FRC": frc_fail,
        "Total Coliform": total_coli_fail,
        "Faecal Coliform": faecal_fail,
        "pH": ph_fail
    }

    dominant_failure = max(
        failure_dict,
        key=failure_dict.get
    )

    st.success(
        f"Dominant Issue: {dominant_failure}"
    )

st.markdown("<br>", unsafe_allow_html=True)
# ==========================================================
# WATER QUALITY EXECUTIVE DASHBOARD - PART 5
# TREND ANALYSIS
# ==========================================================

st.markdown("### 📈 Water Quality Trend Analysis")

# ==========================================================
# TREND DATA
# ==========================================================

trend_df = wq.copy()

trend_df["created_da"] = pd.to_datetime(
    trend_df["created_da"],
    errors="coerce"
)

trend_df = trend_df.sort_values("created_da")

# ==========================================================
# TABS
# ==========================================================

t1, t2, t3, t4 = st.tabs([
    "Turbidity",
    "FRC",
    "pH",
    "Rating"
])

# ==========================================================
# TURBIDITY TREND
# ==========================================================

with t1:

    fig_turb_trend = go.Figure()

    fig_turb_trend.add_trace(

        go.Scatter(

            x=trend_df["Cust_Name_"],

            y=trend_df["Turbidity"],

            mode="lines+markers",

            marker=dict(
                size=8
            ),

            line=dict(
                color="#EF4444",
                width=2,
                shape="spline"
            ),

            customdata=trend_df["created_da"],

            hovertemplate=
            "<b>%{x}</b><br>" +
            "Turbidity: %{y:.2f} NTU<br>" +
            "Date: %{customdata|%d-%b-%Y}" +
            "<extra></extra>"
        )
    )

    fig_turb_trend.add_hline(
        y=1,
        line_dash="dash",
        line_color="green"
    )

    fig_turb_trend.update_layout(
        title="Turbidity Trend by Sampling Point",
        height=450,
        template="plotly_white",
        xaxis_title="Customer / Sampling Point",
        yaxis_title="Turbidity (NTU)"
    )

    st.plotly_chart(
        fig_turb_trend,
        use_container_width=True
    )

# ==========================================================
# FRC TREND
# ==========================================================

with t2:

    fig_frc_trend = go.Figure()

    fig_frc_trend.add_trace(

        go.Scatter(

            x=trend_df["Cust_Name_"],

            y=trend_df["FRC_PPM"],

            mode="lines+markers",

            marker=dict(
                size=8
            ),

            line=dict(
                color="#00B4D8",
                width=2,
                shape="spline"
            ),

            customdata=trend_df["created_da"],

            hovertemplate=
            "<b>%{x}</b><br>" +
            "FRC: %{y:.2f} ppm<br>" +
            "Date: %{customdata|%d-%b-%Y}" +
            "<extra></extra>"
        )
    )

    fig_frc_trend.add_hline(
        y=0.2,
        line_dash="dash",
        line_color="red"
    )

    fig_frc_trend.add_hline(
        y=1.0,
        line_dash="dash",
        line_color="green"
    )

    fig_frc_trend.update_layout(
        title="Free Residual Chlorine Trend by Sampling Point",
        height=450,
        template="plotly_white",
        xaxis_title="Customer / Sampling Point",
        yaxis_title="FRC (ppm)"
    )

    st.plotly_chart(
        fig_frc_trend,
        use_container_width=True
    )

# ==========================================================
# PH TREND
# ==========================================================

with t3:

    fig_ph_trend = go.Figure()

    fig_ph_trend.add_trace(

        go.Scatter(

            x=trend_df["Cust_Name_"],

            y=trend_df["PH"],

            mode="lines+markers",

            marker=dict(
                size=8
            ),

            line=dict(
                color="#22C55E",
                width=2,
                shape="spline"
            ),

            customdata=trend_df["created_da"],

            hovertemplate=
            "<b>%{x}</b><br>" +
            "pH: %{y:.2f}<br>" +
            "Date: %{customdata|%d-%b-%Y}" +
            "<extra></extra>"
        )
    )

    fig_ph_trend.add_hline(
        y=6.5,
        line_dash="dash",
        line_color="red"
    )

    fig_ph_trend.add_hline(
        y=8.5,
        line_dash="dash",
        line_color="red"
    )

    fig_ph_trend.update_layout(
        title="pH Trend by Sampling Point",
        height=450,
        template="plotly_white",
        xaxis_title="Customer / Sampling Point",
        yaxis_title="pH"
    )

    st.plotly_chart(
        fig_ph_trend,
        use_container_width=True
    )

# ==========================================================
# RATING TREND
# ==========================================================

with t4:

    fig_rating = go.Figure()

    fig_rating.add_trace(

        go.Scatter(

            x=trend_df["Cust_Name_"],

            y=trend_df["Rating"],

            mode="lines+markers",

            marker=dict(
                size=8
            ),

            line=dict(
                color="#F59E0B",
                width=2,
                shape="spline"
            ),

            customdata=trend_df["created_da"],

            hovertemplate=
            "<b>%{x}</b><br>" +
            "Rating: %{y:.1f}<br>" +
            "Date: %{customdata|%d-%b-%Y}" +
            "<extra></extra>"
        )
    )

    fig_rating.update_layout(
        title="Customer Rating Trend by Sampling Point",
        height=450,
        template="plotly_white",
        xaxis_title="Customer / Sampling Point",
        yaxis_title="Rating"
    )

    st.plotly_chart(
        fig_rating,
        use_container_width=True
    )

st.markdown("<br>", unsafe_allow_html=True)
# ==========================================================
# WATER QUALITY EXECUTIVE DASHBOARD - PART 6
# RISK RANKING & CRITICAL AREA IDENTIFICATION
# ==========================================================

st.markdown("### 🏆 Risk Ranking & Critical Area Analysis")

# ==========================================================
# RISK SCORE CALCULATION
# ==========================================================

risk_df = wq.copy()

risk_df["Turbidity_Risk"] = (
    risk_df["Turbidity"] > 1
).astype(int)

risk_df["FRC_Risk"] = (
    risk_df["FRC_PPM"] < 0.2
).astype(int)

risk_df["TotalColi_Risk"] = (
    risk_df["Total_Coli"]
    .astype(str)
    .str.lower()
    .eq("present")
).astype(int)

risk_df["Faecal_Risk"] = (
    risk_df["Faecal_Col"]
    .astype(str)
    .str.lower()
    .eq("present")
).astype(int)

risk_df["Rating_Risk"] = (
    pd.to_numeric(
        risk_df["Rating"],
        errors="coerce"
    ) < 2
).astype(int)

# Weighted Score

risk_df["Risk_Score"] = (
    risk_df["Turbidity_Risk"] * 2 +
    risk_df["FRC_Risk"] * 2 +
    risk_df["TotalColi_Risk"] * 5 +
    risk_df["Faecal_Risk"] * 5 +
    risk_df["Rating_Risk"] * 1
)

# ==========================================================
# ZONE RISK
# ==========================================================

zone_risk = (
    risk_df.groupby("Cust_Name_")
    .agg({
        "Risk_Score":"sum",
        "Turbidity":"mean",
        "FRC_PPM":"mean",
        "PH":"mean",
        "Rating":"mean"
    })
    .reset_index()
)

zone_risk = zone_risk.sort_values(
    "Risk_Score",
    ascending=False
)

# ==========================================================
# RISK CATEGORY
# ==========================================================

def risk_category(score):

    if score >= 10:
        return "🔴 Critical"

    elif score >= 5:
        return "🟡 Moderate"

    else:
        return "🟢 Safe"

zone_risk["Status"] = (
    zone_risk["Risk_Score"]
    .apply(risk_category)
)

# ==========================================================
# LAYOUT
# ==========================================================

left_rank,right_rank = st.columns([2,1])

# ==========================================================
# RANKING TABLE
# ==========================================================

with left_rank:

    st.markdown(
        "#### Risk Ranking Table"
    )

    ranking_table = zone_risk[
        [
            "Cust_Name_",
            "Risk_Score",
            "Status",
            "Turbidity",
            "FRC_PPM",
            "Rating"
        ]
    ]

    st.dataframe(
        ranking_table,
        use_container_width=True,
        height=420
    )

# ==========================================================
# TOP 5 CRITICAL AREAS
# ==========================================================

with right_rank:

    st.markdown(
        "#### Top Critical Areas"
    )

    top5 = zone_risk.head(5)

    for _,row in top5.iterrows():

        st.error(
            f"""
            📍 {row['Cust_Name_']}

            Risk Score : {row['Risk_Score']}

            Status : {row['Status']}
            """
        )

# ==========================================================
# RISK BAR CHART
# ==========================================================

fig_risk = px.bar(

    zone_risk.head(15),

    x="Cust_Name_",

    y="Risk_Score",

    color="Risk_Score",

    title="Area Risk Ranking"

)

fig_risk.update_layout(

    height=400,

    xaxis_tickangle=-45,

    margin=dict(
        l=10,
        r=10,
        t=50,
        b=10
    )
)

st.plotly_chart(
    fig_risk,
    use_container_width=True
)

st.markdown("<br>", unsafe_allow_html=True)
# ==========================================================
# WATER QUALITY EXECUTIVE DASHBOARD - PART 7
# WATER QUALITY SCORE BY ZONE
# ==========================================================

st.markdown("### 💧 Water Quality Score (WQI) by Zone")

# ==========================================================
# WQI CALCULATION
# ==========================================================

wqi_df = wq.copy()

# Turbidity Score
wqi_df["Turbidity_Score"] = wqi_df["Turbidity"].apply(
    lambda x: 25 if x <= 1 else max(0, 25 - (x*5))
)

# FRC Score
wqi_df["FRC_Score"] = wqi_df["FRC_PPM"].apply(
    lambda x: 25 if 0.2 <= x <= 1.0 else 10
)

# PH Score
wqi_df["PH_Score"] = wqi_df["PH"].apply(
    lambda x: 25 if 6.5 <= x <= 8.5 else 10
)

# Coliform Score
wqi_df["Coliform_Score"] = wqi_df["Total_Coli"].astype(str).apply(
    lambda x: 25 if x.lower() == "absent" else 0
)

# Total WQI
wqi_df["WQI"] = (
    wqi_df["Turbidity_Score"] +
    wqi_df["FRC_Score"] +
    wqi_df["PH_Score"] +
    wqi_df["Coliform_Score"]
)

# ==========================================================
# ZONE WQI
# ==========================================================

zone_wqi = (
    wqi_df.groupby("Cust_Name_")["WQI"]
    .mean()
    .reset_index()
)

zone_wqi = zone_wqi.sort_values(
    "WQI",
    ascending=False
)

# ==========================================================
# CATEGORY
# ==========================================================

def wqi_status(score):

    if score >= 90:
        return "Excellent"

    elif score >= 75:
        return "Good"

    elif score >= 60:
        return "Moderate"

    else:
        return "Poor"

zone_wqi["Category"] = (
    zone_wqi["WQI"]
    .apply(wqi_status)
)

# ==========================================================
# LAYOUT
# ==========================================================

left_wqi,right_wqi = st.columns([2,1])

# ==========================================================
# WQI BAR CHART
# ==========================================================

with left_wqi:

    fig_wqi_zone = px.bar(

        zone_wqi,

        x="Cust_Name_",

        y="WQI",

        color="WQI",

        title="Water Quality Index by Zone",

        text_auto=".1f"
    )

    fig_wqi_zone.update_layout(

        height=450,

        xaxis_tickangle=-45,

        margin=dict(
            l=10,
            r=10,
            t=50,
            b=10
        )
    )

    st.plotly_chart(
        fig_wqi_zone,
        use_container_width=True
    )

# ==========================================================
# BEST & WORST AREA
# ==========================================================

with right_wqi:

    best_area = zone_wqi.iloc[0]

    worst_area = zone_wqi.iloc[-1]

    st.success(
        f"""
        🏆 Best Area

        {best_area['Cust_Name_']}

        WQI : {best_area['WQI']:.1f}
        """
    )

    st.error(
        f"""
        ⚠ Worst Area

        {worst_area['Cust_Name_']}

        WQI : {worst_area['WQI']:.1f}
        """
    )

    st.markdown("#### Zone Status")

    for _,row in zone_wqi.head(10).iterrows():

        if row["Category"] == "Excellent":

            st.success(
                f"{row['Cust_Name_']} - {row['Category']}"
            )

        elif row["Category"] == "Good":

            st.info(
                f"{row['Cust_Name_']} - {row['Category']}"
            )

        elif row["Category"] == "Moderate":

            st.warning(
                f"{row['Cust_Name_']} - {row['Category']}"
            )

        else:

            st.error(
                f"{row['Cust_Name_']} - {row['Category']}"
            )

st.markdown("<br>", unsafe_allow_html=True)
# ==========================================================
# WATER QUALITY EXECUTIVE DASHBOARD - PART 8
# CUSTOMER SATISFACTION ANALYSIS
# ==========================================================

st.markdown("### ⭐ Customer Satisfaction Dashboard")

# ==========================================================
# CLEAN DATA
# ==========================================================

cust_df = wq.copy()

cust_df["Rating"] = pd.to_numeric(
    cust_df["Rating"],
    errors="coerce"
)

cust_df = cust_df.dropna(
    subset=["Rating"]
)

# ==========================================================
# RATING CATEGORY
# ==========================================================

def rating_category(x):

    if x >= 4:
        return "Excellent"

    elif x >= 3:
        return "Good"

    elif x >= 2:
        return "Average"

    else:
        return "Poor"

cust_df["Rating_Category"] = (
    cust_df["Rating"]
    .apply(rating_category)
)

# ==========================================================
# SUMMARY
# ==========================================================

avg_rating = round(
    cust_df["Rating"].mean(),
    2
)

excellent = len(
    cust_df[
        cust_df["Rating_Category"]
        == "Excellent"
    ]
)

good = len(
    cust_df[
        cust_df["Rating_Category"]
        == "Good"
    ]
)

average = len(
    cust_df[
        cust_df["Rating_Category"]
        == "Average"
    ]
)

poor = len(
    cust_df[
        cust_df["Rating_Category"]
        == "Poor"
    ]
)

# ==========================================================
# KPI ROW
# ==========================================================

r1,r2,r3,r4,r5 = st.columns(5)

r1.metric(
    "Avg Rating",
    avg_rating
)

r2.metric(
    "Excellent",
    excellent
)

r3.metric(
    "Good",
    good
)

r4.metric(
    "Average",
    average
)

r5.metric(
    "Poor",
    poor
)

# ==========================================================
# LAYOUT
# ==========================================================

left_rate,right_rate = st.columns([2,1])

# ==========================================================
# DONUT CHART
# ==========================================================

with left_rate:

    fig_rating_donut = go.Figure(
        data=[
            go.Pie(
                labels=[
                    "Excellent",
                    "Good",
                    "Average",
                    "Poor"
                ],
                values=[
                    excellent,
                    good,
                    average,
                    poor
                ],
                hole=0.60,
                textinfo="label+percent"
            )
        ]
    )

    fig_rating_donut.update_layout(
        title="Customer Rating Distribution",
        height=420
    )

    st.plotly_chart(
        fig_rating_donut,
        use_container_width=True
    )

# ==========================================================
# CUSTOMER PERCEPTION
# ==========================================================

with right_rate:

    st.markdown(
        "#### Customer Perception"
    )

    if "Customer_P" in cust_df.columns:

        perception = (
            cust_df["Customer_P"]
            .astype(str)
            .value_counts()
        )

        for item,count in perception.head(10).items():

            st.info(
                f"{item} : {count}"
            )

# ==========================================================
# AREA WISE CUSTOMER SATISFACTION
# ==========================================================

st.markdown(
    "#### Area-wise Customer Rating"
)

area_rating = (
    cust_df.groupby("Cust_Name_")
    ["Rating"]
    .mean()
    .reset_index()
)

fig_area_rating = px.bar(

    area_rating,

    x="Cust_Name_",

    y="Rating",

    color="Rating",

    text_auto=".1f",

    title="Average Customer Rating by Area"

)

fig_area_rating.update_layout(

    height=420,

    xaxis_tickangle=-45,

    margin=dict(
        l=10,
        r=10,
        t=50,
        b=10
    )
)

st.plotly_chart(
    fig_area_rating,
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

