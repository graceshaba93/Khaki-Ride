from components.navigation import page_header, require_role
from models.user import Role

require_role(Role.ADMIN)
page_header("Transport Assignments", "Placeholder. This page is built in a later stage.")
