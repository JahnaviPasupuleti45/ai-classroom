import streamlit as st
from src.database.db import enroll_student_to_subject
from src.database.config import supabase


def _close():
    st.query_params.clear()
    st.rerun()


@st.dialog("Quick Enrollment")
def auto_enroll_dialog(subject_code):
    student_id = st.session_state.student_data['student_id']

    try:
        res = supabase.table('subjects').select('subject_id, name').eq('subject_code', subject_code).execute()
    except Exception:
        st.error("Couldn't reach the server. Please try again.")
        return

    if not res.data:
        st.error('Subject code not found!')
        if st.button('Close', width='stretch'):
            _close()
        return
    subject = res.data[0]

    check = supabase.table('subject_students').select("*").eq('subject_id', subject['subject_id']).eq('student_id', student_id).execute()
    if check.data:
        st.info(f"You're already enrolled in **{subject['name']}**.")
        if st.button('Got it!', type='primary', width='stretch'):
            _close()
        return

    st.markdown(f"Would you like to join **{subject['name']}**?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("No thanks", width='stretch'):
            _close()

    with col2:
        if st.button("Yes, join now", type='primary', width='stretch'):
            try:
                enroll_student_to_subject(student_id, subject['subject_id'])
            except Exception:
                st.error("Couldn't join the subject. Please try again.")
                return
            st.toast(f"Joined {subject['name']}!", icon=":material/check_circle:")
            _close()
