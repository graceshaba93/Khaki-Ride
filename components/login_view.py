"""Login and corps member registration for Kopa-Ride."""

import time

import streamlit as st

from models.user import Role
from services.auth_service import (
    authenticate,
    register_demo_account,
    sign_in,
)
from services.mock_data_service import (
    get_members,
    register_corps_member,
)
from utils.constants import APP_NAME, APP_TAGLINE


def render_login() -> None:
    _, centre, _ = st.columns([1, 1.6, 1])

    with centre:
        st.markdown(
            f'<div class="brand">{APP_NAME}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="brand-sub">{APP_TAGLINE}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<span class="demo-badge">DEMONSTRATION ENVIRONMENT</span>',
            unsafe_allow_html=True,
        )
        st.write("")

        mode = st.radio(
            "Welcome to Kopa-Ride",
            ["Sign in", "Register as Corps Member"],
            horizontal=True,
            key="auth_mode",
        )

        if mode == "Sign in":
            _render_sign_in()
        else:
            _render_registration()


def _render_sign_in() -> None:
    with st.form("login_form"):
        st.subheader("Sign in")

        account_label = st.radio(
            "Account type",
            [role.label for role in Role],
            horizontal=False,
        )

        email = st.text_input(
            "Email",
            placeholder="name@example.com",
        )
        password = st.text_input(
            "Password",
            type="password",
        )

        submitted = st.form_submit_button(
            "Sign in",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        _handle_submit(account_label, email, password)

    with st.expander("Demo accounts"):
        st.markdown(
            "**Admin / Transport Coordinator**  \n"
            "`coordinator@demo.kopa-ride.test` / `Admin#Demo2026`\n\n"
            "**Corps Member**  \n"
            "`corps@demo.kopa-ride.test` / `Corps#Demo2026`"
        )
        st.caption(
            "Demonstration credentials only. "
            "They do not work anywhere else."
        )


def _render_registration() -> None:
    st.subheader("Corps Member Registration")
    st.write(
        "Submit your details for administrator review. "
        "You can sign in after your registration is approved."
    )

    with st.form("corps_registration_form"):
        st.markdown("#### Personal information")

        full_name = st.text_input("Full name")
        email = st.text_input("Email address")
        phone = st.text_input("Phone number")

        st.markdown("#### NYSC information")

        state_code = st.text_input(
            "NYSC state code",
            placeholder="e.g. NG/26A/001",
        )
        batch = st.text_input(
            "NYSC batch",
            placeholder="e.g. 2026 Batch B",
        )

        col1, col2 = st.columns(2)

        with col1:
            deployment_state = st.text_input(
                "Deployment state",
                placeholder="e.g. Niger State",
            )

        with col2:
            deployment_lga = st.text_input(
                "Deployment LGA",
                placeholder="e.g. Bida",
            )

        ppa = st.text_input(
            "Place of Primary Assignment (PPA)"
        )

        st.markdown("#### Emergency contact")

        emergency_contact_name = st.text_input(
            "Emergency contact name"
        )
        emergency_contact_phone = st.text_input(
            "Emergency contact phone number"
        )

        st.markdown("#### Create your login")

        password = st.text_input(
            "Password",
            type="password",
            help="Use at least 8 characters for this demonstration.",
        )
        confirm_password = st.text_input(
            "Confirm password",
            type="password",
        )

        submitted = st.form_submit_button(
            "Submit registration",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return

    required_fields = [
        full_name,
        email,
        phone,
        state_code,
        batch,
        deployment_state,
        deployment_lga,
        ppa,
        emergency_contact_name,
        emergency_contact_phone,
        password,
        confirm_password,
    ]

    if not all(value.strip() for value in required_fields):
        st.error("Please complete all required fields.")
        return

    email = email.strip().lower()

    if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
        st.error("Enter a valid email address.")
        return

    reserved_emails = {
        "coordinator@demo.kopa-ride.test",
        "corps@demo.kopa-ride.test",
    }

    if email in reserved_emails:
        st.error("That email is reserved for a demonstration account.")
        return

    if len(password) < 8:
        st.error("Your password must contain at least 8 characters.")
        return

    if password != confirm_password:
        st.error("The passwords do not match.")
        return

    success, message = register_corps_member(
        name=full_name,
        email=email,
        phone=phone,
        state_code=state_code,
        batch=batch,
        deployment_state=deployment_state,
        deployment_lga=deployment_lga,
        ppa=ppa,
        emergency_contact_name=emergency_contact_name,
        emergency_contact_phone=emergency_contact_phone,
    )

    if not success:
        st.error(message)
        return

    # Find the newly created registration to obtain its member ID.
    member = next(
        (
            item
            for item in get_members()
            if str(item.get("email", "")).lower() == email
        ),
        None,
    )

    if member is None:
        st.error(
            "Registration was saved, but the demo account could not be created. "
            "Please contact the administrator."
        )
        return

    account_success, account_message = register_demo_account(
        email=email,
        password=password,
        name=full_name,
        member_id=member["member_id"],
    )

    if not account_success:
        st.error(
            f"Registration was saved, but account creation failed: "
            f"{account_message}"
        )
        return

    st.success(
        f"{message} Your member ID is {member['member_id']}. "
        "Please wait for administrator approval before signing in."
    )


def _handle_submit(
    account_label: str,
    email: str,
    password: str,
) -> None:
    if not email.strip():
        st.error("Enter your email address.")
        return

    if "@" not in email:
        st.error("Enter a valid email address.")
        return

    if not password:
        st.error("Enter your password.")
        return

    selected_role = next(
        role for role in Role if role.label == account_label
    )

    with st.spinner("Signing in..."):
        time.sleep(0.3)
        result = authenticate(email, password, selected_role)

    if result.success and result.user:
        sign_in(result.user)
        st.rerun()
    else:
        st.error(result.error or "Sign-in failed. Try again.")

