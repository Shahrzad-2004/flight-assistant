"""
منطق استخراج اطلاعات پرواز از پیام کاربر با LLM (Mistral) و ادغام آن
با وضعیت فعلی مکالمه.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate

from models import FlightRequest


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
