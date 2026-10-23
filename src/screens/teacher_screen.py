import streamlit as st

from ui.base_layout import style_background_dashboard
from ui.base_layout import style_base_layout

from src.components.top_bar import top_bar
from src.components.footer import footer_dashboard
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.subject_card import subject_card
from src.components.dialog_add_photos import add_photos_dialog
from src.components.dialog_attendance_result import attendance_result_dialog
from src.components.dialog_voice_attendance import voice_attendance_dialog

from src.database.db import check_teacher_exists, create_teacher, teacher_login, get_teacher_subjects, get_attendance_for_teacher

from src.pipelines.face_pipiline import predict_attendance
from src.database.config import supabase

import re
import numpy as np
from datetime import datetime
import pandas as pd

TEACHER_TABS = {
    "take_attendance": ":material/ar_on_you: Take Attendance",
    "manage_subjects": ":material/book_ribbon: Subjects",
    "attendance_records": ":material/cards_stack: Records",
}

TEACHER_SESSION_KEYS = (
    "teacher_data", "is_logged_in", "user_role", "attendance_images",
    "attendance_photo_ids", "voice_attendance_results",
)


def teacher_screen():

    style_background_dashboard()
    style_base_layout()

    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif st.session_state.get("teacher_login_type", "login") == "register":
        teacher_screen_register()
    else:
        teacher_screen_login()


def logout_teacher():
    for key in TEACHER_SESSION_KEYS:
        st.session_state.pop(key, None)


def empty_state(title, text):
    st.markdown(f"<div class='sc-empty'><h4>{title}</h4><p>{text}</p></div>", unsafe_allow_html=True)


def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    teacher_id = teacher_data['teacher_id']

    top_bar(teacher_data['name'], logout_teacher)

    try:
        subjects = get_teacher_subjects(teacher_id)
    except Exception:
        st.error("Couldn't load your subjects. Check your internet connection and refresh.", icon=":material/cloud_off:")
        subjects = []

    m1, m2, m3 = st.columns(3)
    m1.metric("Subjects", len(subjects))
    m2.metric("Enrolled students", sum(s['total_students'] for s in subjects))
    m3.metric("Classes held", sum(s['total_classes'] for s in subjects))

    st.space()

    if st.session_state.get("current_teacher_tab") not in TEACHER_TABS:
        st.session_state.current_teacher_tab = "take_attendance"

    st.segmented_control(
        "Navigation",
        options=list(TEACHER_TABS),
        format_func=TEACHER_TABS.get,
        key="current_teacher_tab",
        required=True,
        label_visibility="collapsed",
        width="stretch",
    )

    st.space()

    tab = st.session_state.current_teacher_tab
    if tab == "take_attendance":
        teacher_tab_take_attendance(subjects)
    elif tab == "manage_subjects":
        teacher_tab_manage_subjects(subjects, teacher_id)
    elif tab == "attendance_records":
        teacher_tab_attendance_records(teacher_id)

    footer_dashboard()


def teacher_tab_take_attendance(subjects):
    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    with st.container(key="card_take_attendance"):
        st.subheader("Take AI Attendance")
        st.caption("Pick a subject, add classroom photos, then let the AI mark who's present.")

        if not subjects:
            empty_state("No subjects yet", "Create your first subject in the <b>Subjects</b> tab to start taking attendance.")
            return

        subject_options = {f"{s['name']} · {s['subject_code']}": s['subject_id'] for s in subjects}

        col1, col2 = st.columns([3, 1], vertical_alignment='bottom')

        with col1:
            selected_subject_label = st.selectbox('Subject', options=list(subject_options.keys()), key="attendance_subject")

        with col2:
            if st.button("Add Photos", type='secondary', icon=':material/add_a_photo:', width='stretch'):
                add_photos_dialog()

        selected_subject_id = subject_options[selected_subject_label]

        images = st.session_state.attendance_images

        if images:
            st.markdown(f"**{len(images)} photo{'s' if len(images) != 1 else ''} added**")
            gallery_cols = st.columns(4)
            for idx, img in enumerate(images):
                with gallery_cols[idx % 4]:
                    st.image(img, width='stretch', caption=f"Photo {idx+1}")
        else:
            empty_state("No photos yet", "Click <b>Add Photos</b> to capture or upload classroom pictures.")

        has_photos = bool(images)
        c1, c2, c3 = st.columns(3)

        with c1:
            if st.button("Clear photos", width='stretch', type='tertiary', icon=':material/delete:', disabled=not has_photos):
                st.session_state.attendance_images = []
                st.session_state.attendance_photo_ids = []
                st.rerun()

        with c2:
            if st.button("Run Face Analysis", width='stretch', type='primary', icon=":material/analytics:", disabled=not has_photos):
                run_face_analysis(selected_subject_id)

        with c3:
            if st.button("Voice Attendance", type='secondary', width='stretch', icon=':material/mic:'):
                voice_attendance_dialog(selected_subject_id)


