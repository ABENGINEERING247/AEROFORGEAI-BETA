# AeroForge AI Beta

A Streamlit beta starter for an AI engineering copilot, extending the AeroForge concept with an OpenAI-powered chatbot and structured engineering workspaces.

## Included
- Demo Mode and OpenAI API Mode
- Drone category explorer: multirotor, hexacopter, octocopter, fixed-wing, VTOL, helicopter, nano/micro, FPV/racing, agriculture, mapping, inspection, search and rescue, environment, delivery, and education/research profiles
- Requirement analysis
- Conceptual system architecture drafting
- Preliminary BOM and procurement planning
- Risk register drafting
- Verification and validation planning
- Conversational engineering chatbot with recent-turn context
- Session artifact storage and JSON/CSV export
- Streamlit Secrets configuration and API connection test

## Run locally

Python 3.10+ recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Configure OpenAI

Create `.streamlit/secrets.toml`:

```toml
OPENAI_API_KEY = "your-api-key"
OPENAI_MODEL = "gpt-4o-mini"
```

Use a model available to your OpenAI account. Do not commit `secrets.toml` to GitHub.

For Streamlit Community Cloud:
1. Push `app.py`, `requirements.txt`, and `README.md` to a GitHub repository.
2. Create or open the Streamlit app.
3. In app settings, open **Secrets** and add `OPENAI_API_KEY` and `OPENAI_MODEL`.
4. Deploy/reboot the app and choose **OpenAI API Mode** in the sidebar.

## Notes and limitations
- This is a standalone beta starter, not a modification of the deployed production app. Existing app source code/repository access is required to merge it into the current project.
- Artifacts are stored in Streamlit session state and are not durable database storage; they may disappear when the session resets.
- Demo Mode returns explanatory templates, not genuine LLM responses.
- No CAD generation, physical simulation, validated aerodynamic calculation, supplier lookup, or flight certification is performed by this starter.
- Treat all generated engineering content as preliminary. Qualified engineers must review safety-critical decisions and verify them using validated tools before procurement, fabrication, or flight testing.
