import base64
import uuid
from pathlib import Path

import streamlit as st

from chat_database import create_tables, save_message, load_messages
from flight_graph import flight_graph

from styles import (
    inject_background_style,
    inject_main_style,
    inject_cabin_and_passenger_style,
    render_header,
)
from ui_handlers import (
    scroll_to_bottom,
    select_cabin_class,
    select_passenger_option,
    save_passenger_counts,
)
from chat_response import handle_user_prompt

create_tables()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# تنظیمات صفحه
st.set_page_config(
    page_title="دستیار هوشمند بلیط",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# خواندن عکس
BASE_DIR = Path(__file__).parent


def get_base64(file_name):
    path = BASE_DIR / file_name
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


background = get_base64("ee.jpg")

# تزریق استایل‌ها
inject_background_style(background)
inject_main_style()
inject_cabin_and_passenger_style()

# هدر
render_header()


if "messages" not in st.session_state:

    st.session_state.messages = [

        {
            "role": "assistant",
            "content": "سلام من دستیارهوشمند رزرو بلیط هستم. چطور می توانم در رزرو بلیط کمکتان کنم ؟ "
        }

    ]


# -----------------------------
# نمایش پیام‌ها
# -----------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# -----------------------------
# بررسی نوع رابطی که LangGraph درخواست کرده و ورودی کاربر
# -----------------------------
# بررسی نوع رابطی که LangGraph درخواست کرده
current_ui = st.session_state.get(
    "flight_state",
    {}
).get("ui_type")


if current_ui == "passenger_choice":

    st.markdown(
        """
        <div class="cabin-title">
            آیا می‌خواهید تعداد مسافران را مشخص کنید؟
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    col1.button(
        "وارد می‌کنم",
        key="passenger_enter_button",
        use_container_width=True,
        on_click=select_passenger_option,
        args=("enter",)
    )

    col2.button(
        "وارد نمی‌کنم",
        key="passenger_default_button",
        use_container_width=True,
        on_click=select_passenger_option,
        args=("default",)
    )

    scroll_to_bottom()

    # هنگام نمایش دکمه‌ها chat_input نباشد
    prompt = None

elif current_ui == "passenger_counter":

    st.markdown(
        """
        <div class="cabin-title">
            تعداد مسافران را مشخص کنید:
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.number_input(
            "بزرگسال",
            min_value=1,
            value=1,
            step=1,
            key="adult_count"
        )

    with col2:

        st.number_input(
            "کودک",
            min_value=0,
            value=0,
            step=1,
            key="child_count"
        )

    with col3:

        st.number_input(
            "نوزاد",
            min_value=0,
            value=0,
            step=1,
            key="infant_count"
        )

    st.button(
        "ثبت تعداد مسافران",
        key="save_passenger_counts_button",
        use_container_width=True,
        on_click=save_passenger_counts
    )

    scroll_to_bottom()

    prompt = None

elif current_ui == "cabin_buttons":

    st.markdown(
    """
    <div class="cabin-title">
        کلاس پرواز را انتخاب کنید:
    </div>
    """,
    unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.button(
        "اکونومی",
        key="economy_button",
        use_container_width=True,
        on_click=select_cabin_class,
        args=("economy", "اکونومی")
    )

    col2.button(
        "بیزنس",
        key="business_button",
        use_container_width=True,
        on_click=select_cabin_class,
        args=("business", "بیزنس")
    )

    col3.button(
        "فرست‌ کلاس",
        key="first_button",
        use_container_width=True,
        on_click=select_cabin_class,
        args=("first", "فرست‌ کلاس")
    )

    col4.button(
        "اهمیت ندارد",
        key="unspecified_button",
        use_container_width=True,
        on_click=select_cabin_class,
        args=("unspecified", "اهمیت ندارد")
    )
    scroll_to_bottom()
    # در این مرحله کادر چت نمایش داده نشود
    prompt = None

else:
    prompt = st.chat_input(
        "درخواست خود را بنویسید"
    )

st.markdown(
    "</div>",
    unsafe_allow_html=True
)

# -----------------------------
# پاسخ ربات
# -----------------------------

if prompt:

    # پیام کاربر
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )
    save_message(
    st.session_state.session_id,
    "user",
    prompt
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    handle_user_prompt(prompt)

    st.rerun()
