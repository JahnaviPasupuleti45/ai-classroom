import streamlit as st
from PIL import Image
from src.components.header import LOGO_PATH
from src.screens.home_screen import home_screen
from src.screens.student_screen import student_screen
from src.screens.teacher_screen import teacher_screen
from src.components.dialog_auto_enroll import auto_enroll_dialog


def main():
    st.set_page_config(
        page_title="SnapClass - Making Attendance faster using AI",
        page_icon=Image.open(LOGO_PATH),
        layout="centered",
    )

    if 'login_type' not in st.session_state:
        st.session_state['login_type'] = None

    join_code = st.query_params.get('join-code')
    if join_code and st.session_state.login_type != 'student':
        st.session_state.login_type = 'student'

    match st.session_state['login_type']:
        case 'teacher':
            teacher_screen()

        case 'student':
            student_screen()

        case _:
            home_screen()

    # Prompt once per join code; closing the dialog with X must not reopen it on every rerun
    if (join_code and st.session_state.get('user_role') == 'student'
            and st.session_state.get('student_data')
            and st.session_state.get('join_prompted') != join_code):
        st.session_state.join_prompted = join_code
        auto_enroll_dialog(join_code)


main()
