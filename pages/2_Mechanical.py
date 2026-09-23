import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Clariflocculator SCADA",
    layout="wide"
)

# ==========================
# LOAD EXCEL
# ==========================

df = pd.read_excel(
    "Clariflocculator Running Status.xlsx"
)

# ==========================
# LIGHT SCADA THEME
# ==========================

st.markdown("""
<style>

.stApp{
    background:#f4f6f8;
}

.block-container{
    padding-top:1rem;
}

.scada-card{
    background:white;
    border-radius:15px;
    padding:20px;
    box-shadow:0px 2px 8px rgba(0,0,0,0.15);
}

.tank{
    width:280px;
    height:280px;
    border:10px solid #2F80ED;
    border-radius:50%;
    position:relative;
    margin:auto;
    background:#dceeff;
}

.bridge{
    position:absolute;
    top:50%;
    left:50%;
    width:200px;
    height:8px;
    background:#444;
}

.running{
    animation:rotate 8s linear infinite;
    transform-origin:center center;
    transform:translate(-50%,-50%);
}

.stopped{
    transform:translate(-50%,-50%);
}

.green-light{
    width:24px;
    height:24px;
    border-radius:50%;
    background:#00C853;
    margin:auto;
    box-shadow:0 0 20px #00C853;
}

.red-light{
    width:24px;
    height:24px;
    border-radius:50%;
    background:#D50000;
    margin:auto;
    box-shadow:0 0 20px #D50000;
}

@keyframes rotate{
    from{
        transform:translate(-50%,-50%) rotate(0deg);
    }
    to{
        transform:translate(-50%,-50%) rotate(360deg);
    }
}

</style>
""", unsafe_allow_html=True)

# ==========================
# TITLE
# ==========================
st.markdown("""
<div style="
background:#F4F8FF;
border-left:8px solid #0A2E6B;
padding:15px;
border-radius:8px;
font-size:24px;
font-weight:bold;
color:#0A2E6B;">
💧 Clariflocculator Running Status
</div>
""", unsafe_allow_html=True)

# ==========================
# SIDEBAR
# ==========================

st.sidebar.header("Control Panel")

mode = st.sidebar.radio(
    "View",
    [
        "Single Location",
        "Multiple Locations"
    ],
    index=1
)

locations = sorted(df["Location"].unique())

# ==========================
# UNIT DRAW
# ==========================

def draw_unit(location):

    row = df[df["Location"] == location].iloc[0]

    bridge_status = str(
        row["Bridge Running Status"]
    ).strip().upper()

    blowdown_status = str(
        row["Blowdown Valve Status"]
    ).strip().upper()

    running = (
        bridge_status == "OK"
        and blowdown_status == "OK"
    )

    if not running:

        mech_msg = (
            f"{location} Clariflocculator Not Running"
        )

        if mech_msg not in st.session_state.mechanical_alarm_list:

            st.session_state.mechanical_alarm_list.append(
                mech_msg
            )

    if running:

        bridge_class = "bridge running"
        light = "green-light"
        text = "🟢 RUNNING"

    else:

        bridge_class = "bridge stopped"
        light = "red-light"
        text = "🔴 NOT RUNNING"

    problem = "-"

    if "Problem" in df.columns:
        problem = row["Problem"]

    st.markdown(
        f"""
        <div class="scada-card">

        <h2 style="text-align:center">
        {location}
        </h2>

        <div class="tank">
            <div class="{bridge_class}">
            </div>
        </div>

        <br>

        <div class="{light}"></div>

        <h3 style="text-align:center">
        {text}
        </h3>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.write(
        "**Bridge Status:**",
        bridge_status
    )

    st.write(
        "**Blowdown Valve Status:**",
        blowdown_status
    )

    st.write(
        "**Problem:**",
        problem
    )
   
# ==========================
# SINGLE LOCATION
# ==========================

if mode == "Single Location":

    selected_location = st.sidebar.selectbox(
        "Select Location",
        locations
    )

    draw_unit(selected_location)

# ==========================
# MULTIPLE LOCATION
# ==========================

else:

    selected_locations = st.sidebar.multiselect(
        "Select Locations",
        locations,
        default=locations
    )

    cols = st.columns(2)

    for i, loc in enumerate(selected_locations):

        with cols[i % 2]:

            draw_unit(loc)


