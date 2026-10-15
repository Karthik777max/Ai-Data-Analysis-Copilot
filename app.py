"""Streamlit UI for an AI data analyst copilot prototype."""
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Northstar · Data Copilot", page_icon="✳", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --ink:#182a28; --muted:#788783; --line:#e8eeeb; --green:#1e735e; --mint:#eaf5ef; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; color:var(--ink); }
.stApp { background:#f7f9f7; }
[data-testid="stSidebar"] { background:#fff; border-right:1px solid var(--line); }
[data-testid="stSidebar"] > div:first-child { padding-top:1.4rem; }
h1,h2,h3 { font-family:'Manrope',sans-serif !important; letter-spacing:-.035em; }
.brand { font:800 22px Manrope,sans-serif; letter-spacing:-1px; padding:4px 0 26px; }
.brand span { color:#2b8b6c; }
.eyebrow { color:#668078; font-size:11px; font-weight:700; letter-spacing:.12em; text-transform:uppercase; }
.hero { padding:28px 32px; border-radius:18px; color:#fff; background:linear-gradient(115deg,#1a5146,#287b62); margin:8px 0 24px; }
.hero h1 { color:white; margin:5px 0 8px; font-size:30px; }
.hero p { color:#d1e4dc; margin:0; }
.card { background:#fff; border:1px solid var(--line); border-radius:14px; padding:20px; min-height:110px; }
.metric { color:#788783; font-size:12px; font-weight:600; }
.metric-value { font:700 27px Manrope,sans-serif; margin:8px 0 2px; }
.metric-note { color:#71817b; font-size:11px; }
.section-title { font:700 18px Manrope,sans-serif; margin:24px 0 12px; }
.tag { display:inline-block; background:#eaf5ef; color:#227259; border-radius:99px; padding:4px 9px; font-size:11px; font-weight:700; }
.login-wrap { max-width:480px; margin:7vh auto; background:white; border:1px solid var(--line); border-radius:20px; padding:38px; box-shadow:0 16px 55px #254c3b0c; }
div.stButton > button[kind="primary"] { background:#20745d; border-color:#20745d; }
</style>
""", unsafe_allow_html=True)

def login_screen():
    st.markdown('<div class="login-wrap"><div class="brand">northstar<span>✳</span></div><div class="eyebrow">Your analytics workspace</div><h1 style="font-size:30px;margin:8px 0">Welcome back</h1><p style="color:#788783">Sign in to explore your data with AI.</p></div>', unsafe_allow_html=True)
    with st.form("login_form"):
        email = st.text_input("Work email", placeholder="you@company.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)
        if submitted:
            if email.strip() and password:
                st.session_state.authenticated = True
                st.session_state.email = email.strip()
                st.rerun()
            else:
                st.error("Enter your email and password to continue.")
    st.caption("Prototype sign-in: any non-empty email and password will open the workspace. Connect a real identity provider before production.")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if not st.session_state.authenticated:
    login_screen()
    st.stop()

if "datasets" not in st.session_state:
    st.session_state.datasets = []
if "profile_name" not in st.session_state:
    st.session_state.profile_name = "Alex Morgan"

with st.sidebar:
    st.markdown('<div class="brand">northstar<span>✳</span></div>', unsafe_allow_html=True)
    st.caption("WORKSPACE")
    page = st.radio("Navigate", ["Overview", "Datasets", "Account settings", "Admin"], label_visibility="collapsed")
    st.divider()
    st.markdown("<div class='eyebrow'>CURRENT WORKSPACE</div><b>Acme Analytics</b>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("SIGNED IN AS")
    st.write("👤  " + st.session_state.profile_name)
    if st.button("Sign out", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

if page == "Overview":
    st.markdown('<div class="hero"><div class="eyebrow" style="color:#c3ded2">MONDAY, YOUR WORKSPACE IS READY</div><h1>Good to see you, ' + st.session_state.profile_name.split()[0] + '.</h1><p>Bring your data together and let your next question lead the way.</p></div>', unsafe_allow_html=True)
    cols = st.columns(4)
    metrics = [("Datasets", str(len(st.session_state.datasets)), "Ready to explore"), ("Questions asked", "128", "+12 this week"), ("Insights saved", "24", "Across 6 projects"), ("Workspace members", "8", "2 admins")]
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
    uploaded = st.file_uploader("Upload a CSV file", type=["csv"], help="CSV files are processed in this browser session for this prototype.")
    if uploaded is not None:
        try:
            frame = pd.read_csv(uploaded)
            if not any(d["name"] == uploaded.name for d in st.session_state.datasets):
                st.session_state.datasets.append({"name": uploaded.name, "rows": len(frame), "columns": len(frame.columns), "added": datetime.now().strftime("%b %d, %Y"), "data": frame})
            st.success(f"{uploaded.name} is ready — {len(frame):,} rows and {len(frame.columns)} columns.")
            st.markdown("**Preview**")
            st.dataframe(frame.head(10), use_container_width=True, hide_index=True)
        except Exception as exc:
            st.error(f"Could not read this CSV: {exc}")
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

else:
    st.markdown('<div class="eyebrow">WORKSPACE CONTROL</div><h1>Admin</h1><p style="color:#788783">Manage workspace access and review usage.</p>', unsafe_allow_html=True)
    a, b, c = st.columns(3)
    for col, label, value in [(a, "Members", "8"), (b, "Admins", "2"), (c, "Storage used", "1.4 GB")]:
        with col: st.markdown(f'<div class="card"><div class="metric">{label}</div><div class="metric-value">{value}</div><div class="metric-note">Acme Analytics workspace</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Team members</div>', unsafe_allow_html=True)
    members = pd.DataFrame([
        {"Name": st.session_state.profile_name, "Email": st.session_state.get("email", "alex@acme.com"), "Role": "Admin", "Status": "Active"},
        {"Name": "Jordan Lee", "Email": "jordan@acme.com", "Role": "Admin", "Status": "Active"},
        {"Name": "Sam Rivera", "Email": "sam@acme.com", "Role": "Analyst", "Status": "Active"},
        {"Name": "Taylor Chen", "Email": "taylor@acme.com", "Role": "Viewer", "Status": "Invited"},
    ])
    st.dataframe(members, use_container_width=True, hide_index=True)
    with st.expander("Invite a teammate"):
        with st.form("invite_form"):
            invite_email = st.text_input("Work email", placeholder="teammate@company.com")
            invite_role = st.selectbox("Role", ["Analyst", "Viewer", "Admin"])
            if st.form_submit_button("Send invite", type="primary"):
                if invite_email.strip(): st.success(f"Invite prepared for {invite_email.strip()} as {invite_role}. Connect email delivery to send it.")
                else: st.error("Enter an email address.")
    st.caption("Admin controls are a UI prototype. Add server-side role checks and persistent storage before using with a team.")
