"""Entry point. Chooses which pages exist based on the signed-in user's role."""
import streamlit as st

from components.login_view import render_login
from components.navigation import render_sidebar_user
from components.theme import inject_css
from models.user import Role
from services.auth_service import get_current_user
from utils.constants import APP_NAME

st.set_page_config(page_title=APP_NAME, layout="wide", initial_sidebar_state="auto")
inject_css()

user = get_current_user()

if user is None:
    # Only the login page exists for signed-out visitors.
    pg = st.navigation([st.Page(render_login, title="Sign in", url_path="login")], position="hidden")
elif user.role == Role.ADMIN:
    pg = st.navigation({
        "Operations": [
            st.Page("pages/1_Admin_Dashboard.py", title="Dashboard", url_path="dashboard", default=True),
            st.Page("pages/2_Live_Tracking.py", title="Live Tracking", url_path="tracking"),
        ],
        "Records": [
            st.Page("pages/3_Corps_Members.py", title="Corps Members", url_path="members"),
            st.Page("pages/4_Buses_and_Routes.py", title="Buses and Routes", url_path="buses"),
            st.Page("pages/5_Transport_Assignments.py", title="Assignments", url_path="assignments"),
        ],
        "Safety": [
            st.Page("pages/6_SOS_Incidents.py", title="SOS Incidents", url_path="sos"),
        ],
    })
else:
    pg = st.navigation({
        "My journey": [
            st.Page("pages/7_Corps_Member_Dashboard.py", title="My Journey", url_path="my-journey", default=True),
            st.Page("pages/8_Journey_Details.py", title="Journey Details", url_path="journey-details"),
        ],
    })

render_sidebar_user()
pg.run()