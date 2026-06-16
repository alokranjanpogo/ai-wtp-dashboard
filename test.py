import streamlit as st
import onnxruntime as ort

st.title("ONNX Test")

@st.cache_resource
def load_model():
    return ort.InferenceSession(
        "best.onnx",
        providers=["CPUExecutionProvider"]
    )

session = load_model()

st.success("✅ ONNX Model Loaded Successfully")

st.write("Inputs:")
for inp in session.get_inputs():
    st.write(inp.name, inp.shape)

st.write("Outputs:")
for out in session.get_outputs():
    st.write(out.name, out.shape)
