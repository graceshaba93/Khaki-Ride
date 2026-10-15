"""Kopa-Ride simulated fleet tracking dashboard."""

import pandas as pd
import pydeck as pdk
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from components.navigation import page_header, require_role
from models.user import Role
from services.mock_data_service import (
    advance_demo_vehicle_positions,
    get_buses,
    get_routes,
)
from utils.constants import (
    COLOR_DANGER,
    COLOR_PRIMARY,
    COLOR_WARNING,
)

# ---------------------------------------------------------
# Page configuration and automatic refresh
# ---------------------------------------------------------

require_role(Role.ADMIN)

st_autorefresh(
    interval=2500,
    limit=None,
    key="kopa_live_tracking_refresh",
)

# Advance the fictional vehicle positions before reading data.
advance_demo_vehicle_positions()

page_header(
    "Live Fleet Tracking",
    "Inspect vehicle positions, route assignments and fleet status.",
)

st.caption(
    "DEMO ENVIRONMENT · Positions and movement are simulated. "
    "This page does not receive live GPS signals."
)

buses = get_buses()
routes = get_routes()

route_lookup = {
    route.get("route_id"): route for route in routes
}


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def get_bus_status(bus):
    return str(bus.get("status", "Unknown")).strip().lower()


def get_registration(bus):
    return bus.get("registration_number") or bus.get("registration") or "Unknown"


def get_driver(bus):
    return bus.get("driver_name") or bus.get("driver") or "Unassigned"


def format_route(bus):
    route = route_lookup.get(bus.get("route_id"), {})

    if route:
        origin = route.get("origin", "")
        destination = route.get("destination", "")

        if origin and destination:
            return f"{origin} → {destination}"

    return bus.get("route_id") or "Unassigned"


def format_coordinates(bus):
    latitude = bus.get("latitude")
    longitude = bus.get("longitude")

    if latitude is None or longitude is None:
        return "Location unavailable"

    return f"{latitude:.5f}, {longitude:.5f}"


moving_statuses = {"moving", "in_transit", "in transit"}
attention_statuses = {
    "delayed", "maintenance", "offline", "issue"
}
idle_statuses = {"idle", "available", "parked"}

moving_buses = [
    bus for bus in buses
    if get_bus_status(bus) in moving_statuses
]
attention_buses = [
    bus for bus in buses
    if get_bus_status(bus) in attention_statuses
]
idle_buses = [
    bus for bus in buses
    if get_bus_status(bus) in idle_statuses
]


# ---------------------------------------------------------
# Fleet overview
# ---------------------------------------------------------

st.subheader("Fleet overview")

metric_columns = st.columns(4)

metric_columns[0].metric("Total vehicles", len(buses))
metric_columns[1].metric("Moving", len(moving_buses))
metric_columns[2].metric("Idle / available", len(idle_buses))
metric_columns[3].metric("Needs attention", len(attention_buses))

# ---------------------------------------------------------
# Prominent active vehicle cards
# ---------------------------------------------------------

st.divider()
st.subheader("🟢 Vehicles currently in transit")

if moving_buses:
    active_columns = st.columns(min(len(moving_buses), 3))

    for index, bus in enumerate(moving_buses):
        with active_columns[index % len(active_columns)]:
            with st.container(border=True):
                st.markdown(f"### 🟢 {get_registration(bus)}")
                st.markdown(f"**Route:** {format_route(bus)}")
                st.caption(f"Driver: {get_driver(bus)}")

                motion = bus.get("motion_state", "Moving")
                st.markdown(f"**{motion}**")

                progress = float(bus.get("journey_progress", 0))
                st.progress(max(0.0, min(progress / 100.0, 1.0)))
                st.caption(f"{progress:.1f}% of simulated route completed")

else:
    st.info("No vehicles are currently in transit in this demo.")

st.divider()


# ---------------------------------------------------------
# Vehicle filters
# ---------------------------------------------------------

st.subheader("Vehicle locations")

filter_columns = st.columns([2, 1])

with filter_columns[0]:
    search_term = st.text_input(
        "Search vehicles",
        placeholder="Search registration, driver or route...",
        key="tracking_search",
    ).strip().lower()

