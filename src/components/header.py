import base64
from pathlib import Path

import streamlit as st

LOGO_PATH = Path(__file__).resolve().parents[2] / "utils" / "logo.png"
LOGO_URL = "data:image/png;base64," + base64.b64encode(LOGO_PATH.read_bytes()).decode()


def header_home():

    st.markdown(f"""
<div class='sc-logo-container'>
<img src='{LOGO_URL}' style='height:96px;' />
<div class='sc-logo'>SNAP<br/>CLASS</div>
<div class='sc-tagline'>AI-powered attendance, done in a snap.</div>
</div>
""", unsafe_allow_html=True)


def header_dashboard():

    st.markdown(f"""
<div class='sc-brand'>
<img src='{LOGO_URL}' style='height:56px;' />
<div class='sc-brand-name'>SNAP<br/>CLASS</div>
</div>
""", unsafe_allow_html=True)
