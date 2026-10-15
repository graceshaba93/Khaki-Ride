from components.navigation import page_header, require_role
from models.user import Role

require_role(Role.CORPS_MEMBER)
page_header("Journey Details", "Placeholder. This page is built in a later stage.")
