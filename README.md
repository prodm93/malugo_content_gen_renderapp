
# Malugo Content Gen (Flask)

This is a Flask conversion of the Streamlit app, suitable for deployment on Render.

## Quickstart (local)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ADMIN_USERNAME=admin ADMIN_PASSWORD=admin
python app.py
```

Visit http://localhost:5000

## Deploy on Render

- Push this folder to a Git repo
- Create a new **Web Service** on Render
- Select repo, use Python environment
- Render will detect `render.yaml` or use:
  - Build command: `pip install -r requirements.txt`
  - Start command: `gunicorn app:app`
- Set `ADMIN_USERNAME` and `ADMIN_PASSWORD` env vars

## Notes

- The app uses your existing `agents/*` modules and prompt files.
- Where the Streamlit app relied on `st.session_state`, this Flask app uses form posts and sessions.
- For advanced auth, swap to Flask-Login or an SSO of your choice.

