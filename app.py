import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import plotly.graph_objects as go

st.set_page_config(page_title="AI Smart WTP", layout="wide")

st.title("💧 AI Smart Water Treatment Monitoring System")

np.random.seed(42)
n = 1000

clar_eff = np.random.uniform(0.6, 0.9, n)
filt_eff = np.random.uniform(0.7, 0.95, n)
frc_loss = np.random.uniform(0.1, 0.6, n)
cond_change = np.random.uniform(-10, 40, n)

problem_stage = []

for i in range(n):
    if clar_eff[i] < 0.65:
        problem_stage.append("Clarifier")
    elif filt_eff[i] < 0.75:
        problem_stage.append("Filter")
    elif frc_loss[i] > 0.5:
        problem_stage.append("Distribution")
    else:
        problem_stage.append("Normal")

data = pd.DataFrame({
    'clarifier_eff': clar_eff,
    'filter_eff': filt_eff,
    'frc_loss': frc_loss,
    'cond_change': cond_change,
    'problem_stage': problem_stage
})

X = data[['clarifier_eff','filter_eff','frc_loss','cond_change']]
y = data['problem_stage']

model = RandomForestClassifier()
model.fit(X, y)

st.sidebar.header("🔧 Enter Current Plant Data")

clar_eff_input = st.sidebar.slider("Clarifier Efficiency", 0.4, 0.95, 0.75)
filt_eff_input = st.sidebar.slider("Filter Efficiency", 0.5, 0.99, 0.85)
frc_loss_input = st.sidebar.slider("FRC Loss", 0.0, 1.0, 0.3)
cond_change_input = st.sidebar.slider("Conductivity Change", -50.0, 100.0, 10.0)

input_data = pd.DataFrame([[clar_eff_input,
                            filt_eff_input,
                            frc_loss_input,
                            cond_change_input]],
                          columns=['clarifier_eff','filter_eff','frc_loss','cond_change'])

prediction = model.predict(input_data)[0]

st.subheader("📊 System Status")

if prediction == "Normal":
    st.success("🟢 SYSTEM NORMAL")
elif prediction == "Clarifier":
    st.warning("🟡 CLARIFIER ISSUE DETECTED")
elif prediction == "Filter":
    st.warning("🟠 FILTER ISSUE DETECTED")
elif prediction == "Distribution":
    st.error("🔴 DISTRIBUTION ISSUE DETECTED")

st.subheader("📈 Efficiency Trend")

time = np.arange(0, 20)
clar_trend = clar_eff_input + np.random.normal(0, 0.01, 20)
filt_trend = filt_eff_input + np.random.normal(0, 0.01, 20)

fig = go.Figure()
fig.add_trace(go.Scatter(x=time, y=clar_trend, mode='lines', name='Clarifier'))
fig.add_trace(go.Scatter(x=time, y=filt_trend, mode='lines', name='Filter'))

fig.update_layout(template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)
