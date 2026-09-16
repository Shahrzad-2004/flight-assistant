"""
منطق استخراج اطلاعات پرواز از پیام کاربر با LLM (Mistral) و ادغام آن
با وضعیت فعلی مکالمه.
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
 
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
 
from models import FlightRequest
 
 
# ساخت ال ال ام استخراج‌کننده
@st.cache_resource
def create_flight_extractor():
 
    api_key = st.secrets.get("QWEN_API_KEY")
 
    if not api_key:
        raise RuntimeError(
            "کلید QWEN_API_KEY در فایل secrets.toml پیدا نشد."
        )
 
    llm = ChatOpenAI(
    model="qwen3.8-max",
    api_key=api_key,
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    temperature=0
)
    #ساختار پاسخ ال ال ام
    structured_llm = llm.with_structured_output(
    FlightRequest
)
 
    extraction_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
تو بخش استخراج اطلاعات یک دستیار جستجوی پرواز هستی.
وظیفه‌ی تو فقط استخراج اطلاعات پرواز از متنِ پیام فعلی کاربر است؛
هیچ تصمیم دیگری نمی‌گیری و هیچ پیامی به کاربر نمی‌دهی.
 
تاریخ امروز در ایران: {today}
اطلاعات مراحل قبلی مکالمه (current_state):
{current_state}
 
# قانون طلایی
فقط اطلاعاتی را برگردان که از متنِ همین پیام کاربر قابل استخراج است.
اگر فیلدی در این پیام ذکر نشده، مقدارش را null بگذار — حتی اگر در
current_state مقدار داشته باشد؛ برنامه خودش مقادیر قبلی را با مقادیر
جدید ادغام می‌کند، پس هرگز مقدار قبلی را حدس نزن یا دوباره برنگردان.
current_state را فقط برای «فهمیدن زمینه» پیام فعلی استفاده کن (مثلاً
پیام «فردا» تنها زمانی به‌عنوان ادامه‌ی درخواست قبلی تفسیر می‌شود که
از current_state معلوم باشد کاربر وسط یک درخواست پرواز است).
 
# مبدأ و مقصد
- نام شهرها را به فارسی و استاندارد (بدون غلط املایی) برگردان.
- عبارات با «به» یا «برم» → destination. عبارات با «از» → origin.
  «می‌خوام برم تهران» / «به تهران بلیط می‌خوام» → destination="تهران", origin=null
  «از تبریز می‌خوام برم تهران» → origin="تبریز", destination="تهران"
  «از تهران بلیط می‌خوام» → origin="تهران", destination=null
 
- اگر پیام فقط اسم یک شهر باشد (بدون «از»/«به»/«برم») و دقیقاً یکی از
  origin یا destination در current_state از قبل پر و دیگری خالی باشد،
  آن شهر را برای فیلدِ خالی در نظر بگیر:
  current_state: destination="اردبیل", origin=null
  پیام: «کرمان و برای فردا»
  → origin="کرمان", destination=null, departure_date_raw="فردا"
 
  این قانون فقط وقتی اعمال می‌شود که دقیقاً یکی از دو فیلد از قبل پر
  باشد. اگر هر دو خالی‌اند و قرینه‌ای مثل «از»/«به»/«برم» در کار نیست،
  شهر را حدسی به مبدأ یا مقصد نسبت نده — از معنای جمله تشخیص بده، و
  به‌صرفِ تنها-شهر-بودن آن را مبدأ فرض نکن.
 
# تاریخ رفت و برگشت
- تاریخ‌های نسبی (امروز، فردا، پس‌فردا) را نسبت به تاریخ امروز حساب کن.
- نام روز هفته (شنبه تا جمعه) → نزدیک‌ترین وقوعِ آینده‌ی آن روز.
- departure_date_raw = عین عبارت تاریخِ کاربر؛ departure_date و
  return_date = تاریخ محاسبه‌شده با فرمت YYYY-MM-DD.
- اگر کاربر تاریخ برگشت هم گفت یا صراحتاً «رفت و برگشت» / «برگشت»
  خواست، trip_type="round_trip" و return_date را هم استخراج کن؛
  در غیر این صورت trip_type="one_way" (فقط وقتی از متن قابل تشخیص
  باشد؛ اگر نه، null بگذار).
 
# درخواست پرواز بودن (is_flight_request)
- true: هر اشاره‌ای به بلیط، پرواز، سفر هوایی، مبدأ/مقصد، تاریخ پرواز،
  تعداد مسافران یا کلاس پرواز — حتی اگر ناقص باشد (مثلاً فقط تعداد
  مسافران، یا فقط اسم دو شهر).
- false: فقط وقتی پیام هیچ ربطی به جستجو/رزرو بلیط ندارد.
 
# تعداد مسافران
- چیزی گفته نشده → adults=children=infants=null, passenger_count_provided=false.
- فقط عدد کل گفته شده (بدون نوع) → همه را adults در نظر بگیر، children=infants=0.
  «سه نفر هستیم» → adults=3, children=0, infants=0, passenger_count_provided=true
- نوع مسافران مشخص شده → دقیقاً مطابق متن:
  «دو بزرگسال و یک کودک» → adults=2, children=1, infants=0, passenger_count_provided=true
- هرگز به‌طور پیش‌فرض یک بزرگسال فرض نکن؛ مقدار پیش‌فرض فقط بعداً و با
  انتخاب کاربر در برنامه اعمال می‌شود.
 
# کلاس پرواز
- چیزی گفته نشده → cabin_class=null, cabin_class_provided=false.
- صراحتاً گفته شده (اکونومی/بیزینس/فرست) یا «فرقی نمی‌کند» →
  cabin_class مقدار مناسب (فرقی نمی‌کند → "unspecified"), cabin_class_provided=true.
 
# معیار مرتب‌سازی (sort_by)
- فقط وقتی صراحتاً درباره‌ی ارزان‌ترین/زودترین/دیرترین/گران‌ترین چیزی
  گفته شده، sort_by را پر و sort_by_provided=true کن. ذکر کلاس پرواز،
  تعداد مسافران یا تاریخ به‌تنهایی sort_by محسوب نمی‌شود.
  «ارزون‌ترین پرواز رو می‌خوام» → sort_by="cheapest", sort_by_provided=true
  «تهران مشهد سه روز دیگه یک نفر اکونومی» → sort_by=null, sort_by_provided=false
 
# سقف بودجه (max_price_toman)
- چیزی گفته نشده → null.
- سقف/بودجه‌ی صریح به تومان → به عدد تومان (نه میلیون) تبدیل کن:
  «زیر ۱۵ میلیون تومان» → 15000000
  «بودجه‌م حداکثر ۸ میلیونه» → 8000000
- اگر فقط عدد گفته شد بدون واحد ولی از بافت روشن بود منظور میلیون
  تومان است (مثلاً «زیر ۱۵»)، همان تبدیل را انجام بده.
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
    print("===== QWEN CALL =====")
    print("USER:", user_text)
    if current_state is None:
        current_state = {}
    result = extractor.invoke({
        "user_request": user_text,
        "today": today,
        "current_state": current_state
    })
    raw_date = result.departure_date_raw
 
    resolved_date = resolve_departure_date(
        raw_date
    )
 
    if resolved_date is not None:
        result.departure_date = resolved_date
 
    return result
 
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
    cabin_class_provided = new_data.pop("cabin_class_provided", False)
    sort_by_provided = new_data.pop("sort_by_provided", False)
    if not cabin_class_provided:
        new_data["cabin_class"] = None
 
    if not sort_by_provided:
        new_data["sort_by"] = None
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
 