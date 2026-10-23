import streamlit as st
from src.database.db import enroll_student_to_subject
from src.database.config import supabase


@st.dialog("Join a Subject")
def enroll_dialog():
    st.caption("Enter the subject code your teacher shared with you.")

    with st.form("enroll_form", border=False):
        join_code = st.text_input('Subject Code', placeholder='e.g. CS101')
        submitted = st.form_submit_button("Join now", type='primary', icon=':material/login:', width='stretch')

    if not submitted:
        return

    join_code = join_code.strip()
    if not join_code:
        st.warning("Please enter a subject code")
        return

    student_id = st.session_state.student_data['student_id']

    try:
        res = (
            supabase.table('subjects')
            .select("subject_id, name, subject_code")
            .eq('subject_code', join_code)
            .execute()
        )

        if not res.data:
            st.error("Invalid subject code")
            return

        subject = res.data[0]

        check = (
            supabase.table('subject_students')
            .select("*")
            .eq("subject_id", subject['subject_id'])
            .eq("student_id", student_id)
            .execute()
        )

        if check.data:
            st.warning(f"You're already enrolled in {subject['name']}")
            return

        enroll_student_to_subject(student_id, subject['subject_id'])
    except Exception:
        st.error("Couldn't reach the server. Please try again.")
        return

    st.toast(f"Joined {subject['name']}!", icon=":material/check_circle:")
    st.rerun()
