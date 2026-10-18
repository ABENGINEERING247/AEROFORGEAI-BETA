import json
import os
from datetime import datetime
from io import BytesIO

import pandas as pd
import streamlit as st

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

APP_NAME = "AeroForge AI Beta"
DEFAULT_MODEL = "gpt-4o-mini"

st.set_page_config(page_title=APP_NAME, page_icon="âœˆï¸", layout="wide")

st.markdown("""
<style>
:root { --af-blue:#173b63; --af-cyan:#29b6d1; }
.block-container {padding-top: 1.4rem; max-width: 1400px;}
.hero {padding: 1.4rem 1.6rem; border-radius: 18px; background: linear-gradient(120deg,#102a43,#175d83); color:white; margin-bottom:1rem;}
.hero h1 {color:white; margin-bottom:.25rem;}
.hero p {color:#e2f5ff; margin-bottom:0;}
.small-muted {color:#6b7280;font-size:.88rem;}
</style>
""", unsafe_allow_html=True)

def get_secret(name, default=None):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return os.getenv(name, default)

def get_client():
    key = get_secret("OPENAI_API_KEY", "")
    if not key or OpenAI is None:
        return None
    return OpenAI(api_key=key)

def get_model():
    return get_secret("OPENAI_MODEL", DEFAULT_MODEL)

