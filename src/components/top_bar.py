import html

import streamlit as st

from src.components.header import header_dashboard


def top_bar(user_name=None, on_logout=None):
    """Brand on the left; greeting + logout (logged in) or a Home button (logged out) on the right."""

    c1, c2 = st.columns([3, 2], vertical_alignment="center")

    with c1:
        header_dashboard()

    with c2:
        with st.container(horizontal=True, horizontal_alignment="right", vertical_alignment="center"):
            if user_name:
                st.markdown(
                    f"<p class='sc-greeting'>Hi, <b>{html.escape(str(user_name))}</b></p>",
                    unsafe_allow_html=True,
                )
                if st.button("Logout", icon=":material/logout:", key="topbar_logout"):
                    if on_logout:
                        on_logout()
                    st.rerun()
            else:
                if st.button("Home", icon=":material/arrow_back:", key="topbar_home"):
                    st.session_state["login_type"] = None
                    st.rerun()

    st.space()
