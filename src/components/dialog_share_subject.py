import streamlit as st

import segno
import io
from urllib.parse import quote


@st.dialog("Share Subject", width="large")
def share_subject_dialog(subject_name, subject_code):
    app_host = st.context.headers.get("Host", "localhost:8501")
    is_local = app_host.startswith(("localhost", "127.0.0.1"))
    scheme = "http" if is_local else "https"
    join_url = f"{scheme}://{app_host}/?join-code={quote(str(subject_code))}"

    qr = segno.make(join_url)
    out = io.BytesIO()
    qr.save(out, kind='png', scale=10, border=1)

    st.markdown(f"Invite students to **{subject_name}**")

    col1, col2 = st.columns([3, 2], vertical_alignment='center')

    with col1:
        st.caption("Join link")
        st.code(join_url, language='text')
        st.caption("Subject code")
        st.code(subject_code, language='text')
        if is_local:
            st.info("This link only works on this computer. Deploy the app to share it with students.", icon=":material/info:")

    with col2:
        st.image(out.getvalue(), caption='Scan to join', width='stretch')
