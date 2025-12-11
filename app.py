import streamlit as st
from supabase import create_client, Client
from logic import analyse_number, HOME_TZ, BLOCKED_COUNTRIES

# ---------- SUPABASE CLIENT ----------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_ANON_KEY = st.secrets["SUPABASE_ANON_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# ---------- PAGE SETUP ----------
st.set_page_config(
    page_title="Call Qualification Checker · Shulver DataWorks",
    page_icon="📞",
    layout="centered",
)

# ---------- GLOBAL STYLING (CSS) ----------
st.markdown(
    """
<style>
/* === GLOBAL BACKGROUND === */
.stApp {
    background-color: #1c1c1c;   /* dark grey background */
    color: #ffffff !important;
    font-family: "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Bring main content a little lower on the page */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    max-width: 900px !important;
}

/* Make all labels readable on dark background */
label, .stRadio label, .stCheckbox label {
    color: #ffffff !important;
}

/* Markdown text */
.stMarkdown p {
    color: #ffffff !important;
}

/* === HEADER BAR (British Racing Green) === */
.top-header {
    width: 100%;
    background-color: #004225;         /* British racing green */
    padding: 1.0rem 1.4rem;
    border-radius: 12px;
    margin-bottom: 1.8rem;             /* header sits lower */
    color: #ffffff;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 700;
}

.header-title {
    font-size: 1.4rem;
    font-weight: 800;
}

.header-brand {
    font-size: 1.0rem;
    font-weight: 600;
    opacity: 0.9;
}

/* === HERO TEXT === */
.hero-title {
    font-size: 1.7rem;
    font-weight: 800;
    margin-bottom: 0.3rem;
    color: #ffffff;
}

.hero-subtitle {
    color: #dddddd;
    font-size: 0.95rem;
    margin-bottom: 1rem;
}

/* === CARDS (login + main) === */
.main-card,
.login-card {
    background-color: #2b2b2b;   /* slightly lighter grey */
    padding: 1.4rem;
    border-radius: 14px;
    border: 1px solid #3a3a3a;
    margin-bottom: 1.6rem;
}

.login-card {
    max-width: 520px;
    margin-left: auto;
    margin-right: auto;
}

.login-title {
    font-size: 1.2rem;
    font-weight: 700;
    margin-bottom: 0.3rem;
}

.login-subtitle {
    font-size: 0.9rem;
    color: #cccccc;
    margin-bottom: 0.8rem;
}

/* === BUTTONS === */
.stButton > button {
    background-color: #004225 !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    padding: 0.55rem 1.2rem !important;
    font-weight: 600 !important;
    border: none !important;
}

.stButton > button:hover {
    background-color: #006b3c !important;
}

/* === RESULT CARD === */
.result-card {
    background-color: #2b2b2b;
    border: 1px solid #004225;
    padding: 1.2rem;
    border-radius: 12px;
    margin-top: 0.9rem;
}

.result-label {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    opacity: 0.7;
}

/* Bigger, bold main result text */
.result-main {
    font-size: 1.45rem;
    font-weight: 800;
    margin-bottom: 0.4rem;
    color: #ffffff;
}

/* Status pills */
.pill {
    display: inline-block;
    padding: 0.25rem 0.9rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
}

.pill-ok {
    background-color: #004225;
    color: #ffffff;
}

.pill-bad {
    background-color: #7a1a1a;
    color: #ffffff;
}

/* Time grid */
.time-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    column-gap: 2rem;
    row-gap: 0.6rem;
    font-size: 0.9rem;
    margin-top: 0.7rem;
}

.time-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    opacity: 0.8;
}

.time-value {
    font-weight: 600;
}

/* Expander */
div[role="button"][data-baseweb="accordion"] {
    background-color: #2b2b2b !important;
    color: #ffffff !important;
}

/* Footer */
.footer {
    text-align: center;
    color: #aaaaaa;
    font-size: 0.8rem;
    margin-top: 1.8rem;
}
</style>
""",
    unsafe_allow_html=True,
)

# ---------- HEADER BAR ----------
st.markdown(
    """
<div class="top-header">
    <div class="header-title">Call Qualification Checker</div>
    <div class="header-brand">Shulver DataWorks</div>
</div>
""",
    unsafe_allow_html=True,
)

# ---------- AUTH / LOGIN ----------

if "user" not in st.session_state:
    st.session_state["user"] = None

