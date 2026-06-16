import streamlit as st
from ultralytics import YOLO

st.title("YOLO Test")

st.write("Loading model...")

model = YOLO("best.pt")

st.success("✅ YOLO Loaded Successfully")

st.write(model.names)
