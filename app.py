import streamlit as st
from supabase import create_client, Client
from logic import analyse_number, HOME_TZ, BLOCKED_COUNTRIES

# ---------- SUPABASE CLIENT ----------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_ANON_KEY = st.secrets["SUPABASE_ANON_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

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

# ---------- Supabase Auth: Sign Up / Login ----------
if "user" not in st.session_state:
    st.session_state["user"] = None

if st.session_state["user"] is None:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">🔐 Account Login</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="login-subtitle">'
        'Create an account or log in to access Call Qualification Checker.'
        '</div>',
        unsafe_allow_html=True
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
                    st.success("Check your email to confirm your account, then come back and log in.")
                else:
                    res = supabase.auth.sign_in_with_password(
                        {"email": email, "password": password}
                    )
                    if res.user is None:
                        st.error("Login failed. Please check your details.")
                    else:
                        st.session_state["user"] = res.user
                        st.experimental_rerun()
            except Exception as e:
                st.error(f"Auth error: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

user = st.session_state["user"]

# ---------- Ensure customer row exists & check is_paid ----------
try:
    result = supabase.table("customers").select("*").eq("id", user.id).execute()
    rows = result.data or []
    if not rows:
        supabase.table("customers").insert({
            "id": user.id,
            "email": user.email,
            "is_paid": False,
        }).execute()
        is_paid = False
    else:
        is_paid = rows[0].get("is_paid", False)
except Exception as e:
    st.error(f"Error checking subscription status: {e}")
    st.stop()

# ---------- Paywall ----------
if not is_paid:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">💳 Subscription required</div>', unsafe_allow_html=True)
    st.markdown(
        "<div class='login-subtitle'>"
        "Your account is created, but you don't have an active subscription yet."
        "</div>",
        unsafe_allow_html=True
    )

    stripe_checkout_url = "https://YOUR_PAYMENT_LINK_HERE"  # TODO: replace

    st.write("Once you've paid, your access will be activated by Shulver Data Works.")
    st.markdown(f"[Subscribe now]({stripe_checkout_url})", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ---------- MAIN APP (only runs after login & payment) ----------

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

            if allowed:
                status_html = '<span class="pill pill-ok">QUALIFIES</span>'
            else:
                status_html = '<span class="pill pill-bad">DOES NOT QUALIFY</span>'

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

            st.markdown("</div>", unsafe_allow_html=True)

# ---------- BLOCKED COUNTRIES EXPANDER ----------
with st.expander("View NOT-qualified country codes"):
    st.write(sorted(BLOCKED_COUNTRIES))
    st.caption("These countries (plus all of Africa) do NOT qualify.")
