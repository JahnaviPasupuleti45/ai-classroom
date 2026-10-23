import streamlit as st
from PIL import Image


def _add_photo(file):
    """Add an uploaded/captured file once; widget values repeat on every rerun."""
    seen = st.session_state.setdefault('attendance_photo_ids', [])
    if file.file_id in seen:
        return False
    seen.append(file.file_id)
    st.session_state.attendance_images.append(Image.open(file).convert('RGB'))
    return True


@st.dialog("Add classroom photos")
def add_photos_dialog():
    st.caption("Capture or upload photos of the class. You can add several before running the analysis.")

    cam_tab, upload_tab = st.tabs([":material/photo_camera: Camera", ":material/upload: Upload"])

    with cam_tab:
        cam_photo = st.camera_input("Take snapshot", key='dialog_cam', label_visibility="collapsed")
        if cam_photo and _add_photo(cam_photo):
            st.toast("Photo captured", icon=":material/check_circle:")

    with upload_tab:
        uploaded_files = st.file_uploader('Choose image files', type=['jpg', 'png', 'jpeg'],
                                          accept_multiple_files=True, key='dialog_upload')
        added = sum(_add_photo(f) for f in uploaded_files or [])
        if added:
            st.toast(f"{added} photo{'s' if added != 1 else ''} added", icon=":material/check_circle:")

    count = len(st.session_state.attendance_images)
    st.markdown(f"**{count} photo{'s' if count != 1 else ''} ready**")

    if st.button('Done', type='primary', width='stretch'):
        st.rerun()
