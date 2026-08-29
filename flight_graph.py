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

    confirmation_status: Literal[
        "pending",
        "confirmed",
        "editing"
    ]


# =========================================================
# 1) بررسی اطلاعات ضروری
# =========================================================
def check_required_fields(state: FlightState) -> dict:
    """فقط بررسی می‌کند که اطلاعات ضروری کامل هستند یا نه."""
    return {}


def route_required_fields(state: FlightState) -> str:
    if not state.get("origin"):
        return "missing"

    if not state.get("destination"):
        return "missing"

    if not state.get("departure_date"):
        return "missing"

    return "complete"


def ask_required_fields(state: FlightState) -> FlightState:
    missing_fields = []

    if not state.get("origin"):
        missing_fields.append("مبدأ")

    if not state.get("destination"):
        missing_fields.append("مقصد")

    if not state.get("departure_date"):
        missing_fields.append("تاریخ حرکت")

    fields_text = "، ".join(missing_fields)

    return {
        "current_step": "ask_required_fields",
        "assistant_message": (
            f"برای جستجوی پرواز، لطفاً {fields_text} را هم مشخص کنید."
        ),
        "ui_type": "chat_input"
    }


# =========================================================
# 2) بررسی وضعیت تعداد مسافران
# =========================================================
def check_passenger_status(state: FlightState) -> dict:
    """فقط وضعیت مرحله‌ی مسافران را بررسی می‌کند."""
    return {}


def route_passenger_status(state: FlightState) -> str:
    passenger_status = state.get("passenger_status", "unknown")

    if passenger_status == "unknown":
        return "unknown"

    if passenger_status == "entering":
        return "entering"

    return "resolved"


def ask_passenger_choice(state: FlightState) -> FlightState:
    return {
        "current_step": "ask_passenger_choice",
        "assistant_message": "آیا می‌خواهید تعداد مسافران را مشخص کنید؟",
        "ui_type": "passenger_choice"
    }


def enter_passengers(state: FlightState) -> FlightState:
    return {
        "current_step": "enter_passengers",
        "assistant_message": "تعداد بزرگسال، کودک و نوزاد را مشخص کنید.",
        "ui_type": "passenger_counter"
    }


# =========================================================
# 3) بررسی کلاس پرواز
# =========================================================
def check_cabin_class(state: FlightState) -> dict:
    """بررسی می‌کند کلاس پرواز مشخص شده یا نه."""
    return {}


def route_cabin_class(state: FlightState) -> str:
    if state.get("cabin_class") is None:
        return "missing"

    return "complete"


def ask_cabin_class(state: FlightState) -> FlightState:
    return {
        "current_step": "ask_cabin_class",
        "assistant_message": "کدام کلاس پروازی را ترجیح می‌دهید؟",
        "ui_type": "cabin_buttons"
    }


# =========================================================
# 4) بررسی تأیید نهایی
# =========================================================
def check_confirmation_status(state: FlightState) -> dict:
    """وضعیت تأیید نهایی درخواست را بررسی می‌کند."""
    return {}


def route_confirmation_status(state: FlightState) -> str:
    confirmation_status = state.get("confirmation_status", "pending")

    if confirmation_status == "confirmed":
        return "confirmed"

    if confirmation_status == "editing":
        return "editing"

    return "pending"


def show_confirmation(state: FlightState) -> FlightState:
    return {
        "current_step": "confirmation",
        "assistant_message": "اطلاعات پرواز تکمیل شد. آیا آن را تأیید می‌کنید؟",
        "ui_type": "confirmation"
    }


def edit_request(state: FlightState) -> FlightState:
    return {
        "current_step": "edit_request",
        "assistant_message": "چه اطلاعاتی را می‌خواهید تغییر دهید؟",
        "ui_type": "chat_input"
    }


def search_flights(state: FlightState) -> FlightState:
    return {
        "current_step": "search",
        "assistant_message": "اطلاعات تأیید شد. در حال جستجوی پروازها...",
        "ui_type": "search"
    }



# ساخت گراف
graph_builder = StateGraph(FlightState)

# نودهای بررسی
graph_builder.add_node("check_required_fields", check_required_fields)
graph_builder.add_node("check_passenger_status", check_passenger_status)
graph_builder.add_node("check_cabin_class", check_cabin_class)
graph_builder.add_node("check_confirmation_status", check_confirmation_status)

# نودهای رابط کاربری / عملیات
graph_builder.add_node("ask_required_fields", ask_required_fields)
graph_builder.add_node("ask_passenger_choice", ask_passenger_choice)
graph_builder.add_node("enter_passengers", enter_passengers)
graph_builder.add_node("ask_cabin_class", ask_cabin_class)
graph_builder.add_node("show_confirmation", show_confirmation)
graph_builder.add_node("edit_request", edit_request)
graph_builder.add_node("search_flights", search_flights)


# شروع گراف
graph_builder.add_edge(START, "check_required_fields")


# اگر اطلاعات ضروری ناقص بود → سؤال بپرس
# اگر کامل بود → برو سراغ مسافران
graph_builder.add_conditional_edges(
    "check_required_fields",
    route_required_fields,
    {
        "missing": "ask_required_fields",
        "complete": "check_passenger_status"
    }
)


# وضعیت مسافران
graph_builder.add_conditional_edges(
    "check_passenger_status",
    route_passenger_status,
    {
        "unknown": "ask_passenger_choice",
        "entering": "enter_passengers",
        "resolved": "check_cabin_class"
    }
)


# کلاس پرواز
graph_builder.add_conditional_edges(
    "check_cabin_class",
    route_cabin_class,
    {
        "missing": "ask_cabin_class",
        "complete": "check_confirmation_status"
    }
)


# وضعیت تأیید
graph_builder.add_conditional_edges(
    "check_confirmation_status",
    route_confirmation_status,
    {
        "confirmed": "search_flights",
        "editing": "edit_request",
        "pending": "show_confirmation"
    }
)


# نودهایی که باید نتیجه را به UI برگردانند، فعلاً پایان اجرای این دور هستند
graph_builder.add_edge("ask_required_fields", END)
graph_builder.add_edge("ask_passenger_choice", END)
graph_builder.add_edge("enter_passengers", END)
graph_builder.add_edge("ask_cabin_class", END)
graph_builder.add_edge("show_confirmation", END)
graph_builder.add_edge("edit_request", END)
graph_builder.add_edge("search_flights", END)


# آماده‌سازی گراف برای اجرا
flight_graph = graph_builder.compile()
