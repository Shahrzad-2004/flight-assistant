import streamlit as st
import streamlit.components.v1 as components
import base64
from pathlib import Path

from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional, Literal

from pydantic import BaseModel, Field
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from flight_graph import flight_graph
import uuid

from chat_database import (
    create_tables,
    save_message,
    load_messages
)

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


# استایل

st.markdown(
    f"""
<style>

@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800&display=swap');

#MainMenu{{visibility:hidden;}}

footer{{visibility:hidden;}}

header{{visibility:hidden;}}

html,
body,
[data-testid="stAppViewContainer"]{{
    background-image:url("data:image/jpeg;base64,{background}");
    background-size:cover;
    background-position:center;
    background-repeat:no-repeat;
    background-attachment:fixed;
}}

/* اجازه بده بکگراند از زیر نوار پایین هم دیده بشه */
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottomBlockContainer"],
[data-testid="stChatInputContainer"],
.stBottom,
.stBottomBlockContainer{{
    background:transparent !important;
    background-color:transparent !important;
}}

.block-container{{
    padding-top:25px;
    max-width:1050px;
}}
html,
body,
[data-testid="stAppViewContainer"],
[data-testid="stMarkdownContainer"],
textarea,
button{{
font-family:'Vazirmatn',sans-serif !important;
}}

</style>
""",
    unsafe_allow_html=True,
)

st.markdown("""
<style>

/* کارت اصلی */
/* جلوگیری از کم‌رنگ شدن پیام‌ها هنگام اجرای مجدد Streamlit */

[data-testid="stChatMessage"] {
    opacity: 1 !important;
}

[data-testid="stChatMessage"] * {
    opacity: 1 !important;
    color: #111827 !important;
}
.main-card{

    background:rgba(255,255,255,.90);

    backdrop-filter:blur(18px);

    border-radius:28px;

    width:700px;
    max-width:calc(100vw - 40px);
    box-sizing:border-box;

    margin: 0 auto;

    padding:35px;

    box-shadow:0 20px 60px rgba(0,0,0,.18);

    border:1px solid rgba(255,255,255,.75);

}

/* لوگو */

.logo{

    font-size:60px;

    text-align:center;

    margin-bottom:8px;

}

/* عنوان */

.title{
    text-align:center;

    font-size:40px;

    font-weight:800;

    color:#111827;

    letter-spacing:-1px;

}

/* زیرعنوان */

.subtitle{

    text-align:center;

    font-size:15px;

    font-weight:500;

    color:#4B5563;
}

/* پیام‌های چت */

[data-testid="stChatMessage"]{

    background:white;

    border-radius:18px;

    direction: rtl;
    text-align: right;

    padding:12px;

    margin-top:22px;

    margin-bottom:12px;

    box-shadow:0 4px 15px rgba(0,0,0,.06);

}
/* راست‌چین کردن متن داخل پیام */
[data-testid="stChatMessage"]
[data-testid="stMarkdownContainer"] {
    direction: rtl !important;
    text-align: right !important;
    width: 100%;
}

[data-testid="stChatMessage"] p {
    direction: rtl !important;
    text-align: right !important;
}

/* کادر تایپ */

[data-testid="stChatInput"],
[data-testid="stChatInput"] > div{

    background:white !important;
    background-color:white !important;

    border-radius:20px;
    
    direction: rtl;
    text-align: right;

    border:1px solid #d1d5db;

    box-shadow:0 5px 20px rgba(0,0,0,.08);

}

[data-testid="stChatInput"] textarea{

    color:#111827 !important;
    background-color:white !important;

}

[data-testid="stChatInput"] textarea::placeholder{

    color:#6b7280 !important;

}
/* متن حالت جستجو و لودینگ */

[data-testid="stSpinner"] {
    direction: rtl !important;
    text-align: right !important;
}

[data-testid="stSpinner"] p,
[data-testid="stSpinner"] span {
    color: #111827 !important;
    font-family: 'Vazirmatn', sans-serif !important;
    font-size: 16px !important;
    font-weight: 600 !important;
}
/* دکمه */

button{

    background:#2563eb !important;

    color:white !important;

    border-radius:14px !important;

    border:none !important;

    transition:.3s;

}

button:hover{

    background:#1d4ed8 !important;

    transform:translateY(-2px);

}

</style>
""", unsafe_allow_html=True)

