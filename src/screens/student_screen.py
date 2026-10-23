import streamlit as st

from ui.base_layout import style_background_dashboard
from ui.base_layout import style_base_layout

from src.components.top_bar import top_bar
from src.components.footer import footer_dashboard

from PIL import Image
import numpy as np
import hashlib
import io
from src.pipelines.face_pipiline import identify_student
from src.pipelines.face_pipiline import get_face_embeddings
from src.pipelines.voice_pipeline import get_voice_embedding
from src.database.db import create_student
from src.pipelines.face_pipiline import train_classifier
from src.components.dialog_enroll import enroll_dialog
from src.database.db import unenroll_student_to_subject, get_student_subject, get_student_attendance
from src.components.subject_card import subject_card

STUDENT_SESSION_KEYS = ("student_data", "is_logged_in", "user_role", "face_scan")


def logout_student():
    for key in STUDENT_SESSION_KEYS:
        st.session_state.pop(key, None)


def empty_state(title, text):
    st.markdown(f"<div class='sc-empty'><h4>{title}</h4><p>{text}</p></div>", unsafe_allow_html=True)


def student_dashboard():

    student_data = st.session_state.student_data
    student_id = student_data['student_id']

    top_bar(student_data['name'], logout_student)

    try:
        with st.spinner("Loading your subjects..."):
            subjects = get_student_subject(student_id)
            logs = get_student_attendance(student_id)
    except Exception:
        st.error("Couldn't load your subjects. Check your internet connection and refresh.", icon=":material/cloud_off:")
        subjects, logs = [], []

    stats_map = {}
    for log in logs:
        entry = stats_map.setdefault(log['subject_id'], {'total': 0, "attended": 0})
        entry['total'] += 1
        if log.get('is_present'):
            entry['attended'] += 1

    total_classes = sum(s['total'] for s in stats_map.values())
    total_attended = sum(s['attended'] for s in stats_map.values())

    m1, m2, m3 = st.columns(3)
    m1.metric("Enrolled subjects", len(subjects))
    m2.metric("Classes attended", f"{total_attended} / {total_classes}")
    m3.metric("Overall attendance", f"{round(total_attended / total_classes * 100)}%" if total_classes else "-")

    st.space()

    c1, c2 = st.columns([3, 1], vertical_alignment='center')
    with c1:
        st.subheader("Your Subjects")
    with c2:
        if st.button("Join Subject", type='primary', icon=':material/add:', width='stretch'):
            enroll_dialog()

    if not subjects:
        with st.container(key="card_no_subjects"):
            empty_state("You're not in any subjects yet", "Click <b>Join Subject</b> and enter the code your teacher shared.")
        footer_dashboard()
        return

    cols = st.columns(2)
    for i, sub_node in enumerate(subjects):
        sub = sub_node['subjects']
        sid = sub['subject_id']
        stats = stats_map.get(sid, {"total": 0, "attended": 0})

        def unenroll_btn(subject_id=sid, subject_name=sub['name']):
            with st.popover("Leave subject", icon=':material/logout:', width='stretch'):
                st.write(f"Leave **{subject_name}**? Your attendance history stays saved.")
                if st.button("Yes, leave", type='primary', width='stretch', key=f"unenroll_{subject_id}"):
                    try:
                        unenroll_student_to_subject(student_id, subject_id)
                        st.toast(f"Left {subject_name}")
                        st.rerun()
                    except Exception:
                        st.error("Couldn't leave the subject. Please try again.")

        with cols[i % 2]:
            subject_card(
                name=sub['name'],
                code=sub['subject_code'],
                section=sub['section'],
                stats=[
                    ('Classes', stats['total']),
                    ('Attended', stats['attended'])
                ],
                progress=(stats['attended'] / stats['total']) if stats['total'] else None,
                footer_callback=unenroll_btn
            )

    footer_dashboard()


def scan_face(photo_bytes):
    """Run face identification once per photo; reruns reuse the cached result."""
    digest = hashlib.sha1(photo_bytes).hexdigest()
    cached = st.session_state.get("face_scan")
    if cached and cached[0] == digest:
        return cached[1]

    img = np.array(Image.open(io.BytesIO(photo_bytes)).convert("RGB"))
    with st.spinner("AI is scanning your face..."):
        student, _, num_faces = identify_student(img)

    st.session_state.face_scan = (digest, (student, num_faces))
    return student, num_faces


def login_student(student):
    st.session_state.is_logged_in = True
    st.session_state.user_role = 'student'
    st.session_state.student_data = student
    st.session_state.pop("face_scan", None)


def student_screen():

    style_background_dashboard()
    style_base_layout()

    if "student_data" in st.session_state:
        student_dashboard()
        return

    top_bar()

    _, mid, _ = st.columns([1, 3, 1])
    with mid:
        with st.container(key="card_student_login"):
            st.markdown(
                "<div class='sc-auth-head'><h2>Student Login</h2>"
                "<p>Look at the camera and snap a photo to log in with FaceID.</p></div>",
                unsafe_allow_html=True,
            )
            photo_source = st.camera_input("Position your face in the center", label_visibility="collapsed")

        if not photo_source:
            footer_dashboard()
            return

        photo_bytes = photo_source.getvalue()

        try:
            student, num_faces = scan_face(photo_bytes)
        except Exception:
            st.error("Face scan failed. Please retake the photo.")
            footer_dashboard()
            return

        if num_faces == 0:
            st.warning("No face found. Make sure your face is well lit and centered.", icon=":material/face:")
        elif num_faces > 1:
            st.warning("Multiple faces detected. Only you should be in the photo.", icon=":material/group:")
        elif student:
            login_student(student)
            st.toast(f"Welcome back {student['name']}!", icon=":material/waving_hand:")
            st.rerun()
        else:
            st.info("Face not recognized. Looks like you're new here, create your profile below.", icon=":material/person_add:")
            student_registration(photo_bytes)

    footer_dashboard()


def student_registration(photo_bytes):
    with st.container(key="card_student_register"):
        st.subheader("Create your profile")
        new_name = st.text_input("Your name", placeholder='e.g. Jahnavi')

        st.markdown("**Optional: voice enrollment**")
        st.caption("Record a short phrase like \"I am present, my name is Jahnavi\" to enable voice attendance.")
        audio_data = st.audio_input("Record your voice", label_visibility="collapsed")

        if st.button("Create Account", type='primary', icon=':material/how_to_reg:', width='stretch'):
            new_name = new_name.strip()
            if not new_name:
                st.warning("Please enter your name!")
                return

            with st.spinner("Creating your profile..."):
                try:
                    img = np.array(Image.open(io.BytesIO(photo_bytes)).convert("RGB"))
                    encodings = get_face_embeddings(img)
                    if len(encodings) == 0:
                        st.error("Could not capture your facial features. Please retake the photo.")
                        return

                    voice_emb = get_voice_embedding(audio_data.getvalue()) if audio_data else None
                    if audio_data and voice_emb is None:
                        st.warning("Voice couldn't be processed, so your profile was created without it.")

                    response_data = create_student(new_name, face_embedding=encodings[0].tolist(), voice_embedding=voice_emb)
                except Exception:
                    st.error("Couldn't create your profile. Please try again.")
                    return

            if response_data:
                train_classifier()
                login_student(response_data[0])
                st.toast(f'Profile created, welcome {new_name}!', icon=":material/celebration:")
                st.rerun()
            else:
                st.error("Couldn't create your profile. Please try again.")
