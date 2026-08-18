"""
توابع رویدادی (callback) رابط کاربری: اسکرول خودکار، ثبت انتخاب کلاس
پرواز، ثبت گزینه تعداد مسافر و ذخیره تعداد مسافران وارد شده.

همه‌ی این توابع state چت را در st.session_state به‌روزرسانی می‌کنند
و Graph پروازها (flight_graph) را دوباره اجرا می‌کنند.
"""
import streamlit as st
import streamlit.components.v1 as components

from flight_graph import flight_graph
from chat_database import save_message


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

    # اجرای دوباره Graph برای تعیین مرحله بعد
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

    # ذخیره پاسخ مرحله بعد Graph
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

    current_state = st.session_state[
        "flight_state"
    ].copy()

    # کاربر می‌خواهد خودش تعداد را وارد کند
    if option == "enter":

        current_state["passenger_status"] = "entering"

        user_message = "تعداد مسافران را وارد می‌کنم."

    # کاربر نمی‌خواهد تعداد را وارد کند
    else:

        current_state["adults"] = 1
        current_state["children"] = 0
        current_state["infants"] = 0

        current_state["passenger_status"] = "resolved"

        # برای سازگاری با ساختار فعلی Graph
        current_state["passengers_confirmed"] = True

        user_message = "تعداد مسافران را وارد نمی‌کنم."

    # اجرای دوباره Graph
    graph_result = flight_graph.invoke(
        current_state
    )

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

    # پاسخ Graph
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

    current_state = st.session_state[
        "flight_state"
    ].copy()

    # دریافت مقادیر شمارنده‌ها
    current_state["adults"] = (
        st.session_state["adult_count"]
    )

    current_state["children"] = (
        st.session_state["child_count"]
    )

    current_state["infants"] = (
        st.session_state["infant_count"]
    )

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

    # اجرای دوباره LangGraph
    graph_result = flight_graph.invoke(
        current_state
    )

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

    # ذخیره پاسخ Graph
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
        "PASSENGER COUNTER RESULT:",
        graph_result
    )