#استایل باتن های نوع پرواز
st.markdown(
    """
<style>

/* عنوان انتخاب کلاس پرواز */

.cabin-title {
    direction: rtl;
    text-align: right;

    font-family: 'Vazirmatn', sans-serif !important;
    font-size: 17px;
    font-weight: 700;

    color: #1f2937;

    margin-top: 20px;
    margin-bottom: 12px;
}


/* راست‌چین شدن ترتیب دکمه‌های کلاس پرواز */

[data-testid="stHorizontalBlock"]:has(.st-key-economy_button) {
    direction: rtl !important;
    flex-direction: row-reverse !important;
    gap: 10px !important;
}


/* استایل شیشه‌ای مخصوص چهار دکمه کلاس پرواز */

.st-key-economy_button button,
.st-key-business_button button,
.st-key-first_button button,
.st-key-unspecified_button button,
.st-key-passenger_enter_button button,
.st-key-passenger_default_button button {

    width: 100% !important;
    min-height: 48px !important;

    background: rgba(255, 255, 255, 0.45) !important;

    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;

    border: 1px solid rgba(255, 255, 255, 0.75) !important;
    border-radius: 15px !important;

    box-shadow:
        0 5px 18px rgba(31, 41, 55, 0.10),
        inset 0 1px 0 rgba(255, 255, 255, 0.75) !important;

    color: #1f2937 !important;

    font-family: 'Vazirmatn', sans-serif !important;
    font-size: 14px !important;
    font-weight: 600 !important;

    direction: rtl !important;
    text-align: center !important;

    transition: all 0.25s ease !important;
}


/* فونت متن داخل دکمه‌ها */

.st-key-economy_button button p,
.st-key-business_button button p,
.st-key-first_button button p,
.st-key-unspecified_button button p,
.st-key-passenger_enter_button button p,
.st-key-passenger_default_button button p {

    font-family: 'Vazirmatn', sans-serif !important;
    color: #1f2937 !important;

    direction: rtl !important;
    text-align: center !important;
}


/* حالت قرار گرفتن موس روی دکمه */

.st-key-economy_button button:hover,
.st-key-business_button button:hover,
.st-key-first_button button:hover,
.st-key-unspecified_button button:hover,
.st-key-passenger_enter_button button:hover,
.st-key-passenger_default_button button:hover {

    background: rgba(37, 99, 235, 0.16) !important;

    border-color: rgba(37, 99, 235, 0.45) !important;

    box-shadow:
        0 8px 22px rgba(37, 99, 235, 0.16),
        inset 0 1px 0 rgba(255, 255, 255, 0.85) !important;

    transform: translateY(-2px) !important;
}


/* حالت کلیک */

.st-key-economy_button button:active,
.st-key-business_button button:active,
.st-key-first_button button:active,
.st-key-unspecified_button button:active,
.st-key-passenger_enter_button button:active,
.st-key-passenger_default_button button:active {

    transform: translateY(0) scale(0.98) !important;
}

</style>
""",
    unsafe_allow_html=True
)

# هدر
st.markdown("""

<div class="main-card">

<div class="logo">✈️</div>

<div class="title">

دستیار هوشمند بلیط

</div>

<div class="subtitle">

✨✈️ هوشمندانه انتخاب کن، آسوده پرواز کن 

</div>

""", unsafe_allow_html=True)


# ساختار اطلاعات پرواز

