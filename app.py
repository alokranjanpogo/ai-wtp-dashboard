import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import plotly.express as px

st.set_page_config(page_title="AI Water Quality Intelligence", layout="wide")
st.title("💧 AI-Based Customer-End Water Quality Monitoring")

# ===============================
# LOAD EXCEL FILE SAFELY
# ===============================
try:
    data = pd.read_excel("Gis Data.xlsx", engine="openpyxl")
except Exception as e:
    st.error(f"Error loading file: {e}")
    st.stop()

# ===============================
# CLEAN COLUMN NAMES
# ===============================
data.columns = data.columns.str.strip()

# Show columns for safety (can remove later)
# st.write("Columns:", data.columns)

# ===============================
# AUTO-DETECT IMPORTANT COLUMNS
# ===============================
# We search for columns dynamically to avoid mismatch

def find_column(keyword):
    for col in data.columns:
        if keyword.lower() in col.lower():
            return col
    return None

turb_col = find_column("turb")
frc_col = find_column("frc")
ph_col = find_column("ph")
rating_col = find_column("rating")
lat_col = find_column("lat")
lon_col = find_column("lon")
name_col = find_column("cust")

if None in [turb_col, frc_col, ph_col, rating_col, lat_col, lon_col]:
    st.error("Required columns not found. Check Excel headers.")
    st.write("Detected columns:", data.columns)
    st.stop()

# ===============================
# CLEAN NUMERIC DATA
# ===============================
data[turb_col] = pd.to_numeric(data[turb_col], errors="coerce")
data[frc_col] = pd.to_numeric(data[frc_col], errors="coerce")
data[ph_col] = pd.to_numeric(data[ph_col], errors="coerce")

data = data.dropna(subset=[turb_col, frc_col, ph_col, rating_col])

# ===============================
# CREATE RISK LEVEL
# ===============================
def risk_level(row):
    if row[frc_col] < 0.2 or row[turb_col] > 1.5:
        return "High Risk"
    elif row[frc_col] < 0.3:
        return "Moderate Risk"
    else:
        return "Safe"

data["Risk"] = data.apply(risk_level, axis=1)

# ===============================
# TRAIN AI MODEL
# ===============================
features = data[[turb_col, frc_col, ph_col]]
target = data[rating_col]

model = RandomForestClassifier()
model.fit(features, target)

# ===============================
# SIDEBAR INPUT FOR PREDICTION
# ===============================
st.sidebar.header("🔍 Predict New Sample")

turb_input = st.sidebar.number_input("Turbidity", value=1.0)
frc_input = st.sidebar.number_input("FRC (ppm)", value=0.4)
ph_input = st.sidebar.number_input("pH", value=7.8)

input_df = pd.DataFrame([[turb_input, frc_input, ph_input]],
                        columns=[turb_col, frc_col, ph_col])

pred_rating = model.predict(input_df)[0]

st.sidebar.success(f"Predicted Rating: {pred_rating}")

# Risk indicator
if frc_input < 0.2 or turb_input > 1.5:
    st.sidebar.error("High Risk Water")
elif frc_input < 0.3:
    st.sidebar.warning("Moderate Risk Water")
else:
    st.sidebar.success("Safe Water")

# ===============================
# GIS MAP
# ===============================
st.subheader("📍 GIS Water Quality Map")

color_map = {
    "Safe": "green",
    "Moderate Risk": "orange",
    "High Risk": "red"
}

fig = px.scatter_mapbox(
    data,
    lat=lat_col,
    lon=lon_col,
    hover_name=name_col if name_col else lat_col,
    color="Risk",
    color_discrete_map=color_map,
    zoom=12,
    height=500
)

fig.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig, use_container_width=True)

# ===============================
# DATA TABLE
# ===============================
st.subheader("📊 Data Overview")
st.dataframe(data[[name_col, turb_col, frc_col, ph_col, "Risk", rating_col]])

