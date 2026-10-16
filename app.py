"""Streamlit UI for an AI data analyst copilot prototype."""
from datetime import datetime
import base64
import hashlib
from pathlib import Path

import pandas as pd
import streamlit as st
from database import admin_activity, database_status, list_tables, record_login, record_upload, save_upload, table_preview

LOGO_PATH = Path(__file__).parent / "assets" / "analyst-symbol.png"
LOGO_DATA = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")

st.set_page_config(page_title="Analyst Co pilot", page_icon=str(LOGO_PATH), layout="wide", initial_sidebar_state="expanded")

if "theme" not in st.session_state:
    st.session_state.theme = "Blue light"

themes = {
    "Blue light": "--ink:#101b32; --muted:#65748b; --line:#dce5f2; --page:#f3f7ff; --surface:#ffffff; --primary:#2563eb; --soft:#e8f0ff;",
    "Midnight blue": "--ink:#edf4ff; --muted:#a7b8d2; --line:#243651; --page:#07111f; --surface:#0e1b2d; --primary:#60a5fa; --soft:#172b46;",
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --ink:#101b32; --muted:#65748b; --line:#dce5f2; --page:#f3f7ff; --surface:#fff; --primary:#2563eb; --soft:#e8f0ff; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; color:var(--ink); }
.stApp { background:var(--page); color:var(--ink); }
[data-testid="stSidebar"] { background:var(--surface); border-right:1px solid var(--line); }
[data-testid="stSidebar"] > div:first-child { padding-top:1.4rem; }
h1,h2,h3 { font-family:'Manrope',sans-serif !important; letter-spacing:-.035em; }
.brand { display:flex; align-items:center; gap:10px; font:800 20px Manrope,sans-serif; letter-spacing:-.7px; padding:4px 0 26px; }
.brand img { width:38px; height:38px; object-fit:cover; border-radius:8px; }
.eyebrow { color:var(--muted); font-size:11px; font-weight:700; letter-spacing:.12em; text-transform:uppercase; }
.hero { padding:28px 32px; border-radius:18px; color:#fff; background:linear-gradient(115deg,#102653,#2563eb); margin:8px 0 24px; }
.hero h1 { color:white; margin:5px 0 8px; font-size:30px; }
.hero p { color:#dbeafe; margin:0; }
.card { background:var(--surface); border:1px solid var(--line); border-radius:14px; padding:20px; min-height:110px; }
.metric { color:var(--muted); font-size:12px; font-weight:600; }
.metric-value { font:700 27px Manrope,sans-serif; margin:8px 0 2px; }
.metric-note { color:var(--muted); font-size:11px; }
.section-title { font:700 18px Manrope,sans-serif; margin:24px 0 12px; }
.tag { display:inline-block; background:var(--soft); color:var(--primary); border-radius:99px; padding:4px 9px; font-size:11px; font-weight:700; }
.login-wrap { max-width:480px; margin:7vh auto; background:var(--surface); border:1px solid var(--line); border-radius:20px; padding:38px; }
div.stButton > button[kind="primary"] { background:var(--primary); border-color:var(--primary); color:white; }
[data-baseweb="input"] > div, [data-baseweb="select"] > div { background:var(--surface); }
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] { gap:8px; }
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label {
    background:var(--surface); border:1px solid var(--line); border-radius:10px;
    padding:10px 12px; transition:background .15s ease, border-color .15s ease, transform .15s ease;
}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label:hover {
    background:var(--soft); border-color:var(--primary); transform:translateX(2px);
}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) {
    background:linear-gradient(115deg,#102653,#2563eb); border-color:#2563eb;
    box-shadow:0 4px 12px #2563eb33;
}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) p {
    color:#fff !important; font-weight:700;
}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label > div:first-child { display:none; }
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label p { margin:0; }
</style>
""", unsafe_allow_html=True)
st.markdown(f"<style>:root {{{themes[st.session_state.theme]}}}</style>", unsafe_allow_html=True)

def brand_markup():
    return f'<div class="brand"><img src="data:image/png;base64,{LOGO_DATA}" alt=""><span>Analyst Co pilot</span></div>'

def login_screen():
    st.markdown(f'<div class="login-wrap">{brand_markup()}<div class="eyebrow">Your analytics workspace</div><h1 style="font-size:30px;margin:8px 0">Welcome back</h1><p style="color:var(--muted)">Sign in to explore your data with AI.</p></div>', unsafe_allow_html=True)
    with st.form("login_form"):
        name = st.text_input("Full name", placeholder="Your name")
        email = st.text_input("Work email", placeholder="you@company.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)
        if submitted:
            if name.strip() and email.strip() and password:
                try:
                    admin_password = st.secrets.get("ADMIN_PASSWORD", "")
                except FileNotFoundError:
                    admin_password = ""
                st.session_state.authenticated = True
                st.session_state.profile_name = name.strip()
                st.session_state.email = email.strip()
                st.session_state.is_admin = bool(admin_password and password == admin_password)
                engine, error = database_status()
                if engine:
                    try:
                        record_login(engine, email, name)
                        st.session_state.activity_error = ""
                    except Exception as error:
                        st.session_state.activity_error = f"Usage tracking is unavailable: {error}"
                else:
                    st.session_state.activity_error = error
                st.rerun()
            else:
                st.error("Enter your name, email, and password to continue.")
    st.caption("Enter the configured admin password to open the Admin page.")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if not st.session_state.authenticated:
    login_screen()
    st.stop()

if "datasets" not in st.session_state:
    st.session_state.datasets = []
if "profile_name" not in st.session_state:
    st.session_state.profile_name = "Alex Morgan"
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

with st.sidebar:
    st.markdown(brand_markup(), unsafe_allow_html=True)
    selected_theme = st.selectbox("Theme", list(themes), index=list(themes).index(st.session_state.theme))
    if selected_theme != st.session_state.theme:
        st.session_state.theme = selected_theme
        st.rerun()
    st.caption("WORKSPACE")
    pages = ["Overview", "Datasets", "PostgreSQL", "Account settings"]
    if st.session_state.is_admin:
        pages.append("Admin")
    page = st.radio("Navigate", pages, label_visibility="collapsed")
    st.divider()
    st.markdown("<div class='eyebrow'>CURRENT WORKSPACE</div><b>Data Labs</b>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("SIGNED IN AS")
    st.write("👤  " + st.session_state.profile_name)
    if st.button("Sign out", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

if page == "Overview":
    st.markdown('<div class="hero"><div class="eyebrow" style="color:#c3ded2">MONDAY, YOUR WORKSPACE IS READY</div><h1>Good to see you, ' + st.session_state.profile_name.split()[0] + '.</h1><p>Bring your data together and let your next question lead the way.</p></div>', unsafe_allow_html=True)
    cols = st.columns(4)
    metrics = [("Datasets", str(len(st.session_state.datasets)), "Ready to explore"), ("Questions asked", "128", "+12 this week"), ("Insights saved", "24", "Across 6 projects"), ("Workspace members", "1", "1 admin")]
    for col, (label, value, note) in zip(cols, metrics):
        with col: st.markdown(f'<div class="card"><div class="metric">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Recent activity</div>', unsafe_allow_html=True)
    if st.session_state.datasets:
        st.dataframe(pd.DataFrame([{"Dataset": d["name"], "Rows": d["rows"], "Columns": d["columns"], "Added": d["added"]} for d in st.session_state.datasets]), use_container_width=True, hide_index=True)
    else:
        st.info("Your workspace is ready for its first dataset. Open **Datasets** to upload a CSV and start exploring.")
    st.markdown('<div class="section-title">Ask your data</div>', unsafe_allow_html=True)
    question = st.text_input("Ask a question", placeholder="e.g. Which product had the most sales last quarter?", label_visibility="collapsed")
    if st.button("✳  Ask copilot", type="primary"):
        if question.strip(): st.info("Your question is ready. Connect an AI provider and dataset query layer to enable generated answers.")
        else: st.warning("Type a question first.")

elif page == "Datasets":
    st.markdown('<div class="eyebrow">YOUR DATA</div><h1>Datasets</h1><p style="color:#788783">Upload and manage the files your copilot can explore.</p>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload a CSV file", type=["csv"], help="Uploaded CSV files are saved as tables in PostgreSQL.")
    if uploaded is not None:
        try:
            content = uploaded.getvalue()
            upload_id = hashlib.sha256(content).hexdigest()
            frame = pd.read_csv(uploaded)
            table_name = "upload_" + "".join(ch.lower() if ch.isalnum() else "_" for ch in uploaded.name.rsplit(".", 1)[0]).strip("_")
            if not table_name.removeprefix("upload_"):
                table_name = "upload_data"
            if st.session_state.get("last_upload_id") == upload_id:
                st.info(f"This file has already been saved as public.{table_name}.")
            else:
                engine, error = database_status()
                if error:
                    st.error(error)
                else:
                    save_upload(engine, frame, table_name)
                    record_upload(
                        engine, table_name, uploaded.name, len(frame),
                        len(frame.columns), st.session_state.get("email", "unknown"),
                    )
                    st.session_state.last_upload_id = upload_id
                    st.success(f"Saved {uploaded.name} to PostgreSQL as public.{table_name} ({len(frame):,} rows, {len(frame.columns)} columns).")
            st.markdown("**Preview**")
            st.dataframe(frame.head(10), use_container_width=True, hide_index=True)
        except Exception as exc:
            st.error(f"Could not save this CSV to PostgreSQL: {exc}")
    if st.session_state.datasets:
        st.markdown('<div class="section-title">Connected datasets</div>', unsafe_allow_html=True)
        for i, dataset in enumerate(st.session_state.datasets):
            with st.container(border=True):
                left, middle, right = st.columns([4, 2, 1])
                left.markdown(f"**📄 {dataset['name']}**  \n{dataset['rows']:,} rows · {dataset['columns']} columns")
                middle.markdown(f"<span class='tag'>Ready</span> &nbsp; Added {dataset['added']}", unsafe_allow_html=True)
                if right.button("Remove", key=f"remove_{i}"):
                    st.session_state.datasets.pop(i)
                    st.rerun()
    else:
        st.info("No datasets yet. Upload a CSV above to add your first dataset.")

elif page == "PostgreSQL":
    st.markdown('<div class="eyebrow">DATABASE CONNECTION</div><h1>PostgreSQL</h1><p style="color:#788783">Browse tables through a read-only preview connection.</p>', unsafe_allow_html=True)
    engine, connection_error = database_status()
    if connection_error:
        st.warning(connection_error)
        st.code('DATABASE_URL = "postgresql+psycopg://readonly_user:password@host:5432/database_name"', language="toml")
        st.caption("Add this to .streamlit/secrets.toml, or set DATABASE_URL in the process environment. Keep the secrets file out of Git.")
    else:
        st.success("Connected to PostgreSQL")
        try:
            tables = list_tables(engine)
            if not tables:
                st.info("No tables found in accessible schemas.")
            else:
                selection = st.selectbox("Choose a table", tables, format_func=lambda item: f"{item[0]}.{item[1]}")
                preview_limit = st.number_input("Preview rows", min_value=1, max_value=500, value=100, step=10)
                if selection:
                    rows = table_preview(engine, selection[0], selection[1], int(preview_limit))
                    st.caption(f"Showing up to {preview_limit} rows from {selection[0]}.{selection[1]}.")
                    st.dataframe(pd.DataFrame([dict(row) for row in rows]), use_container_width=True, hide_index=True)
        except Exception as exc:
            st.error(f"Could not inspect database tables: {exc}")

elif page == "Account settings":
    st.markdown('<div class="eyebrow">PREFERENCES</div><h1>Account settings</h1><p style="color:#788783">Manage your profile and workspace preferences.</p>', unsafe_allow_html=True)
    with st.form("account_form"):
        st.subheader("Profile")
        name = st.text_input("Full name", value=st.session_state.profile_name)
        email = st.text_input("Email address", value=st.session_state.get("email", ""))
        st.text_input("Role", value="Workspace member", disabled=True)
        st.subheader("Preferences")
        timezone = st.selectbox("Timezone", ["Asia/Kolkata", "UTC", "America/Los_Angeles", "America/New_York", "Europe/London"])
        notifications = st.toggle("Email me about workspace activity", value=True)
        saved = st.form_submit_button("Save changes", type="primary")
        if saved:
            st.session_state.profile_name = name.strip() or "Alex Morgan"
            st.session_state.email = email.strip()
            st.success("Your account settings have been saved for this session.")

elif page == "Admin" and st.session_state.is_admin:
    st.markdown('<div class="eyebrow">WORKSPACE CONTROL</div><h1>Admin</h1><p style="color:#788783">Review registered users, sign-ins, and uploaded datasets.</p>', unsafe_allow_html=True)
    engine, error = database_status()
    if error:
        st.error(error)
    else:
        try:
            counts, logins_by_day, uploads_by_day, uploads, users = admin_activity(engine)
            cards = st.columns(4)
            cards[0].metric("Users", counts["users"])
            cards[1].metric("Dataset uploads", counts["uploads"])
            cards[2].metric("Total sign-ins", counts["logins"])
            cards[3].metric("Admins", 1)

            chart1, chart2 = st.columns(2)
            with chart1:
                st.subheader("Sign-ins by day")
                if logins_by_day:
                    st.line_chart(pd.DataFrame(logins_by_day).set_index("date")["logins"])
                else:
                    st.info("Sign-in activity will appear here.")
            with chart2:
                st.subheader("Uploads by day")
                if uploads_by_day:
                    st.bar_chart(pd.DataFrame(uploads_by_day).set_index("date")["uploads"])
                else:
                    st.info("Upload activity will appear here.")

            st.subheader("Users")
            st.dataframe(pd.DataFrame(users), use_container_width=True, hide_index=True)
            st.subheader("Uploaded datasets")
            st.dataframe(pd.DataFrame(uploads), use_container_width=True, hide_index=True)
            st.caption("Usage tracking starts now; sign-ins and uploads from before this feature was added are not included.")
        except Exception as exc:
            st.error(f"Could not load admin activity: {exc}")
    with st.expander("Invite a teammate"):
        with st.form("invite_form"):
            invite_email = st.text_input("Work email", placeholder="teammate@company.com")
            invite_role = st.selectbox("Role", ["Analyst", "Viewer"])
            if st.form_submit_button("Send invite", type="primary"):
                if invite_email.strip(): st.success(f"Invite prepared for {invite_email.strip()} as {invite_role}. Connect email delivery to send it.")
                else: st.error("Enter an email address.")
    st.caption("Sign-in credentials are still a prototype. Use real user authentication before opening this app to a team.")
else:
    st.error("Admin access requires the configured administrator email and password.")
