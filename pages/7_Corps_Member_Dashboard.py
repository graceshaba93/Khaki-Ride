import streamlit as st

from components.navigation import page_header, require_role
from models.user import Role
from services.auth_service import get_current_user
from services.mock_data_service import (
    create_sos_incident,
    get_buses,
    get_journeys,
    get_members,
    get_routes,
    initialize_demo_data,
)

require_role(Role.CORPS_MEMBER)
initialize_demo_data()

user = get_current_user()

page_header(
    "My Journey",
    "View your transport assignment and report an emergency.",
)

members = get_members()
buses = get_buses()
routes = get_routes()
journeys = get_journeys()

# Match the signed-in account to its own corps member record.
member = next(
    (
        item for item in members
        if str(item.get("email", "")).lower() == user.email.lower()
    ),
    None,
)

# The original demo account predates the registration workflow.
if member is None and user.email.lower() == "corps@demo.kopa-ride.test":
    member = next(
        (
            item for item in members
            if item.get("member_id") == "CM-001"
        ),
        None,
    )

if member is None:
    st.warning(
        "We couldn't find a corps member record linked to your account. "
        "Please contact the transport administrator."
    )
    st.stop()

member_id = member.get("member_id")
bus_id = member.get("bus_id")
journey_id = member.get("journey_id")

bus = next(
    (item for item in buses if item.get("bus_id") == bus_id),
    None,
)

journey = next(
    (
        item for item in journeys
        if item.get("journey_id") == journey_id
    ),
    None,
)

route_id = (
    journey.get("route_id") if journey
    else bus.get("route_id") if bus
    else None
)

route = next(
    (
        item for item in routes
        if item.get("route_id") == route_id
    ),
    None,
)

registration_status = member.get(
    "registration_status",
    "Previously registered demo member",
)

journey_status = (
    journey.get("status")
    if journey
    else member.get("status", "Awaiting assignment")
)

st.subheader(f"Welcome, {member.get('name', user.name)}")
st.caption(f"Member ID: {member_id}")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Registration",
    registration_status,
)

col2.metric(
    "Transport status",
    journey_status,
)

col3.metric(
    "NYSC state code",
    member.get("state_code", "Not provided"),
)

st.divider()

st.subheader("Your transport assignment")

if registration_status == "Pending approval":
    st.warning(
        "Your registration is awaiting administrator approval. "
        "Transport details will become available after approval and assignment."
    )

elif not bus or not journey:
    st.info(
        "You do not have a transport assignment yet. "
        "Please wait for the administrator to assign a bus and journey."
    )

else:
    left, right = st.columns(2)

    with left:
        st.markdown("#### Vehicle and driver")
        st.write(f"**Bus registration:** {bus.get('registration', 'N/A')}")
        st.write(f"**Driver:** {bus.get('driver', 'Not provided')}")
        st.write(f"**Vehicle status:** {bus.get('status', 'Unknown')}")
        st.write(f"**Passenger capacity:** {bus.get('capacity', 'N/A')}")

    with right:
        st.markdown("#### Journey details")

        if route:
            st.write(f"**Origin:** {route.get('origin', 'N/A')}")
            st.write(f"**Destination:** {route.get('destination', 'N/A')}")
            st.write(f"**Scheduled departure:** {journey.get('departure', route.get('departure', 'N/A'))}")
            st.write(f"**Estimated arrival:** {journey.get('estimated_arrival', 'Not available')}")
        else:
            st.write("Route information is not available.")

        st.write(
            f"**Pickup point:** {member.get('pickup_point') or 'To be confirmed'}"
        )
        st.write(f"**Journey ID:** {journey_id}")

    st.info(
        "Vehicle and journey information comes from demonstration records. "
        "It is not a live GPS feed."
    )

st.divider()

st.subheader("Emergency assistance")
st.warning(
    "Use this form to report an emergency to the demonstration system. "
    "This prototype does not send a real emergency dispatch or contact "
    "emergency services."
)

with st.form("member_sos_form"):
    category = st.selectbox(
        "Type of emergency",
        [
            "Personal safety",
            "Medical emergency",
            "Vehicle breakdown",
            "Road incident",
            "Harassment or threat",
            "Other emergency",
        ],
    )

    description = st.text_area(
        "Describe the emergency",
        placeholder="Explain what happened and what assistance is needed.",
    )

    location = st.text_input(
        "Your current location (if known)",
        placeholder="Enter a landmark, town, or nearby location",
        help="Enter your location manually. This form does not access GPS.",
    )

    submitted = st.form_submit_button(
        "🚨 Send SOS Emergency Alert",
        type="primary",
        use_container_width=True,
    )

if submitted:
    if not description.strip():
        st.error("Please describe the emergency before submitting.")
    else:
        success, message = create_sos_incident(
            member_id=member_id,
            journey_id=journey_id,
            category=category,
            description=description,
            location=location,
        )

        if success:
            st.success(message)
            st.info(
                "The incident has been recorded in this demo session. "
                "It has not been sent to an external emergency service."
            )
        else:
            st.error(message)

