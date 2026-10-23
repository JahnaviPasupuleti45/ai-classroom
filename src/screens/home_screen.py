import streamlit as st
from src.components.header import header_home
from ui.base_layout import style_base_layout, style_background_home
from src.components.footer import footer_home


def _portal(key, image_url, image_height, title, description, button_label, login_type):
    with st.container(key=key):
        st.html(f"""
<div class="sc-portal">
<img src="{image_url}" style="height:{image_height}px;" />
<h3>{title}</h3>
<p>{description}</p>
</div>
""")
        if st.button(button_label, type="primary", icon=":material/arrow_outward:",
                     icon_position="right", width="stretch", key=f"go_{login_type}"):
            st.session_state['login_type'] = login_type
            st.rerun()


def home_screen():

    style_base_layout()
    style_background_home()
    header_home()

    col1, col2 = st.columns(2, gap="large")

    with col1:
        _portal("portal_student", "https://i.ibb.co/844D9Lrt/mascot-student.png", 120,
                "I'm a Student", "Log in with FaceID, join classes and track your attendance.",
                "Student Portal", "student")

    with col2:
        _portal("portal_teacher", "https://i.ibb.co/CsmQQV6X/mascot-prof.png", 120,
                "I'm a Teacher", "Create subjects and take attendance from photos or voice.",
                "Teacher Portal", "teacher")

    st.markdown("""
<div class="sc-chips">
<span class="sc-chip">📸 Face recognition</span>
<span class="sc-chip">🎙️ Voice attendance</span>
<span class="sc-chip">🔗 QR class join</span>
<span class="sc-chip">📊 Attendance records</span>
</div>
""", unsafe_allow_html=True)

    footer_home()
