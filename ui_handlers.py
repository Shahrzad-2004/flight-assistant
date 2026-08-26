"""
توابع رویدادی (callback) رابط کاربری: اسکرول خودکار، ثبت انتخاب کلاس
پرواز، ثبت گزینه تعداد مسافر و ذخیره تعداد مسافران وارد شده.

همه‌ی این توابع state چت را در st.session_state به‌روزرسانی می‌کنند
و Graph پروازها (flight_graph) را دوباره اجرا می‌کنند.
"""
import uuid
import streamlit as st
import streamlit.components.v1 as components

from cookie_manager import cookies
from flight_graph import flight_graph
from chat_database import save_message, load_messages, delete_session
WELCOME_MESSAGE = (
    "سلام من دستیارهوشمند رزرو بلیط هستم. "
    "چطور می توانم در رزرو بلیط کمکتان کنم ؟ "
)

def scroll_to_bottom():

    components.html(
        """
        <script>
            setTimeout(function () {
                window.frameElement.scrollIntoView({
                    behavior: "smooth",
                    block: "end"
                });
            }, 400);
        </script>
        """,
        height=0
    )


# ثبت انتخاب کلاس پرواز
def select_cabin_class(cabin_value, cabin_label):

    current_state = st.session_state["flight_state"].copy()

    # قرار دادن انتخاب کاربر در State
    current_state["cabin_class"] = cabin_value

    # اجرای دوباره گراف برای تعیین مرحله بعد
    graph_result = flight_graph.invoke(current_state)
    st.session_state["flight_state"] = graph_result
    print(
        "FINAL SESSION FLIGHT STATE:",
        st.session_state["flight_state"]
    )
    user_message = f"کلاس پرواز: {cabin_label}"

    # ذخیره پیام انتخاب کاربر در حافظه
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    save_message(
        st.session_state.session_id,
        "user",
        user_message
    )

    # ذخیره پاسخ مرحله بعد گراف
    assistant_message = graph_result["assistant_message"]

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": assistant_message
        }
    )

    save_message(
        st.session_state.session_id,
        "assistant",
        assistant_message
    )

def select_passenger_option(option):

    current_state = st.session_state["flight_state"].copy()

    # کاربر می‌ خواهد خودش تعداد را وارد کند
    if option == "enter":

        current_state["passenger_status"] = "entering"

        user_message = "تعداد مسافران را وارد می‌کنم."

    # کاربر نمی‌خواهد تعداد را وارد کند
    else:

        current_state["adults"] = 1
        current_state["children"] = 0
        current_state["infants"] = 0

        current_state["passenger_status"] = "resolved"

        # برای سازگاری با ساختار فعلی گراف
        current_state["passengers_confirmed"] = True
        user_message = "تعداد مسافران را وارد نمی‌کنم."

    # اجرای دوباره گراف
    graph_result = flight_graph.invoke(current_state)

    # ذخیره State جدید
    st.session_state["flight_state"] = graph_result
    print(
        "FINAL SESSION FLIGHT STATE:",
        st.session_state["flight_state"]
    )
    # ذخیره پیام کاربر در چت
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    save_message(
        st.session_state.session_id,
        "user",
        user_message
    )

    # پاسخ گراف
    assistant_message = graph_result[
        "assistant_message"
    ]

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": assistant_message
        }
    )

    save_message(
        st.session_state.session_id,
        "assistant",
        assistant_message
    )

    print(
        "PASSENGER OPTION RESULT:",
        graph_result
    )
def save_passenger_counts():

    current_state = st.session_state["flight_state"].copy()

    # دریافت مقادیر شمارنده‌ها
    current_state["adults"] = (st.session_state["adult_count"])
    current_state["children"] = (st.session_state["child_count"])
    current_state["infants"] = (st.session_state["infant_count"])

    # تعداد مسافران مشخص شده
    current_state["passenger_status"] = "resolved"

    # برای سازگاری با ساختار فعلی Graph
    current_state["passengers_confirmed"] = True

    user_message = (
        f"تعداد مسافران: "
        f"{current_state['adults']} بزرگسال، "
        f"{current_state['children']} کودک، "
        f"{current_state['infants']} نوزاد"
    )

    # اجرای دوباره لنگ گراف
    graph_result = flight_graph.invoke(current_state)

    st.session_state["flight_state"] = graph_result

    # ذخیره پیام انتخاب کاربر
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    save_message(
        st.session_state.session_id,
        "user",
        user_message
    )

    # ذخیره پاسخ گراف
    assistant_message = graph_result["assistant_message"]

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": assistant_message
        }
    )

    save_message(
        st.session_state.session_id,
        "assistant",
        assistant_message
    )

    print(
        "PASSENGER COUNTER RESULT:",
        graph_result
    )
def confirm_flight():

    current_state = st.session_state["flight_state"].copy()

    current_state["confirmation_status"] = "confirmed"

    graph_result = flight_graph.invoke(current_state)

    st.session_state["flight_state"] = graph_result

    user_message = "اطلاعات پرواز را تأیید می‌کنم."

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    save_message(
        st.session_state.session_id,
        "user",
        user_message
    )

    assistant_message = graph_result["assistant_message"]

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": assistant_message
        }
    )

    save_message(
        st.session_state.session_id,
        "assistant",
        assistant_message
    )


def edit_flight():

    current_state = st.session_state["flight_state"].copy()

    current_state["confirmation_status"] = "editing"

    graph_result = flight_graph.invoke(current_state)

    st.session_state["flight_state"] = graph_result

    user_message = "می‌خواهم اطلاعات پرواز را ویرایش کنم."

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    save_message(
        st.session_state.session_id,
        "user",
        user_message
    )

    assistant_message = graph_result["assistant_message"]

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": assistant_message
        }
    )

    save_message(
        st.session_state.session_id,
        "assistant",
        assistant_message
    )
def toggle_sidebar():
    """باز یا بسته کردن نوار کناری کشویی با دکمه شناور بالای صفحه."""
    st.session_state.sidebar_open = not st.session_state.get(
        "sidebar_open",
        True
    )


def start_new_conversation():
    """ساخت یک گفتگوی تازه و خالی و فعال کردن آن."""
    st.session_state.session_id = str(uuid.uuid4())

    st.session_state.messages = [
        {
            "role": "assistant",
            "content": WELCOME_MESSAGE
        }
    ]

    st.session_state.flight_state = {}


def switch_session(session_id: str):
    """جابه‌جایی به یکی از گفتگوهای ذخیره‌شده و بارگذاری تاریخچه آن."""
    st.session_state.session_id = session_id

    messages = load_messages(session_id)

    if not messages:
        messages = [
            {
                "role": "assistant",
                "content": WELCOME_MESSAGE
            }
        ]

    st.session_state.messages = messages
    st.session_state.flight_state = {}


def remove_session(session_id: str):
    """حذف یک گفتگوی ذخیره‌شده از پایگاه داده (به‌صورت تکی)."""
    delete_session(session_id)

    # اگر گفتگوی فعلی حذف شد، یک گفتگوی جدید و خالی بساز
    if session_id == st.session_state.get("session_id"):
        start_new_conversation()


def logout_user():
    """خروج کاربر از حساب: پاک کردن session و کوکی."""
    st.session_state.pop("user", None)

    try:
        del cookies["user_id"]
        cookies.save()
    except KeyError:
        pass
