import base64
import uuid
from pathlib import Path

import streamlit as st
from datetime import datetime
import jdatetime
from chat_database import create_tables, save_message, load_messages,list_sessions,delete_session
from flight_graph import flight_graph

from styles import (
    inject_background_style,
    inject_main_style,
    inject_cabin_and_passenger_style,
    inject_confirmation_style,
    inject_sidebar_style,
    render_header,
)
from ui_handlers import (
    scroll_to_bottom,
    select_cabin_class,
    select_passenger_option,
    save_passenger_counts,
    confirm_flight,
    edit_flight,
    start_new_conversation,
    switch_session,
    remove_session,
    toggle_sidebar,

)
from chat_response import handle_user_prompt

create_tables()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True
# تنظیمات صفحه
st.set_page_config(
    page_title="دستیار هوشمند بلیط",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# خواندن عکس
BASE_DIR = Path(__file__).parent


def get_base64(file_name):
    path = BASE_DIR / file_name
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def to_jalali(date_str):

    if not date_str:
        return "-"

    try:
        gregorian_date = datetime.strptime(
            str(date_str),
            "%Y-%m-%d"
        ).date()

        jalali_date = jdatetime.date.fromgregorian(
            date=gregorian_date
        )

        return jalali_date.strftime("%Y/%m/%d")

    except (ValueError, TypeError):
        return str(date_str)

def get_cabin_label(cabin_class):

    cabin_labels = {
        "economy": "اکونومی",
        "business": "بیزینس",
        "first": "فرست کلاس",
        "unspecified": "اهمیت ندارد"
    }

    return cabin_labels.get(
        cabin_class,
        "-"
    )
background = get_base64("ee.jpg")

# تزریق استایل‌ها
inject_background_style(background)
inject_main_style()
inject_cabin_and_passenger_style()
inject_confirmation_style()
inject_sidebar_style(st.session_state.sidebar_open)
# -----------------------------
# دکمه شناور باز/بسته کردن نوار کناری (همیشه در دسترس)
# -----------------------------
st.button(
    "☰",
    key="sidebar_toggle_button",
    on_click=toggle_sidebar
)

# -----------------------------
# نوار کناری: گفتگوی جدید + فهرست گفتگوهای اخیر
# -----------------------------
with st.sidebar:

    with st.container(key="sidebar_header_box"):

        st.markdown(
            '<div class="sidebar-title">✈️ دستیار هوشمند بلیط</div>',
            unsafe_allow_html=True
        )

        st.button(
            "گفتگوی جدید 💬",
            key="new_chat_button",
            use_container_width=True,
            on_click=start_new_conversation
        )

    st.markdown(
        '<div class="sidebar-section-title">گفتگوهای اخیر</div>',
        unsafe_allow_html=True
    )

    sessions = list_sessions()

    if not sessions:

        st.markdown(
            '<div class="sidebar-empty">هنوز گفتگویی ذخیره نشده است.</div>',
            unsafe_allow_html=True
        )

    for session in sessions:

        row_label, row_delete = st.columns([5, 1])

        is_active = session["session_id"] == st.session_state.session_id

        with row_label:
            st.button(
                ("🟦 " if is_active else "💬 ") + session["title"],
                key=f"session_{session['session_id']}",
                use_container_width=True,
                on_click=switch_session,
                args=(session["session_id"],)
            )

        with row_delete:
            st.button(
                "🗑️",
                key=f"delete_{session['session_id']}",
                use_container_width=True,
                on_click=remove_session,
                args=(session["session_id"],)
            )
# هدر
render_header()


if "messages" not in st.session_state:

    st.session_state.messages = [

        {
            "role": "assistant",
            "content": "سلام من دستیارهوشمند رزرو بلیط هستم. چطور می توانم در رزرو بلیط کمکتان کنم ؟ "
        }

    ]

# ساخت باکس برای پیام ها و نمایش پیام ها در صفحه چت

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# بررسی نوع رابطی که لنگ گراف درخواست کرده و ورودی کاربر
# یعنی رابط کاربری فعلی مثلا الان داره شمارنده مسافران رو نشون میده یا باتن های نوع پرواز یا ....
current_ui = st.session_state.get(
    "flight_state",{}).get("ui_type")
print("current_ui",current_ui)

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
    # در این مرحله کادر چت نمایش داده نشود
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
        "بیزینس",
        key="business_button",
        use_container_width=True,
        on_click=select_cabin_class,
        args=("business", "بیزینس")
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
    prompt = None
elif current_ui == "confirmation":

    flight_state = st.session_state["flight_state"]

    st.markdown(
        """
    <div class="cabin-title">
    لطفاً اطلاعات پرواز را بررسی کنید:
    </div>
    """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
    <div class="confirmation-box">
    <div class="confirmation-row">
    <span class="confirmation-label">مبدأ:</span>
    <span class="confirmation-value">{flight_state.get("origin") or "-"}</span>
    </div>

    <div class="confirmation-row">
    <span class="confirmation-label">مقصد:</span>
    <span class="confirmation-value">{flight_state.get("destination") or "-"}</span>
    </div>

    <div class="confirmation-row">
    <span class="confirmation-label">تاریخ حرکت:</span>
    <span class="confirmation-value">{to_jalali(flight_state.get("departure_date"))}</span>
    </div>

    <div class="confirmation-row">
    <span class="confirmation-label">بزرگسال:</span>
    <span class="confirmation-value">{flight_state.get("adults", 0)}</span>
    </div>

    <div class="confirmation-row">
    <span class="confirmation-label">کودک:</span>
    <span class="confirmation-value">{flight_state.get("children", 0)}</span>
    </div>

    <div class="confirmation-row">
    <span class="confirmation-label">نوزاد:</span>
    <span class="confirmation-value">{flight_state.get("infants", 0)}</span>
    </div>

    <div class="confirmation-row">
    <span class="confirmation-label">کلاس پرواز:</span>
    <span class="confirmation-value">{get_cabin_label(flight_state.get("cabin_class"))}</span>
    </div>
    </div>
    """,
        unsafe_allow_html=True
    )
    col1, col2 = st.columns(2)

    col1.button(
        "تأیید و جستجوی پرواز",
        key="confirm_flight_button",
        use_container_width=True,
        on_click=confirm_flight
    )

    col2.button(
        "ویرایش اطلاعات",
        key="edit_flight_button",
        use_container_width=True,
        on_click=edit_flight
    )

    scroll_to_bottom()

    prompt = None
else:
    prompt = st.chat_input(
        "درخواست خود را بنویسید"
    )

st.markdown(
    "</div>",
    unsafe_allow_html=True
)


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
