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
# RANDOMIZE
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
    zoom_start=10,
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
        tooltip=folium.Tooltip(
            f"📍 {row['Location']}",
            sticky=True
        )
    ).add_to(m)

# ============================================================
# AUTO FIT ALL POINTS
# ============================================================

bounds = [
    [
        washout["Lattitude"].min(),
        washout["Longitude"].min()
    ],
    [
        washout["Lattitude"].max(),
        washout["Longitude"].max()
    ]
]

m.fit_bounds(bounds)

# ============================================================
# DISPLAY MAP
# ============================================================

st_folium(
    m,
    width=None,
    height=650
)