def run_face_analysis(subject_id):
    all_detected_ids = {}

    with st.spinner("Deep scanning classroom photos..."):
        try:
            for idx, img in enumerate(st.session_state.attendance_images):
                img_np = np.array(img.convert('RGB'))
                detected, _, _ = predict_attendance(img_np)

                for sid in (detected or {}).keys():
                    all_detected_ids.setdefault(int(sid), []).append(f"Photo {idx+1}")

            enrolled_students = (
                supabase.table('subject_students').select("*, students(*)")
                .eq('subject_id', subject_id).execute().data
            )
        except Exception as e:
            st.error(f"Face analysis failed: {e}")
            return

    if not enrolled_students:
        st.warning("No students are enrolled in this subject yet. Share the subject code so students can join.")
        return

    results, attendance_to_log = [], []
    current_timestamp = datetime.now().astimezone().isoformat(timespec="seconds")

    for node in enrolled_students:
        student = node['students']
        sources = all_detected_ids.get(int(student['student_id']), [])
        is_present = len(sources) > 0

        results.append({
            "Name": student['name'],
            "ID": student['student_id'],
            "Seen in": ", ".join(sources) if is_present else "-",
            "Status": "✅ Present" if is_present else "❌ Absent"
        })

        attendance_to_log.append({
            'student_id': student['student_id'],
            "subject_id": subject_id,
            "timestamp": current_timestamp,
            "is_present": bool(is_present)
        })

    attendance_result_dialog(pd.DataFrame(results), attendance_to_log)


def teacher_tab_manage_subjects(subjects, teacher_id):
    col1, col2 = st.columns([3, 1], vertical_alignment='center')
    with col1:
        st.subheader("Your Subjects")
    with col2:
        if st.button("New Subject", type='primary', icon=':material/add:', width='stretch'):
            create_subject_dialog(teacher_id)

    if not subjects:
        with st.container(key="card_no_subjects"):
            empty_state("No subjects found", "Create one with the <b>New Subject</b> button above.")
        return

    cols = st.columns(2)
    for i, sub in enumerate(subjects):
        def share_btn(sub=sub):
            if st.button("Share join code", key=f"share_{sub['subject_code']}", icon=":material/share:", width='stretch'):
                share_subject_dialog(sub['name'], sub['subject_code'])

        with cols[i % 2]:
            subject_card(
                name=sub['name'],
                code=sub['subject_code'],
                section=sub['section'],
                stats=[
                    ("Students", sub['total_students']),
                    ("Classes", sub['total_classes'])
                ],
                footer_callback=share_btn
            )


def format_time(ts):
    try:
        return datetime.fromisoformat(ts).astimezone().strftime("%d %b %Y, %I:%M %p")
    except (TypeError, ValueError):
        return "N/A"


def teacher_tab_attendance_records(teacher_id):
    with st.container(key="card_records"):
        st.subheader("Attendance Records")

        try:
            records = get_attendance_for_teacher(teacher_id)
        except Exception:
            st.error("Couldn't load attendance records. Please try again.")
            return

        if not records:
            empty_state("No records yet", "Attendance you save will show up here.")
            return

        data = [{
            "ts_group": (r.get("timestamp") or "").split(".")[0],
            "Time": format_time(r.get("timestamp")),
            "Subject": r['subjects']['name'],
            "Subject Code": r['subjects']['subject_code'],
            "is_present": bool(r.get("is_present", False))
        } for r in records]

        df = pd.DataFrame(data)

        subject_filter = st.selectbox("Filter by subject", ["All subjects"] + sorted(df["Subject"].unique()))
        if subject_filter != "All subjects":
            df = df[df["Subject"] == subject_filter]

        summary = (
            df.groupby(['ts_group', 'Time', "Subject", "Subject Code"])
            .agg(Present=('is_present', 'sum'), Total=("is_present", 'count'))
            .reset_index()
        )
        summary["Attendance"] = summary["Present"] / summary["Total"] * 100
        summary["Present"] = summary["Present"].astype(str) + " / " + summary["Total"].astype(str)

        display_df = summary.sort_values(by='ts_group', ascending=False)[
            ['Time', "Subject", "Subject Code", "Present", "Attendance"]
        ]

        st.dataframe(
            display_df,
            width='stretch',
            hide_index=True,
            column_config={
                "Attendance": st.column_config.ProgressColumn("Attendance", format="%.0f%%", min_value=0, max_value=100),
            },
        )


