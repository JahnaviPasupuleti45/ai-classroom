import streamlit as st
import html


def subject_card(name, code, section, stats=None, footer_callback=None, progress=None):

    name = html.escape(str(name))
    safe_code = html.escape(str(code))
    section = html.escape(str(section or "-"))

    html_content = f"""
<div style="border-left:6px solid #EB459E; padding-left:14px; margin-bottom:12px;">
<h3 style="margin:0; color:#1E293B; font-size:1.35rem;">{name}</h3>
<p style="color:#64748B; margin:6px 0 0;">
<span style="background:#EEF0FF; color:#5865F2; padding:2px 10px; border-radius:999px; font-weight:600;">{safe_code}</span>
&nbsp;Section {section}
</p>
</div>
"""

    if stats:
        html_content += '<div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:12px;">'
        for label, value in stats:
            html_content += (
                '<div style="background:#FCE7F3; padding:5px 12px; border-radius:12px; font-size:0.9rem; color:#1E293B;">'
                f'<b>{html.escape(str(value))}</b> {html.escape(str(label))}</div>'
            )
        html_content += "</div>"

    if progress is not None:
        pct = max(0, min(100, round(progress * 100)))
        html_content += f"""
<div style="display:flex; justify-content:space-between; font-size:0.85rem; color:#64748B; margin-bottom:4px;">
<span>Attendance</span><b style="color:#1E293B;">{pct}%</b>
</div>
<div style="height:8px; background:#EEF0FF; border-radius:999px; overflow:hidden; margin-bottom:12px;">
<div style="height:100%; width:{pct}%; background:linear-gradient(90deg,#5865F2,#EB459E);"></div>
</div>
"""

    with st.container(key=f"card_subject_{code}"):
        st.html(html_content)
        if footer_callback:
            footer_callback()
