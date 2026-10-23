import streamlit as st
from src.database.db import create_attendance


@st.dialog("Attendance Report", width="large")
def attendance_result_dialog(df, logs):
    present = sum(1 for log in logs if log['is_present'])
    st.markdown(f"**{present} of {len(logs)}** students marked present. Review before saving.")
    st.dataframe(df, hide_index=True, width='stretch')

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Discard", width='stretch', icon=':material/close:'):
            st.rerun()

    with col2:
        if st.button("Confirm & Save", width='stretch', type='primary', icon=':material/save:'):
            try:
                create_attendance(logs)
            except Exception:
                st.error("Couldn't save attendance. Please try again.")
                return
            st.toast("Attendance saved", icon=":material/check_circle:")
            st.session_state.attendance_images = []
            st.session_state.attendance_photo_ids = []
            st.rerun()