with filter_columns[1]:
    status_options = ["All statuses"] + sorted({
        str(bus.get("status", "Unknown")) for bus in buses
    })

    selected_status = st.selectbox(
        "Filter by status",
        status_options,
        key="tracking_status_filter",
    )

filtered_buses = []

for bus in buses:
    searchable_text = " ".join([
        str(get_registration(bus)),
        str(bus.get("bus_id", "")),
        str(get_driver(bus)),
        format_route(bus),
    ]).lower()

    matches_search = search_term in searchable_text
    matches_status = (
        selected_status == "All statuses"
        or str(bus.get("status", "Unknown")) == selected_status
    )

    if matches_search and matches_status:
        filtered_buses.append(bus)


if not filtered_buses:
    st.info("No vehicles match your search and status filters.")

else:
    # -----------------------------------------------------
    # Selected vehicle
    # -----------------------------------------------------

    bus_labels = {}

    for index, bus in enumerate(filtered_buses):
        label = f"{get_registration(bus)} — {format_route(bus)}"
        bus_labels[label] = index

    selected_vehicle_label = st.selectbox(
        "Inspect a vehicle",
        list(bus_labels.keys()),
        key="selected_tracking_vehicle",
    )

    selected_bus = filtered_buses[bus_labels[selected_vehicle_label]]

    map_column, details_column = st.columns([2, 1], gap="large")

    # -----------------------------------------------------
    # Interactive map
    # -----------------------------------------------------

    with map_column:
        st.markdown("#### Fleet map")

        map_records = []

        for bus in filtered_buses:
            latitude = bus.get("latitude")
            longitude = bus.get("longitude")

            if latitude is None or longitude is None:
                continue

            try:
                latitude = float(latitude)
                longitude = float(longitude)
            except (TypeError, ValueError):
                continue

            if not (-90 <= latitude <= 90):
                continue

            if not (-180 <= longitude <= 180):
                continue

            status = get_bus_status(bus)

            if status in attention_statuses:
                color = [179, 38, 30, 220]
            elif status in moving_statuses:
                color = [31, 77, 58, 230]
            else:
                color = [183, 121, 31, 220]

            map_records.append({
                "bus_id": str(bus.get("bus_id", "Unknown")),
                "registration": str(get_registration(bus)),
                "driver": str(get_driver(bus)),
                "route": format_route(bus),
                "status": str(bus.get("status", "Unknown")),
                "motion_state": str(bus.get("motion_state", "Unknown")),
                "journey_progress": float(bus.get("journey_progress", 0)),
                "latitude": latitude,
                "longitude": longitude,
                "color": color,
                # Moving vehicles are larger and visually prominent.
                "radius": 1900 if status in moving_statuses else 850,
                "outline_color": (
                    [255, 255, 255, 255]
                    if status in moving_statuses
                    else [70, 75, 70, 180]
                ),
                "route_path": bus.get("route_path", []),
                "travelled_path": bus.get("travelled_path", []),
            })

        if map_records:
            map_dataframe = pd.DataFrame(map_records)

            try:
                selected_latitude = float(selected_bus["latitude"])
                selected_longitude = float(selected_bus["longitude"])
            except (KeyError, TypeError, ValueError):
                selected_latitude = 9.08
                selected_longitude = 6.0

            initial_view = pdk.ViewState(
                latitude=selected_latitude,
                longitude=selected_longitude,
                zoom=8,
                pitch=0,
            )

            route_records = [
                {"path": record["route_path"]}
                for record in map_records
                if len(record["route_path"]) >= 2
            ]

            trail_records = [
                {"path": record["travelled_path"]}
                for record in map_records
                if len(record["travelled_path"]) >= 2
            ]

            layers = []

            # Planned route.
            if route_records:
                layers.append(pdk.Layer(
                    "PathLayer",
                    data=route_records,
                    get_path="path",
                    get_color=[150, 155, 150, 170],
                    get_width=3,
                    width_min_pixels=2,
                    pickable=False,
                ))

            # Route already travelled.
            if trail_records:
                layers.append(pdk.Layer(
                    "PathLayer",
                    data=trail_records,
                    get_path="path",
                    get_color=[183, 121, 31, 240],
                    get_width=5,
                    width_min_pixels=3,
                    pickable=False,
                ))

            # Vehicle markers.
            layers.append(pdk.Layer(
                "ScatterplotLayer",
                data=map_dataframe,
                get_position="[longitude, latitude]",
                get_fill_color="color",
                get_radius="radius",
                radius_min_pixels=7,
                radius_max_pixels=24,
                stroked=True,
                get_line_color="outline_color",
                line_width_min_pixels=2,
                pickable=True,
                auto_highlight=True,
            ))

            tooltip = {
                "html": """
                    <b>Vehicle:</b> {registration}<br/>
                    <b>Driver:</b> {driver}<br/>
                    <b>Route:</b> {route}<br/>
                    <b>Operations status:</b> {status}<br/>
                    <b>Movement:</b> {motion_state}<br/>
                    <b>Journey progress:</b> {journey_progress}%
                """,
                "style": {
                    "backgroundColor": "#23282B",
                    "color": "white",
                },
            }

            deck = pdk.Deck(
                layers=layers,
                initial_view_state=initial_view,
                tooltip=tooltip,
                map_style=None,
            )

            st.pydeck_chart(
                deck,
                use_container_width=True,
                height=430,
            )

            st.caption(
                "Green: moving · Amber: idle or other status · "
                "Red: attention required. "
                "Grey: planned route · Amber line: travelled trail."
            )

            st.caption(
                "Route geometry is illustrative and is not verified "
                "road-by-road navigation data."
            )

        else:
            st.warning(
                "No valid vehicle coordinates are available "
                "for the selected filters."
            )

    # -----------------------------------------------------
    # Selected vehicle details
    # -----------------------------------------------------

    with details_column:
        st.markdown("#### Vehicle details")

        st.markdown(f"**{get_registration(selected_bus)}**")
        st.caption(f"Vehicle ID: {selected_bus.get('bus_id', 'Unknown')}")

        st.markdown(f"**Operations status:** {selected_bus.get('status', 'Unknown')}")
        st.markdown(f"**Movement:** {selected_bus.get('motion_state', 'Unknown')}")
        st.markdown(f"**Driver:** {get_driver(selected_bus)}")
        st.markdown(f"**Route:** {format_route(selected_bus)}")
        st.markdown(f"**Capacity:** {selected_bus.get('capacity', 'Not recorded')}")
        st.markdown(f"**Coordinates:** {format_coordinates(selected_bus)}")
        st.markdown(f"**Last update:** {selected_bus.get('last_update', 'Not recorded')}")

        progress = float(selected_bus.get("journey_progress", 0))

        st.markdown("**Simulated journey progress**")
        st.progress(max(0.0, min(progress / 100.0, 1.0)))
        st.caption(f"{progress:.1f}% of the route")

        st.markdown("**Latest movement event**")
        st.write(selected_bus.get("last_event", "No event recorded"))
        st.caption(selected_bus.get("last_event_time", "Waiting for update"))

        if str(selected_bus.get("motion_state", "")).startswith("Stopped"):
            st.warning("The vehicle is currently stopped in the simulation.")
        elif selected_bus.get("motion_state") == "Moving":
            st.success("The vehicle is moving in the simulation.")
        else:
            st.info("This vehicle is not currently moving in the simulation.")


# ---------------------------------------------------------
# Fleet inventory
# ---------------------------------------------------------

st.divider()
st.subheader("Vehicle inventory")

if filtered_buses:
    inventory_records = []

    for bus in filtered_buses:
        inventory_records.append({
            "Registration": get_registration(bus),
            "Driver": get_driver(bus),
            "Route": format_route(bus),
            "Status": bus.get("status", "Unknown"),
            "Movement": bus.get("motion_state", "Unknown"),
            "Progress": (
                f"{bus.get('journey_progress', 0):.1f}%"
                if bus.get("journey_progress") is not None
                else "—"
            ),
            "Coordinates": format_coordinates(bus),
            "Last update": bus.get("last_update", "Not recorded"),
        })

    inventory_dataframe = pd.DataFrame(inventory_records)

    st.dataframe(
        inventory_dataframe,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        f"Showing {len(inventory_records)} of {len(buses)} demo vehicles."
    )

else:
    st.info("The inventory is empty for the current filters.")
