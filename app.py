# app.py

import streamlit as st
from logic import analyse_number, HOME_TZ, BLOCKED_COUNTRIES

st.set_page_config(page_title="Call Checker", page_icon="📞")

st.title("📞 Call Qualification Checker")

st.write(
    "Paste a phone number with country code (for example: `+447123456789`).\n\n"
    "This app will tell you:\n"
    "- Which country the number is from\n"
    "- Whether it QUALIFIES (not on your blocked list)\n"
    "- The local time there and the time difference from you"
)

number = st.text_input("Phone number (with +country code)", placeholder="+447123456789")

if st.button("Check number"):
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

            st.subheader("Result")

            if allowed:
                st.success(f"✅ QUALIFIES: {country} ({region}) is allowed.")
            else:
                st.error(f"❌ DOES NOT QUALIFY: {country} ({region}) is on the not-qualified list.")

            if result.get("has_timezone"):
                diff = result["diff_hours"]
                diff_str = f"{diff:+.1f} hours"

                st.markdown("---")
                st.markdown(f"**Your timezone:** `{HOME_TZ.zone}`")
                st.markdown(f"**Your local time:** {result['home_time']}")
                st.markdown(f"**Their local time:** {result['dest_time']}")
                st.markdown(f"**Time difference:** {diff_str}")
            else:
                st.info(result.get("error", "No timezone info available for this number."))

with st.expander("View NOT-qualified country codes"):
    st.write(sorted(BLOCKED_COUNTRIES))
    st.caption("These countries (plus all of Africa) do NOT qualify.")
