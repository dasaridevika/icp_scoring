"""
Enterprise ICP Revenue Intelligence Studio
Clean Foundation - Ready for Step-by-Step Scoring Engine Build
"""

import streamlit as st
import os
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

from workers.base_worker import WorkerAIClient

# Page Configuration
st.set_page_config(
    page_title="ICP Revenue Intelligence Studio",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Playfair Display Typography & Modern Luxury Dark Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"], .stMarkdown, .stText, h1, h2, h3, h4, h5, h6, p, div, span, label {
        font-family: 'Playfair Display', serif !important;
    }
    
    .title-text {
        background: linear-gradient(135deg, #FF6B6B 0%, #FFE66D 50%, #4ECDC4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: 0.5px;
        margin-bottom: 0.2rem;
    }

    .subtitle-text {
        color: #94A3B8;
        font-size: 1.05rem;
        font-style: italic;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Client
worker_client = WorkerAIClient()

# Header
st.markdown('<div class="title-text">Enterprise ICP Revenue Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">Clean Foundation - Building Scoring Logic Step-by-Step</div>', unsafe_allow_html=True)

# Lead Input Section
col_in1, col_in2 = st.columns([3, 1])
with col_in1:
    prospect_text = st.text_area(
        "Paste Lead Text / Contact Form / RFP Details:",
        height=200,
        placeholder="Company: NextEra Clean Infrastructure\nContact: Arthur Pendelton (VP of Strategy & Corporate Development)\nLocation: United States | $450M ARR | 1,200 Employees\nInquiry: Requesting custom proposal for multi-GW renewable portfolio...",
        key="lead_input_text"
    )

with col_in2:
    st.markdown("#### Parameters")
    custom_deal_size = st.number_input(
        "Estimated Deal Size ($)",
        min_value=1000,
        max_value=5000000,
        value=50000,
        step=5000
    )
    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
    score_btn = st.button("Score Lead", type="primary", use_container_width=True)

if score_btn:
    if not prospect_text.strip():
        st.error("Please paste lead details above.")
    else:
        st.info("Ready to attach Step 1 scoring logic.")
