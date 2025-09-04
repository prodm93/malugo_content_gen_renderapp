
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from datetime import timedelta
import pandas as pd

# Project modules (copied from Streamlit app)
from agents.prompts import content_prompt, translation_prompt
from shims import ContentAgent
from shims import TranslateAgent
from shims import ReviseAgent
from shims import ComplianceAgent
from shims import IdeasAgent
from save_utils import sanitize_filename

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
DEFAULT_GUIDE_DIR = os.path.join(os.path.dirname(__file__), "default_guidelines")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")
    app.permanent_session_lifetime = timedelta(hours=8)

    @app.before_request
    def make_session_permanent():
        session.permanent = True

    # --- Auth (simple) ---
    def check_auth(username, password):
        return (
            username == os.environ.get("ADMIN_USERNAME", "admin") and 
            password == os.environ.get("ADMIN_PASSWORD", "admin")
        )

    @app.route("/", methods=["GET", "POST"])
    def index():
        if request.method == "POST":
            username = request.form.get("username", "")
            password = request.form.get("password", "")
            if check_auth(username, password):
                session["user"] = username
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid credentials", "danger")
                return redirect(url_for("index"))
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("index"))

    def require_login():
        if "user" not in session:
            return redirect(url_for("index"))
        return None

    @app.route("/dashboard")
    def dashboard():
        redir = require_login()
        if redir: return redir
        return render_template("dashboard.html")

    # Helpers for loading guideline DataFrames
    def _df_or_default(file_storage, default_relpath):
        if file_storage and file_storage.filename:
            filename = secure_filename(file_storage.filename)
            path = os.path.join(UPLOAD_DIR, filename)
            file_storage.save(path)
        else:
            path = os.path.join(DEFAULT_GUIDE_DIR, default_relpath)
        # Excel or txt
        if path.lower().endswith((".xlsx", ".xls")):
            return pd.read_excel(path)
        else:
            # txt file -> return as DataFrame with one column 'text'
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            return pd.DataFrame({"text": [text]})

    # --- Translation ---
    @app.route("/translation", methods=["GET", "POST"])
    def translation():
        redir = require_login()
        if redir: return redir

        output = None
        if request.method == "POST":
            src_text = request.form.get("source_text", "")
            custom_prompt = request.form.get("custom_prompt", "") or translation_prompt
            agent = TranslateAgent(custom_prompt)
            output = agent.translate(src_text)
        return render_template("translation.html", default_prompt=translation_prompt, output=output)

    # --- Idea Generation ---
    
@app.route("/ideas", methods=["GET", "POST"])
def ideas():
    redir = require_login()
    if redir: return redir

    output = None
    if request.method == "POST":
        topic = request.form.get("topic", "")
        content_type = request.form.get("content_type", "")
        num_ideas = int(request.form.get("num_ideas", "10") or "10")
        agent = IdeasAgent()
        output = agent.generate(topic=topic, content_type=content_type, num_ideas=num_ideas)
    return render_template("ideas.html", output=output)

    # --- Content Generation ---
    
@app.route("/content", methods=["GET", "POST"])
def content():
    redir = require_login()
    if redir: return redir

    output = None
    if request.method == "POST":
        title = request.form.get("title","")
        broad_topic = request.form.get("broad_topic","")
        text_or_video = request.form.get("text_or_video","Text")
        language = request.form.get("language","EN")
        brand_guidelines = request.form.get("brand_guidelines","")
        structure_guidelines = request.form.get("structure_guidelines","")
        tov_guidelines = request.form.get("tov_guidelines","")
        editorial_standards = request.form.get("editorial_standards","")
        examples = request.form.get("examples","")
        supp_info = request.form.get("supp_info","")
        freq_terms_raw = request.form.get("freq_terms","{}")
        try:
            import json
            freq_terms = json.loads(freq_terms_raw) if freq_terms_raw.strip() else {}
        except Exception:
            freq_terms = {}
        enable_web_search = request.form.get("enable_web_search") == "on"

        agent = ContentAgent()
        # Optional Linkup
        linkup_query = request.form.get("linkup_query","")
        linkup_mode = request.form.get("linkup_mode","searchResults")
        agent.linkup_mode(linkup_mode)
        research_text = ""
        if linkup_query:
            try:
                research_text = agent.linkup_search(linkup_query)
            except Exception as e:
                research_text = f"[Linkup error: {e}]"

        # Merge research into supplemental info
        supp_info = (supp_info + "

" + research_text).strip()

        output = agent.generate(title, broad_topic, text_or_video, language,
                                brand_guidelines, structure_guidelines, tov_guidelines, editorial_standards,
                                examples, supp_info, freq_terms, enable_web_search)
    return render_template("content.html", default_prompt=content_prompt, output=output)

    # --- Revision ---
    @app.route("/revision", methods=["GET", "POST"])
    def revision():
        redir = require_login()
        if redir: return redir

        output = None
        if request.method == "POST":
            draft = request.form.get("draft", "")
            instructions = request.form.get("instructions", "")
            agent = ReviseAgent()
            output = agent.revise(draft, instructions)
        return render_template("revision.html", output=output)

    # --- QA & Compliance ---
    @app.route("/compliance", methods=["GET", "POST"])
    def compliance():
        redir = require_login()
        if redir: return redir

        output = None
        if request.method == "POST":
            draft = request.form.get("draft", "")
            rules = request.form.get("rules", "")
            agent = ComplianceAgent()
            output = agent.check(draft, rules)
        return render_template("compliance.html", output=output)

    return app

app = create_app()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
