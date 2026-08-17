from typing import TypedDict, Optional, Literal
from langgraph.graph import StateGraph, START, END

class FlightState(TypedDict, total=False):

    # متن فعلی کاربر
    user_text: str

    # اطلاعات اصلی پرواز
    origin: Optional[str]
    destination: Optional[str]
    departure_date: Optional[str]
    return_date: Optional[str]

    trip_type: Optional[
        Literal["one_way", "round_trip"]
    ]

    # کلاس پرواز
    cabin_class: Optional[
        Literal[
            "economy",
            "business",
            "first",
            "unspecified"
        ]
    ]

    # تعداد مسافران
    # تعداد مسافران
    adults: Optional[int]
    children: Optional[int]
    infants: Optional[int]

    passengers_confirmed: bool

    passenger_status: Literal[
        "unknown",
        "entering",
        "resolved"
    ]
        # اطلاعات مربوط به رابط کاربری
    current_step: str
    assistant_message: str

    ui_type: Literal[
        "chat_input",
        "cabin_buttons",
        "passenger_choice",
        "passenger_counter",
        "confirmation",
        "search"
    ]
def decide_next_step(state: FlightState) -> FlightState:
    # بررسی وضعیت تعداد مسافران
    passenger_status = state.get(
        "passenger_status",
        "unknown"
    )

    if passenger_status == "unknown":

        return {
            "current_step": "ask_passenger_choice",
            "assistant_message": (
                "آیا می‌خواهید تعداد مسافران را مشخص کنید؟"
            ),
            "ui_type": "passenger_choice"
        }
    if passenger_status == "entering":

        return {
            "current_step": "enter_passengers",
            "assistant_message": (
                "تعداد بزرگسال، کودک و نوزاد را مشخص کنید."
            ),
            "ui_type": "passenger_counter"
        }
    missing_fields = []

    if not state.get("origin"):
        missing_fields.append("مبدأ")

    if not state.get("destination"):
        missing_fields.append("مقصد")

    if not state.get("departure_date"):
        missing_fields.append("تاریخ حرکت")

    # ابتدا اطلاعات ضروری را می‌پرسیم
    if missing_fields:

        fields_text = "، ".join(missing_fields)

        return {
            "current_step": "ask_required_fields",
            "assistant_message": (
                f"لطفاً {fields_text} را هم مشخص کنید."
            ),
            "ui_type": "chat_input"
        }

    # سپس کلاس پرواز را می‌پرسیم
    if state.get("cabin_class") is None:

        return {
            "current_step": "ask_cabin_class",
            "assistant_message": (
                "کدام کلاس پروازی را ترجیح می‌دهید؟"
            ),
            "ui_type": "cabin_buttons"
        }

    # تمام اطلاعات تکمیل شده‌اند
    return {
        "current_step": "confirmation",
        "assistant_message": (
            "اطلاعات پرواز تکمیل شد. آیا آن را تأیید می‌کنید؟"
        ),
        "ui_type": "confirmation"
    }
# ساخت گراف
graph_builder = StateGraph(FlightState)

# افزودن نود تشخیص مرحله بعد
graph_builder.add_node(
    "decide_next_step",
    decide_next_step
)

# مسیر شروع و پایان
graph_builder.add_edge(
    START,
    "decide_next_step"
)

graph_builder.add_edge(
    "decide_next_step",
    END
)

# آماده‌سازی گراف برای اجرا
flight_graph = graph_builder.compile()