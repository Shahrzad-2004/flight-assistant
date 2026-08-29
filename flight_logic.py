"""
منطق استخراج اطلاعات پرواز از پیام کاربر با LLM (Mistral) و ادغام آن
با وضعیت فعلی مکالمه.
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import streamlit as st
from langchain_mistralai import ChatMistralAI 
from langchain_core.prompts import ChatPromptTemplate

from models import FlightRequest


# ساخت ال ال ام استخراج‌کننده
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
        max_retries=4
    )
    #ساختار پاسخ ال ال ام
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
اطلاعاتی که از مراحل قبلی مکالمه داریم:
{current_state}
ممکن است پیام فعلی کاربر ادامه‌ی درخواست قبلی باشد.
مثلاً اگر قبلاً مبدأ و مقصد مشخص شده و اکنون کاربر فقط گفته
«فردا»، این پیام را به‌عنوان تاریخ حرکت همان درخواست قبلی در نظر بگیر.

فقط اطلاعات جدیدی که از پیام فعلی کاربر قابل استخراج است برگردان.
اطلاعات قبلی را دوباره حدس نزن، چون برنامه آن‌ها را جداگانه نگه می‌دارد.
وظیفه تو فقط استخراج اطلاعات پرواز از متن کاربر است.

قوانین:
- هیچ اطلاعاتی را حدس نزن.
- اگر اطلاعاتی گفته نشده، مقدار آن را null قرار بده.
- نام شهرها را به فارسی و استاندارد برگردان.
- در تشخیص مبدأ و مقصد به ساختار جمله فارسی دقت کن.

- اگر کاربر گفت:
  «می‌خوام برم تهران»
  «می‌خوام به تهران برم»
  «برم تهران»
  «به تهران بلیط می‌خوام»
  مقصد برابر تهران است و مبدأ null است.

- عباراتی که با «به» یا «برم» مقصد سفر را بیان می‌کنند،
  باید به عنوان destination استخراج شوند.

- عباراتی که با «از» مبدأ سفر را بیان می‌کنند،
  باید به عنوان origin استخراج شوند.

- مثال:
  «از تبریز می‌خوام برم تهران»
  origin = "تبریز"
  destination = "تهران"

- مثال:
  «می‌خوام از شیراز برم مشهد»
  origin = "شیراز"
  destination = "مشهد"

- مثال:
  «می‌خوام برم تهران»
  origin = null
  destination = "تهران"

- مثال:
  «از تهران بلیط می‌خوام»
  origin = "تهران"
  destination = null
  - هنگام استخراج مبدأ و مقصد، اطلاعات مرحله‌های قبلی را که در
  current_state قرار دارند در نظر بگیر.

- اگر destination از قبل مشخص شده باشد ولی origin هنوز مشخص نشده باشد،
  و کاربر در پیام جدید فقط نام یک شهر را بدون عبارت «از» یا «به» بیان کند،
  آن شهر را به عنوان origin در نظر بگیر.

- مثال:
  current_state:
  destination = "اردبیل"
  origin = null

  پیام کاربر:
  «کرمان و برای فردا»

  خروجی:
  origin = "کرمان"
  destination = null
  departure_date_raw = "فردا"

- اگر origin از قبل مشخص شده باشد ولی destination هنوز مشخص نشده باشد،
  و کاربر در پیام جدید فقط نام یک شهر را بیان کند،
  آن شهر را به عنوان destination در نظر بگیر.

- مثال:
  current_state:
  origin = "کرمان"
  destination = null

  پیام کاربر:
  «اردبیل برای فردا»

  خروجی:
  destination = "اردبیل"
  origin = null
  departure_date_raw = "فردا"

- این قانون فقط زمانی استفاده شود که دقیقاً یکی از origin یا destination
  از قبل مشخص شده و دیگری هنوز خالی باشد.

- اگر هر دو origin و destination خالی باشند و کاربر فقط نام یک شهر را
  بدون قرینه‌ای مثل «از»، «به»، «برم» یا «حرکت از» بگوید،
  آن شهر را به صورت حدسی به مبدأ یا مقصد نسبت نده.

- اگر فقط یک شهر گفته شده است، از معنی جمله مشخص کن که
  آن شهر مبدأ است یا مقصد؛ شهر را صرفاً به دلیل اینکه تنها شهر
  موجود در جمله است به عنوان مبدأ در نظر نگیر.
- تاریخ‌های نسبی مانند فردا و پس‌فردا را نسبت به امروز محاسبه کن.
- اگر کاربر نام یکی از روزهای هفته مانند شنبه، یکشنبه، دوشنبه،
  سه‌شنبه، چهارشنبه، پنجشنبه یا جمعه را گفت، نزدیک‌ترین تاریخ
  آینده‌ی آن روز را نسبت به تاریخ امروز محاسبه کن.
- در این حالت departure_date_raw باید همان عبارت کاربر باشد
  و departure_date باید تاریخ محاسبه‌شده با فرمت YYYY-MM-DD باشد.
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
- اگر کاربر هیچ اشاره‌ای به تعداد مسافران نکرده است:
  adults = null
  children = null
  infants = null
  passenger_count_provided = false
- اگر کاربر تعداد کل مسافران را مشخص کرد ولی نوع مسافران
  (بزرگسال، کودک یا نوزاد) را مشخص نکرد، تمام تعداد را بزرگسال در نظر بگیر.
- مثال:
  «برای دو نفر بلیط می‌خواهم»
  adults = 2
  children = 0
  infants = 0
  passenger_count_provided = true
- مثال:
  «سه نفر هستیم»
  adults = 3
  children = 0
  infants = 0
  passenger_count_provided = true
- اگر کاربر نوع مسافران را مشخص کرد، دقیقاً مطابق متن استخراج کن.
- مثال:
  «دو بزرگسال و یک کودک»
  adults = 2
  children = 1
  infants = 0
  passenger_count_provided = true
- مثال:
  «یک بزرگسال و یک نوزاد»
  adults = 1
  children = 0
  infants = 1
  passenger_count_provided = true
- عباراتی مانند «یک نفر»، «دو نفر»، «سه نفر»، «۴ نفر»
  و شکل‌های مشابه همگی بیان صریح تعداد مسافران محسوب می‌شوند.
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

def resolve_departure_date(raw_date: str | None):

    if not raw_date:
        return None

    # یکسان‌سازی متن فارسی
    text = (
        raw_date
        .strip()
        .replace("\u200c", " ")
        .replace("ي", "ی")
        .replace("ك", "ک")
    )

    text = " ".join(text.split())

    today = datetime.now(
        ZoneInfo("Asia/Tehran")
    ).date()

    # پس‌فردا باید قبل از فردا بررسی شود
    if "پس فردا" in text:
        return (today + timedelta(days=2)).isoformat()

    if "فردا" in text:
        return (today + timedelta(days=1)).isoformat()

    if "امروز" in text:
        return today.isoformat()

    weekdays = {
        "دوشنبه": 0,
        "دو شنبه": 0,

        "سه شنبه": 1,
        "سه‌شنبه": 1,

        "چهارشنبه": 2,
        "چهار شنبه": 2,

        "پنجشنبه": 3,
        "پنج شنبه": 3,

        "جمعه": 4,

        "شنبه": 5,

        "یکشنبه": 6,
        "یک شنبه": 6,
    }

    for day_name, target_weekday in sorted(
        weekdays.items(),
        key=lambda item: len(item[0]),
        reverse=True
    ):

        if day_name in text:

            days_ahead = (
                target_weekday - today.weekday()
            ) % 7

            target_date = today + timedelta(
                days=days_ahead
            )

            return target_date.isoformat()

    return None
def extract_flight_request(user_text: str,current_state: dict | None = None) -> FlightRequest:

    today = datetime.now(ZoneInfo("Asia/Tehran")).date().isoformat()

    extractor = create_flight_extractor()
    if current_state is None:
        current_state = {}
    result = extractor.invoke({
        "user_request": user_text,
        "today": today,
        "current_state": current_state
    })
    raw_date = result.get("departure_date_raw")

    resolved_date = resolve_departure_date(
        raw_date
    )

    if resolved_date is not None:
        result["departure_date"] = resolved_date

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
