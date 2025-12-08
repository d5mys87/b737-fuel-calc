import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Fuel Calc (Totalizer Fix)", layout="wide")
st.title("✈️ B737 Fuel Calculator")
import streamlit as st

# --- PASTE THIS FUNCTION AT THE TOP OF YOUR FILE ---
def render_header():
    """
    Renders a professional aviation-style technical header
    at the top of the application.
    """
    header_html = """
    <style>
        /* Container for the header */
        .tech-header-container {
            background-color: #2c3e50; /* Dark Slate Blue */
            color: #ecf0f1;
            padding: 15px 25px;
            margin: -6rem -4rem 1rem -4rem; /* Negative margins to fill Streamlit top gap */
            border-bottom: 4px solid #34495e;
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
        }

        /* The 'Reference Only' Badge */
        .ref-badge {
            background-color: #34495e;
            color: #bdc3c7;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            border: 1px solid #46637f;
            white-space: nowrap;
        }

        /* The Technical Data Text */
        .tech-text {
            font-family: 'Source Code Pro', 'Courier New', monospace;
            font-size: 0.9rem;
            color: #ffffff;
            display: flex;
            gap: 15px;
            align-items: center;
        }

        .tech-text span {
            display: inline-block;
        }
        
        /* Mobile adjustment */
        @media (max-width: 700px) {
            .tech-header-container {
                justify-content: center;
                text-align: center;
                gap: 10px;
            }
            .tech-text {
                flex-direction: column;
                gap: 5px;
                font-size: 0.8rem;
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

# --- MAIN APP EXECUTION ---

# 1. Setup your page configuration first
st.set_page_config(page_title="Fuel Calc", layout="wide")

# 2. Call the header function immediately
render_header()

# 3. Your existing code goes here...
st.title("Fuel Quantity Indication Check")
# ... rest of your app

# --- 1. DATA LOADER ---
@st.cache_data
def load_data():
    try:
        try: db = pd.read_csv('App_Ready_Fuel_Database.csv')
        except: db = pd.read_csv('App_Ready_Fuel_Database.csv', sep=';')

        # Clean Types
        db['Roll_Input'] = pd.to_numeric(db['Roll_Input'], errors='coerce')
        db['Reading'] = pd.to_numeric(db['Reading'], errors='coerce')
        db['Fuel_Qty'] = pd.to_numeric(db['Fuel_Qty'], errors='coerce')
        for col in ['Stick', 'Pitch', 'Wing_Side']:
            if col in db.columns: db[col] = db[col].astype(str).str.strip()

        recs = pd.read_csv('Master_Stick_Recommendations.csv')
        return db, recs
    except Exception as e:
        return None, str(e)

data_res = load_data()
if data_res[0] is None:
    st.error("Data Load Failed.")
    st.stop()
df_db, df_recs = data_res

# --- 2. SESSION STATE ---
# Ensure these exist so the totalizer doesn't crash on first load
for k in ['left_qty', 'center_qty', 'right_qty']:
    if k not in st.session_state: st.session_state[k] = 0

# --- 3. PLACEHOLDER FOR TOTALIZER ---
# We reserve this spot at the top, but we will fill it at the BOTTOM of the script
scoreboard = st.empty()

# --- 4. LOGIC ---
def get_fuel_qty(stick, pitch, roll, reading, wing_side):
    subset = df_db[
        (df_db['Stick'] == stick) &
        (df_db['Pitch'] == pitch) &
        (df_db['Wing_Side'] == wing_side)
    ]
    # Float match for Roll
    subset = subset[np.isclose(subset['Roll_Input'], roll, atol=0.01)]
    
    if subset.empty: return None

    # Exact Match
    exact = subset[subset['Reading'] == reading]
    if not exact.empty: return exact.iloc[0]['Fuel_Qty']
    return None

# --- 5. SIDEBAR ---
with st.sidebar:
    st.header("Settings")
    
    # Pitch
    db_pitches = sorted(df_db['Pitch'].unique())
    # Sort E..M
    try: db_pitches.sort(key=lambda x: x[0])
    except: pass
    g_pitch = st.selectbox("Pitch", db_pitches)

    # Roll
    avail_rolls = sorted(df_db['Roll_Input'].dropna().unique())
    def_idx = avail_rolls.index(10.0) if 10.0 in avail_rolls else 0
    g_roll = st.selectbox("Roll", avail_rolls, index=def_idx)
    
    st.markdown("---")
    if st.button("Reset Calculator"):
        for k in ['left_qty', 'center_qty', 'right_qty']: st.session_state[k] = 0
        st.experimental_rerun()

# --- 6. TABS & CALCULATION ---
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

# --- 7. UPDATE THE SCOREBOARD (LAST STEP) ---
# Now that session_state is updated, we calculate the sum and push it to the top
final_total = (
    st.session_state.left_qty + 
    st.session_state.center_qty + 
    st.session_state.right_qty
)

# This updates the empty box we created at line 39
scoreboard.markdown(f"""
    <div style="background-color:#1E1E1E;padding:15px;border-radius:10px;text-align:center;margin-bottom:20px;border:1px solid #444;">
        <h3 style="color:#AAA;margin:0;font-size:14px;">TOTAL FUEL ON BOARD</h3>
        <h1 style="color:#00FF00;font-size:48px;margin:0;">{int(final_total):,} <span style="font-size:20px;color:#888;">KGS</span></h1>
    </div>
""", unsafe_allow_html=True)