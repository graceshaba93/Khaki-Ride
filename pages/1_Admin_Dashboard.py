"""Kopa-Ride administrator operations dashboard."""

import pandas as pd
import pydeck as pdk
import streamlit as st

from components.navigation import page_header, require_role
from models.user import Role
from services.mock_data_service import (
    get_buses,
    get_dashboard_metrics,
    get_incidents,
    get_journeys,
    get_members,
    get_recent_activity,
    get_routes,
)
from utils.constants import COLOR_PRIMARY

require_role(Role.ADMIN)

page_header(
    "Operations Dashboard",
    "Monitor transport activity, fleet availability and journey exceptions.",
)

st.caption(
    "DEMO ENVIRONMENT · All vehicles, journeys, locations and incidents "
    "are simulated."
)

# -------------------------------------------------------------------
# Data
# -------------------------------------------------------------------

metrics = get_dashboard_metrics()
buses = get_buses()
routes = get_routes()
members = get_members()
journeys = get_journeys()
incidents = get_incidents()
activity = get_recent_activity()

route_lookup = {
    route["route_id"]: route
    for route in routes
}

member_lookup = {
    member["member_id"]: member
    for member in members
}

# -------------------------------------------------------------------
# Operational metrics
# -------------------------------------------------------------------

st.subheader("Operational summary")

metric_columns = st.columns(5)

metric_columns[0].metric(
    "Total buses",
    metrics["total_buses"],
)

metric_columns[1].metric(
    "Active journeys",
    metrics["active_journeys"],
)

metric_columns[2].metric(
    "Members assigned",
    metrics["assigned_members"],
)

metric_columns[3].metric(
    "Delayed journeys",
    metrics["delayed_journeys"],
)

metric_columns[4].metric(
    "Open incidents",
    metrics["open_incidents"],
)

st.divider()

# -------------------------------------------------------------------
# Map and operational alerts
# -------------------------------------------------------------------

map_column, alerts_column = st.columns(
    [1.65, 1],
    gap="large",
)

with map_column:
    st.subheader("Fleet overview")
    st.caption(
        "Illustrative bus positions only. This is not live GPS tracking."
    )

    mapped_buses = [
        bus for bus in buses
        if bus.get("latitude") is not None
        and bus.get("longitude") is not None
    ]

    if mapped_buses:
        map_data = pd.DataFrame(mapped_buses)

        map_data["route"] = map_data["route_id"].map(
            lambda route_id: (
                f"{route_lookup[route_id]['origin']} – "
                f"{route_lookup[route_id]['destination']}"
                if route_id in route_lookup
                else "Route not assigned"
            )
        )

        # Use colour to reinforce the text status.
        status_colours = {
            "In transit": [31, 105, 75, 220],
            "Available": [95, 110, 104, 220],
            "Delayed": [183, 121, 31, 230],
            "Maintenance": [100, 105, 110, 220],
        }

        map_data["colour"] = map_data["status"].map(
            lambda status: status_colours.get(
                status,
                [95, 110, 104, 220],
            )
        )

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_data,
            get_position="[longitude, latitude]",
            get_fill_color="colour",
            get_radius=1800,
            pickable=True,
            auto_highlight=True,
        )

        tooltip = {
            "html": (
                "<b>{bus_id}</b><br/>"
                "Route: {route}<br/>"
                "Status: {status}<br/>"
                "Last simulated update: {last_update}"
            ),
            "style": {
                "backgroundColor": "#23282B",
                "color": "white",
                "fontSize": "12px",
                "padding": "8px",
            },
        }

        view_state = pdk.ViewState(
            latitude=float(map_data["latitude"].mean()),
            longitude=float(map_data["longitude"].mean()),
            zoom=9,
            pitch=0,
        )

        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip=tooltip,
            map_style=None,
        )

        try:
            st.pydeck_chart(
                deck,
                use_container_width=True,
                height=330,
            )
        except Exception:
            st.info(
                "The map could not be rendered in this environment. "
                "Use the bus table below to inspect the simulated positions."
            )

        st.caption(
            "Map markers represent fictional coordinates. "
            "A basemap may require network access."
        )
    else:
        st.info("No simulated bus coordinates are available.")

    fleet_table = pd.DataFrame(
        [
            {
                "Bus": bus["bus_id"],
                "Route": (
                    f"{route_lookup[bus['route_id']]['origin']} – "
                    f"{route_lookup[bus['route_id']]['destination']}"
                    if bus.get("route_id") in route_lookup
                    else "Unassigned"
                ),
                "Status": bus["status"],
                "Last update": bus.get("last_update", "Not available"),
            }
            for bus in buses
        ]
    )

    st.dataframe(
        fleet_table,
        hide_index=True,
        use_container_width=True,
    )

