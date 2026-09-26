import streamlit as st

# باید قبل از ایمپورت کتابخانه پچ بشه، چون خود کتابخانه
# در لحظه‌ی ایمپورت از @st.cache استفاده می‌کند
st.cache = st.cache_resource

from streamlit_cookies_manager import EncryptedCookieManager

cookie_password = st.secrets.get("COOKIE_PASSWORD")

if not cookie_password:
    raise RuntimeError(
        "کلید COOKIE_PASSWORD در فایل secrets.toml پیدا نشد. "
        "یک مقدار تصادفی و طولانی برایش بساز و در "
        ".streamlit/secrets.toml قرار بده (این فایل نباید کامیت شود)."
    )

cookies = EncryptedCookieManager(
    prefix="flight_assistant",
    password=cookie_password
)


if not cookies.ready():
    st.stop()