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
/* === GLOBAL APP BACKGROUND ========================================= */
.stApp {
    background: radial-gradient(circle at top left, #06141f 0%, #020617 40%, #000000 90%);
    color: #e5e7eb;
}

/* Constrain main content width and center it */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 980px !important;
    margin: 0 auto !important;
}

/* === TOP DARK NAVBAR =============================================== */
.sdw-nav {
    width: 100%;
    background: linear-gradient(90deg, #020617 0%, #020b10 60%, #020617 100%);
    border-radius: 18px;
    padding: 0.85rem 1.4rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border: 1px solid rgba(148, 163, 184, 0.25);
    box-shadow: 0 16px 45px rgba(0, 0, 0, 0.5);
    margin-bottom: 1.8rem;
}

.sdw-nav-left {
    display: flex;
    align-items: center;
    gap: 0.55rem;
}

.sdw-logo-pill {
    width: 30px;
    height: 30px;
    border-radius: 999px;
    background: radial-gradient(circle, #22c55e 0%, #16a34a 40%, #052e16 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    color: #020617;
    font-size: 0.9rem;
}

.sdw-brand {
    font-weight: 800;
    font-size: 1.05rem;
    letter-spacing: 0.05em;
    color: #22c55e;
}

.sdw-nav-right {
    font-size: 0.8rem;
    text-transform: uppercase;
    color: #9ca3af;
    letter-spacing: 0.16em;
}

/* === HERO AREA ===================================================== */
.hero-title {
    font-size: 1.9rem;
    font-weight: 800;
    letter-spacing: 0.01em;
    margin-bottom: 0.15rem;
    background: linear-gradient(120deg, #f9fafb, #22c55e);
    -webkit-background-clip: text;
    color: transparent;
}

.hero-subtitle {
    font-size: 0.98rem;
    color: #9ca3af;
    margin-bottom: 1.1rem;
}

/* === INPUT / FORM CARD ============================================= */
.main-card {
    background: radial-gradient(circle at top left, #1f2937 0%, #020617 60%);
    border-radius: 18px;
    padding: 1.3rem 1.4rem 1.6rem 1.4rem;
    border: 1px solid rgba(148, 163, 184, 0.35);
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);
    margin-bottom: 1.2rem;
}

/* Streamlit text input tweaks */
div[data-baseweb="input"] {
    background-color: #020617 !important;
    border-radius: 999px !important;
    border: 1px solid rgba(148, 163, 184, 0.7) !important;
}

div[data-baseweb="input"] input {
    color: #e5e7eb !important;
}

/* === BUTTONS ======================================================= */
.stButton>button {
    background: linear-gradient(135deg, #16a34a, #22c55e) !important;
    color: #020617 !important;
    border: none !important;
    padding: 0.7rem 1.6rem !important;
    border-radius: 999px !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    cursor: pointer;
    box-shadow: 0 14px 30px rgba(34, 197, 94, 0.45);
}

.stButton>button:hover {
    background: linear-gradient(135deg, #22c55e, #4ade80) !important;
}

/* === LOGIN & PAYWALL CARD ========================================== */
.login-card {
    max-width: 520px;
    margin: 1.6rem auto;
    padding: 1.5rem 1.6rem 1.6rem 1.6rem;
    background: radial-gradient(circle at top left, #111827 0%, #020617 70%);
    border-radius: 18px;
    border: 1px solid rgba(148, 163, 184, 0.35);
    box-shadow: 0 18px 50px rgba(0, 0, 0, 0.8);
}

.login-title {
    font-size: 1.2rem;
    font-weight: 700;
    margin-bottom: 0.3rem;
}

.login-subtitle {
    font-size: 0.9rem;
    color: #9ca3af;
    margin-bottom: 0.9rem;
}

/* === RESULT CARD =================================================== */
.result-card {
    margin-top: 1.0rem;
    padding: 1.0rem 1.2rem 1.1rem 1.2rem;
    border-radius: 16px;
    background: radial-gradient(circle at top left, #020617 0%, #0b1120 60%);
    border: 1px solid rgba(34, 197, 94, 0.55);
    box-shadow: 0 18px 55px rgba(22, 163, 74, 0.6);
}

.result-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #9ca3af;
    margin-bottom: 0.1rem;
}

.result-main {
    font-size: 1.15rem;
    font-weight: 700;
    color: #e5e7eb;
}

/* === STATUS PILLS ================================================== */
.pill {
    display: inline-block;
    padding: 0.25rem 0.8rem;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 600;
}

.pill-ok {
    background: linear-gradient(135deg, #16a34a, #22c55e);
    color: #020617;
}

.pill-bad {
    background-color: #7f1d1d;
    color: #fecaca;
    border: 1px solid #fca5a5;
}

/* === TIME GRID ===================================================== */
.time-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    column-gap: 2rem;
    row-gap: 0.6rem;
    font-size: 0.9rem;
    margin-top: 0.7rem;
}

.time-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    color: #9ca3af;
}

.time-value {
    font-weight: 600;
}

/* === EXPANDER ====================================================== */
div[role="button"][data-baseweb="accordion"] {
    background-color: #020617 !important;
    color: #e5e7eb !important;
}

/* === FOOTER ======================================================== */
.footer {
    margin-top: 2.2rem;
    font-size: 0.78rem;
    color: #6b7280;
    text-align: center;
}
</style>
""",
    unsafe_allow_html=True,
)

# ---------- TOP NAV (Shulver DataWorks style) ----------
st.markdown(
    '''
    <div class="sdw-nav">
        <div class="sdw-nav-left">
            <div class="sdw-logo-pill">SD</div>
            <div class="sdw-brand">Shulver DataWorks</div>
        </div>
        <div class="sdw-nav-right">
            CALL QUALIFICATION PLATFORM
        </div>
    </div>
    ''',
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
                    res = supabase.auth.sign_up({"email": email, "password": password})
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

    # IMPORTANT: use your real Stripe payment link here
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
Check if a number qualifies and instantly see its country and local time —
built by Shulver DataWorks.
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
                f"<div class='result-label' style='margin-top:0.45rem;'>Status</div>"
                f"{status_html}",
                unsafe_allow_html=True,
            )

            if result.get("has_timezone"):
                diff = result["diff_hours"]
                diff_str = f"{diff:+.1f} hours"

                st.markdown(
                    "<div class='result-label' style='margin-top:0.8rem;'>Time information</div>",
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
