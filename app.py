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

st.set_page_config(page_title=APP_NAME, page_icon="✈️", layout="wide")

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
    return f"""# AeroForge AI Beta — Demo Analysis

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
    st.title("✈️ AeroForge AI")
    st.caption("Engineering Copilot • Beta")
    mode = st.radio("Operating mode", ["Demo Mode", "OpenAI API Mode"], index=0)
    st.divider()
    page = st.radio("Workspace", [
        "Dashboard", "Requirement Analyst", "System Architecture",
        "BOM & Procurement", "Risk Register", "Verification Planner",
        "Engineering Chatbot", "Reports & Export", "API Settings"
    ])
    st.divider()
    st.caption("Beta notice")
    st.write("Conceptual engineering support only. Human review is required.")

st.markdown(f"""<div class="hero"><h1>✈️ {APP_NAME}</h1>
<p>From mission requirements to traceable engineering decisions — with an OpenAI-powered engineering chatbot.</p></div>""", unsafe_allow_html=True)

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
    st.info(f"Selected profile: **{selected_category}** · Application: **{selected_use}**")
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
    user_prompt = st.chat_input("Ask AeroForge AI a question…")
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

elif page == "Reports & Export":
    st.subheader("Reports & Export")
    st.write(f"Saved artifacts in this session: **{len(st.session_state.artifacts)}**")
    if st.session_state.artifacts:
        for i, artifact in enumerate(reversed(st.session_state.artifacts), 1):
            with st.expander(f"{i}. {artifact['module']} — {artifact['created_at']}"):
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
    st.write("Add these values in your app's **Settings → Secrets**. You can also set environment variables locally.")
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
st.caption("AeroForge AI Beta • Conceptual engineering assistance only • All outputs require human review.")
