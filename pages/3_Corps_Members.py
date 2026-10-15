import pandas as pd
import streamlit as st

from components.navigation import page_header, require_role
from models.user import Role
from services.mock_data_service import (
    assign_member_to_journey,
    approve_corps_member,
    get_buses,
    get_journeys,
    get_members,
    initialize_demo_data,
)

require_role(Role.ADMIN)
initialize_demo_data()

page_header(
    "Corps Members",
    "Review registrations, approve members, and assign transport.",
)

members = get_members()
buses = get_buses()
journeys = get_journeys()

pending = [
    member for member in members
    if member.get("registration_status") == "Pending approval"
]

approved = [
    member for member in members
    if member.get("registration_status") == "Approved"
]

col1, col2, col3 = st.columns(3)

col1.metric("Total registrations", len(members))
col2.metric("Pending approval", len(pending))
col3.metric("Approved members", len(approved))

st.divider()

st.subheader("Registration records")

if members:
    rows = [
        {
            "Member ID": member.get("member_id"),
            "Full name": member.get("name"),
            "NYSC state code": member.get("state_code"),
            "Email": member.get("email", "Demo record"),
            "Registration": member.get(
                "registration_status",
                "Previously registered demo member",
            ),
            "Bus": next(
                (
                    bus.get("registration")
                    for bus in buses
                    if bus.get("bus_id") == member.get("bus_id")
                ),
                "Not assigned",
            ),
            "Journey": member.get("journey_id") or "Not assigned",
        }
        for member in members
    ]

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No corps member registrations found.")

st.divider()

st.subheader("Review a registration")

if pending:
    pending_options = {
        f"{member['name']} — {member['member_id']}": member["member_id"]
        for member in pending
    }

    selected_label = st.selectbox(
        "Select a pending registration",
        list(pending_options),
        key="review_member",
    )

    selected_id = pending_options[selected_label]

    selected_member = next(
        member for member in pending
        if member["member_id"] == selected_id
    )

    with st.expander("View registration details", expanded=True):
        st.write(f"**Name:** {selected_member['name']}")
        st.write(f"**Email:** {selected_member.get('email', 'Not provided')}")
        st.write(f"**Phone:** {selected_member.get('phone', 'Not provided')}")
        st.write(f"**State code:** {selected_member.get('state_code', 'Not provided')}")
        st.write(f"**Batch:** {selected_member.get('batch', 'Not provided')}")
        st.write(
            f"**Deployment:** "
            f"{selected_member.get('deployment_state', 'Not provided')} — "
            f"{selected_member.get('deployment_lga', 'Not provided')}"
        )
        st.write(f"**PPA:** {selected_member.get('ppa', 'Not provided')}")
        st.write(
            f"**Emergency contact:** "
            f"{selected_member.get('emergency_contact_name', 'Not provided')} — "
            f"{selected_member.get('emergency_contact_phone', 'Not provided')}"
        )

    if st.button(
        "Approve registration",
        type="primary",
        key="approve_registration",
    ):
        success, message = approve_corps_member(selected_id)

        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)
else:
    st.info("There are no registrations awaiting approval.")

st.divider()

st.subheader("Assign a bus and journey")

eligible_members = [
    member for member in members
    if member.get("registration_status") == "Approved"
    and not member.get("bus_id")
]

assignable_journeys = [
    journey for journey in journeys
    if str(journey.get("status", "")).lower()
    not in {"arrived", "completed", "cancelled"}
]

available_buses = [
    bus for bus in buses
    if str(bus.get("status", "")).lower()
    not in {"maintenance", "offline"}
]

if eligible_members and available_buses and assignable_journeys:
    with st.form("transport_assignment_form"):
        member_options = {
            f"{member['name']} — {member['member_id']}": member["member_id"]
            for member in eligible_members
        }

        selected_member_label = st.selectbox(
            "Approved corps member",
            list(member_options),
        )

        bus_options = {
            f"{bus['registration']} — {bus['driver']}": bus["bus_id"]
            for bus in available_buses
        }

        selected_bus_label = st.selectbox(
            "Bus and driver",
            list(bus_options),
        )

        selected_bus_id = bus_options[selected_bus_label]

        matching_journeys = [
            journey for journey in assignable_journeys
            if journey.get("bus_id") == selected_bus_id
        ]

        if matching_journeys:
            journey_options = {
                (
                    f"{journey['journey_id']} — "
                    f"{journey['status']} — "
                    f"{journey['route_id']}"
                ): journey["journey_id"]
                for journey in matching_journeys
            }

            selected_journey_label = st.selectbox(
                "Journey",
                list(journey_options),
            )

            submit_assignment = st.form_submit_button(
                "Assign transport",
                type="primary",
            )
        else:
            journey_options = {}
            selected_journey_label = None
            submit_assignment = st.form_submit_button(
                "No matching journey available",
                disabled=True,
            )

    if submit_assignment and selected_journey_label:
        success, message = assign_member_to_journey(
            member_options[selected_member_label],
            selected_bus_id,
            journey_options[selected_journey_label],
        )

        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)

else:
    if not eligible_members:
        st.info("No approved, unassigned corps members are waiting for transport.")
    elif not available_buses:
        st.warning("No buses are currently eligible for assignment.")
    else:
        st.warning("No assignable journeys are available.")
