import streamlit as st

# باید قبل از ایمپورت کتابخانه پچ بشه، چون خود کتابخانه
# در لحظه‌ی ایمپورت از @st.cache استفاده می‌کند
st.cache = st.cache_resource

from streamlit_cookies_manager import EncryptedCookieManager


def get_cookie_manager():
    cookies = EncryptedCookieManager(
        prefix="flight_assistant",
        password=st.secrets["COOKIE_PASSWORD"]
    )

    if not cookies.ready():
        st.stop()

    return cookies