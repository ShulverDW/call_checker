import streamlit as st
from supabase import create_client, Client
from logic import analyse_number, HOME_TZ, BLOCKED_COUNTRIES

# Supabase client using Streamlit secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_ANON_KEY = st.secrets["SUPABASE_ANON_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# ---------- LOGIN CREDENTIALS ----------
USERNAME = "NightHawk"
PASSWORD = "Dragon"

# ---------- PAGE SETUP ----------
st.set_page_config(
    page_title="Call Qualification Checker",
    page_icon="📞",
    layout="centered",
)

# ---------- GLOBAL STYLING (CSS) ----------
st.markdown("""
<style>
/* === GLOBAL ========================================================== */
.stApp {
    background-color: #e3e3e3 !important;
}

.block-container {
    padding-top: 1.8rem !important;
    padding-bottom: 2rem !important;
}

/* === TOP GREEN NAVBAR =============================================== */
.top-navbar {
    width: 100%;
    background-color: #004225;
    padding: 1rem 1.4rem;
    color: white;
    border-radius: 0 0 12px 12px;
    margin-bottom: 1.8rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.nav-title {
    font-size: 1.35rem;
    font-weight: 700;
    letter-spacing: 0.03em;
}

.nav-brand {
    font-size: 0.95rem;
    font-weight: 500;
    opacity: 0.9;
}

/* === HEADER SECTION ================================================== */
.shdw-title {
    font-size: 2rem;
    font-weight: 800;
    margin: 0;
    padding: 0;
}

.shdw-subtitle {
    font-size: 1rem;
    color: #444444;
    margin-top: 0.3rem;
    margin-bottom: 1rem;
}

/* === BUTTONS ========================================================== */
.stButton>button {
    background-color: #004225 !important;
    color: white !important;
    border: none !important;
    padding: 0.65rem 1.3rem !important;
    border-radius: 0.45rem !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    cursor: pointer;
}

.stButton>button:hover {
    background-color: #00361d !important;
}

/* === LOGIN CARD ====================================================== */
.login-card {
    max-width: 420px;
    margin: 0 auto;
    margin-top: 1.5rem;
    padding: 1.2rem 1.4rem;
    background-color: #ffffff;
    border-radius: 0.9rem;
    border: 1px solid #dddddd;
    box-shadow: 0 3px 12px rgba(0,0,0,0.06);
}

.login-title {
    font-size: 1.2rem;
    font-weight: 700;
    margin-bottom: 0.3rem;
}

.login-subtitle {
    font-size: 0.9rem;
    color: #555555;
    margin-bottom: 0.8rem;
}

/* === RESULT CARD ===================================================== */
.result-card {
    padding: 1.1rem 1.35rem;
    border-radius: 1rem;
    background-color: #ffffff;
    border: 2px solid #00422522;   /* subtle green border */
    box-shadow: 0 3px 10px rgba(0,0,0,0.07);
    margin-top: 0.75rem;
    margin-bottom: 1.2rem;
}

.result-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #666666;
    margin-bottom: 0.2rem;
}

.result-main {
    font-size: 1.15rem;
    font-weight: 700;
}

/* === STATUS PILLS ==================================================== */
.pill {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
}

.pill-ok {
    background-color: #004225;
    color: white;
    border: none;
}

.pill-bad {
    background-color: #ffdad6;
    color: #8b0000;
    border: 1px solid #ffb3ad;
}

/* === TIME GRID ======================================================= */
.time-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    column-gap: 2rem;
    row-gap: 0.5rem;
    font-size: 0.9rem;
    margin-top: 0.6rem;
}

.time-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    color: #777777;
}

.time-value {
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ---------- TOP NAVBAR ----------
st.markdown("""
<div class="top-navbar">
    <div class="nav-title">Call Qualification Checker</div>
    <div class="nav-brand">Shulver Data Works</div>
</div>
""", unsafe_allow_html=True)

# ---------- LOGIN GATE (NightHawk / Dragon) ----------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">🔐 Secure Access</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="login-subtitle">'
        'Enter your credentials to access the Call Qualification Checker.'
        '</div>',
        unsafe_allow_html=True
    )

    username_input = st.text_input("Username")
    password_input = st.text_input("Password", type="password")

    login_clicked = st.button("Login")

    if login_clicked:
        if username_input == USERNAME and password_input == PASSWORD:
            st.session_state["authenticated"] = True
            st.success("Access granted.")
            st.rerun()
        else:
            st.error("Incorrect username or password.")

    st.markdown("</div>", unsafe_allow_html=True)  # close login-card
    st.stop()

# ---------- MAIN APP (only runs after login) ----------

st.markdown(
    "<div class='shdw-title'>📞 Call Qualification Checker</div>"
    "<div class='shdw-subtitle'>Check if a number qualifies, and see its country & local time in seconds.</div>",
    unsafe_allow_html=True
)

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

            # Status pill
            if allowed:
                status_html = '<span class="pill pill-ok">QUALIFIES</span>'
            else:
                status_html = '<span class="pill pill-bad">DOES NOT QUALIFY</span>'

            # Result card
            st.markdown("<div class='result-card'>", unsafe_allow_html=True)

            st.markdown(
                f"<div class='result-label'>Number origin</div>"
                f"<div class='result-main'>{country} ({region})</div>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<div class='result-label' style='margin-top:0.5rem;'>Status</div>"
                f"{status_html}",
                unsafe_allow_html=True
            )

            # Time info
            if result.get("has_timezone"):
                diff = result["diff_hours"]
                diff_str = f"{diff:+.1f} hours"

                st.markdown(
                    "<div class='result-label' style='margin-top:0.75rem;'>Time information</div>",
                    unsafe_allow_html=True
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
                    unsafe_allow_html=True
                )
            else:
                st.info(result.get("error", "No timezone info available for this number."))

            st.markdown("</div>", unsafe_allow_html=True)  # close result-card

# ---------- BLOCKED COUNTRIES EXPANDER ----------
with st.expander("View NOT-qualified country codes"):
    st.write(sorted(BLOCKED_COUNTRIES))
    st.caption("These countries (plus all of Africa) do NOT qualify.")