class FlightRequest(BaseModel):
    is_flight_request: bool = Field(
        description="آیا درخواست کاربر مربوط به جستجوی پرواز است؟"
    )

    origin: Optional[str] = Field(
        default=None,
        description="شهر یا فرودگاه مبدأ"
    )

    destination: Optional[str] = Field(
        default=None,
        description="شهر یا فرودگاه مقصد"
    )

    departure_date_raw: Optional[str] = Field(
        default=None,
        description="تاریخ رفت دقیقاً همان‌ طور که کاربر بیان کرده است"
    )

    departure_date: Optional[str] = Field(
        default=None,
        description="تاریخ رفت به فرمت YYYY-MM-DD"
    )

    return_date: Optional[str] = Field(
        default=None,
        description="تاریخ برگشت به فرمت YYYY-MM-DD"
    )

    trip_type: Optional[Literal["one_way", "round_trip"]] = Field(
        default=None,
        description="نوع سفر: یک‌ طرفه یا رفت‌ و برگشت"
    )

    adults: Optional[int] = Field(
        default=None,
        ge=1,
        description="تعداد مسافران بزرگسال"
    )

    children: Optional[int] = Field(
        default=None,
        ge=0,
        description="تعداد کودکان"
    )

    infants: Optional[int] = Field(
        default=None,
        ge=0,
        description="تعداد نوزادان"
    )
    passenger_count_provided: bool = Field(
        default=False,
        description=(
            "آیا کاربر تعداد مسافران را در درخواست خود "
            "به‌صورت واضح مشخص کرده است؟"
        )
    )
    cabin_class: Optional[
        Literal[
            "economy",
            "business",
            "first",
            "unspecified"
        ]
    ] = Field(
        default=None,
        description=(
            "کلاس پروازی کاربر؛ اگر کاربر کلاس را مشخص نکرده "
            "مقدار null و اگر گفت اهمیت ندارد unspecified باشد"
        )
    )

    max_price_toman: Optional[int] = Field(
        default=None,
        description="حداکثر بودجه کاربر به تومان"
    )

    preferred_airline: Optional[str] = Field(
        default=None,
        description="شرکت هواپیمایی موردنظر کاربر"
    )

    preferred_departure_time: Optional[
        Literal["morning", "afternoon", "evening", "night"]
    ] = Field(
        default=None,
        description="زمان ترجیحی حرکت"
    )

    direct_only: Optional[bool] = Field(
        default=None,
        description="آیا کاربر فقط پرواز مستقیم می‌خواهد؟"
    )

    sort_by: Optional[
        Literal["cheapest", "earliest", "shortest", "best"]
    ] = Field(
        default=None,
        description="معیار اصلی انتخاب پرواز"
    )


# -----------------------------
# ساخت LLM استخراج‌کننده
# -----------------------------

@st.cache_resource
def create_flight_extractor():

    api_key = st.secrets.get("MISTRAL_API_KEY")

    if not api_key:
        raise RuntimeError(
            "کلید MISTRAL_API_KEY در فایل secrets.toml پیدا نشد."
        )

    llm = ChatMistralAI(
        model="mistral-small-latest",
        temperature=0,
        api_key=api_key,
        max_retries=2
    )
    # روش سازگار با نسخه جدید LangChain
    structured_llm = llm.with_structured_output(
        schema=FlightRequest.model_json_schema(),
        method="json_schema"
    )

    extraction_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
تو بخش استخراج اطلاعات یک دستیار جستجوی پرواز هستی.

تاریخ امروز در ایران: {today}

وظیفه تو فقط استخراج اطلاعات پرواز از متن کاربر است.

قوانین:
- هیچ اطلاعاتی را حدس نزن.
- اگر اطلاعاتی گفته نشده، مقدار آن را null قرار بده.

