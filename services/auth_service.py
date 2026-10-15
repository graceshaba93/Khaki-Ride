"""
Demonstration authentication for Kopa-Ride.

This is prototype-only authentication. A production application must use
a secure backend and persistent user database.
"""

import hashlib
import hmac
import secrets
from dataclasses import dataclass

import streamlit as st

from models.user import Role, User


_DEMO_ACCOUNTS = {
    "coordinator@demo.kopa-ride.test": {
        "user": User(
            "U-ADM-001",
            "Demo Coordinator",
            "coordinator@demo.kopa-ride.test",
            Role.ADMIN,
        ),
        "hash": (
            "pbkdf2_sha256$200000$a1f3c9d27b6e4a10$"
            "4e1205e5c191a3890ab49ad03427df5b0855cb942b89c826"
            "e03c017708b28632"
        ),
    },
    "corps@demo.kopa-ride.test": {
        "user": User(
            "U-CM-001",
            "Demo Corps Member",
            "corps@demo.kopa-ride.test",
            Role.CORPS_MEMBER,
        ),
        "hash": (
            "pbkdf2_sha256$200000$5e8b0d4c91f27a63$"
            "30a8e375f60c586fd00063d1165b2007331c44f11eb612452"
            "c9987e5c8d3ff50"
        ),
    },
}


@dataclass
class AuthResult:
    success: bool
    user: User | None = None
    error: str | None = None


def _hash_password(password: str) -> str:
    """Create a salted PBKDF2 password hash."""
    iterations = 200_000
    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations,
    )

    return (
        f"pbkdf2_sha256${iterations}$"
        f"{salt.hex()}${password_hash.hex()}"
    )


def _verify(password: str, stored: str) -> bool:
    """Compare a password with its stored hash."""
    try:
        algorithm, iterations, salt_hex, hash_hex = stored.split("$")

        if algorithm != "pbkdf2_sha256":
            return False

        candidate = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations),
        )

        return hmac.compare_digest(candidate.hex(), hash_hex)

    except (ValueError, TypeError):
        return False


def register_demo_account(
    email: str,
    password: str,
    name: str,
    member_id: str,
) -> tuple[bool, str]:
    """Create a demo login for a registered corps member."""
    email = email.strip().lower()

    accounts = st.session_state.setdefault(
        "demo_registered_accounts", {}
    )

    if email in _DEMO_ACCOUNTS or email in accounts:
        return False, "An account with this email already exists."

    accounts[email] = {
        "user": User(
            f"U-{member_id}",
            name.strip(),
            email,
            Role.CORPS_MEMBER,
        ),
        "hash": _hash_password(password),
        "member_id": member_id,
    }

    return True, "Demo account created."


def authenticate(
    email: str,
    password: str,
    selected_role: Role,
) -> AuthResult:
    """Authenticate a demo or registered account."""
    email = email.strip().lower()

    account = _DEMO_ACCOUNTS.get(email)

    if account is None:
        account = st.session_state.get(
            "demo_registered_accounts", {}
        ).get(email)

    if account is None or not _verify(password, account["hash"]):
        return AuthResult(
            False,
            error="Incorrect email or password.",
        )

    user: User = account["user"]

    if user.role != selected_role:
        return AuthResult(
            False,
            error=(
                f"This account is not a {selected_role.label} account. "
                "Select the correct account type and try again."
            ),
        )

    # Newly registered corps members must be approved first.
    if email not in _DEMO_ACCOUNTS:
        from services.mock_data_service import get_members

        member_id = account.get("member_id")
        member = next(
            (
                item
                for item in get_members()
                if item.get("member_id") == member_id
            ),
            None,
        )

        if member is None:
            return AuthResult(
                False,
                error="Registration record not found. Contact the administrator.",
            )

        if member.get("registration_status") != "Approved":
            return AuthResult(
                False,
                error=(
                    "Your registration is awaiting administrator approval. "
                    "Please try again after it has been approved."
                ),
            )

    return AuthResult(True, user=user)


def get_current_user() -> User | None:
    return st.session_state.get("user")


def sign_in(user: User) -> None:
    st.session_state["user"] = user


def sign_out() -> None:
    """Sign out without deleting the demo application's other session data."""
    st.session_state.pop("user", None)
