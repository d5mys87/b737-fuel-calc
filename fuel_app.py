import streamlit as st
import pandas as pd
import numpy as np

# --- 1. CONFIGURATION (Must be the very first Streamlit command) ---
st.set_page_config(page_title="Fuel Calc (Totalizer Fix)", layout="wide")

# --- 2. HEADER FUNCTION (Fixed Z-Index Version) ---
def render_header():
    """
    Renders a professional aviation-style technical header.
    UPDATED: Lower z-index to allow access to Streamlit menus.
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
            background-color: #2c3e50; /* Dark Slate Blue */
            color: #ecf0f1;
            
            /* Z-INDEX FIX: 
               Set to 50 so it sits ABOVE content but BELOW Streamlit's 
               system buttons (which are usually z-index 100+) 
            */
            z-index: 50; 
            
            display: flex;
            align-items: center;
            justify-content: space-between;
            
            /* PADDING FIX: 
               Added 60px side padding so text doesn't overlap the 
               sidebar arrow (left) or hamburger menu (right) 
            */
            padding: 0 60px; 
            
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            border-bottom: 3px solid #34495e;
        }

        /* 2. PUSH MAIN CONTENT DOWN */
        .block-container {
            padding-top: 5rem !important;
        }

        /* 3. OPTIONAL: Make Streamlit header transparent so it doesn't clash */
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
                padding: 10px 40px; /* Keep side padding for mobile menu buttons */
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
        except: db = pd.read_csv('App_Ready_