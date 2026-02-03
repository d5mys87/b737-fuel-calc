import streamlit as st
import pandas as pd
import numpy as np
import os

# ================= BEGIN BRANDING BLOCK =================
# 1. SETUP & CONFIGURATION
LOGO_FILENAME = "logo.png"  
GITHUB_USER = "d5mys87"
REPO_NAME = "b737-fuel-calc"
BRANCH = "main"
LOGO_URL = "https://raw.githubusercontent.com/d5mys87/b737-fuel-calc/main/logo.png"

# 2. SET PAGE CONFIG (Must be the first Streamlit command)
# Check if you already have 'st.set_page_config' further down. 
# If you do, DELETE IT there and use this one instead.
st.set_page_config(
    page_title="B737 Fuel Calc",
    page_icon=LOGO_URL,
    layout="wide"
)

# 3. HIDE STREAMLIT BRANDING (CSS)
hide_streamlit_style = """
<style>
    footer {visibility: hidden;}
    [data-testid="stConnectionStatus"] {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    .block-container {padding-top: 1rem;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 4. INJECT PWA META TAGS AND MANIFEST FOR INSTALLABLE WEB APP
MANIFEST_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/manifest.json"

st.markdown(
    f"""
    <head>
        <!-- PWA Manifest -->
        <link rel="manifest" href="{MANIFEST_URL}">

        <!-- iOS PWA Support -->
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <meta name="apple-mobile-web-app-title" content="B737 Fuel">
        <link rel="apple-touch-icon" href="{LOGO_URL}">

        <!-- Android/Chrome PWA Support -->
        <meta name="mobile-web-app-capable" content="yes">
        <meta name="theme-color" content="#2c3e50">
        <meta name="application-name" content="B737 Fuel Calculator">

        <!-- Standard favicon -->
        <link rel="icon" type="image/png" href="{LOGO_URL}">
        <link rel="shortcut icon" href="{LOGO_URL}">
    </head>
    """,
    unsafe_allow_html=True
)

# 5. PWA INSTALL PROMPT BANNER
pwa_install_css = """
<style>
    .pwa-install-banner {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(135deg, #2c3e50, #34495e);
        color: white;
        padding: 12px 24px;
        border-radius: 30px;
        font-family: sans-serif;
        font-size: 0.9rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        z-index: 9999;
        display: none;
        align-items: center;
        gap: 10px;
        cursor: pointer;
        border: 2px solid #46637f;
    }
    .pwa-install-banner:hover {
        background: linear-gradient(135deg, #34495e, #2c3e50);
    }
    .pwa-install-icon {
        font-size: 1.2rem;
    }
</style>

<div class="pwa-install-banner" id="pwa-banner" onclick="installPWA()">
    <span class="pwa-install-icon">+</span>
    <span>Install App</span>
</div>

<script>
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    document.getElementById('pwa-banner').style.display = 'flex';
});

function installPWA() {
    if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                document.getElementById('pwa-banner').style.display = 'none';
            }
            deferredPrompt = null;
        });
    }
}

window.addEventListener('appinstalled', () => {
    document.getElementById('pwa-banner').style.display = 'none';
});