if st.session_state["user"] is None:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">🔐 Account Login</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="login-subtitle">'
        'Create an account or log in to access the Shulver DataWorks Call Qualification Checker.'
        '</div>',
        unsafe_allow_html=True,
    )

    mode = st.radio("Mode", ["Login", "Sign Up"], horizontal=True)
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Continue"):
        if not email or not password:
            st.error("Please enter both email and password.")
        else:
            try:
                if mode == "Sign Up":
                    supabase.auth.sign_up({"email": email, "password": password})
                    st.success(
                        "Check your email to confirm your account, then come back and log in."
                    )
                else:
                    res = supabase.auth.sign_in_with_password(
                        {"email": email, "password": password}
                    )
                    if res.user is None:
                        st.error("Login failed. Please check your details.")
                    else:
                        st.session_state["user"] = res.user
                        st.rerun()
            except Exception as e:
                st.error(f"Auth error: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

user = st.session_state["user"]

# ---------- SUBSCRIPTION CHECK ----------
try:
    result = supabase.table("customers").select("*").eq("id", user.id).execute()
    rows = result.data or []
    if not rows:
        supabase.table("customers").insert(
            {"id": user.id, "email": user.email, "is_paid": False}
        ).execute()
        is_paid = False
    else:
        is_paid = rows[0].get("is_paid", False)
except Exception as e:
    st.error(f"Error checking subscription status: {e}")
    st.stop()

# ---------- PAYWALL ----------
if not is_paid:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="login-title">💳 Subscription required</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='login-subtitle'>"
        "You’re almost there — activate your subscription to unlock the Call Qualification Checker."
        "</div>",
        unsafe_allow_html=True,
    )

    st.write("After subscribing, Shulver DataWorks will enable your access.")

    # TODO: replace with your real Stripe payment link
    stripe_checkout_url = "https://YOUR_REAL_STRIPE_LINK_HERE"

    st.markdown(
        f"<a href='{stripe_checkout_url}' target='_blank'>**Subscribe now**</a>",
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ---------- MAIN TOOL UI (only after login + paid) ----------

st.markdown(
    """
<div class="hero-title">Call Qualification Checker</div>
<div class="hero-subtitle">
Check if a number qualifies and see its country & local time in seconds.
</div>
""",
    unsafe_allow_html=True,
)

st.markdown('<div class="main-card">', unsafe_allow_html=True)

number = st.text_input(
    "Phone number (with + country code)",
    placeholder="+447123456789",
    help="Paste a full number including the + and country code.",
)

check_button = st.button("Check number")

if check_button:
    if not number.strip():
        st.warning("Please enter a number first.")
    else:
        result = analyse_number(number)

        if not result.get("valid"):
            st.error(result.get("error", "Unknown error"))
        else:
            allowed = result["allowed"]
            country = result["country"]
            region = result["region"]

            if allowed:
                status_html = '<span class="pill pill-ok">QUALIFIES</span>'
            else:
                status_html = '<span class="pill pill-bad">DOES NOT QUALIFY</span>'

            st.markdown('<div class="result-card">', unsafe_allow_html=True)

            st.markdown(
                f"<div class='result-label'>Number origin</div>"
                f"<div class='result-main'>{country} ({region})</div>",
                unsafe_allow_html=True,
            )

            st.markdown(
                f"<div class='result-label' style='margin-top:0.4rem;'>Status</div>"
                f"{status_html}",
                unsafe_allow_html=True,
            )

            if result.get("has_timezone"):
                diff = result["diff_hours"]
                diff_str = f"{diff:+.1f} hours"

                st.markdown(
                    "<div class='result-label' style='margin-top:0.7rem;'>Time information</div>",
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f"""
                    <div class="time-grid">
                      <div>
                        <div class="time-label">Your timezone</div>
                        <div class="time-value">{HOME_TZ.zone}</div>
                        <div class="time-label" style="margin-top:0.15rem;">Your local time</div>
                        <div class="time-value">{result['home_time']}</div>
                      </div>
                      <div>
                        <div class="time-label">Their local time</div>
                        <div class="time-value">{result['dest_time']}</div>
                        <div class="time-label" style="margin-top:0.15rem;">Difference</div>
                        <div class="time-value">{diff_str}</div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.info(
                    result.get(
                        "error", "No timezone info available for this number."
                    )
                )

            st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)  # close main-card

# ---------- BLOCKED COUNTRIES EXPANDER ----------
with st.expander("View NOT-qualified country codes"):
    st.write(sorted(BLOCKED_COUNTRIES))
    st.caption("These countries (plus all of Africa) do NOT qualify.")

# ---------- FOOTER ----------
st.markdown(
    "<div class='footer'>© Shulver DataWorks — Call Qualification Checker</div>",
    unsafe_allow_html=True,
)