with alerts_column:
    st.subheader("Operational alerts")

    delayed_journeys = [
        journey for journey in journeys
        if journey["status"] == "Delayed"
    ]

    open_incidents = [
        incident for incident in incidents
        if incident["status"] != "Resolved"
    ]

    unassigned_members = [
        member for member in members
        if member["status"] == "Awaiting assignment"
    ]

    st.markdown("**Delayed journeys**")
    if delayed_journeys:
        for journey in delayed_journeys:
            route = route_lookup.get(journey["route_id"], {})
            route_name = (
                f"{route.get('origin', 'Unknown')} – "
                f"{route.get('destination', 'Unknown')}"
            )
            st.warning(
                f"{journey['journey_id']} · {journey['bus_id']} · "
                f"{route_name}"
            )
    else:
        st.caption("No delayed journeys in the demo data.")

    st.markdown("**SOS incidents requiring attention**")
    if open_incidents:
        for incident in open_incidents:
            member = member_lookup.get(incident["member_id"], {})
            st.warning(
                f"{incident['incident_id']} · "
                f"{incident['category']} · "
                f"{member.get('name', 'Unknown member')} · "
                f"{incident['status']}"
            )
    else:
        st.caption("No unresolved incidents in the demo data.")

    st.markdown("**Members awaiting assignment**")
    if unassigned_members:
        for member in unassigned_members:
            st.write(
                f"• {member['member_id']} — {member['name']}"
            )
    else:
        st.caption("All demo members have an assignment.")

    st.markdown("**Fleet availability**")
    available_buses = sum(
        bus["status"] == "Available"
        for bus in buses
    )
    st.write(
        f"{available_buses} of {len(buses)} buses currently "
        "have the simulated status 'Available'."
    )

st.divider()

# -------------------------------------------------------------------
# Recent journeys
# -------------------------------------------------------------------

st.subheader("Recent journeys")

if journeys:
    journey_rows = []

    for journey in journeys:
        route = route_lookup.get(journey["route_id"], {})

        journey_rows.append(
            {
                "Journey ID": journey["journey_id"],
                "Bus": journey["bus_id"],
                "Route": (
                    f"{route.get('origin', 'Unknown')} – "
                    f"{route.get('destination', 'Unknown')}"
                ),
                "Assigned members": journey["assigned_members"],
                "Departure": journey["departure"],
                "Estimated arrival": journey["estimated_arrival"],
                "Status": journey["status"],
            }
        )

    st.dataframe(
        pd.DataFrame(journey_rows),
        hide_index=True,
        use_container_width=True,
    )
else:
    st.info("No journeys are currently recorded in the demo dataset.")

# -------------------------------------------------------------------
# Recent activity
# -------------------------------------------------------------------

st.subheader("Recent activity")
st.caption(
    "This section displays actions recorded during the current demo session."
)

if activity:
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Action": item["action"],
                    "Details": item["details"],
                    "Time": item["time"],
                }
                for item in activity
            ]
        ),
        hide_index=True,
        use_container_width=True,
    )
else:
    st.caption(
        "No actions have been recorded during this session yet."
    )

st.caption(
    "Kopa-Ride · NYSC Corps Member Transport and Tracking · "
    "Demonstration environment only"
)
