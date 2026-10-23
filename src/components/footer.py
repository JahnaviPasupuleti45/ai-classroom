import streamlit as st

SIGNATURE_NAME = "Jahnavi"


def _footer(text_color, signature_color, line_color):
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Great+Vibes&display=swap');
.sc-signature{{
    font-family: 'Great Vibes', cursive !important;
    font-size: 3rem;
    line-height: 1;
    color: {signature_color};
    padding: 0 0.4rem 0.2rem;
    border-bottom: 2px solid {line_color};
}}
</style>
<div style="margin-top:3.5rem; display:flex; flex-direction:column; align-items:center; gap:4px;">
<p style="color:{text_color}; font-size:0.85rem; letter-spacing:0.18em; text-transform:uppercase; margin:0; opacity:0.75;">Created by</p>
<div class="sc-signature">{SIGNATURE_NAME}</div>
</div>
""", unsafe_allow_html=True)


def footer_home():
    _footer("white", "#FFFFFF", "rgba(255,255,255,0.45)")


def footer_dashboard():
    _footer("#64748B", "#5865F2", "rgba(235,69,158,0.45)")