// Hide banner if already installed (standalone mode)
if (window.matchMedia('(display-mode: standalone)').matches) {
    document.addEventListener('DOMContentLoaded', function() {
        var banner = document.getElementById('pwa-banner');
        if (banner) banner.style.display = 'none';
    });
}
</script>
"""
st.markdown(pwa_install_css, unsafe_allow_html=True)
# ================= END BRANDING BLOCK =================

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
    
    # --- UPDATED: Safe Default to Pitch K ---
    pitch_index = 0
    for i, p in enumerate(db_pitches):
        if "K" in p: # Check if Pitch label contains 'K'
            pitch_index = i
            break
            
    g_pitch = st.selectbox("Pitch", db_pitches, index=pitch_index)

    # --- UPDATED: Safe Default to Roll 10 ---
    avail_rolls = sorted(df_db['Roll_Input'].dropna().unique())
    
    roll_index = 0
    if 10.0 in avail_rolls:
        roll_index = avail_rolls.index(10.0)
        
    g_roll = st.selectbox("Roll", avail_rolls, index=roll_index)

# --- 9. TABS & CALCULATION ---
tab1, tab2, tab3 = st.tabs(["Left Wing", "Center", "Right Wing"])

def render_tab(label, key, scope, default_side):
    st.subheader(f"{label} Tank")
    
    # --- Default value=True so tanks start as EMPTY ---
    if st.checkbox(f"Mark {label} EMPTY", value=True, key=f"{key}_empty"):
        st.session_state[f"{key}_qty"] = 0
        st.info(f"{label} Tank = 0 Kgs")
        return 

    acc_side = default_side
    if label == "Center":
        acc_side = st.radio(
            "Access Side", 
            ["Left", "Right"], 
            horizontal=True, 
            key=f"{key}_side"
        )

    c1, c2 = st.columns(2)
    with c1:
        est = st.number_input(f"Est. {label}", step=100, key=f"{key}_est")
        if est > 0:
            rec = df_recs[
                (df_recs['Tank_Scope']==scope) & 
                (df_recs['Min_Kg']<=est) & 
                (df_recs['Max_Kg']>est)
            ]
            if not rec.empty: 
                st.info(f"💡 {rec.iloc[0]['Recommended_Stick']}")
    
    with c2:
        # --- Set Stick 8 as default for Left/Right ---
        default_stick_index = 0
        
        if label == "Center": 
            sticks = ["Stick 1", "Stick 2"]
            default_stick_index = 0 # Default to Stick 1
        else: 
            sticks = ["Stick 3", "Stick 4", "Stick 5", "Stick 6", "Stick 7", "Stick 8"]
            # Default to Stick 8 (Index 5)
            default_stick_index = 5 
            
        s_val = st.selectbox(f"Stick ({label})", sticks, index=default_stick_index, key=f"{key}_st")
        
        # Data Filtering
        broad_data = df_db[
            (df_db['Stick'] == s_val) & 
            (df_db['Pitch'] == g_pitch) & 
            (df_db['Wing_Side'] == acc_side)
        ]
        strict_data = broad_data[
            np.isclose(broad_data['Roll_Input'], g_roll, atol=0.01)
        ]
        
        if strict_data.empty:
            readings = [0.0]
            if not broad_data.empty:
                valid_rolls = sorted(broad_data['Roll_Input'].unique())
                st.warning(f"No Data for Roll {g_roll}")
        else:
            readings = sorted(strict_data['Reading'].unique())
            
        r_val = st.selectbox(f"Reading ({label})", readings, key=f"{key}_rd")

    # Calculation
    if r_val > 0:
        val = get_fuel_qty(s_val, g_pitch, g_roll, r_val, acc_side)

        if val is not None:
            limit_kg = 520 if label == "Center" else 160
            
            is_alert = False
            if est > 0:
                diff = abs(est - val)
                if diff > limit_kg: is_alert = True
            
            if is_alert:
                st.error(f"⚠️ VARIANCE > {limit_kg} KGS")
                st.write(f"Calc: **{int(val)}** | Est: **{est}**")
                st.session_state[f"{key}_qty"] = 0
            else:
                st.success(f"✅ Verified: {int(val)}")
                st.session_state[f"{key}_qty"] = val
        else:
            st.session_state[f"{key}_qty"] = 0

with tab1: render_tab("Left", "left", "Main Wing Tank", "Left")
with tab2: render_tab("Center", "center", "Center Tank", "Left")
with tab3: render_tab("Right", "right", "Main Wing Tank", "Right")

# --- 10. SCOREBOARD ---
final_total = (
    st.session_state.left_qty + 
    st.session_state.center_qty + 
    st.session_state.right_qty
)

total_color = "#00FF00" if final_total > 0 else "#888"

st_style = """
<style>
    .cockpit-display {
        background-color: #1E1E1E; border: 3px solid #444;
        border-radius: 15px; padding: 20px; text-align: center;
        font-family: monospace; color: #E0E0E0; margin-bottom: 20px;
    }
    .gauge-row {
        display: flex; justify-content: space-around;
        border-bottom: 2px solid #333; padding-bottom: 15px;
        flex-wrap: wrap;
    }
    .gauge-container {
        display: flex; flex-direction: column;
        align-items: center; margin: 5px; min-width: 80px;
    }
    .gauge-label {
        color: #00BFFF; font-size: 1rem; font-weight: bold;
    }
    .gauge-value {
        font-size: 1.5rem; font-weight: bold; color: #FFF;
        background-color: #000; padding: 5px 10px;
        border-radius: 5px; border: 2px solid #333;
    }
    .total-value {
        font-size: 2.5rem; font-weight: bold; color: COLOR_PLACEHOLDER;
        margin-top: 10px;
    }
</style>
""".replace("COLOR_PLACEHOLDER", total_color)

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
    <div style="margin-top:10px;">TOTAL FUEL</div>
    <div class="total-value">{int(final_total):,} <span style="font-size:1rem;color:#888;">KGS</span></div>
</div>
"""


scoreboard.markdown(st_style + st_html, unsafe_allow_html=True)