- نام شهرها را به فارسی و استاندارد برگردان.
- تاریخ‌های نسبی مانند فردا و پس‌فردا را نسبت به امروز محاسبه کن.
- departure_date_raw باید عبارت تاریخ داخل پیام کاربر باشد.
- departure_date و return_date باید به فرمت YYYY-MM-DD باشند.
- اگر سفر رفت‌وبرگشت بود trip_type برابر round_trip باشد.
- اگر کاربر درباره بلیط هواپیما، پرواز، سفر هوایی، مبدأ، مقصد،
  تاریخ پرواز، تعداد مسافران یا کلاس پرواز صحبت می‌کند،
  is_flight_request را true قرار بده.
- حتی اگر اطلاعات درخواست ناقص باشد، مثلاً فقط تعداد مسافران
  یا فقط مبدأ و مقصد را گفته باشد، باز هم is_flight_request باید true باشد.
- فقط زمانی is_flight_request را false قرار بده که پیام کاربر
  هیچ ارتباطی با جستجو یا رزرو بلیط هواپیما نداشته باشد.
- اگر کاربر تعداد بزرگسال، کودک، نوزاد یا تعداد کل مسافران را مشخص کرده بود،
  passenger_count_provided را true قرار بده.
- اگر کاربر تعداد مسافران را مشخص نکرده است،
  adults و children و infants را null قرار بده
  و passenger_count_provided را false قرار بده.

- اگر کاربر تعداد مسافران را مشخص کرده است،
  تعداد بزرگسال، کودک و نوزاد را مطابق متن استخراج کن
  و passenger_count_provided را true قرار بده.

- اگر کاربر مثلاً گفت «۲ بزرگسال و یک کودک»،
  adults برابر 2، children برابر 1 و infants برابر 0 باشد.

- هیچ‌وقت به صورت خودکار یک بزرگسال در نظر نگیر.
  مقدار پیش‌فرض یک بزرگسال فقط بعداً و در صورت انتخاب کاربر
  توسط برنامه اعمال می‌شود.
"""
        ),
        (
            "human",
            "{user_request}"
        )
    ])

    return extraction_prompt | structured_llm


def extract_flight_request(user_text: str) -> FlightRequest:

    today = datetime.now(
        ZoneInfo("Asia/Tehran")
    ).date().isoformat()

    extractor = create_flight_extractor()

    result = extractor.invoke({
        "user_request": user_text,
        "today": today
    })

    # خروجی json_schema از نوع dict است
    return FlightRequest.model_validate(result)
def merge_flight_state(new_request: FlightRequest):

    # اطلاعات قبلی را می‌گیریم
    current_state = st.session_state.get(
        "flight_state",
        {}
    ).copy()

    new_data = new_request.model_dump()

    # این دو فیلد را جدا مدیریت می‌کنیم
    new_data.pop("is_flight_request", None)
    new_data.pop("passenger_count_provided", None)

    # فقط اطلاعاتی که در پیام جدید وجود دارند
    # روی اطلاعات قبلی نوشته می‌شوند
    for key, value in new_data.items():

        if value is not None:
            current_state[key] = value

    # اگر کاربر خودش تعداد مسافران را گفته باشد
    if new_request.passenger_count_provided:

        # اگر کودک یا نوزاد ذکر نشده، صفر در نظر گرفته شود
        if current_state.get("children") is None:
            current_state["children"] = 0

        if current_state.get("infants") is None:
            current_state["infants"] = 0

        current_state["passenger_status"] = "resolved"

    else:

        # فقط بار اول ساخته شود
        current_state.setdefault(
            "passenger_status",
            "unknown"
        )

    return current_state
# -----------------------------
# حافظه چت
# -----------------------------

if "messages" not in st.session_state:

    st.session_state.messages = [

        {
            "role": "assistant",
            "content": "سلام من دستیارهوشمند رزرو بلیط هستم. چطور می توانم در رزرو بلیط کمکتان کنم ؟ "
        }

    ]
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
# -----------------------------
# نمایش پیام‌ها
# -----------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


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

    # نمایش حالت تایپ کردن
    with st.chat_message("assistant"):

      with st.spinner("✈️ در حال جستجوی بهترین پرواز..."):

            import time

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
    st.markdown("""
