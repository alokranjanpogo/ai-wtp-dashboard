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
