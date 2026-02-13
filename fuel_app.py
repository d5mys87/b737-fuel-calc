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
# Embed manifest directly as blob URL to bypass CORS and Streamlit's manifest
pwa_override_script = f"""
<script>
(function() {{
    // Create manifest as blob URL (bypasses external loading issues)
    var manifestData = {{
        "name": "B737 Fuel Calculator",
        "short_name": "B737 Fuel",
        "description": "Fuel Quantity Indication Check for Boeing 737 aircraft",
        "start_url": window.location.href.split('?')[0],
        "scope": window.location.origin + "/",
        "display": "standalone",
        "background_color": "#1E1E1E",
        "theme_color": "#2c3e50",
        "orientation": "any",
        "icons": [{{
            "src": "{LOGO_URL}",
            "sizes": "512x512",
            "type": "image/png",
            "purpose": "any"
        }}]
    }};

    var manifestBlob = new Blob([JSON.stringify(manifestData)], {{type: 'application/json'}});
    var manifestURL = URL.createObjectURL(manifestBlob);

    function overridePWA() {{
        // Remove ALL existing manifest links
        document.querySelectorAll('link[rel="manifest"]').forEach(function(el) {{
            el.parentNode.removeChild(el);
        }});

        // Remove existing apple-touch-icon links
        document.querySelectorAll('link[rel="apple-touch-icon"]').forEach(function(el) {{
            el.parentNode.removeChild(el);
        }});

        // Remove existing favicons
        document.querySelectorAll('link[rel="icon"], link[rel="shortcut icon"]').forEach(function(el) {{
            el.parentNode.removeChild(el);
        }});

        // Add our manifest (blob URL)
        var manifestLink = document.createElement('link');
        manifestLink.rel = 'manifest';
        manifestLink.href = manifestURL;
        document.head.insertBefore(manifestLink, document.head.firstChild);

        // Add our favicon
        var favicon = document.createElement('link');
        favicon.rel = 'icon';
        favicon.type = 'image/png';
        favicon.sizes = '512x512';
        favicon.href = '{LOGO_URL}';
        document.head.appendChild(favicon);

        // Add apple-touch-icon (critical for iOS)
        var appleIcon = document.createElement('link');
        appleIcon.rel = 'apple-touch-icon';
        appleIcon.sizes = '180x180';
        appleIcon.href = '{LOGO_URL}';
        document.head.appendChild(appleIcon);

        // Add/update meta tags for PWA
        var metaTags = [
            {{'name': 'apple-mobile-web-app-capable', 'content': 'yes'}},
            {{'name': 'apple-mobile-web-app-status-bar-style', 'content': 'black-translucent'}},
            {{'name': 'apple-mobile-web-app-title', 'content': 'B737 Fuel'}},
            {{'name': 'mobile-web-app-capable', 'content': 'yes'}},
            {{'name': 'application-name', 'content': 'B737 Fuel'}},
            {{'name': 'theme-color', 'content': '#2c3e50'}}
        ];

        metaTags.forEach(function(tag) {{
            var existing = document.querySelector('meta[name="' + tag.name + '"]');
            if (existing) existing.parentNode.removeChild(existing);
            var meta = document.createElement('meta');
            meta.name = tag.name;
            meta.content = tag.content;
            document.head.appendChild(meta);
        }});

        document.title = 'B737 Fuel Calc';
    }}

    // Override aggressively - Streamlit may re-inject its manifest
    overridePWA();
    setTimeout(overridePWA, 50);
    setTimeout(overridePWA, 200);
    setTimeout(overridePWA, 500);
    setTimeout(overridePWA, 1000);
    setTimeout(overridePWA, 2000);

    // Also observe for any new manifest links being added
    var observer = new MutationObserver(function(mutations) {{
        mutations.forEach(function(mutation) {{
            mutation.addedNodes.forEach(function(node) {{
                if (node.tagName === 'LINK' && node.rel === 'manifest' && node.href !== manifestURL) {{
                    node.parentNode.removeChild(node);
                    overridePWA();
                }}
            }});
        }});
    }});
    observer.observe(document.head, {{ childList: true }});
}})();
</script>
"""
st.markdown(pwa_override_script, unsafe_allow_html=True)

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
for k in ['left_alert', 'center_alert', 'right_alert']:
    if k not in st.session_state: st.session_state[k] = False

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
        st.session_state[f"{key}_alert"] = False
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

            # Always set the fuel value, track alert status separately
            st.session_state[f"{key}_qty"] = val
            st.session_state[f"{key}_alert"] = is_alert

            if is_alert:
                st.error(f"⚠️ VARIANCE > {limit_kg} KGS")
                st.write(f"Calc: **{int(val)}** | Est: **{est}**")
            else:
                st.success(f"✅ Verified: {int(val)}")
        else:
            st.session_state[f"{key}_qty"] = 0
            st.session_state[f"{key}_alert"] = False

