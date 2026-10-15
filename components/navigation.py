"""Page header, sidebar user block, and role guard shared by every page."""
import streamlit as st

from models.user import Role
from services.auth_service import get_current_user, sign_out
from utils.constants import APP_NAME, DEMO_DATE


def require_role(role: Role) -> None:
    """Stop the page if the signed-in user doesn't have `role`.

    Frontend check only. The real backend must enforce authorization too.
    """
    user = get_current_user()
    if user is None or user.role != role:
        st.error("You do not have access to this page.")
        st.stop()


def page_header(title: str, subtitle: str = "") -> None:
    sub = f'<div class="page-sub">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f"""
        <div class="page-title-row">
          <div><h1>{title}</h1>{sub}</div>
          <div class="page-meta">
            <span class="demo-badge">DEMO DATA</span><br>
            Demonstration date: {DEMO_DATE.strftime('%d %b %Y')}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_user() -> None:
    user = get_current_user()
    if user is None:
        return
    with st.sidebar:
        st.divider()
        st.markdown(f"**{user.name}**")
        st.caption(f"{user.role.label}\n\n{user.email}")
        if st.button("Sign out", use_container_width=True):
            sign_out()
            st.rerun()
        st.caption(f"{APP_NAME} demo. All data is simulated.")
