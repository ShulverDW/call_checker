import streamlit as st
from supabase import create_client, Client
from logic import analyse_number, HOME_TZ, BLOCKED_COUNTRIES

# ---------- PAGE + SUPABASE SETUP ----------

st.set_page_config(
    page_title="Call Qualification Checker · Shulver DataWorks",
    page_icon="📞",
    layout="centered",
)

# Read Supabase credentials from .streamlit/secrets.toml
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_ANON_KEY = st.secrets["SUPABASE_ANON_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# ---------- GLOBAL STYLES (CSS) ----------
st.markdown(
    """
<style>
/* Global background & font */
body, html, .stApp {
    background-color: #161616 !important;  /* Dark grey */
    color: #f5f5f5 !important;            /* White-ish text */
    font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Remove big default header spacing */
header[data-testid="stHeader"] { height: 0; }

/* Center & tighten main content */
.block-container {
    max-width: 900px !important;
    padding-top: 2.5rem !important;
    padding-bottom: 2rem !important;
}

/* ---- Top navigation bar ---- */
.top-nav {
    width: 100%;
    background-color: #004225;  /* British Racing Green */
    padding: 1rem 1.4rem;
    border-radius: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.8rem;
}

.nav-title {
    font-size: 1.4rem;
    font-weight: 800;
    color: #ffffff;
}

.nav-brand {
    font-size: 0.95rem;
    font-weight: 600;
    color: #e0f0e8;
}

/* Make login / sign-up radio text white */
div[role="radiogroup"] label {
    color: #ffffff !important;
}

/* Ensure login card labels are white too */
.login-card label {
    color: #ffffff !important;
}

/* ---- Cards ---- */
.card, .login-card {
    background-color: #242424;
    border-radius: 12px;
    border: 1px solid #323232;
    padding: 1.3rem 1.4rem;
    margin-bottom: 1.4rem;
}

.login-card {
    max-width: 520px;
    margin: 0 auto 1.6rem auto;
}

/* ---- Text ---- */
h1, h2, h3 {
    color: #ffffff;
}

.hero-title {
    font-size: 1.7rem;
    font-weight: 800;
    margin-bottom: 0.2rem;
}

.hero-subtitle {
    font-size: 0.95rem;
    color: #dddddd;
    margin-bottom: 0.9rem;
}

/* Labels (Login, Email, etc.) */
label, .stRadio label {
    color: #f5f5f5 !important;
}

/* ---- Inputs ---- */
input, textarea {
    background-color: #1f1f1f !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    border: 1px solid #4a4a4a !important;
}

/* Placeholder */
input::placeholder {
    color: #b3b3b3 !important;
}

/* ---- Buttons ---- */
.stButton > button {
    background-color: #004225 !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    border: none !important;
    padding: 0.6rem 1.4rem !important;
    font-weight: 600 !important;
    font-size: 0.98rem !important;
}

.stButton > button:hover {
    background-color: #006837 !important;
}

/* ---- Result card ---- */
.result-card {
    background-color: #242424;
    border-radius: 12px;
    border: 1px solid #004225;
    padding: 1.1rem 1.3rem;
    margin-top: 1.0rem;
}

.result-label {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #c7c7c7;
}

.result-main {
    font-size: 1.4rem;
    font-weight: 700;
    margin-top: 0.25rem;
}

/* Status pills */
.pill {
    display: inline-block;
    padding: 0.25rem 0.9rem;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-top: 0.25rem;
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
    margin-top: 0.8rem;
    font-size: 0.9rem;
}

.time-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    color: #c7c7c7;
}

.time-value {
    font-weight: 600;
}

/* History */
.history-title {
    margin-top: 2.0rem;
    font-size: 1.2rem;
    font-weight: 700;
}

.history-item {
    background-color: #242424;
    border-radius: 10px;
    border: 1px solid #323232;
    padding: 0.6rem 0.8rem;
    margin-bottom: 0.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.history-status {
    font-size: 0.8rem;
    color: #d0d0d0;
}

/* Footer */
.footer {
    text-align: center;
    font-size: 0.8rem;
    color: #aaaaaa;
    margin-top: 2rem;
}

/* Mobile tweaks */
@media (max-width: 768px) {
    .time-grid {
        grid-template-columns: 1fr;
        row-gap: 0.9rem;
    }
}

</style>
""",
    unsafe_allow_html=True,
)

# ---------- SIMPLE TOP NAV ----------
st.markdown(
    """
    <div class="top-nav">
        <div class="nav-title">Call Qualification Checker</div>
        <div class="nav-brand">Shulver DataWorks</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- AUTH / LOGIN ----------
if "user" not in st.session_state:
    st.session_state["user"] = None

if st.session_state["user"] is None:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown("### 🔐 Account Login", unsafe_allow_html=False)
    st.write(
        "Create an account or log in to access the Shulver DataWorks Call Qualification Checker."
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

if not is_paid:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown("### 💳 Subscription required")
    st.write(
        "Your account is created, but you don't have an active subscription yet."
    )
    st.write("Once you've paid, your access will be activated by Shulver DataWorks.")

    # TODO: replace with your real Stripe checkout link
    subscribe_url = "https://YOUR_STRIPE_CHECKOUT_LINK_HERE"
    st.markdown(f"[Subscribe now]({subscribe_url})")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ---------- MAIN TOOL UI ----------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="hero-title">Call Qualification Checker</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">Check if a number qualifies and see its country & local time in seconds.</div>',
    unsafe_allow_html=True,
)

number = st.text_input("Phone number (with + country code)", placeholder="+447123456789")
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

            # Status pill HTML
            if allowed:
                status_html = '<span class="pill pill-ok">QUALIFIES</span>'
            else:
                status_html = '<span class="pill pill-bad">DOES NOT QUALIFY</span>'

 # Save to history (optional)
history_error_placeholder = st.empty()
try:
    supabase.table("call_history").insert(
        {
            "user_id": user.id,
            "number": number,
            "country": f"{country} ({region})",
            "qualifies": allowed,
        }
    ).execute()
except Exception as e:
    # Show a small warning if history fails, but don't crash the app
    history_error_placeholder.warning(f"History not saved: {e}")


         # --- Show result card ---
st.markdown('<div class="result-card">', unsafe_allow_html=True)

# Number origin section
st.markdown(
    f"""
    <div class='result-label'>Number origin</div>
    <div class='result-main'>{country} ({region})</div>
    """,
    unsafe_allow_html=True,
)

# Status section
st.markdown(
    f"""
    <div class='result-label' style='margin-top:0.4rem;'>Status</div>
    {status_html}
    """,
    unsafe_allow_html=True,
)

# Timezone section (only if API included timezone data)
if result.get("has_timezone"):

    diff = result["diff_hours"]
    diff_str = f"{diff:+.1f} hours"

    st.markdown(
        f"""
        <div class='result-label' style='margin-top:0.7rem;'>Time information</div>

        <div class='result-time'>
            <div>
                <div class='time-sub'>YOUR TIMEZONE</div>
                <div>{result['your_timezone']}</div>
                <div class='time-sub' style='margin-top:0.4rem;'>YOUR LOCAL TIME</div>
                <div>{result['your_time']}</div>
            </div>

            <div>
                <div class='time-sub'>THEIR LOCAL TIME</div>
                <div>{result['their_time']}</div>
                <div class='time-sub' style='margin-top:0.4rem;'>DIFFERENCE</div>
                <div>{diff_str}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)


# ---------- BLOCKED LIST ----------
with st.expander("View NOT-qualified country codes"):
    st.write(sorted(BLOCKED_COUNTRIES))
    st.caption("These countries (plus all of Africa) do NOT qualify.")

# ---------- HISTORY SECTION ----------
st.markdown('<div class="history-title">Recently checked numbers</div>', unsafe_allow_html=True)

try:
    hist_res = (
        supabase.table("call_history")
        .select("*")
        .eq("user_id", user.id)
        .order("created_at", desc=True)
        .limit(10)
        .execute()
    )
if logged_in:
    # do result display
    ...

    # --- Retrieve history ---
    history = []
    try:
        hist_res = supabase.table("call_history").select("*").eq("user_id", user.id).order("id", desc=True).execute()
        history = hist_res.data or []
    except Exception as e:
        st.error(f"Error loading history: {e}")

    # --- Show history ---
    if history:
        st.subheader("Recently checked numbers")
        for h in history:
            st.markdown(
                f"**{h['number']}** — {h['country']} ({h['qualifies']})",
                unsafe_allow_html=True
            )
    else:
        st.write("No history yet.")

        )
else:
    st.markdown("<div class='history-empty'>No history yet.</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='history-empty'>No history yet.</div>", unsafe_allow_html=True)

# ---------- FOOTER ----------
st.markdown(
    "<div class='footer'>© Shulver DataWorks — Call Qualification Checker</div>",
    unsafe_allow_html=True,
)




