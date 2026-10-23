import streamlit as st
from src.database.config import supabase
from src.pipelines.voice_pipeline import process_bulk_audio
from datetime import datetime
import pandas as pd
from src.database.db import create_attendance


def analyze_audio(selected_subject_id, audio_bytes):
    enrolled_students = (
        supabase.table("subject_students").select("*, students(*)")
        .eq("subject_id", selected_subject_id).execute().data
    )

    if not enrolled_students:
        st.warning("No students are enrolled in this subject yet")
        return

    candidates_dict = {
        s['students']['student_id']: s['students']['voice_embedding']
        for s in enrolled_students if s['students'].get('voice_embedding')
    }

    if not candidates_dict:
        st.error('None of the enrolled students have a voice profile yet')
        return

    detected_scores = process_bulk_audio(audio_bytes, candidates_dict) or {}

    results, attendance_to_log = [], []
    current_timestamp = datetime.now().astimezone().isoformat(timespec="seconds")

    for node in enrolled_students:
        student = node['students']

        if not student.get('voice_embedding'):
            results.append({
                "Name": student['name'],
                "ID": student['student_id'],
                "Score": "-",
                "Status": "⚪ No voice profile"
            })
            continue

        score = detected_scores.get(student['student_id'], 0.0)
        is_present = score > 0

        results.append({
            "Name": student['name'],
            "ID": student['student_id'],
            "Score": f"{float(score):.3f}" if is_present else "-",
            "Status": "✅ Present" if is_present else "❌ Absent"
        })

        attendance_to_log.append({
            "student_id": student['student_id'],
            "subject_id": selected_subject_id,
            "timestamp": current_timestamp,
            "is_present": bool(is_present)
        })

    st.session_state.voice_attendance_results = (selected_subject_id, pd.DataFrame(results), attendance_to_log)


@st.dialog("Voice Attendance", width="large")
def voice_attendance_dialog(selected_subject_id):
    st.caption("Record students saying \"I am present\". The AI matches each voice to a student profile.")

    audio_data = st.audio_input("Record classroom audio", label_visibility="collapsed")

    if st.button("Analyze audio", width='stretch', type='primary', icon=':material/graphic_eq:'):
        if audio_data is None:
            st.warning("Please record classroom audio first")
        else:
            with st.spinner("Processing audio..."):
                try:
                    analyze_audio(selected_subject_id, audio_data.getvalue())
                except Exception:
                    st.error("Audio analysis failed. Please try recording again.")

    saved = st.session_state.get('voice_attendance_results')
    if not saved or saved[0] != selected_subject_id:
        return

    _, df_results, logs = saved
    st.divider()
    st.write("Please review attendance before confirming.")
    st.dataframe(df_results, hide_index=True, width='stretch')

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Discard", width='stretch', icon=':material/close:'):
            del st.session_state.voice_attendance_results
            st.rerun()

    with col2:
        if st.button("Confirm & Save", width='stretch', type='primary', icon=':material/save:', disabled=not logs):
            try:
                create_attendance(logs)
            except Exception:
                st.error("Couldn't save attendance. Please try again.")
                return
            del st.session_state.voice_attendance_results
            st.toast("Attendance saved", icon=":material/check_circle:")
            st.rerun()
