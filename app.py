import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import plotly.express as px

st.set_page_config(page_title="AI Water Quality Intelligence", layout="wide")

st.title("💧 AI-Based Customer-End Water Quality Monitoring")

# Load your real Excel data
data = pd.read_excel("Gis Data.xlsx" , engine="openpyxl")

# Clean Turbidity column
data['Turbidity'] = pd.to_numeric(data['Turbidity'], errors='coerce')

# Create Risk Level
def risk_level(row):
    if row['FRC(ppm)'] < 0.2 or row['Turbidity'] > 1.5:
        return "High Risk"
    elif row['FRC(ppm)'] < 0.3:
        return "Moderate Risk"
    else:
        return "Safe"

data['Risk'] = data.apply(risk_level, axis=1)

# AI Model for Rating Prediction
features = data[['Turbidity','FRC(ppm)','PH']]
target = data['Rating']

model = RandomForestClassifier()
model.fit(features, target)

# Sidebar Input
st.sidebar.header("🔍 Predict New Sample")

turb = st.sidebar.number_input("Turbidity", value=1.0)
frc = st.sidebar.number_input("FRC (ppm)", value=0.4)
ph = st.sidebar.number_input("pH", value=7.8)

input_df = pd.DataFrame([[turb, frc, ph]],
                        columns=['Turbidity','FRC(ppm)','PH'])

pred_rating = model.predict(input_df)[0]

st.sidebar.success(f"Predicted Rating: {pred_rating}")

# Risk Output
if frc < 0.2 or turb > 1.5:
    st.sidebar.error("High Risk Water")
elif frc < 0.3:
    st.sidebar.warning("Moderate Risk Water")
else:
    st.sidebar.success("Safe Water")

# Map Visualization
st.subheader("📍 GIS Water Quality Map")

color_map = {
    "Safe": "green",
    "Moderate Risk": "orange",
    "High Risk": "red"
}

fig = px.scatter_mapbox(
    data,
    lat="Latitude",
    lon="Longitude",
    hover_name="Cust.Name/Public Hydrant",
    color="Risk",
    color_discrete_map=color_map,
    zoom=12,
    height=500
)

fig.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig, use_container_width=True)

# Show Data Table
st.subheader("📊 Sample Data Overview")
st.dataframe(data[['Cust.Name/Public Hydrant','Turbidity','FRC(ppm)','PH','Risk','Rating']])