<style>

/* ---------- فونت ---------- */

html, body, [class*="css"]{
    font-family:'Segoe UI',sans-serif;
}

/* ---------- کارت اصلی ---------- */

.main-card{

    background:rgba(255,255,255,.82);

    backdrop-filter:blur(30px);

    border-radius:30px;

    padding:35px;

    border:1px solid rgba(255,255,255,.7);

    box-shadow:
        0 30px 80px rgba(0,0,0,.18);

}

/* ---------- لوگو ---------- */

.logo{

    font-size:75px;

    text-align:center;

    animation:float 3s ease-in-out infinite;

}

/* ---------- عنوان ---------- */

.title{

    text-align:center;

    font-size:46px;

    font-weight:700;

    color:#111827;

}

/* ---------- زیرعنوان ---------- */

.subtitle{

    text-align:center;

    font-size:18px;

    color:#6b7280;

    margin-bottom:25px;

}

/* ---------- پیام ها ---------- */

[data-testid="stChatMessage"]{

    background:white;

    border-radius:20px;


    padding:15px;

    margin-bottom:14px;

    box-shadow:0 5px 18px rgba(0,0,0,.08);

    transition:.3s;

}

[data-testid="stChatMessage"]:hover{

    transform:translateY(-2px);

    box-shadow:0 12px 25px rgba(0,0,0,.12);

}

/* ---------- کادر تایپ ---------- */

[data-testid="stChatInput"]{

    background:white;

    border-radius:22px;

    border:1px solid #d1d5db;

    box-shadow:0 10px 25px rgba(0,0,0,.10);

}

/* ---------- دکمه ---------- */

button{

    background:#2563eb !important;

    color:white !important;

    border-radius:15px !important;

    border:none !important;

    font-weight:bold !important;

    transition:.25s;

}


button:hover{

    background:#1d4ed8 !important;

    transform:scale(1.05);

}

/* ---------- اسکرول ---------- */

::-webkit-scrollbar{

    width:8px;

}

::-webkit-scrollbar-thumb{

    background:#9ca3af;

    border-radius:20px;

}

/* ---------- انیمیشن ---------- */

@keyframes float{

0%{

transform:translateY(0px);

}

50%{

transform:translateY(-8px);

}

100%{

transform:translateY(0px);

}

}

</style>
""",unsafe_allow_html=True)
# ===========================
# تم روشن حرفه‌ای
# ===========================

st.markdown("""
<style>

/* حذف منوها */
#MainMenu{
visibility:hidden;
}

footer{
visibility:hidden;
}

header{
visibility:hidden;
}

/* انیمیشن */
@keyframes fadeIn{

from{
opacity:0;
transform:translateY(20px);
}

to{
opacity:1;
transform:translateY(0px);
}

}

/* کارت اصلی */

.main-card{

animation:fadeIn .8s ease;

}

/* پیام کاربر */

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]){

background:#2563EB10;

border-left:5px solid #2563EB;

}

/* پیام ربات */

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]){

background:white;

border-left:5px solid #10B981;

}

/* متن */

[data-testid="stMarkdownContainer"]{

  font-family:'Vazirmatn',sans-serif !important;

    font-size:17px;

    line-height:2;

    color:#111827;

}

/* ورودی */

textarea{

font-size:16px !important;

}

/* دکمه */

button{

height:48px !important;

font-size:16px !important;

}

/* لوگو */

.logo{

filter:drop-shadow(0 8px 20px rgba(0,0,0,.15));

}

/* عنوان */

.title{

letter-spacing:-1px;

}

/* زیرعنوان */

.subtitle{

font-weight:500;

}

</style>
""",unsafe_allow_html=True)