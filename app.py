import streamlit as st
from supabase import create_client, Client
from logic import analyse_number, HOME_TZ, BLOCKED_COUNTRIES

# ---------- PAGE SETUP ----------
st.set_page_config(
    page_title="Call Qualification Checker · Shulver DataWorks",
    page_icon="📞",
    layout="centered",
)

# ---------- GLOBAL STYLES ----------
st.markdown(
    """
<style>

/* ----------------------------
   Global Layout & Background
-----------------------------*/

body, html, .stApp {
    background-color: #1b1b1b !important;  /* Dark grey */
    color: #f2f2f2 !important;            /* White text */
    font-family: 'Inter', sans-serif;
}

/* Remove top padding Streamlit adds */
header[data-testid="stHeader"] {
    height: 1rem;
}

/* ----------------------------
   Branding Header Bar
-----------------------------*/

.top-nav {
    width: 100%;
    background-color: #004225; /* British Racing Green */
    padding: 1.1rem 1.6rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 3px solid #002e19;
}

.nav-title {
    font-size: 1.7rem;
    font-weight: 800;
    color: white;
    letter-spacing: 0.5px;
}

.nav-subtitle {
    font-size: 0.95rem;
    color: #d8e8df;
    opacity: 0.9;
}

/* ----------------------------
   Input Fields
-----------------------------*/

input, textarea {
    background-color: #2b2b2b !important;
    color: #ffffff !important;
    border: 1px solid #555 !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    font-size: 1rem !important;
}

input::placeholder {
    color: #bfbfbf !important;
}

/* Radio buttons text */
.stRadio label {
    color: #f2f2f2 !important;
}

/* ----------------------------
   Buttons
-----------------------------*/

.stButton button {
    background-color: #004225 !important;
    color: white !important;
    font-weight: 700 !important;
    padding: 0.7rem 1.3rem !important;
    border-radius: 10px !important;
    border: none !important;
    transition: 0.2s ease-in-out;
    font-size: 1rem;
}

.stButton button:hover {
    background-color: #006837 !important;
    transform: scale(1.03);
}

/* ----------------------------
   Cards (Results + History)
-----------------------------*/

.result-card, .history-item {
    background: #262626;
    border: 1px solid #3b3b3b;
    border-radius: 14px;
    padding: 18px 20px;
    margin-top: 1.2rem;
}

.result-label {
    font-size: 1rem;
    color: #cccccc;
}

.result-main {
    font-size: 1.45rem;
    font-weight: 600;
    margin-top: 0.2rem;
}

/* ----------------------------
   Status Pills
-----------------------------*/

.pill-ok {
    background: #1c6e39;
    padding: 6px 12px;
    border-radius: 25px;
    font-weight: 700;
    color: white;
    display: inline-block;
    margin-top: 5px;
}

.pill-bad {
    background: #7a0000;
    padding: 6px 12px;
    border-radius: 25px;
    font-weight: 700;
    color: white;
    display: inline-block;
    margin-top: 5px;
}

/* ----------------------------
   Time Info
-----------------------------*/

.time-grid {
    display: flex;
    justify-content: space-between;
    margin-top: 1rem;
    gap: 40px;
}

.small-label {
    font-size: 0.75rem;
    color: #bbbbbb;
}

.small-value {
    font-size: 1rem;
    color: white;
}

/* ----------------------------
   History Section
-----------------------------*/

.history-title {
    margin-top: 2.5rem;
    font-size: 1.5rem;
    font-weight: 700;
    color: #e8e8e8;
}

.history-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.history-status {
    font-size: 0.85rem;
    color: #d1d1d1;
}

.history-empty {
    margin-top: 1rem;
    color: #999;
}

/* ----------------------------
   Mobile Responsiveness
-----------------------------*/

@media (max-width: 768px) {
    .time-grid {
        flex-direction: column;
        gap: 15px;
    }

    .nav-title {
        font-size: 1.4rem;
    }

    .result-main {
        font-size: 1.25rem;
    }
}

</style>
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

        # --- Save to history in Supabase ---
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
            st.error(f"Error saving history: {e}")

        # --- Show result card ---
       # --- SHOW RESULT CARD ---
st.markdown('<div class="result-card">', unsafe_allow_html=True)

# Number origin
st.markdown(
    f"""
    <div class="result-label">Number origin</div>
    <div class="result-main">{country} ({region})</div>
    """,
    unsafe_allow_html=True,
)

# Status (qualifies / not)
st.markdown(
    f"""
    <div class="result-label" style="margin-top:0.4rem;">Status</div>
    {status_html}
    """,
    unsafe_allow_html=True,
)

# Timezone information
if result.get("has_timezone"):
    diff = result["diff_hours"]
    diff_str = f"{diff:+.1f} hours"
    st.markdown(
        """
        <div class="result-label" style="margin-top:0.7rem;">Time Information</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="time-grid">
            <div>
                <div class="small-label">YOUR TIMEZONE</div>
                <div class="small-value">{user_tz}</div>
                <div class="small-label" style="margin-top:0.3rem;">YOUR LOCAL TIME</div>
                <div class="small-value">{your_time}</div>
            </div>

            <div>
                <div class="small-label">THEIR LOCAL TIME</div>
                <div class="small-value">{their_time}</div>
                <div class="small-label" style="margin-top:0.3rem;">DIFFERENCE</div>
                <div class="small-value">{diff_str}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Close the result card container
st.markdown('</div>', unsafe_allow_html=True)


# --- SAVE TO HISTORY ---
try:
    supabase.table("call_history").insert({
        "user_id": user.id,
        "number": number,
        "country": f"{country} ({region})",
        "qualifies": allowed
    }).execute()

except Exception as e:
    st.error(f"Error saving history: {e}")


# --- SHOW HISTORY ---
st.markdown("<h3 class='history-title'>Previously Checked Numbers</h3>", unsafe_allow_html=True)

history = supabase.table("call_history") \
    .select("*") \
    .eq("user_id", user.id) \
    .order("created_at", desc=True) \
    .limit(5) \
    .execute()

if history.data:
    for row in history.data:
        st.markdown(
            f"""
            <div class="history-item">
                <div><strong>{row['number']}</strong> — {row['country']}</div>
                <div class="history-status">{'QUALIFIES' if row['qualifies'] else 'NOT QUALIFIED'}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.markdown("<div class='history-empty'>No history yet.</div>", unsafe_allow_html=True)


# ---------- BLOCKED COUNTRIES EXPANDER ----------
with st.expander("View NOT-qualified country codes"):
    st.write(sorted(BLOCKED_COUNTRIES))
    st.caption("These countries (plus all of Africa) do NOT qualify.")

# ---------- FOOTER ----------
st.markdown(
    "<div class='footer'>© Shulver DataWorks — Call Qualification Checker</div>",
    unsafe_allow_html=True,
)






