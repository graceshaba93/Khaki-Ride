"""The User model and the Role enum."""
from dataclasses import dataclass
from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    CORPS_MEMBER = "corps_member"

    @property
    def label(self) -> str:
        return {
            Role.ADMIN: "Admin / Transport Coordinator",
            Role.CORPS_MEMBER: "Corps Member",
        }[self]


@dataclass(frozen=True)
class User:
    id: str
    name: str
    email: str
    role: Role
