"""
تولید پاسخ ربات برای پیام تازه‌ی کاربر: استخراج اطلاعات پرواز،
ادغام با وضعیت مکالمه، اجرای LangGraph و ذخیره‌ی نتیجه در چت.
"""
import time

import streamlit as st

from flight_graph import flight_graph
from chat_database import save_message
from flight_logic import extract_flight_request, merge_flight_state


def handle_user_prompt(prompt: str) -> None:
    """پردازش پیام کاربر و افزودن پاسخ دستیار به تاریخچه‌ی چت.

    این تابع معادل بلوک ``if prompt:`` در نسخه‌ی قبلی app.py است.
    """
    # نمایش حالت تایپ کردن
    with st.chat_message("assistant"):

      with st.spinner("✈️ در حال جستجوی بهترین پرواز..."):

            time.sleep(1.5)

            with st.spinner("✈️ در حال بررسی درخواست شما..."):

                try:
                    flight_request = extract_flight_request(prompt)
                    print(
                    "Passengers:",
                    flight_request.adults,
                    flight_request.children,
                    flight_request.infants,
                    "Provided:",
                    flight_request.passenger_count_provided
                    )
                    current_state = merge_flight_state(
                        flight_request
                    )

                    st.session_state["flight_state"] = current_state

                    print(
                        "MERGED FLIGHT STATE:",
                        current_state
                    )

                    if not flight_request.is_flight_request:

                        answer = (
                            "لطفاً درخواست خود را درباره جستجوی "
                            "بلیط هواپیما بنویسید."
                        )

                    else:
                        missing_fields = []

                        if not current_state.get("origin"):
                            missing_fields.append("مبدأ")

                        if not current_state.get("destination"):
                            missing_fields.append("مقصد")

                        if not current_state.get("departure_date"):
                            missing_fields.append("تاریخ حرکت")

                        if missing_fields:
                            fields_text = "، ".join(missing_fields)

                            answer = (
                                f"برای جستجوی پرواز، لطفاً "
                                f"{fields_text} را هم مشخص کنید."
                            )

                        else:
                            # تبدیل State کامل به ورودی LangGraph
                            graph_input = current_state.copy()  

                            graph_input["passengers_confirmed"] = (
                            current_state.get("passenger_status") == "resolved"
                            )
                            print(
                            "GRAPH INPUT:",
                            graph_input
                            )
                            # اجرای LangGraph
                            graph_result = flight_graph.invoke(graph_input)
                            print(
                                "GRAPH RESULT:",
                                graph_result
                            )
                            # ذخیره وضعیت Graph در حافظه Streamlit
                            st.session_state["flight_state"] = graph_result
                            print(
                                "FINAL SESSION FLIGHT STATE:",
                                st.session_state["flight_state"]
                            )
                            # دریافت سؤال مرحله بعد از LangGraph
                            answer = graph_result["assistant_message"]

                except Exception as error:

                    error_type = type(error).__name__
                    error_text = str(error)

                    answer = f"""
                در اتصال به Mistral خطایی رخ داد ❌

                نوع خطا: `{error_type}`

                جزئیات خطا:

                `{error_text}`
                """

                    print("Flight extraction error:", repr(error))

                st.markdown(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )
    save_message(
        session_id=st.session_state.session_id,
        role="assistant",
        content=answer
        )

    st.rerun()