def login_teacher(username, password):
    teacher = teacher_login(username, password)

    if teacher:
        st.session_state.user_role = 'teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True

    return False


def auth_header(title, subtitle):
    st.markdown(f"<div class='sc-auth-head'><h2>{title}</h2><p>{subtitle}</p></div>", unsafe_allow_html=True)


def teacher_screen_login():
    top_bar()

    _, mid, _ = st.columns([1, 3, 1])
    with mid:
        with st.container(key="card_teacher_login"):
            auth_header("Welcome back, Teacher", "Log in to manage your classes.")

            with st.form("teacher_login_form", border=False):
                username = st.text_input("Gmail", placeholder='e.g. jahnavi@gmail.com')
                password = st.text_input("Password", type='password', placeholder='Your password')
                submitted = st.form_submit_button('Log in', type='primary', icon=':material/login:', width='stretch')

            if submitted:
                username = username.strip().lower()
                if not username or not password:
                    st.warning("Please enter your Gmail and password.")
                else:
                    try:
                        ok = login_teacher(username, password)
                    except Exception:
                        ok = None
                        st.error("Couldn't reach the server. Check your internet connection.")
                    if ok:
                        st.toast(f"Welcome back {st.session_state.teacher_data['name']}!", icon=":material/waving_hand:")
                        st.rerun()
                    elif ok is False:
                        st.error("Invalid Gmail or password.")

            st.divider()
            st.caption("New to SnapClass?")
            if st.button('Create a teacher account', type='secondary', icon=':material/person_add:', width='stretch'):
                st.session_state.teacher_login_type = 'register'
                st.rerun()

    footer_dashboard()


def register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm):
    if not teacher_username or not teacher_name or not teacher_pass:
        return False, "All fields are required!"
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", teacher_username):
        return False, "Please enter a valid Gmail address"
    if len(teacher_pass) < 6:
        return False, "Password must be at least 6 characters"
    if teacher_pass != teacher_pass_confirm:
        return False, "Passwords don't match"

    try:
        if check_teacher_exists(teacher_username):
            return False, "An account with this Gmail already exists"
        create_teacher(teacher_username, teacher_pass, teacher_name)
        return True, "Account created! Log in now."
    except Exception:
        return False, "Couldn't create your account. Please try again."


def teacher_screen_register():
    top_bar()

    _, mid, _ = st.columns([1, 3, 1])
    with mid:
        with st.container(key="card_teacher_register"):
            auth_header("Create teacher account", "Set up your profile in seconds.")

            with st.form("teacher_register_form", border=False):
                teacher_name = st.text_input("Full name", placeholder='Jahnavi Pasupuleti')
                teacher_username = st.text_input("Gmail", placeholder='e.g. jahnavi@gmail.com')
                teacher_pass = st.text_input("Password", type='password', placeholder='At least 6 characters')
                teacher_pass_confirm = st.text_input("Confirm password", type='password', placeholder='Repeat password')
                submitted = st.form_submit_button('Register', type='primary', icon=':material/how_to_reg:', width='stretch')

            if submitted:
                success, message = register_teacher(
                    teacher_username.strip().lower(), teacher_name.strip(), teacher_pass, teacher_pass_confirm
                )

                if success:
                    st.toast(message, icon=":material/check_circle:")
                    st.session_state.teacher_login_type = "login"
                    st.rerun()
                else:
                    st.error(message)

            st.divider()
            st.caption("Already have an account?")
            if st.button('Log in instead', type='secondary', icon=':material/login:', width='stretch'):
                st.session_state.teacher_login_type = 'login'
                st.rerun()

    footer_dashboard()
