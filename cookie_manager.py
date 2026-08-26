from streamlit_cookies_manager import EncryptedCookieManager
import streamlit as st


cookies = EncryptedCookieManager(
    prefix="flight_assistant",
    password="FhS4WE7pk"
)


if not cookies.ready():
    st.stop()