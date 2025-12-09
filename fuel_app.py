import streamlit as st
import pandas as pd
import numpy as np
import os

# --- 1. CONFIGURATION ---
if os.path.exists("logo.png"):
    app_icon = "logo.png"
else:
    app_icon = "✈️"

st.set_page_config(
    page_title="B737 Fuel Dip",
    page_icon=app_icon,
    layout="wide"
)

# --- 2. HEADER FUNCTION ---
def render_header():
    header_html = """
    <style>
        .tech-header-container {
            position: fixed; top: 0; left: 0; width: 100%;
            height: 3.5rem; background-color: #2c3e50;
            color: #ecf0f1; z-index: 50; display: flex;
            align-items: center; justify-content: space-between;
            padding: 0 60px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            font-family: sans-serif; border-bottom: 3px solid #34495e;
        }
        .block-container { padding-top: 5rem !important; }
        header[data-testid="stHeader"] { background-color: transparent; }
        .ref-badge {
            background-color: #34495e; color: #bdc3c7;
            padding: 4px 10px; border-radius: 4px;
            font-size: 0.75rem; font-weight: 700;
            border: 1px solid #46637f;
        }
        .tech-text {
            font-family: monospace; font-size: 0.85rem;
            color: #ffffff; display: flex; gap: 15px;
        }
        @media (max-width: 700px) {
            .tech-header-container {
                height: auto; padding: 10px 40px;
                flex-direction: column; gap: 8px;
            }
            .block-container { padding-top: 7rem !important; }
        }
    </style>
    <div class="tech-header-container">
        <div class="ref-badge">ℹ️ For Reference Only</div>
        <div class="tech-text">
            <span>FMSM 12-11-03</span>
            <span>|</span>
            <span>AMM-28-41-00</span>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

# --- 3. RENDER UI ---
render_header()
st.title("✈️ B737 Fuel Calculator")
st.caption("Fuel Quantity Indication Check")

# --- 4. DATA LOADER ---
@st.cache_data
def load_data():
    try:
        try: 
            db = pd.read_csv('App_Ready_Fuel_Database.csv')
        except: 
            db = pd.read_csv('App_Ready_Fuel_Database.csv', sep=';')

        # Clean Types
        for col in ['Roll_Input', 'Reading', 'Fuel_Qty']:
            db[col] = pd.to_numeric(db[col], errors='coerce')
        
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

# --- 6. SCOREBOARD PLACEHOLDER ---
scoreboard = st.empty()

# --- 7. LOGIC ---
def get_fuel_qty(stick, pitch, roll, reading, wing_side):
    subset = df_db[
        (df_db['Stick'] == stick) &
        (df_db['Pitch'] == pitch) &
        (df_db['Wing_Side'] == wing_side)
    ]
    # Robust Roll Match
    subset = subset[np.isclose(subset['Roll_Input'], roll, atol=0.01)]
    
    if subset.empty: return None

    # Robust Reading Match
    exact = subset[np.isclose(subset['Reading'], reading, atol=0.01)]
    
    if not exact.empty: return exact.iloc[0]['Fuel_Qty']
    return None

# --- 8. SIDEBAR ---
with st.sidebar:
    st.header("Settings")
    
    # Sort Pitches
    def try_float(x):
        try: return float(x)
        except: return x
    
    db_pitches = sorted(df_db['Pitch'].unique())
    db_pitches.sort(key=try_float)
    
    # --- UPDATED: Default to Pitch K ---
    def_pitch