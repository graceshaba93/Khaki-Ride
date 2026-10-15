"""Centralized fictional data for the Kopa-Ride demonstration.

This module contains no production API calls.
Records are fictional and must not be treated as live transport data.
"""

from copy import deepcopy

import streamlit as st


INITIAL_BUSES = [
    {
        "bus_id": "KR-BUS-001",
        "registration": "DEMO-001",
        "capacity": 18,
        "driver": "Musa Ibrahim",
        "route_id": "RT-001",
        "status": "In transit",
        "latitude": 9.0820,
        "longitude": 6.0150,
        "last_update": "10:30",
    },
    {
        "bus_id": "KR-BUS-002",
        "registration": "DEMO-002",
        "capacity": 18,
        "driver": "Grace Okafor",
        "route_id": "RT-002",
        "status": "In transit",
        "latitude": 9.0579,
        "longitude": 5.9970,
        "last_update": "10:25",
    },
    {
        "bus_id": "KR-BUS-003",
        "registration": "DEMO-003",
        "capacity": 14,
        "driver": "Peter James",
        "route_id": "RT-003",
        "status": "Delayed",
        "latitude": 9.1200,
        "longitude": 6.0800,
        "last_update": "10:20",
    },
    {
        "bus_id": "KR-BUS-004",
        "registration": "DEMO-004",
        "capacity": 18,
        "driver": "Amina Bello",
        "route_id": "RT-001",
        "status": "Maintenance",
        "latitude": 9.1000,
        "longitude": 6.0300,
        "last_update": "10:15",
    },
]

INITIAL_ROUTES = [
    {
        "route_id": "RT-001",
        "origin": "Bida",
        "destination": "Minna",
        "departure": "08:15",
        "duration_minutes": 120,
        "status": "Active",
    },
    {
        "route_id": "RT-002",
        "origin": "Minna",
        "destination": "Bida",
        "departure": "09:00",
        "duration_minutes": 120,
        "status": "Active",
    },
    {
        "route_id": "RT-003",
        "origin": "Bida",
        "destination": "Lapai",
        "departure": "10:00",
        "duration_minutes": 75,
        "status": "Active",
    },
]

INITIAL_MEMBERS = [
    {
        "member_id": "CM-001",
        "name": "Amina Yusuf",
        "state_code": "NG/26A/001",
        "camp": "Niger State Orientation Camp",
        "pickup_point": "Bida Central Park",
        "bus_id": "KR-BUS-001",
        "journey_id": "JRN-001",
        "status": "In transit",
    },
    {
        "member_id": "CM-002",
        "name": "Samuel Okoro",
        "state_code": "NG/26A/002",
        "camp": "Niger State Orientation Camp",
        "pickup_point": "Minna City Gate",
        "bus_id": "KR-BUS-002",
        "journey_id": "JRN-002",
        "status": "Assigned",
    },
    {
        "member_id": "CM-003",
        "name": "Fatima Ibrahim",
        "state_code": "NG/26A/003",
        "camp": "Niger State Orientation Camp",
        "pickup_point": "Bida Central Park",
        "bus_id": None,
        "journey_id": None,
        "status": "Awaiting assignment",
    },
    {
        "member_id": "CM-004",
        "name": "David James",
        "state_code": "NG/26A/004",
        "camp": "Niger State Orientation Camp",
        "pickup_point": "Lapai Junction",
        "bus_id": "KR-BUS-003",
        "journey_id": "JRN-003",
        "status": "Delayed",
    },
    {
        "member_id": "CM-005",
        "name": "Grace Musa",
        "state_code": "NG/26A/005",
        "camp": "Niger State Orientation Camp",
        "pickup_point": "Minna City Gate",
        "bus_id": None,
        "journey_id": None,
        "status": "Awaiting assignment",
    },
]

