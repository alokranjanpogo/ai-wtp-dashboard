import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import datetime

st.set_page_config(page_title="WTP Moharda SCADA", layout="wide")

st.title("🏭 WTP Moharda – AI Smart Monitoring System")
st.markdown(f"### ⏱ {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")

# =====================================================
# SAFE DATA LOADING
# =====================================================
try:
    data = pd.read_excel("Gis Data.xlsx", engine="openpyxl")
except Exception as e:
    st.error(f"Error loading Excel file: {e}")
    st.stop()

data.columns = data.columns.str.strip()

# Safe column finder
def find_col(keyword):
    for col in data.columns:
        if keyword.lower() in col.lower():
            return col
    return None

turb_col = find_col("turb")
frc_col = find_col("frc")
lat_col = find_col("lat")
lon_col = find_col("lon")
name_col = find_col("cust")
date_col = find_col("date")

if turb_col is None or frc_col is None:
    st.error("Required turbidity or FRC column not found in Excel.")
    st.write("Available columns:", data.columns)
    st.stop()

# Convert numeric safely
data[turb_col] = pd.to_numeric(data[turb_col], errors="coerce")
data[frc_col] = pd.to_numeric(data[frc_col], errors="coerce")
data = data.dropna(subset=[turb_col, frc_col])

consumer_turb = data[turb_col].mean()
consumer_frc = data[frc_col].mean()

# =====================================================
# ASSUMED PLANT VALUES
# =====================================================
intake_turb = 11
clarifier_turb = intake_turb * 0.35
filter_turb = clarifier_turb * 0.2
sump_frc = 1.0

clar_eff = (intake_turb - clarifier_turb) / intake_turb
filter_eff = (clarifier_turb - filter_turb) / clarifier_turb
frc_loss = sump_frc - consumer_frc

# =====================================================
# STATUS COLOR FUNCTION
# =====================================================
def get_color(value, good, warn):
    if value >= good:
        return "green"
    elif value >= warn:
        return "orange"
    else:
        return "red"

clar_color = get_color(clar_eff, 0.65, 0.60)
filter_color = get_color(filter_eff, 0.80, 0.75)

if frc_loss <= 0.4:
    dist_color = "green"
elif frc_loss <= 0.6:
    dist_color = "orange"
else:
    dist_color = "red"

# =====================================================
# DRAW PROCESS DIAGRAM
# =====================================================
st.subheader("🏗 WTP Process Flow Diagram")

fig = go.Figure()

def add_box(x0, y0, x1, y1, text, color):
    fig.add_shape(type="rect",
                  x0=x0, y0=y0, x1=x1, y1=y1,
                  line=dict(color="black", width=2),
                  fillcolor=color)
    fig.add_annotation(x=(x0+x1)/2,
                       y=(y0+y1)/2,
                       text=text,
                       showarrow=False,
                       font=dict(size=11, color="white"))

def add_circle(x0, y0, x1, y1, text, color):
    fig.add_shape(type="circle",
                  x0=x0, y0=y0, x1=x1, y1=y1,
                  line=dict(color="black", width=2),
                  fillcolor=color)
    fig.add_annotation(x=(x0+x1)/2,
                       y=(y0+y1)/2,
                       text=text,
                       showarrow=False,
                       font=dict(size=11, color="white"))

# Units
add_box(0, 2, 2, 3.5, "Raw Water", "blue")
add_box(3, 2.2, 5, 3.3, "Mixing", "green")
add_circle(6, 1.8, 9, 4, "Clariflocculator", clar_color)
add_box(10, 2, 12, 3.5, "Filter Bed", filter_color)
add_box(13, 2, 15, 3.5, "Sump", dist_color)
add_box(16, 2, 18, 3.5, "Pump House", dist_color)
add_box(19, 2, 21, 3.5, "Water Tower", dist_color)

def arrow(x0, y0, x1, y1):
    fig.add_annotation(x=x1, y=y1,
                       ax=x0, ay=y0,
                       xref="x", yref="y",
                       axref="x", ayref="y",
                       showarrow=True,
                       arrowhead=3,
                       arrowwidth=2)

arrow(2, 2.75, 3, 2.75)
arrow(5, 2.75, 6, 2.75)
arrow(9, 2.75, 10, 2.75)
arrow(12, 2.75, 13, 2.75)
arrow(15, 2.75, 16, 2.75)
arrow(18, 2.75, 19, 2.75)

fig.update_xaxes(visible=False)
fig.update_yaxes(visible=False)
fig.update_layout(height=450)

st.plotly_chart(fig, use_container_width=True)

# =====================================================
# DATE-WISE TURBIDITY TREND
# =====================================================
st.subheader("📈 Date-wise Customer Turbidity Trend")

if date_col:
    data[date_col] = pd.to_datetime(data[date_col], errors="coerce")
    trend = data.groupby(date_col)[turb_col].mean().reset_index()
    fig2 = px.line(trend, x=date_col, y=turb_col)
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("No Date column found in Excel.")

# =====================================================
# GIS MAP
# =====================================================
if lat_col and lon_col:
    st.subheader("📍 Customer-End Risk Map")

    def risk(row):
        if row[frc_col] < 0.2 or row[turb_col] > 1.5:
            return "High Risk"
        elif row[frc_col] < 0.3:
            return "Moderate"
        else:
            return "Safe"

    data["Risk"] = data.apply(risk, axis=1)

    fig3 = px.scatter_mapbox(
        data,
        lat=lat_col,
        lon=lon_col,
        color="Risk",
        hover_name=name_col,
        zoom=12,
        height=500,
        color_discrete_map={
            "Safe": "green",
            "Moderate": "orange",
            "High Risk": "red"
        }
    )

    fig3.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("Latitude / Longitude columns not found.")

# =====================================================
# ALARM PANEL
# =====================================================
st.subheader("🚨 Alarm Panel")

if clar_color == "red":
    st.error("Clarifier Efficiency Critical")
if filter_color == "red":
    st.error("Filter Efficiency Critical")
if dist_color == "red":
    st.error("Distribution Issue")
if clar_color == filter_color == dist_color == "green":
    st.success("Plant Operating Normally")



    





