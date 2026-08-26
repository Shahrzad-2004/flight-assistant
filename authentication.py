from authlib.integrations.requests_client import OAuth2Session
from user_database import create_google_user
from cookie_manager import cookies
import streamlit as st


def get_google_auth_url():

    google = OAuth2Session(
        client_id=st.secrets["google"]["client_id"],
        client_secret=st.secrets["google"]["client_secret"],
        redirect_uri=st.secrets["google"]["redirect_uri"]
    )

    authorization_url, state = google.create_authorization_url(
        "https://accounts.google.com/o/oauth2/auth",
        scope="openid email profile"
    )

    st.session_state["oauth_state"] = state
    return authorization_url


def render_auth_buttons():

    if "show_email_login" not in st.session_state:
        st.session_state.show_email_login = False

    google_url = get_google_auth_url()

    left_space, col1, col2, right_space = st.columns([1, 2, 2, 1])

    with col1:
        st.markdown(
            f"""
            <a href="{google_url}" target="_self" class="auth-btn auth-btn-link">
                🔐 Google ورود / ثبت نام با 
            </a>
            """,
            unsafe_allow_html=True
        )

    with col2:
        if st.button(
            "🔐 Gmail ورود / ثبت نام با ",
            key="email_login_button",
            use_container_width=True
        ):
            st.session_state.show_email_login = True
def handle_google_callback():

    if "code" not in st.query_params:
        return False


    google = OAuth2Session(
        client_id=st.secrets["google"]["client_id"],
        client_secret=st.secrets["google"]["client_secret"],
        redirect_uri=st.secrets["google"]["redirect_uri"]
    )


    token = google.fetch_token(
        "https://oauth2.googleapis.com/token",
        code=st.query_params["code"]
    )


    google = OAuth2Session(
        st.secrets["google"]["client_id"],
        token=token
    )


    user_info = google.get(
        "https://openidconnect.googleapis.com/v1/userinfo"
    ).json()


    user_id = create_google_user(
    user_info["sub"],
    user_info["email"],
    user_info.get("name"),
    user_info.get("picture")
)


    st.session_state.user = {

        "id": user_id,

        "google_id": user_info["sub"],

        "email": user_info["email"],

        "name": user_info.get("name"),

        "picture": user_info.get("picture")

    }
    cookies["user_id"] = str(user_id)
    cookies.save()


    st.query_params.clear()

    st.rerun()