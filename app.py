import streamlit as st
import base64
from pathlib import Path


from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional, Literal

from pydantic import BaseModel, Field
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
import uuid

from chat_database import (
    create_tables,
    save_message,
    load_messages
)
create_tables()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
# -----------------------------
# تنظیمات صفحه


st.set_page_config(
    page_title="دستیار هوشمند بلیط",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# خواندن عکس
# -----------------------------

BASE_DIR = Path(__file__).parent


def get_base64(file_name):

    path = BASE_DIR / file_name

    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


background = get_base64("ee.jpg")

# -----------------------------
# استایل
# -----------------------------

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

# -----------------------------
# هدر
# -----------------------------

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

# -----------------------------
# ساختار اطلاعات پرواز
# -----------------------------

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
        description="تاریخ رفت دقیقاً همان‌طور که کاربر بیان کرده است"
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
        description="نوع سفر: یک‌طرفه یا رفت‌وبرگشت"
    )

    adults: int = Field(
        default=1,
        ge=1,
        description="تعداد مسافران بزرگسال"
    )

    children: int = Field(
        default=0,
        ge=0,
        description="تعداد کودکان"
    )

    infants: int = Field(
        default=0,
        ge=0,
        description="تعداد نوزادان"
    )

    cabin_class: Literal[
        "economy",
        "business",
        "first",
        "unspecified"
    ] = Field(
        default="unspecified",
        description="کلاس پروازی"
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
            "کلید GOOGLE_API_KEY در فایل secrets.toml پیدا نشد."
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
- اگر تعداد مسافر گفته نشده، یک بزرگسال در نظر بگیر.
- نام شهرها را به فارسی و استاندارد برگردان.
- تاریخ‌های نسبی مانند فردا و پس‌فردا را نسبت به امروز محاسبه کن.
- departure_date_raw باید عبارت تاریخ داخل پیام کاربر باشد.
- departure_date و return_date باید به فرمت YYYY-MM-DD باشند.
- اگر سفر رفت‌وبرگشت بود trip_type برابر round_trip باشد.
- اگر پیام مربوط به پرواز نبود is_flight_request را false قرار بده.
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

# -----------------------------
# نمایش پیام‌ها
# -----------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# -----------------------------
# ورودی کاربر
# -----------------------------
messages = load_messages(
    st.session_state.session_id
)

for message in messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
prompt = st.chat_input(
  'درخواست خود را بنویسید'
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

                    # ذخیره اطلاعات برای مرحله Playwright
                    st.session_state["flight_request"] = (
                        flight_request.model_dump()
                    )

                    if not flight_request.is_flight_request:

                        answer = (
                            "لطفاً درخواست خود را درباره جستجوی "
                            "بلیط هواپیما بنویسید."
                        )

                    else:
                        missing_fields = []

                        if not flight_request.origin:
                            missing_fields.append("مبدأ")

                        if not flight_request.destination:
                            missing_fields.append("مقصد")

                        if not flight_request.departure_date:
                            missing_fields.append("تاریخ حرکت")

                        if missing_fields:
                            fields_text = "، ".join(missing_fields)

                            answer = (
                                f"برای جستجوی پرواز، لطفاً "
                                f"{fields_text} را هم مشخص کنید."
                            )

                        else:
                            trip_label = (
                                "رفت‌وبرگشت"
                                if flight_request.trip_type == "round_trip"
                                else "یک‌طرفه"
                            )

                            answer = f"""
            اطلاعات درخواست شما استخراج شد ✅

            - مبدأ: {flight_request.origin}
            - مقصد: {flight_request.destination}
            - تاریخ رفت: {flight_request.departure_date}
            - تاریخ برگشت: {flight_request.return_date or "ندارد"}
            - نوع سفر: {trip_label}
            - تعداد بزرگسال: {flight_request.adults}
            - تعداد کودک: {flight_request.children}
            - کلاس پرواز: {flight_request.cabin_class}
            - حداکثر قیمت: {flight_request.max_price_toman or "مشخص نشده"}

            در مرحله بعد با این اطلاعات پروازها جستجو می‌شوند.
            """

                except Exception as error:

                    error_type = type(error).__name__
                    error_text = str(error)

                    answer = f"""
                در اتصال به Gemini خطایی رخ داد ❌

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