def call_ai(system_prompt, user_prompt, temperature=0.3):
    client = get_client()
    if client is None:
        return None, "OpenAI API is not configured. Add OPENAI_API_KEY in Streamlit Secrets or use Demo Mode."
    try:
        response = client.chat.completions.create(
            model=get_model(),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content or "", None
    except Exception as exc:
        return None, f"OpenAI request failed: {exc}"

DRONE_CATEGORIES = [
    "Multirotor / Quadrotor",
    "Hexacopter",
    "Octocopter",
    "Fixed-Wing",
    "VTOL / Hybrid VTOL",
    "Single-Rotor Helicopter",
    "Nano / Micro Drone",
    "FPV / Racing Drone",
    "Agricultural / Crop Monitoring",
    "Mapping / Surveying",
    "Inspection / Industrial",
    "Search & Rescue",
    "Environmental Monitoring",
    "Delivery / Logistics",
    "Educational / Research",
    "Other / Custom",
]

def demo_response(task, details):
    return f"""# AeroForge AI Beta â€” Demo Analysis

**Module:** {task}

## Initial assessment
- The request has been captured for preliminary engineering review.
- Confirm missing requirements, assumptions, units, and acceptance criteria before making design decisions.
- Link each design decision to a unique requirement ID so it can be reviewed later.

## Inputs received
{details}

## Recommended next steps
1. Review the assumptions with the responsible engineer.
2. Check mass, power, payload, mission duration, environmental limits, and applicable regulations.
3. Create a verification method and measurable pass/fail criteria for every critical requirement.
4. Obtain qualified engineering review before procurement, fabrication, or flight testing.

> Demo Mode uses a deterministic template. It does not perform a real simulation, certification, or validated aerospace calculation.
"""

SYSTEM = """You are AeroForge AI Beta, an engineering copilot supporting conceptual civil UAV development.
Help engineers organize requirements, explore trade-offs, draft traceable engineering artifacts, and identify assumptions and risks. Recognize common drone categories including multirotor/quadrotor, hexacopter, octocopter, fixed-wing, VTOL/hybrid VTOL, single-rotor helicopter, nano/micro, FPV/racing, agriculture, mapping/surveying, industrial inspection, search and rescue, environmental monitoring, delivery/logistics, and education/research. Ask for mission details when category alone is insufficient.
Be clear about uncertainty. Do not claim a design is safe, flight-ready, certified, or simulation-validated unless evidence is provided.
Do not invent test results or standards compliance. Distinguish user-provided facts, assumptions, and recommendations.
For potentially safety-critical engineering decisions, recommend review by a qualified aerospace engineer and verification using validated tools.
Keep responses structured, practical, and traceable to the supplied inputs."""

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "artifacts" not in st.session_state:
    st.session_state.artifacts = []

with st.sidebar:
    st.title("âœˆï¸ AeroForge AI")
    st.caption("Engineering Copilot â€¢ Beta")
    mode = st.radio("Operating mode", ["Demo Mode", "OpenAI API Mode"], index=0)
    st.divider()
    page = st.radio("Workspace", [
        "Dashboard", "Requirement Analyst", "System Architecture",
        "BOM & Procurement", "Risk Register", "Verification Planner",
        "Engineering Chatbot", "Drone Knowledge & Parts", "Engineering Calculator",
        "Cross-Agent Workbench",
        "Mission Planner Agent", "Propulsion Agent", "Battery & Power Agent",
        "Flight Control Agent", "Airframe & Materials Agent", "Payload Integration Agent",
        "Navigation & Communications Agent", "Sensors & Perception Agent",
        "Aerodynamics Agent", "Thermal & Environmental Agent", "Manufacturing Agent",
        "Maintenance & Diagnostics Agent", "Compliance & Operations Agent",
        "Cost & Procurement Agent", "Test & Simulation Agent",
        "Reports & Export", "API Settings"
    ])
    st.divider()
    st.caption("Beta notice")
    st.write("Conceptual engineering support only. Human review is required.")

st.markdown(f"""<div class="hero"><h1>âœˆï¸ {APP_NAME}</h1>
<p>From mission requirements to traceable engineering decisions â€” with an OpenAI-powered engineering chatbot.</p></div>""", unsafe_allow_html=True)

if mode == "OpenAI API Mode" and get_client() is None:
    st.warning("OpenAI API mode selected, but no API key is detected. Add OPENAI_API_KEY under API Settings / Streamlit Secrets, or switch to Demo Mode.")

def generate_artifact(module, prompt):
    if mode == "Demo Mode":
        result = demo_response(module, prompt)
    else:
        result, error = call_ai(SYSTEM + f"\nYou are currently working on the {module} module. Return a professional, well-structured engineering draft.", prompt)
        if error:
            st.error(error)
            return
    st.markdown(result)
    st.session_state.artifacts.append({
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "module": module,
        "prompt": prompt,
        "result": result
    })



AGENT_PROFILES = {
    "Mission Planner Agent": "Mission planning, mission profiles, route assumptions, payload and operational constraints.",
    "Propulsion Agent": "Motor, propeller, ESC and propulsion matching; interpret manufacturer data and identify compatibility checks.",
    "Battery & Power Agent": "Battery energy, current draw, power distribution, charging, reserve assumptions and electrical safety.",
    "Flight Control Agent": "Flight controller, firmware architecture, control loops, failsafes, sensor calibration and integration checks.",
    "Airframe & Materials Agent": "Frame, wing, fuselage, landing gear, fasteners, materials, structural load paths and mass budget.",
    "Payload Integration Agent": "Payload mounting, mass properties, vibration isolation, power/data interfaces and center-of-gravity checks.",
    "Navigation & Communications Agent": "GNSS, telemetry, radio links, antennas, link budgets at conceptual level and lost-link procedures.",
    "Sensors & Perception Agent": "Cameras, LiDAR, IMU, barometer, radar and other sensors; field of view, data rate and integration.",
    "Aerodynamics Agent": "Lift, drag, wing loading, propeller/airframe interactions and conceptual aerodynamic trade-offs.",
    "Thermal & Environmental Agent": "Cooling, ingress protection, vibration, weather, temperature, dust and environmental qualification planning.",
    "Manufacturing Agent": "Design for assembly, tolerances, process planning, quality checks, materials and manufacturability.",
    "Maintenance & Diagnostics Agent": "Inspection intervals, fault isolation, logs, maintenance records, repair criteria and lifecycle health.",
    "Compliance & Operations Agent": "Civil operations planning, documentation, privacy, airspace and jurisdiction-specific compliance questions.",
    "Cost & Procurement Agent": "BOM structuring, cost assumptions, supplier comparison criteria, lead-time and lifecycle cost planning.",
    "Test & Simulation Agent": "Test plans, simulation assumptions, acceptance criteria, data capture and verification evidence."
}

PARTS_GUIDE = {
    "Powertrain": "Motor, propeller, ESC, motor mounts, power cables, connectors, power distribution board, current/voltage monitor.",
    "Energy storage": "Battery cells/pack, BMS where applicable, charger, battery straps, enclosure, temperature monitoring and fire-safe handling provisions.",
    "Flight electronics": "Flight controller, IMU, barometer, GNSS receiver, compass, airspeed sensor where relevant, telemetry radio and antennas.",
    "Structure": "Frame/arms, plates, fuselage or wing, landing gear, fasteners, vibration isolators, payload rails and protective enclosure.",
    "Navigation and control": "RC receiver/transmitter, telemetry link, GNSS, antenna placement, remote identification equipment where required, failsafe configuration.",
    "Payload": "Camera, gimbal, multispectral sensor, LiDAR, delivery mechanism, agricultural spray system, thermal camera or scientific instrument.",
    "Safety and support": "Propeller guards where suitable, status indicators, buzzer, parachute system where appropriate, maintenance tools, spares and transport case.",
    "Fixed-wing specific": "Wing, spar, ribs, fuselage, tailplane, control surfaces, servos, linkages, pitot/static system and launch/recovery equipment.",
    "VTOL specific": "Lift motors/propellers, cruise propulsion, transition controller logic, additional ESCs, reinforced structure and transition test instrumentation."
}

def _agent_page(agent_name):
    st.subheader(agent_name)
    st.caption(AGENT_PROFILES[agent_name])
    category = st.selectbox("Drone category", DRONE_CATEGORIES, key=f"{agent_name}_category")
    task = st.text_area("What do you need this agent to solve?", key=f"{agent_name}_task",
                        placeholder="Describe the mission, observed issue, constraints, available parts, units, and what a successful result looks like.", height=150)
    constraints = st.text_area("Related context / findings from other agents (optional)", key=f"{agent_name}_context",
                               placeholder="Paste requirements, measurements, part datasheets, or another agent's findings.", height=90)
    if st.button(f"Ask {agent_name}", type="primary", key=f"{agent_name}_run"):
        if not task.strip():
            st.warning("Describe the task or issue first.")
        else:
            prompt = f"""Act as the {agent_name} specialist for a civil/educational UAV.
Platform: {category}
Scope: {AGENT_PROFILES[agent_name]}
Task or issue: {task}
Cross-agent context: {constraints or 'None supplied'}
Provide: (1) summary, (2) facts supplied vs assumptions vs unknowns, (3) step-by-step reasoning at an engineering level, (4) calculations only when inputs and equations are available with units, (5) part-level implications and interface/compatibility checks, (6) likely causes and diagnostic steps if troubleshooting, (7) risks and mitigations, (8) recommended handoff to another specialist, and (9) verification checklist.
Never invent datasheet values, prices, test results, regulatory approvals, or safety claims. Mark missing values TBD. Flag any result that needs qualified engineering review."""
            generate_artifact(agent_name, prompt)


if page == "Dashboard":
    c1, c2, c3 = st.columns(3)
    c1.metric("Engineering workspaces", "6")
    c2.metric("Operating mode", mode)
    c3.metric("Saved artifacts", len(st.session_state.artifacts))
    st.subheader("Beta workspace")
    st.write("Use the modules to draft connected engineering artifacts from a shared requirement baseline.")
    st.markdown("""
- **Drone Categories:** choose a platform type and mission application to tailor your engineering workflow.
- **Requirement Analyst:** extract requirements, ambiguities, assumptions, and acceptance criteria.
- **System Architecture:** propose subsystem boundaries, interfaces, and requirement traceability.
- **BOM & Procurement:** create a preliminary component list with selection rationale and verification needs.
- **Risk Register:** identify technical, operational, manufacturing, and compliance risks.
- **Verification Planner:** define test methods, evidence, and pass/fail criteria.
- **Engineering Chatbot:** discuss UAV requirements and ask follow-up questions in natural language.
- **14 specialist agents:** mission planning, propulsion, battery/power, flight control, airframe, payload, navigation/comms, sensing, aerodynamics, environment, manufacturing, maintenance, compliance, cost, and testing.
- **Cross-Agent Workbench:** pass a task and prior findings between agents while retaining a reviewable handoff record.
- **Engineering Calculator:** transparent first-order estimates for energy, endurance, thrust-to-weight, payload fraction, range, and wing loading.
- **Drone Knowledge & Parts:** explore categories, subsystem parts, interfaces, selection criteria, and compatibility checks.
""")
    st.subheader("Drone category explorer")
    cat1, cat2 = st.columns(2)
    with cat1:
        selected_category = st.selectbox("Platform category", DRONE_CATEGORIES, key="dashboard_drone_category")
    with cat2:
        selected_use = st.selectbox("Primary application", [
            "Aerial photography", "Mapping and surveying", "Agriculture", "Industrial inspection",
            "Search and rescue", "Education and research", "Environmental monitoring",
            "Delivery logistics", "Racing and recreation", "Custom mission"
        ])
    st.info(f"Selected profile: **{selected_category}** Â· Application: **{selected_use}**")
    if st.button("Open tailored engineering workflow"):
        st.session_state["selected_drone_category"] = selected_category
        st.session_state["selected_drone_use"] = selected_use
        st.session_state["drone_profile_ready"] = True
        st.success("Profile saved for this session. Use it as context in the engineering modules.")
    st.info("Tip: start with Requirement Analyst, then reuse the same mission context in each module.")

elif page == "Requirement Analyst":
    st.subheader("Requirement Analyst")
    default_category = st.session_state.get("selected_drone_category", DRONE_CATEGORIES[0])
    category = st.selectbox("Drone category", DRONE_CATEGORIES, index=DRONE_CATEGORIES.index(default_category) if default_category in DRONE_CATEGORIES else 0)
    use_case = st.text_input("Mission application", value=st.session_state.get("selected_drone_use", ""))
    mission = st.text_area("Mission / requirement baseline", placeholder="Describe intended civil UAV mission, payload, range, endurance, environment, constraints, and stakeholders.", height=180)
    uploaded = st.file_uploader("Optional: upload requirements (.txt, .md, .csv)", type=["txt","md","csv"])
    if uploaded:
        try:
            file_text = uploaded.getvalue().decode("utf-8", errors="replace")
            mission = (mission + "\n\nUploaded source:\n" + file_text).strip()
        except Exception:
            st.warning("Could not read the uploaded file as text.")
    if st.button("Analyze requirements", type="primary"):
        if not mission.strip():
            st.error("Enter a mission or requirement baseline first.")
        else:
            generate_artifact("Requirement Analysis", f"""Analyze the following mission requirements for drone category: {category}.
Mission application: {use_case or 'Not specified'}.
Return: executive summary; numbered requirements (REQ-001...); functional/non-functional constraints; ambiguities; assumptions; dependencies; acceptance criteria; verification method; traceability table.
Do not invent missing values; mark them TBD.

BASELINE:
{mission}""")

elif page == "System Architecture":
    st.subheader("System Architecture")
    mission = st.text_area("Mission context / approved requirements", height=160, placeholder="Paste the requirements or summarize the mission.")
    constraints = st.text_area("Constraints and interfaces", placeholder="Payload, power, communications, operating environment, size/weight limits, budget...")
    if st.button("Draft architecture", type="primary"):
        if not mission.strip():
            st.error("Add mission context first.")
        else:
            generate_artifact("System Architecture", f"""Create a conceptual civil UAV system architecture.
Include subsystem breakdown, responsibilities, interfaces, data/power flows, key trade-offs, requirement-to-subsystem traceability, unresolved decisions, and review checklist.
Clearly label assumptions and avoid unsupported performance claims.
Mission: {mission}
Constraints: {constraints}""")

elif page == "BOM & Procurement":
    st.subheader("Preliminary BOM & Procurement")
    platform = st.selectbox("Drone category", DRONE_CATEGORIES, index=DRONE_CATEGORIES.index(st.session_state.get("selected_drone_category", DRONE_CATEGORIES[0])) if st.session_state.get("selected_drone_category", DRONE_CATEGORIES[0]) in DRONE_CATEGORIES else 0)
    application = st.selectbox("Primary application", [
        "Aerial photography", "Mapping and surveying", "Agriculture", "Industrial inspection",
        "Search and rescue", "Education and research", "Environmental monitoring",
        "Delivery logistics", "Racing and recreation", "Custom mission"
    ])
    mission = st.text_area("Mission and design context", height=130)
    budget = st.text_input("Target budget (optional)", placeholder="e.g., PKR 500,000")
    if st.button("Draft preliminary BOM", type="primary"):
        if not mission.strip():
            st.error("Provide the mission context.")
        else:
            generate_artifact("Preliminary BOM", f"""Draft a preliminary, non-authoritative bill of materials for a civil drone platform: {platform}.
Primary application: {application}
Mission: {mission}
Budget: {budget or 'Not specified'}
Return a table with item, function, quantity, selection criteria, key compatibility checks, estimated cost only if grounded in supplied data, supplier information needed, and verification notes. If prices or suppliers are unknown, mark TBD rather than inventing them. Highlight items requiring qualified engineering review.""")

elif page == "Risk Register":
    st.subheader("Engineering Risk Register")
    mission = st.text_area("Design / mission context", height=130)
    focus = st.multiselect("Risk categories", ["Flight stability", "Power and battery", "Structures", "Communications", "Weather/environment", "Human factors", "Manufacturing", "Cybersecurity", "Regulatory/compliance"], default=["Flight stability","Power and battery","Structures","Weather/environment"])
    if st.button("Generate risk register", type="primary"):
        if not mission.strip():
            st.error("Provide a design or mission context.")
        else:
            generate_artifact("Risk Register", f"""Create a preliminary civil UAV risk register.
Context: {mission}
Categories: {', '.join(focus)}
Use columns: risk ID, hazard/failure mode, cause, consequence, likelihood (qualitative), severity (qualitative), mitigation, verification evidence, owner, residual risk, status. Do not imply that qualitative ratings are validated. Include unknowns and recommend a formal safety review.""")

elif page == "Verification Planner":
    st.subheader("Verification & Validation Planner")
    requirements = st.text_area("Requirements / design claims to verify", height=150)
    environment = st.text_input("Test environment (optional)", placeholder="Bench, lab, ground test, simulation, controlled flight test...")
    if st.button("Build verification plan", type="primary"):
        if not requirements.strip():
            st.error("Enter requirements or design claims.")
        else:
            generate_artifact("Verification Plan", f"""Build a verification and validation plan for the supplied requirements.
Requirements: {requirements}
Test environment: {environment or 'TBD'}
For each item provide ID, requirement ID, method (inspection/analysis/demo/test), setup, instruments/data, measurable pass/fail criteria, evidence to retain, responsible reviewer, safety prerequisites, and status. Mark criteria TBD when not specified. Do not claim tests were executed.""")

elif page == "Engineering Chatbot":
    st.subheader("AeroForge Engineering Chatbot")
    st.write("Ask about requirements, UAV subsystems, design trade-offs, documentation, risks, or verification planning.")
    for item in st.session_state.chat_history:
        with st.chat_message(item["role"]):
            st.markdown(item["content"])
    user_prompt = st.chat_input("Ask AeroForge AI a questionâ€¦")
    if user_prompt:
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)
        if mode == "Demo Mode":
            answer = ("**Demo Mode response**\n\nI can help structure this engineering question. Define the mission, constraints, units, and acceptance criteria; identify assumptions; and verify safety-critical conclusions with validated engineering methods. Switch to OpenAI API Mode and configure `OPENAI_API_KEY` for model-generated responses.\n\n**Your question:** " + user_prompt)
        else:
            client = get_client()
            if client is None:
                answer = "OpenAI is not configured. Add `OPENAI_API_KEY` in Streamlit Secrets and try again."
            else:
                try:
                    messages = [{"role": "system", "content": SYSTEM}]
                    messages.extend({"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history[-12:])
                    response = client.chat.completions.create(model=get_model(), messages=messages, temperature=0.4)
                    answer = response.choices[0].message.content or "I couldn't generate a response."
                except Exception as exc:
                    answer = f"OpenAI request failed: {exc}"
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)
    if st.button("Clear chat history"):
        st.session_state.chat_history = []
        st.rerun()

elif page == "Drone Knowledge & Parts":
    st.subheader("Drone Knowledge & Parts Explorer")
    st.write("Use this as a structured starting point for subsystem knowledge. Exact part specifications must be checked against the selected manufacturer's datasheet.")
    category = st.selectbox("Drone type", DRONE_CATEGORIES, key="parts_category")
    subsystem = st.selectbox("Subsystem", list(PARTS_GUIDE.keys()), key="parts_subsystem")
    mission = st.text_area("Mission, size class, payload, environment, and constraints", height=110, key="parts_mission")
    st.markdown("**Typical parts in this subsystem**")
    st.write(PARTS_GUIDE[subsystem])
    question = st.text_area("Ask AI for part-by-part details, calculations, selection, compatibility, or troubleshooting", height=120, key="parts_question")
    if st.button("Explain parts and interfaces", type="primary"):
        if not question.strip():
            st.warning("Enter a question to continue.")
        else:
            generate_artifact("Drone Knowledge & Parts", f"""Platform: {category}
Subsystem: {subsystem}
Typical subsystem items: {PARTS_GUIDE[subsystem]}
Mission context: {mission or 'Not supplied'}
User question: {question}
Explain each relevant part's function, typical interfaces, selection criteria, datasheet parameters to check, common failure modes, maintenance, and compatibility with adjacent subsystems. Include equations with units where appropriate, but do not invent specifications or present typical values as guaranteed. Cover multirotor, fixed-wing, hybrid VTOL, single-rotor, nano/micro, FPV, agricultural, mapping, inspection, rescue, delivery, and research differences when relevant.""")

elif page == "Engineering Calculator":
    st.subheader("First-Order UAV Engineering Calculator")
    st.warning("These are screening estimates, not validated flight-design calculations. Use consistent units and verify battery limits, manufacturer data, margins, and applicable safety requirements.")
    st.markdown("**Battery energy and estimated endurance**")
    c1, c2, c3 = st.columns(3)
    voltage = c1.number_input("Nominal battery voltage (V)", min_value=0.1, value=22.2, step=0.1)
    capacity = c2.number_input("Capacity (Ah)", min_value=0.1, value=10.0, step=0.5)
    load = c3.number_input("Average electrical load (W)", min_value=1.0, value=350.0, step=10.0)
    reserve = st.slider("Energy unavailable as reserve (%)", 0, 60, 25)
    energy_wh = voltage * capacity
    usable_wh = energy_wh * (1 - reserve / 100)
    endurance_min = usable_wh / load * 60
    st.write(f"Nominal energy: **{energy_wh:.1f} Wh** Â· Usable energy after reserve: **{usable_wh:.1f} Wh** Â· Idealized endurance: **{endurance_min:.1f} min**")
    st.caption("Formula: energy = voltage Ã— capacity; endurance = usable energy Ã· average load. Real endurance may be lower due to voltage sag, aging, temperature, wind, maneuvering, and discharge limits.")
    st.divider()
    st.markdown("**Mass, thrust and payload screening**")
    a, b, c = st.columns(3)
    mass = a.number_input("All-up mass (kg)", min_value=0.01, value=3.0, step=0.1)
    thrust = b.number_input("Total rated static thrust (kgf)", min_value=0.0, value=6.0, step=0.2)
    payload = c.number_input("Payload mass (kg)", min_value=0.0, value=0.5, step=0.1)
    twr = thrust / mass if mass else 0
    payload_fraction = payload / mass * 100 if mass else 0
    st.write(f"Rated static thrust-to-weight ratio (approx.): **{twr:.2f}:1** Â· Payload fraction of all-up mass: **{payload_fraction:.1f}%**")
    st.caption("Use compatible, measured manufacturer thrust data for the actual motor/propeller/ESC/battery combination. Static ratings do not establish controllability or safe flight.")
    st.divider()
    st.markdown("**Simple range and fixed-wing wing loading**")
    d, e, f = st.columns(3)
    speed = d.number_input("Ground speed estimate (km/h)", min_value=0.0, value=36.0, step=1.0)
    minutes = e.number_input("Mission duration estimate (min)", min_value=0.0, value=20.0, step=1.0)
    area = f.number_input("Wing area (mÂ²; fixed-wing only)", min_value=0.0, value=0.8, step=0.1)
    range_km = speed * minutes / 60
    wing_loading = mass * 9.80665 / area if area > 0 else None
    st.write(f"Straight-line range estimate: **{range_km:.2f} km**")
    st.write(f"Wing loading: **{wing_loading:.1f} N/mÂ²**" if wing_loading is not None else "Wing loading: enter a positive wing area for fixed-wing calculations.")
    st.caption("Range ignores turns, climb, wind, reserve, route restrictions, and energy limitations. Wing loading is a comparison metric, not a stall-speed or safety certification.")
    st.divider()
    calc_question = st.text_area("Ask AI to explain these results or calculate another engineering quantity", placeholder="Include known values and units, for example: estimate current at a stated electrical power and voltage.", height=100)
    if st.button("Ask AI to review calculations"):
        if not calc_question.strip():
            st.warning("Enter a calculation question.")
        else:
            generate_artifact("Engineering Calculator AI Review", f"""Review these screening calculations and explain limitations.
Voltage={voltage} V; capacity={capacity} Ah; nominal energy={energy_wh:.2f} Wh; reserve={reserve}%; usable energy={usable_wh:.2f} Wh; load={load} W; idealized endurance={endurance_min:.2f} min.
All-up mass={mass} kg; rated total static thrust={thrust} kgf; thrust-to-weight approximation={twr:.2f}; payload={payload} kg; payload fraction={payload_fraction:.2f}%.
Ground speed={speed} km/h; duration={minutes} min; simple range={range_km:.2f} km; wing area={area} mÂ²; wing loading={wing_loading if wing_loading is not None else 'not calculated'} N/mÂ².
User question: {calc_question}
Check units, show equations, state assumptions, identify omitted real-world effects, and flag whether the available inputs are sufficient. Do not claim validated performance or flight safety.""")

elif page == "Cross-Agent Workbench":
    st.subheader("Cross-Agent Workbench")
    st.write("Create a controlled handoff: one specialist's findings become context for another specialist. The system does not run agents autonomously in the background; each handoff is explicitly initiated by you.")
    agents = list(AGENT_PROFILES.keys())
    source = st.selectbox("Sending agent", agents, key="handoff_source")
    target = st.selectbox("Receiving agent", agents, index=1, key="handoff_target")
    shared_task = st.text_area("Shared mission / problem", height=100, key="handoff_problem")
    findings = st.text_area("Existing findings, calculations, or source-agent output", height=140, key="handoff_findings")
    handoff_question = st.text_area("What should the receiving agent do?", height=90, key="handoff_question")
    if st.button("Run cross-agent handoff", type="primary"):
        if not shared_task.strip() or not handoff_question.strip():
            st.warning("Enter the shared problem and handoff request.")
        else:
            prompt = f"""Cross-agent engineering handoff for a civil UAV.
Shared problem: {shared_task}
Sending agent: {source} â€” {AGENT_PROFILES[source]}
Receiving agent: {target} â€” {AGENT_PROFILES[target]}
Prior findings supplied: {findings or 'None supplied'}
Requested action: {handoff_question}
Receiving agent instructions: identify which findings are accepted, which need verification, missing inputs, relevant equations and units, downstream impacts on other subsystems, risks, and a concrete next-step checklist. Do not treat prior agent output as verified fact. Explicitly flag contradictions and request original datasheets/measurements where needed."""
            generate_artifact(f"Agent Handoff: {source} â†’ {target}", prompt)

elif page == "Mission Planner Agent":
    _agent_page("Mission Planner Agent")

elif page == "Propulsion Agent":
    _agent_page("Propulsion Agent")

elif page == "Battery & Power Agent":
    _agent_page("Battery & Power Agent")

elif page == "Flight Control Agent":
    _agent_page("Flight Control Agent")

elif page == "Airframe & Materials Agent":
    _agent_page("Airframe & Materials Agent")

elif page == "Payload Integration Agent":
    _agent_page("Payload Integration Agent")

elif page == "Navigation & Communications Agent":
    _agent_page("Navigation & Communications Agent")

elif page == "Sensors & Perception Agent":
    _agent_page("Sensors & Perception Agent")

elif page == "Aerodynamics Agent":
    _agent_page("Aerodynamics Agent")

elif page == "Thermal & Environmental Agent":
    _agent_page("Thermal & Environmental Agent")

elif page == "Manufacturing Agent":
    _agent_page("Manufacturing Agent")

elif page == "Maintenance & Diagnostics Agent":
    _agent_page("Maintenance & Diagnostics Agent")

elif page == "Compliance & Operations Agent":
    _agent_page("Compliance & Operations Agent")

elif page == "Cost & Procurement Agent":
    _agent_page("Cost & Procurement Agent")

elif page == "Test & Simulation Agent":
    _agent_page("Test & Simulation Agent")

elif page == "Reports & Export":
    st.subheader("Reports & Export")
    st.write(f"Saved artifacts in this session: **{len(st.session_state.artifacts)}**")
    if st.session_state.artifacts:
        for i, artifact in enumerate(reversed(st.session_state.artifacts), 1):
            with st.expander(f"{i}. {artifact['module']} â€” {artifact['created_at']}"):
                st.markdown(artifact["result"])
        payload = json.dumps(st.session_state.artifacts, indent=2, ensure_ascii=False)
        st.download_button("Download all artifacts (JSON)", payload, file_name="aeroforge_beta_artifacts.json", mime="application/json")
        df = pd.DataFrame([{"created_at": a["created_at"], "module": a["module"], "prompt": a["prompt"], "result": a["result"]} for a in st.session_state.artifacts])
        st.download_button("Download artifact index (CSV)", df.to_csv(index=False), file_name="aeroforge_beta_artifacts.csv", mime="text/csv")
    else:
        st.info("Generate an artifact in one of the engineering modules to see it here.")

elif page == "API Settings":
    st.subheader("OpenAI API Configuration")
    st.markdown("For deployment, configure secrets in Streamlit Community Cloud. **Never paste a production API key into source code or commit it to GitHub.**")
    st.code('OPENAI_API_KEY = "your-api-key"\nOPENAI_MODEL = "gpt-4o-mini"', language="toml")
    st.write("Add these values in your app's **Settings â†’ Secrets**. You can also set environment variables locally.")
    st.write(f"Detected model setting: `{get_model()}`")
    if get_client():
        st.success("An OpenAI API key is detected.")
    else:
        st.warning("No OpenAI API key detected, or the OpenAI Python package is unavailable.")
    if st.button("Test OpenAI connection"):
        client = get_client()
        if not client:
            st.error("Connection unavailable. Check OPENAI_API_KEY and install dependencies.")
        else:
            try:
                r = client.chat.completions.create(
                    model=get_model(),
                    messages=[{"role":"user","content":"Reply with exactly: AeroForge connection successful."}],
                    max_tokens=30,
                )
                st.success(r.choices[0].message.content or "Request completed.")
            except Exception as exc:
                st.error(f"Connection test failed: {exc}")

st.divider()
st.caption("AeroForge AI Beta â€¢ Conceptual engineering assistance only â€¢ All outputs require human review.")
