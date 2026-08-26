import time
import streamlit as st # type: ignore
from flight_graph import flight_graph
from chat_database import save_message
from flight_logic import extract_flight_request, merge_flight_state


def handle_user_prompt(prompt: str) -> None:
    """پردازش پیام کاربر و افزودن پاسخ دستیار به تاریخچه‌ی چت."""
    # نمایش حالت تایپ کردن
    with st.chat_message("assistant"):

            with st.spinner("✈️ در حال بررسی درخواست شما..."):
                time.sleep(1.5)
                try:
                    #ببینیم چه اطلاعاتی از این کاربر داریم یعنی اگر در همین مکالمه مبدا و مقصد مشخص شده و در پرامپتی دیگر تاریخ حرکت را گفته متوجه شویم راجب یک پرواز صحبت می شود
                    previous_state = st.session_state.get(
                        "flight_state",
                        {}
                    )

                    flight_request = extract_flight_request(
                        prompt,
                        previous_state
                    )
                    print(
                    "Passengers:",
                    flight_request.adults,
                    flight_request.children,
                    flight_request.infants,
                    "Provided:",
                    flight_request.passenger_count_provided

                    )
                    #مرج کردن اطلاعات 
                    current_state = merge_flight_state(
                        flight_request
                    )
                    print(
                        "MERGED FLIGHT STATE:",
                        current_state
                    )

                    if previous_state.get("confirmation_status") == "editing":
                        current_state["confirmation_status"] = "pending"
                        
                    graph_result = flight_graph.invoke(current_state)

                    st.session_state["flight_state"] = graph_result

                    answer = graph_result["assistant_message"]

                    print(
                        "GRAPH RESULT:",
                        graph_result
                    )

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
