import pandas as pd
import numpy as np
import random
import time
from datetime import datetime
import pytz
import os

# ==========================================
# INDIA TIMEZONE
# ==========================================

ist = pytz.timezone("Asia/Kolkata")

# ==========================================
# FILE NAMES
# ==========================================

raw_file = "live_raw_water_data.xlsx"
turb_file = "live_turbidity_data.xlsx"
filter_file = "live_filterbed_data.xlsx"

# ==========================================
# CONTINUOUS LOOP
# ==========================================

while True:

    now = datetime.now(ist)

    current_date = now.strftime("%d-%m-%Y")
    current_time = now.strftime("%H:%M:%S")

    # ======================================
    # REALISTIC RAW WATER
    # ======================================

    intake_turbidity = round(random.uniform(35, 120), 2)

    aerator_turbidity = round(
        intake_turbidity * random.uniform(0.88, 0.96),
        2
    )

    conductivity = round(random.uniform(280, 420), 2)

    flow_rate = round(random.uniform(1088, 1112), 2)

    # ======================================
    # CLARIFIER STAGES
    # ======================================

    clarifier_p1 = round(aerator_turbidity * 0.75, 2)

    clarifier_p2 = round(clarifier_p1 * 0.72, 2)

    clarifier_p3 = round(clarifier_p2 * 0.65, 2)

    clarifier_p4 = round(clarifier_p3 * 0.52, 2)

    clarifier_outlet = round(
        max(clarifier_p4 * 0.45, 2.5),
        2
    )

    # ======================================
    # FILTER BEDS
    # ======================================

    filter_rows = []

    for i in range(1, 7):

        outlet = round(
            random.uniform(0.08, 0.6),
            2
        )

        filter_rows.append({

            "Date": current_date,

            "Unit": f"Filter Bed {i}",

            "Inlet Turbidity": clarifier_outlet,

            "Outlet Turbidity": outlet,

            "Conductivity (µS/cm)": conductivity

        })

    # ======================================
    # CLARIFIER ROWS
    # ======================================

    clarifier_rows = [

        {
            "Date": current_date,
            "Unit": "Clarifier Point 1",
            "Inlet Turbidity": aerator_turbidity,
            "Outlet Turbidity": clarifier_p1,
            "Conductivity (µS/cm)": conductivity
        },

        {
            "Date": current_date,
            "Unit": "Clarifier Point 2",
            "Inlet Turbidity": clarifier_p1,
            "Outlet Turbidity": clarifier_p2,
            "Conductivity (µS/cm)": conductivity
        },

        {
            "Date": current_date,
            "Unit": "Clarifier Point 3",
            "Inlet Turbidity": clarifier_p2,
            "Outlet Turbidity": clarifier_p3,
            "Conductivity (µS/cm)": conductivity
        },

        {
            "Date": current_date,
            "Unit": "Clarifier Point 4",
            "Inlet Turbidity": clarifier_p3,
            "Outlet Turbidity": clarifier_p4,
            "Conductivity (µS/cm)": conductivity
        },

        {
            "Date": current_date,
            "Unit": "Clarifier",
            "Inlet Turbidity": aerator_turbidity,
            "Outlet Turbidity": clarifier_outlet,
            "Conductivity (µS/cm)": conductivity
        }

    ]

    # ======================================
    # RAW WATER DATAFRAME
    # ======================================

    raw_df = pd.DataFrame([{

        "Date": current_date,

        "Time": current_time,

        "Turbidity (NTU)": intake_turbidity,

        "Conductivity (µS/cm)": conductivity

    }])

    # ======================================
    # TURBIDITY DATAFRAME
    # ======================================

    turb_df = pd.DataFrame([{

        "Date": current_date,

        "Turbidity (NTU)": intake_turbidity,

        "Outlet Turbidity (NTU)": clarifier_outlet,

        "Alum Dosage (ppm)": round(
            intake_turbidity * 0.55,
            2
        )

    }])

    # ======================================
    # FILTER + CLARIFIER DATAFRAME
    # ======================================

    trend_df = pd.DataFrame(
        clarifier_rows + filter_rows
    )

    # ======================================
    # SAVE EXCEL FILES
    # ======================================

    raw_df.to_excel(raw_file, index=False)

    turb_df.to_excel(turb_file, index=False)

    trend_df.to_excel(filter_file, index=False)

    print("Live WTP Data Updated")

    # ======================================
    # UPDATE EVERY 10SEC
    # ======================================

    time.sleep(10)