INITIAL_JOURNEYS = [
    {
        "journey_id": "JRN-001",
        "bus_id": "KR-BUS-001",
        "route_id": "RT-001",
        "assigned_members": 8,
        "departure": "08:15",
        "estimated_arrival": "10:15",
        "status": "In transit",
    },
    {
        "journey_id": "JRN-002",
        "bus_id": "KR-BUS-002",
        "route_id": "RT-002",
        "assigned_members": 6,
        "departure": "09:00",
        "estimated_arrival": "11:00",
        "status": "In transit",
    },
    {
        "journey_id": "JRN-003",
        "bus_id": "KR-BUS-003",
        "route_id": "RT-003",
        "assigned_members": 5,
        "departure": "10:00",
        "estimated_arrival": "11:15",
        "status": "Delayed",
    },
]

INITIAL_INCIDENTS = [
    {
        "incident_id": "SOS-001",
        "member_id": "CM-001",
        "journey_id": "JRN-001",
        "category": "Journey delay",
        "location": "Simulated location near Bida",
        "reported_at": "10:05",
        "priority": "Medium",
        "status": "Open",
    },
    {
        "incident_id": "SOS-002",
        "member_id": "CM-004",
        "journey_id": "JRN-003",
        "category": "Vehicle issue",
        "location": "Simulated location near Lapai",
        "reported_at": "10:20",
        "priority": "High",
        "status": "Acknowledged",
    },
]