with tab1: render_tab("Left", "left", "Main Wing Tank", "Left")
with tab2: render_tab("Center", "center", "Center Tank", "Left")
with tab3: render_tab("Right", "right", "Main Wing Tank", "Right")

# --- 10. SCOREBOARD ---
final_total = (
    st.session_state.left_qty +
    st.session_state.center_qty +
    st.session_state.right_qty
)

has_any_alert = (
    st.session_state.left_alert or
    st.session_state.center_alert or
    st.session_state.right_alert
)

# Determine colors based on alert status
if has_any_alert:
    total_color = "#ff4444"
    border_color = "#ff4444"
    box_shadow = "0 0 15px rgba(255, 68, 68, 0.3)"
elif final_total > 0:
    total_color = "#00FF00"
    border_color = "#444"
    box_shadow = "none"
else:
    total_color = "#888"
    border_color = "#444"
    box_shadow = "none"

# Individual tank colors
left_color = "#ff4444" if st.session_state.left_alert else "#FFF"
center_color = "#ff4444" if st.session_state.center_alert else "#FFF"
right_color = "#ff4444" if st.session_state.right_alert else "#FFF"

st_style = f"""
<style>
    .cockpit-display {{
        background-color: #1E1E1E; border: 3px solid {border_color};
        border-radius: 15px; padding: 20px; text-align: center;
        font-family: monospace; color: #E0E0E0; margin-bottom: 20px;
        box-shadow: {box_shadow};
    }}
    .gauge-row {{
        display: flex; justify-content: space-around;
        border-bottom: 2px solid #333; padding-bottom: 15px;
        flex-wrap: wrap;
    }}
    .gauge-container {{
        display: flex; flex-direction: column;
        align-items: center; margin: 5px; min-width: 80px;
    }}
    .gauge-label {{
        color: #00BFFF; font-size: 1rem; font-weight: bold;
    }}
    .gauge-value {{
        font-size: 1.5rem; font-weight: bold;
        background-color: #000; padding: 5px 10px;
        border-radius: 5px; border: 2px solid #333;
    }}
    .total-value {{
        font-size: 2.5rem; font-weight: bold; color: {total_color};
        margin-top: 10px;
    }}
</style>
"""

st_html = f"""
<div class="cockpit-display">
    <div class="gauge-row">
        <div class="gauge-container">
            <div class="gauge-label">TANK 1</div>
            <div class="gauge-value" style="color: {left_color};">{int(st.session_state.left_qty):,}</div>
        </div>
        <div class="gauge-container">
            <div class="gauge-label">CTR</div>
            <div class="gauge-value" style="color: {center_color};">{int(st.session_state.center_qty):,}</div>
        </div>
        <div class="gauge-container">
            <div class="gauge-label">TANK 2</div>
            <div class="gauge-value" style="color: {right_color};">{int(st.session_state.right_qty):,}</div>
        </div>
    </div>
    <div style="margin-top:10px;">TOTAL FUEL</div>
    <div class="total-value">{int(final_total):,} <span style="font-size:1rem;color:#888;">KGS</span></div>
</div>
"""

scoreboard.markdown(st_style + st_html, unsafe_allow_html=True)
