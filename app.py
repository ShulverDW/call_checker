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


st.markdown("""
<style>

/* === GLOBAL BACKGROUND === */
.stApp {
    background-color: #1c1c1c;   /* Dark grey */
    color: #ffffff !important;
    font-family: 'Segoe UI', sans-serif;
}

/* Move content DOWN slightly */
.block-container {
    padding-top: 2rem !important;
    max-width: 900px !important;
}

/* === HEADER BAR === */
.top-header {
    width: 100%;
    background-color: #004225;  /* British Racing Green */
    padding: 1.1rem 1.4rem;
    border-radius: 12px;
    margin-bottom: 1.8rem;   /* DROP HEADER LOWER */
    color: white;
    font-weight: 700;
    font-size: 1.35rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header-brand {
    font-size: 1rem;
    font-weight: 600;
    opacity: 0.9;
}

/* === TITLES === */
.hero-title {
    font-size: 1.7rem;
    font-weight: 800;
    margin-bottom: 0.3rem;
    color: white;
}

.hero-subtitle {
    color: #cccccc;
    font-size: 0.95rem;
    margin-bottom: 1rem;
}

/* === CARDS === */
.main-card, .login-card {
    background-color: #2a2a2a;   /* slightly lighter dark grey */
    padding: 1.4rem;
    border-radius: 14px;
    border: 1px solid #3a3a3a;
    margin-bottom: 1.6rem;
}

/* === BUTTONS === */
.stButton>button {
    background-color: #004225 !important;   /* British racing green */
    color: white !important;
    border-radius: 8px !important;
    padding: 0.55rem 1.2rem !important;
    font-weight: 600 !important;
    border: none;
}

.stButton>button:hover {
    background-color: #006b3c !important;
}

/* === RESULT CARD === */
.result-card {
    background-color: #2a2a2a;
    border: 1px solid #004225;
    padding: 1.3rem;
    border-radius: 12px;
}

.result-label {
    font-size: 0.8rem;
    text-transform: uppercase;
    opacity: 0.7;
}

/* Bigger + clearer result text */
.result-main {
    font-size: 1.45rem;
    font-weight: 800;
    margin-bottom: 0.4rem;
    color: white;
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
    color: white;
}

.pill-bad {
    background-color: #7a1a1a;
    color: white;
}

/* Fix radio + labels not showing */
label, .stRadio label {
    color: white !important;
}

/* Footer */
.footer {
    text-align: center;
    color: #aaaaaa;
    font-size: 0.8rem;
    margin-top: 1.8rem;
}

</style>
""", unsafe_allow_html=True)

