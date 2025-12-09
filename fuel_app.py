import streamlit as st
import pandas as pd
import numpy as np

# --- 1. CONFIGURATION (Must be the very first Streamlit command) ---
st.set_page_config(
    page_title="Boeing 737 Fuel Dip", 
    page_icon="✈️", 
    layout="wide"
)

# --- 2. HEADER FUNCTION ---
def render_header():
    """
    Renders a professional aviation-style technical header.
    """
    header_html = """
    <style>
        /* 1. PIN THE HEADER TO THE TOP */
        .tech-header-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 3.5rem;
            background-color: #2c3e50;
            color: #ecf0f1;
            z-index: 50; 
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 60px; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            border-bottom: 3px solid #34495e;
        }

        /* 2. PUSH MAIN CONTENT DOWN */
        .block-container {
            padding-top: 5rem !important;
        }

        /* 3. Make Streamlit header transparent */
        header[data-testid="stHeader"] {
            background-color: transparent;
        }

        /* BADGE STYLES */
        .ref-badge {
            background-color: #34495e;
            color: #bdc3c7;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            border: 1px solid #46637f;
            white-space: nowrap;
        }

        /* TEXT STYLES */
        .tech-text {
            font-family: 'Source Code Pro', 'Courier New', monospace;
            font-size: 0.85rem;
            color: #ffffff;
            display: flex;
            gap: 15px;
            align-items: center;
        }

        /* MOBILE ADJUSTMENTS */
        @media (max-width: 700px) {
            .tech-header-container {
                height: auto;
                padding: 10px 40px; 
                flex-direction: column;
                gap: 8px;
            }
            .block-container {
                padding-top: 7rem !important;
            }
            .tech-text {
                flex-direction: column;
                gap: 2px;
                font-size: 0.75rem;
                text-align: center;
            }
        }
    </style>

    <div class="tech-header-container">
        <div class="ref-badge">
            ℹ️ For Reference Only
        </div>
        <div class="tech-text">
            <span><strong>FMSM 12-11-03</strong> REV 9</span>
            <span style="color: #7f8c8d;">|</span>
            <span>AMM-28-41-00-720-801</span>
            <span style="color: #7f8c8d;">|</span>
            <span style="color: #95a5a6;">Jun 10/2007</span>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

# --- 3. RENDER UI ELEMENTS ---
render_header()

st.title("✈️ B737 Fuel Calculator")
st.caption("Fuel Quantity Indication Check")

# --- 4. DATA LOADER ---
@st.cache_data
def load_data():
    try:
        try: db = pd.read_csv('App_Ready_Fuel_Database.csv')
        except: db = pd.read_csv('App_Ready_Fuel_Database.csv', sep=';')

        # Clean Types
        db['Roll_Input'] = pd.to_numeric(db['Roll_Input'], errors='coerce')
        db['Reading'] = pd.to_numeric(db['Reading'], errors='coerce')
        db['Fuel_Qty'] = pd.to_numeric(db['Fuel_Qty'], errors='coerce')
        
        # Ensure strings and strip whitespace
        for col in ['Stick', 'Pitch', 'Wing_Side']:
            if col in db.columns: 
                db[col] = db[col].astype(str).str.strip()

        recs = pd.read_csv('Master_Stick_Recommendations.csv')
        return db, recs
    except Exception as e:
        return None, str(e)

data_res = load_data()
if data_res[0] is None:
    st.error(f"Data Load Failed: {data_res[1]}")
    st.stop()
df_db, df_recs = data_res

# --- 5. SESSION STATE ---
for k in ['left_qty', 'center_qty', 'right_qty']:
    if k not in st.session_state: st.session_state[k] = 0

# --- 6. PLACEHOLDER FOR TOTALIZER ---
scoreboard = st.empty()

# --- 7. LOGIC ---
def get_fuel_qty(stick, pitch, roll, reading, wing_side):
    subset = df_db[
        (df_db['Stick'] == stick) &
        (df_db['Pitch'] == pitch) &
        (df_db['Wing_Side'] == wing_side)
    ]
    # Float match for Roll (Robust)
    subset = subset[np.