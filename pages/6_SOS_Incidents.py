import pandas as pd
import streamlit as st

from components.navigation import page_header, require_role
from models.user import Role
from services.mock_data_service import (
    get_buses,
    get_incidents,
    get_journeys,
    get_members,
    get_routes,
    initialize_demo_data,
    update_incident_status,
)

require_role(Role.ADMIN)
initialize_demo_data()

page_header(
    "SOS Incidents",
    "Review emergency reports and update incident response status.",
)

incidents = get_incidents()
members = get_members()
journeys = get_journeys()
buses = get_buses()
routes = get_routes()

member_lookup = {
    item.get("member_id"): item
    for item in members
}

journey_lookup = {
    item.get("journey_id"): item
    for item in journeys
}

bus_lookup = {
    item.get("bus_id"): item
    for item in buses
}

route_lookup = {
    item.get("route_id"): item
    for item in routes
}

open_incidents = [
    incident for incident in incidents
    if incident.get("status") == "Open"
]

active_incidents = [
    incident for incident in incidents
    if incident.get("status") != "Resolved"
]

high_priority = [
    incident for incident in active_incidents
    if incident.get("priority") == "High"
]

col1, col2, col3 = st.columns(3)

col1.metric("Total incidents", len(incidents))
col2.metric("Open incidents", len(open_incidents))
col3.metric("Active high-priority incidents", len(high_priority))

if open_incidents:
    st.error(
        f"{len(open_incidents)} incident(s) require attention."
    )
else:
    st.success("There are no open incidents.")

st.divider()
st.subheader("Incident register")

if not incidents:
    st.info("No SOS incidents have been reported.")
else:
    rows = []

    for incident in incidents:
        member = member_lookup.get(incident.get("member_id"), {})
        journey = journey_lookup.get(incident.get("journey_id"), {})
        bus = bus_lookup.get(journey.get("bus_id"), {})
        route = route_lookup.get(journey.get("route_id"), {})

        rows.append(
            {
                "Incident ID": incident.get("incident_id"),
                "Corps member": member.get("name", "Unknown member"),
                "Member ID": incident.get("member_id"),
                "Category": incident.get("category"),
                "Priority": incident.get("priority"),
                "Status": incident.get("status"),
                "Location": incident.get("location"),
                "Bus": bus.get("registration", "Not assigned"),
                "Route": (
                    f"{route.get('origin', '?')} → "
                    f"{route.get('destination', '?')}"
                    if route
                    else "Not assigned"
                ),
                "Reported at": incident.get("reported_at"),
            }
        )

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
    )

st.divider()
st.subheader("Review and update an incident")

if incidents:
    incident_options = {
        (
            f"{item.get('incident_id')} — "
            f"{item.get('category')} — "
            f"{item.get('status')}"
        ): item.get("incident_id")
        for item in incidents
    }

    selected_label = st.selectbox(
        "Select an incident",
        list(incident_options.keys()),
    )

    selected_id = incident_options[selected_label]

    selected = next(
        (
            item for item in incidents
            if item.get("incident_id") == selected_id
        ),
        None,
    )

    if selected:
        member = member_lookup.get(selected.get("member_id"), {})
        journey = journey_lookup.get(selected.get("journey_id"), {})
        bus = bus_lookup.get(journey.get("bus_id"), {})
        route = route_lookup.get(journey.get("route_id"), {})

        st.markdown(f"### {selected.get('incident_id')}")

        left, right = st.columns(2)

        with left:
            st.write(
                f"**Corps member:** {member.get('name', 'Unknown member')}"
            )
            st.write(
                f"**Member ID:** {selected.get('member_id', 'N/A')}"
            )
            st.write(
                f"**Emergency type:** {selected.get('category', 'N/A')}"
            )
            st.write(
                f"**Priority:** {selected.get('priority', 'N/A')}"
            )

        with right:
            st.write(
                f"**Current status:** {selected.get('status', 'N/A')}"
            )
            st.write(
                f"**Location:** {selected.get('location', 'Not provided')}"
            )
            st.write(
                f"**Bus:** {bus.get('registration', 'Not assigned')}"
            )

            if route:
                st.write(
                    f"**Route:** {route.get('origin')} → "
                    f"{route.get('destination')}"
                )

        st.write(
            f"**Description:** "
            f"{selected.get('description', 'No description provided.')}"
        )

        current_status = selected.get("status", "Open")

        col1, col2 = st.columns(2)

        with col1:
            if current_status == "Open":
                if st.button(
                    "Acknowledge incident",
                    type="primary",
                    use_container_width=True,
                ):
                    success, message = update_incident_status(
                        selected_id,
                        "Acknowledged",
                    )

                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

        with col2:
            if current_status != "Resolved":
                if st.button(
                    "Mark as resolved",
                    use_container_width=True,
                ):
                    success, message = update_incident_status(
                        selected_id,
                        "Resolved",
                    )

                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
