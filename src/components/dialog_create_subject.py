import streamlit as st
from src.database.db import create_subject


@st.dialog("Create New Subject")
def create_subject_dialog(teacher_id):
    st.caption("Students will join using the subject code.")

    with st.form("create_subject_form", border=False):
        sub_id = st.text_input("Subject Code", placeholder='CS101')
        sub_name = st.text_input("Subject Name", placeholder='Machine Learning')
        sub_section = st.text_input("Section", placeholder='A')
        submitted = st.form_submit_button("Create Subject", type='primary', icon=':material/add:', width='stretch')

    if submitted:
        sub_id, sub_name, sub_section = sub_id.strip(), sub_name.strip(), sub_section.strip()
        if not (sub_id and sub_name and sub_section):
            st.warning("Please fill all the fields")
            return
        try:
            create_subject(sub_id, sub_name, sub_section, teacher_id)
        except Exception as e:
            if "duplicate" in str(e).lower() or "23505" in str(e):
                st.error("That subject code already exists. Choose a different one.")
            else:
                st.error("Couldn't create the subject. Please try again.")
            return
        st.toast("Subject created", icon=":material/check_circle:")
        st.rerun()