def initialize_demo_data() -> None:
    """Initialize session data once, preserving changes across reruns."""
    defaults = {
        "demo_buses": INITIAL_BUSES,
        "demo_routes": INITIAL_ROUTES,
        "demo_members": INITIAL_MEMBERS,
        "demo_journeys": INITIAL_JOURNEYS,
        "demo_incidents": INITIAL_INCIDENTS,
        "demo_notifications": [],
        "demo_activity": [],
        "demo_next_incident_number": 3,
        "demo_next_journey_number": 4,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = deepcopy(value)


def _records(key: str) -> list[dict]:
    """Return a mutable session-state collection."""
    initialize_demo_data()
    return st.session_state[key]


def get_buses() -> list[dict]:
    return deepcopy(_records("demo_buses"))


def get_routes() -> list[dict]:
    return deepcopy(_records("demo_routes"))


def get_members() -> list[dict]:
    return deepcopy(_records("demo_members"))


def get_journeys() -> list[dict]:
    return deepcopy(_records("demo_journeys"))


def get_incidents() -> list[dict]:
    return deepcopy(_records("demo_incidents"))


def get_dashboard_metrics() -> dict[str, int]:
    buses = get_buses()
    members = get_members()
    journeys = get_journeys()
    incidents = get_incidents()

    return {
        "total_buses": len(buses),
        "active_journeys": sum(
            journey["status"] == "In transit" for journey in journeys
        ),
        "assigned_members": sum(
            member["status"] != "Awaiting assignment" for member in members
        ),
        "delayed_journeys": sum(
            journey["status"] == "Delayed" for journey in journeys
        ),
        "open_incidents": sum(
            incident["status"] != "Resolved" for incident in incidents
        ),
    }


def get_recent_activity() -> list[dict]:
    initialize_demo_data()
    return deepcopy(st.session_state["demo_activity"])


def record_activity(action: str, details: str) -> None:
    """Record an action performed in this demo session."""
    initialize_demo_data()

    activity = st.session_state["demo_activity"]
    activity.insert(
        0,
        {
            "action": action,
            "details": details,
            "time": "Demo session",
        },
    )

    # Keep the activity list small and readable.
    st.session_state["demo_activity"] = activity[:20]


def advance_demo_vehicle_positions() -> None:
    """Simulate vehicle movement, checkpoint stops and travelled trails."""
    import math
    import time
    from datetime import datetime

    initialize_demo_data()

    buses = st.session_state["demo_buses"]
    journeys = st.session_state["demo_journeys"]

    # Illustrative coordinates, not verified road geometry.
    route_shapes = {
        "RT-001": [
            (9.0800, 5.9900),
            (9.1600, 6.0600),
            (9.2600, 6.1400),
            (9.3600, 6.2300),
            (9.4600, 6.3500),
            (9.5400, 6.4400),
            (9.6139, 6.5569),
        ],
        "RT-002": [
            (9.6139, 6.5569),
            (9.5400, 6.4400),
            (9.4600, 6.3500),
            (9.3600, 6.2300),
            (9.2600, 6.1400),
            (9.1600, 6.0600),
            (9.0800, 5.9900),
        ],
        "RT-003": [
            (9.0800, 5.9900),
            (9.0700, 6.1000),
            (9.0600, 6.2200),
            (9.0500, 6.3400),
            (9.0444, 6.5700),
        ],
    }

    tracking_states = st.session_state.setdefault(
        "demo_tracking_states", {}
    )

    active_bus_ids = {
        str(journey["bus_id"])
        for journey in journeys
        if str(journey.get("status", "")).lower() == "in transit"
        and journey.get("bus_id")
    }

    now = time.monotonic()
    clock = datetime.now().strftime("%H:%M:%S")

    def interpolate_route(points, progress):
        """Interpolate a position along the complete route."""
        if len(points) < 2:
            return points[0] if points else (9.08, 5.99)

        lengths = []

        for first, second in zip(points, points[1:]):
            mean_lat = math.radians((first[0] + second[0]) / 2)
            longitude_scale = math.cos(mean_lat)

            distance = math.sqrt(
                (second[0] - first[0]) ** 2
                + ((second[1] - first[1]) * longitude_scale) ** 2
            )
            lengths.append(distance)

        total = sum(lengths)

        if total == 0:
            return points[0]

        target = max(0.0, min(1.0, progress)) * total
        travelled = 0.0

        for index, length in enumerate(lengths):
            if travelled + length >= target:
                fraction = (
                    (target - travelled) / length if length else 0.0
                )
                first, second = points[index], points[index + 1]

                return (
                    first[0] + (second[0] - first[0]) * fraction,
                    first[1] + (second[1] - first[1]) * fraction,
                )

            travelled += length

        return points[-1]

    for index, bus in enumerate(buses):
        bus_id = str(bus.get("bus_id", f"vehicle-{index}"))
        route = route_shapes.get(bus.get("route_id"))

        if bus_id not in active_bus_ids or route is None:
            status = str(bus.get("status", "")).lower()

            if status == "arrived":
                bus["motion_state"] = "Arrived"
            elif status in {"available", "maintenance", "parked"}:
                bus["motion_state"] = "Stationary"
            else:
                bus["motion_state"] = "Not moving"

            continue

        state = tracking_states.setdefault(
            bus_id,
            {
                "progress": min(0.15 + index * 0.12, 0.85),
                "direction": 1,
                "phase": "moving",
                "last_tick": now,
                "resume_at": 0.0,
                "trail": [],
                "last_event": "Journey in progress",
                "event_time": clock,
            },
        )

        if state["phase"] == "stopped":
            if now < state["resume_at"]:
                bus["motion_state"] = f"Stopped — {state['last_event']}"
            else:
                state["phase"] = "moving"
                state["last_tick"] = now
                state["last_event"] = "Journey resumed"
                state["event_time"] = clock
                bus["motion_state"] = "Moving"

        else:
            elapsed = max(0.0, min(now - state["last_tick"], 5.0))
            state["last_tick"] = now

            old_progress = state["progress"]
            direction = state["direction"]

            # Simulation rate, not a real vehicle speed.
            speed = 0.012
            new_progress = old_progress + direction * speed * elapsed

            crossed_checkpoint = (
                direction == 1
                and old_progress < 0.5 <= new_progress
            ) or (
                direction == -1
                and old_progress > 0.5 >= new_progress
            )

            reached_destination = (
                direction == 1 and new_progress >= 1.0
            ) or (
                direction == -1 and new_progress <= 0.0            )

            if crossed_checkpoint:
                new_progress = 0.5
                state["phase"] = "stopped"
                state["resume_at"] = now + 10.0
                state["last_event"] = "Checkpoint stop"
                state["event_time"] = clock

            elif reached_destination:
                new_progress = 1.0 if direction == 1 else 0.0
                state["phase"] = "arrived"
                state["last_event"] = "Journey completed"
                state["event_time"] = clock

                bus["status"] = "Arrived"
                bus["motion_state"] = "Arrived"

                for journey in journeys:
                    if str(journey.get("bus_id")) == bus_id:
                        journey["status"] = "Arrived"

            state["progress"] = max(0.0, min(1.0, new_progress))

            if state["phase"] == "arrived":
                bus["motion_state"] = "Arrived"

            else:
                bus["motion_state"] = (
                    f"stopped — {state['last_event']}"
                    if state["phase"] == "stopped"
                    else "Moving"
                )
                
                
            

        latitude, longitude = interpolate_route(
            route, state["progress"]
        )

        bus["latitude"] = round(latitude, 6)
        bus["longitude"] = round(longitude, 6)
        bus["last_update"] = clock
        bus["route_path"] = [[lon, lat] for lat, lon in route]

        position = [longitude, latitude]
        trail = state["trail"]

        if not trail or math.dist(trail[-1], position) > 0.000001:
            trail.append(position)

        state["trail"] = trail[-200:]

        bus["travelled_path"] = list(state["trail"])
        bus["journey_progress"] = round(state["progress"] * 100, 1)
        bus["last_event"] = state["last_event"]
        bus["last_event_time"] = state["event_time"]

def register_corps_member(
    name: str,
    email: str,
    phone: str,
    state_code: str,
    batch: str,
    deployment_state: str,
    deployment_lga: str,
    ppa: str,
    emergency_contact_name: str,
    emergency_contact_phone: str,
) -> tuple[bool, str]:
    """Register a corps member in the current demo session."""
    initialize_demo_data()

    members = st.session_state["demo_members"]

    email = email.strip().lower()
    state_code = state_code.strip().upper()

    if not all([
        name.strip(),
        email,
        phone.strip(),
        state_code,
        batch.strip(),
        deployment_state.strip(),
        deployment_lga.strip(),
        ppa.strip(),
        emergency_contact_name.strip(),
        emergency_contact_phone.strip(),
    ]):
        return False, "Please complete all required fields."

    if "@" not in email:
        return False, "Enter a valid email address."

    if any(
        str(member.get("email", "")).lower() == email
        or str(member.get("state_code", "")).upper() == state_code
        for member in members
        if member.get("email") or member.get("state_code")
    ):
        return False, "A registration with this email or state code already exists."

    member_number = st.session_state.get("demo_next_member_number", 6)
    member_id = f"CM-{member_number:03d}"
    st.session_state["demo_next_member_number"] = member_number + 1

    members.append({
        "member_id": member_id,
        "name": name.strip(),
        "email": email,
        "phone": phone.strip(),
        "state_code": state_code,
        "batch": batch.strip(),
        "deployment_state": deployment_state.strip(),
        "deployment_lga": deployment_lga.strip(),
        "ppa": ppa.strip(),
        "emergency_contact_name": emergency_contact_name.strip(),
        "emergency_contact_phone": emergency_contact_phone.strip(),
        "camp": f"{deployment_state.strip()} Orientation Camp",
        "pickup_point": "",
        "bus_id": None,
        "journey_id": None,
        "registration_status": "Pending approval",
        "status": "Awaiting approval",
    })

    record_activity("Corps member registration", f"{name.strip()} registered.")
    return True, "Registration submitted successfully. Await administrator approval."


def approve_corps_member(member_id: str) -> tuple[bool, str]:
    """Approve a pending corps member registration."""
    initialize_demo_data()

    members = st.session_state["demo_members"]

    for member in members:
        if member.get("member_id") == member_id:
            if member.get("registration_status") != "Pending approval":
                return False, "This registration is not pending approval."

            member["registration_status"] = "Approved"
            member["status"] = "Awaiting assignment"

            record_activity(
                "Registration approved",
                f"{member.get('name', member_id)} was approved.",
            )
            return True, "Registration approved."

    return False, "Corps member not found."


def assign_member_to_journey(
    member_id: str,
    bus_id: str,
    journey_id: str,
) -> tuple[bool, str]:
    """Assign an approved member to a bus and its journey."""
    initialize_demo_data()

    members = st.session_state["demo_members"]
    buses = st.session_state["demo_buses"]
    journeys = st.session_state["demo_journeys"]

    member = next(
        (item for item in members if item.get("member_id") == member_id),
        None,
    )
    bus = next(
        (item for item in buses if item.get("bus_id") == bus_id),
        None,
    )
    journey = next(
        (
            item for item in journeys
            if item.get("journey_id") == journey_id
            and item.get("bus_id") == bus_id
        ),
        None,
    )

    if member is None:
        return False, "Corps member not found."

    if member.get("registration_status") != "Approved":
        return False, "Approve the corps member before assigning transport."

    if bus is None or journey is None:
        return False, "Select a valid bus and its matching journey."

    if str(bus.get("status", "")).lower() in {"maintenance", "offline"}:
        return False, "This bus is not available for assignment."

    if str(journey.get("status", "")).lower() in {"arrived", "completed", "cancelled"}:
        return False, "This journey has already ended or been cancelled."

    if member.get("bus_id"):
        return False, "This corps member already has a bus assignment."

    assigned_count = sum(
        1 for item in members
        if item.get("journey_id") == journey_id
    )

    if assigned_count >= int(bus.get("capacity", 0)):
        return False, "This bus has reached its passenger capacity."

    member["bus_id"] = bus_id
    member["journey_id"] = journey_id
    member["status"] = journey.get("status", "Assigned")
    member["pickup_point"] = member.get("pickup_point") or "To be confirmed"

    journey["assigned_members"] = max(
        int(journey.get("assigned_members", 0)),
        assigned_count + 1,
    )

    record_activity(
        "Transport assignment",
        f"{member.get('name', member_id)} assigned to {bus.get('registration', bus_id)}.",
    )

    return True, "Transport assignment completed."

def create_sos_incident(
    member_id: str,
    journey_id: str | None,
    category: str,
    description: str,
    location: str,
) -> tuple[bool, str]:
    """Create a high-priority SOS incident in the current demo session."""
    from datetime import datetime

    initialize_demo_data()

    members = st.session_state["demo_members"]
    incidents = st.session_state["demo_incidents"]

    member = next(
        (
            item for item in members
            if item.get("member_id") == member_id
        ),
        None,
    )

    if member is None:
        return False, "Your member record could not be found."

    incident_number = st.session_state.get(
        "demo_next_incident_number", 3
    )
    incident_id = f"SOS-{incident_number:03d}"
    st.session_state["demo_next_incident_number"] = incident_number + 1

    incidents.insert(
        0,
        {
            "incident_id": incident_id,
            "member_id": member_id,
            "journey_id": journey_id,
            "category": category,
            "description": description.strip(),
            "location": location.strip() or "Location not provided",
            "reported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "priority": "High",
            "status": "Open",
        },
    )

    record_activity(
        "SOS emergency reported",
        f"{incident_id} reported by {member.get('name', member_id)}.",
    )

    return True, f"Emergency report submitted. Reference: {incident_id}"


def update_incident_status(
    incident_id: str,
    new_status: str,
) -> tuple[bool, str]:
    """Update the status of an existing demo incident."""
    initialize_demo_data()

    allowed_statuses = {"Open", "Acknowledged", "Resolved"}

    if new_status not in allowed_statuses:
        return False, "Invalid incident status."

    incidents = st.session_state["demo_incidents"]

    incident = next(
        (
            item for item in incidents
            if item.get("incident_id") == incident_id
        ),
        None,
    )

    if incident is None:
        return False, "Incident not found."

    incident["status"] = new_status

    record_activity(
        "SOS incident updated",
        f"{incident_id} status changed to {new_status}.",
    )

    return True, f"{incident_id} marked as {new_status}."