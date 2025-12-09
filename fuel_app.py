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
    subset = subset[np.isclose(subset['Roll_Input'], roll, atol=0.01)]
    
    if subset.empty: return None

    # Exact Match
    exact = subset[subset['Reading'] == reading]
    if not exact.empty: return exact.iloc[0]['Fuel_Qty']
    return None

# --- 8. SIDEBAR ---
with st.sidebar:
    st.header("Settings")
    
    # Pitch - Helper function for robust sorting
    def try_float(x):
        try: return float(x)
        except: return x

    db_pitches = sorted(df_db['Pitch'].unique())
    # Sort numerically if possible, otherwise alphabetically
    db_pitches.sort(key=try_float)
    
    g_pitch = st.selectbox("Pitch", db_pitches)

    # Roll
    avail_rolls = sorted(df_db['Roll_Input'].dropna().unique())
    def_idx = avail_rolls.index(10.0) if 10.0 in avail_rolls else 0
    g_roll = st.selectbox("Roll", avail_rolls, index=def_idx)
    
    st.markdown("---")
    if st.button("Reset Calculator"):
        for k in ['left_qty', 'center_qty', 'right_qty']: 
            st.session_state[k] = 0
        st.rerun() 

# --- 9. TABS & CALCULATION ---
tab1, tab2, tab3 = st.tabs(["Left Wing", "Center Tank", "Right Wing"])

def render_tab(label, key, scope, default_side):
    st.subheader(f"{label} Tank")
    
    # Empty Checkbox
    if st.checkbox(f"Mark {label} as EMPTY", key=f"{key}_empty"):
        st.session_state[f"{key}_qty"] = 0
        st.info(f"{label} Tank = 0 Kgs")
        return 

    acc_side = default_side
    if label == "Center":
        acc_side = st.radio("Access Side", ["Left", "Right"], horizontal=True, key=f"{key}_side")

    c1, c2 = st.columns(2)
    with c1:
        est = st.number_input(f"Est. Fuel ({label})", step=100, key=f"{key}_est")
        if est > 0:
            rec = df_recs[(df_recs['Tank_Scope']==scope) & (df_recs['Min_Kg']<=est) & (df_recs['Max_Kg']>est)]
            if not rec.empty: st.info(f"💡 {rec.iloc[0]['Recommended_Stick']}")
    
    with c2:
        if label == "Center": sticks = ["Stick 1", "Stick 2"]
        else: sticks = ["Stick 3", "Stick 4", "Stick 5", "Stick 6", "Stick 7", "Stick 8"]
            
        s_val = st.selectbox(f"Stick ({label})", sticks, key=f"{key}_st")
        
        # Roll Detective
        broad_data = df_db[
            (df_db['Stick'] == s_val) & 
            (df_db['Pitch'] == g_pitch) & 
            (df_db['Wing_Side'] == acc_side)
        ]
        strict_data = broad_data[np.isclose(broad_data['Roll_Input'], g_roll, atol=0.01)]
        
        if strict_data.empty:
            readings = [0.0]
            if not broad_data.empty:
                valid_rolls = sorted(broad_data['Roll_Input'].unique())
                st.warning(f"No data for Roll {g_roll}. Valid Rolls: {valid_rolls}")
        else:
            readings = sorted(strict_data['Reading'].unique())
            
        r_val = st.selectbox(f"Select Reading ({label})", readings, key=f"{key}_rd")

    # Calculation Trigger
    if r_val > 0:
        val = get_fuel_qty(s_val, g_pitch, g_roll, r_val, acc_side)
        if val is not None:
            # Variance Check
            is_alert = False
            if est > 0:
                diff_pct = abs(est - val) / est
                if diff_pct > 0.05: is_alert = True
            
            if is_alert:
                st.error(f"⚠️ VARIANCE ALERT (>5%)")
                st.write(f"Calc: **{int(val)}** | Est: **{est}**")
                st.session_state[f"{key}_qty"] = 0 # Safety: Don't add to total
            else:
                st.success(f"✅ Verified: {int(val)} Kgs")
                st.session_state[f"{key}_qty"] = val # Add to total
        else:
            st.session_state[f"{key}_qty"] = 0

# Render Tabs (This updates the session_state)
with tab1: render_tab("Left", "left", "Main Wing Tank", "Left")
with tab2: render_tab("Center", "center", "Center Tank", "Left")
with tab3: render_tab("Right", "right", "Main Wing Tank", "Right")

# --- 10. UPDATE THE SCOREBOARD (SYNTAX SAFE VERSION) ---
final_total = (
    st.session_state.left_qty + 
    st.session_state.center_qty + 
    st.session_state.right_qty
)

total_color = "#00FF00" if final_total > 0 else "#888"

# We split CSS and HTML to avoid f-string syntax errors with curly braces
st_style = """
<style>
    .cockpit-display {
        background-color: #1E1E1E;
        border: 3px solid #444;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        font-family: 'Source Code Pro', 'Courier New', monospace;
        color: #E0E0E0;
        margin-bottom: 20px;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.5);
    }
    .gauge-row {
        display: flex;
        justify-content: space-around;
        margin-bottom: 15px;
        border-bottom: 2px solid #333;
        padding-bottom: 15px;
        flex-wrap: wrap;
    }
    .gauge-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        min-width: 100px;
        margin: 5px;
    }
    .gauge-label {
        color: #00BFFF; /* Cyan-like color */
        font-size: 1.1rem;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .gauge-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #FFFFFF;
        background-color: #000;
        padding: 5px 12px;
        border-radius: 5px;
        border: 2px solid #333;
        min-width: 90px;
    }
    .total-container {
        margin-top: 10px;
    }
    .total-label {
        color: #AAA;
        font-size: 1rem;
        margin-bottom: 5px;
        text-transform: uppercase;
    }
    .total-value {
        font-size: 3rem;
        font-weight: bold;
        color: VARIABLE_COLOR;
        margin: 0;
        text-shadow: 0 0 10px rgba(0,255,0,0.3);
    }
    .unit-label {
        font-size: 1.5rem;
        color: #888;
    }
</style>
""".replace("VARIABLE_COLOR", total_color)

st_html = f"""
<div class="cockpit-display">
    <div class="gauge-row">
        <div class="gauge-container">
            <div class="gauge-label">TANK 1</div>
            <div class="gauge-value">{int(st.session_state.left_qty):,}</div>
        </div>
        <div class="gauge-container">
            <div class="gauge-label">CTR</div>
            <div class="gauge-value">{int(st.session_state.center_qty):,}</div>
        </div>
        <div class="gauge-container">
            <div class="gauge-label">TANK 2</div>
            <div class="gauge-value">{int(st.session_state.right_qty):,}</div>
        </div>
    </div>
    <div class="total-container">
        <div class="total-label">Total Fuel On Board</div>
        <h1 class="total-value">{int(final_total):,} <span class="unit-label">KGS</span></h1>
    </div>
</div>
"""

scoreboard.markdown(st_style + st_html, unsafe_allow_html=True)