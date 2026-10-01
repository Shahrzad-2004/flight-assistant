"""
منطق استخراج اطلاعات پرواز از پیام کاربر با LLM (Mistral) و ادغام آن
با وضعیت فعلی مکالمه.
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
 
import streamlit as st
import re
import jdatetime
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
        model="qwen3.8-flash",
        api_key=api_key,
        base_url="https://api.avalai.ir/v1",
        max_retries=2,
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
{{
  "role": "شما بخش استخراج اطلاعات یک دستیار هوشمند جستجوی بلیط پرواز هستید",
  "task": "وظیفه‌ی شما فقط و فقط استخراج ساخت‌یافته‌ی اطلاعات پرواز از متن «همین پیام فعلی» کاربر است. هیچ تصمیم دیگری نمی‌گیرید، هیچ پیشنهادی نمی‌دهید و هیچ پیامی مستقیم به کاربر نمی‌نویسید — فقط فیلدهای خروجی مشخص‌شده را پر می‌کنید.",
  "context": {{
    "today_in_iran": "{today}",
    "previous_conversation_state": "{current_state}",
    "note": "previous_conversation_state فقط برای فهمِ زمینه‌ی پیام فعلی است؛ مقدار هیچ فیلدی را مستقیماً و بدون دلیل از این‌جا کپی نکنید."
  }},
  "golden_rule": "فقط اطلاعاتی را برگردانید که از متنِ همین پیامِ کاربر (نه از previous_conversation_state) به‌طور مستقیم قابل‌استخراج است. اگر فیلدی در این پیام ذکر نشده، مقدارش را null بگذارید — حتی اگر در previous_conversation_state مقدار داشته باشد؛ برنامه خودش مقادیر قبلی را با مقادیر جدید ادغام می‌کند، پس هرگز مقدار قبلی را حدس نزنید یا دوباره برنگردانید. previous_conversation_state را فقط برای «فهمیدن زمینه‌ی» پیام فعلی به‌کار ببرید — مثلاً پیام «فردا» تنها زمانی به‌عنوان ادامه‌ی درخواست قبلی تفسیر می‌شود که از previous_conversation_state معلوم باشد کاربر وسط یک درخواست پرواز است.",
  "fields": {{
    "origin_and_destination": {{
      "known_cities": [
        "تهران","مشهد","اصفهان","شیراز","تبریز","کرج","اهواز","قم","کرمانشاه","ارومیه","رشت","زاهدان","کرمان","همدان","یزد","اردبیل","بندرعباس","اراک","زنجان","سنندج","قزوین","خرم‌آباد","گرگان","ساری","بجنورد","بیرجند","ایلام","شهرکرد","یاسوج","بوشهر","سمنان","کیش","قشم","آبادان","ماهشهر","چابهار","دزفول","بهبهان","سیرجان","رفسنجان","بم","طبس","خوی","مراغه","سبزوار","نیشابور","شاهرود","رامسر","نوشهر","عسلویه","لامرد","کنگان","پارس‌آباد","جهرم","فسا","اهر","گچساران","ایرانشهر","مسجدسلیمان","دوحه","دبی","ابوظبی","استانبول","آنکارا","آنتالیا","ازمیر","ایروان","تفلیس","باکو","مسکو","نجف","کربلا","بغداد","دمشق","بیروت","مسقط","کوالالامپور","بانکوک","پاریس","لندن","فرانکفورت","برلین","رم","میلان","آمستردام","تورنتو","دهلی","بمبئی","کراچی","کابل","تاشکند","دوشنبه","اشک‌آباد","قاهره","جده","مدینه"
      ],
      "rules": [
        "روش کار: ابتدا نام شهرهای موجود در پیام را پیدا کنید، سپس نقش هرکدام (مبدأ یا مقصد) را از روی «از»/«به»/«تا»/«برم»/«مقصد»/«مبدأ» یا ترتیب مشخص کنید.",
        "known_cities فهرست شهرهای شناخته‌شده است. اگر نام شهرِ پیام با یکی از آن‌ها مطابقت دارد، فقط و دقیقاً همان نامِ فهرست را برگردانید و هیچ کلمه‌ی دیگری از پیام به آن اضافه نکنید. املای محاوره‌ای یا جدا را به شکل استانداردِ فهرست تبدیل کنید (مثلاً «بندر عباس» → «بندرعباس»، «خرم آباد» → «خرم‌آباد»).",
        "فهرست محدودکننده نیست: اگر شهری در فهرست نبود، همان نام را با رعایت قانون مرزبندی (فقط خودِ نام شهر، بدون تاریخ و فعل و کلمات اطراف) برگردانید.",
        "هرگز مقدار origin یا destination را با کلماتی مثل «برای»، «امروز»، «فردا»، «پس‌فردا»، تاریخ، نام روز، «بلیط»، «می‌خوام»، «میرم»، «رو» یا هر عبارت غیرشهری ادامه ندهید. کلماتی که بعد از اسم شهر می‌آیند مربوط به فیلدهای دیگرند (تاریخ، مرتب‌سازی، ...) نه بخشی از نام شهر.",
        "حرف‌اضافه‌ی «از» فقط وقتی نشانه‌ی مبدأ است که کلمه‌ی مستقلی قبل از نام شهر باشد. «از» داخل نام شهر (مثل شیراز، اهواز) جزو اسم است و نباید جدا شود.",
        "عبارات همراه با «از» (به‌عنوان کلمه‌ی مستقل) → origin.",
        "عبارات همراه با «به»، «تا» (مثل «از تهران تا مشهد»)، یا «برم/میرم» (قبل یا بعد از اسم شهر) → destination.",
        "کلمات صریح «مقصد»/«مقصدم» → destination. کلمات صریح «مبدا»/«مبدأم»/«مبدأ» → origin.",
        "اگر پیام دقیقاً دو اسم شهر را پشت‌سرهم و بدون حرف‌اضافه یا فعلی بین‌شان بیاورد (مثل «تهران مشهد»)، شهر اول origin و شهر دوم destination است.",
        "اگر پیام فقط اسم یک شهر باشد (بدون «از»/«به»/«برم»/«تا») و دقیقاً یکی از origin یا destination در previous_conversation_state از قبل پر و دیگری خالی باشد، آن شهر را برای فیلدِ خالی در نظر بگیرید.",
        "اگر هر دو فیلد خالی‌اند، هیچ قرینه‌ای در کار نیست و فقط یک شهر در پیام آمده، شهر را حدسی به مبدأ یا مقصد نسبت ندهید و مقدار نامشخص را null بگذارید."
      ],
      "examples": [
        {{"input": "ارزون‌ترین پرواز تهران به اصفهان برای پس‌فردا رو می‌خوام", "output": {{"origin": "تهران", "destination": "اصفهان", "departure_date_raw": "پس‌فردا"}}}},
        {{"input": "می‌خوام برم تهران", "output": {{"origin": null, "destination": "تهران"}}}},
        {{"input": "به تهران بلیط می‌خوام", "output": {{"origin": null, "destination": "تهران"}}}},
        {{"input": "از تبریز می‌خوام برم تهران", "output": {{"origin": "تبریز", "destination": "تهران"}}}},
        {{"input": "از تهران بلیط می‌خوام", "output": {{"origin": "تهران", "destination": null}}}},
        {{"input": "از تهران تا مشهد", "output": {{"origin": "تهران", "destination": "مشهد"}}}},
        {{"input": "تهران مشهد", "output": {{"origin": "تهران", "destination": "مشهد"}}}},
        {{"input": "می‌خوام مشهد برم", "output": {{"origin": null, "destination": "مشهد"}}}},
        {{"input": "از شیراز به اهواز", "output": {{"origin": "شیراز", "destination": "اهواز"}}}},
        {{"input": "استانبول ۱۰ آبان بلیط می‌خوام", "output": {{"origin": null, "destination": "استانبول"}}}},
        {{"input": "مشهد امروز میرم", "output": {{"origin": null, "destination": "مشهد"}}}},
        {{"input": "دبی برای فردا", "output": {{"origin": null, "destination": "دبی"}}}},
        {{"input": "بندر عباس", "output": {{"origin": null, "destination": null, "note": "فقط یک شهر و بدون قرینه؛ اگر previous_conversation_state یک فیلد خالی دارد به آن نسبت داده می‌شود"}}}},
        {{
          "input": "کرمان و برای فردا",
          "previous_conversation_state": {{"origin": null, "destination": "اردبیل"}},
          "output": {{"origin": "کرمان", "destination": null, "departure_date_raw": "فردا"}}
        }}
      ]
    }},
    "departure_date": {{
      "rules": [
        "departure_date_raw باید عیناً همان عبارت تاریخی باشد که کاربر گفته، بدون هیچ تغییری.",
        "departure_date باید همیشه به فرمت YYYY-MM-DD میلادی باشد، مگر این‌که کاربر اصلاً هیچ اشاره‌ای به تاریخ نکرده باشد — در آن صورت هر دو فیلد null می‌مانند.",
        "هرگز صرفاً به‌خاطر نبودن یک مثالِ دقیقاً مشابه، departure_date را خالی نگذارید؛ همیشه تلاش کنید بر اساس today آن را محاسبه کنید.",
        "امروز/فردا/پس‌فردا → نسبت به today محاسبه کنید.",
        "نام روز هفته (شنبه تا جمعه) → نزدیک‌ترین وقوعِ آینده‌ی همان روز نسبت به today.",
        "عبارات نسبیِ دیگر با بازه‌ی زمانی مشخص، مثل «N روز دیگه»، «هفته دیگه»/«یک هفته دیگه»، «ماه دیگه»/«یک ماه دیگه» → خودتان با جمع‌کردن همان بازه به today محاسبه کنید: «هفته دیگه» یعنی today + ۷ روز، «N روز دیگه» یعنی today + N روز، «ماه دیگه» یعنی today + ۳۰ روز.",
        "تاریخ‌های تقویمیِ دقیق (مثل «۱۵ آبان» یا «۱۴۰۵/۸/۱۵») را هم تا حد امکان به میلادی تبدیل و در departure_date قرار دهید؛ اگر از صحتِ تبدیل مطمئن نیستید همچنان بهترین حدس خود را بگذارید، نه null — یک بخش دیگر از برنامه این‌گونه تاریخ‌ها را جداگانه و به‌صورت قطعی هم دوباره محاسبه و در صورت لزوم جایگزین می‌کند."
      ],
      "examples": [
        {{"input": "فردا میرم", "today": "2026-09-26", "output": {{"departure_date_raw": "فردا", "departure_date": "2026-09-27"}}}},
        {{"input": "هفته دیگه", "today": "2026-09-26", "output": {{"departure_date_raw": "هفته دیگه", "departure_date": "2026-10-03"}}}},
        {{"input": "سه روز دیگه", "today": "2026-09-26", "output": {{"departure_date_raw": "سه روز دیگه", "departure_date": "2026-09-29"}}}}
      ]
    }},
    "is_flight_request": {{
      "rules": [
        "true: هر اشاره‌ای به بلیط، پرواز، سفر هوایی، مبدأ/مقصد، تاریخ پرواز، تعداد مسافران یا کلاس پرواز — حتی اگر ناقص باشد (مثلاً فقط تعداد مسافران، یا فقط اسم دو شهر).",
        "false: فقط وقتی پیام هیچ ربطی به جستجو/رزرو بلیط ندارد."
      ]
    }},
    "passenger_counts": {{
      "rules": [
        "چیزی گفته نشده → adults=children=infants=null, passenger_count_provided=false.",
        "فقط عدد کل گفته شده (بدون نوع) → همه را adults در نظر بگیرید، children=infants=0.",
        "نوع مسافران مشخص شده → دقیقاً مطابق متن.",
        "هرگز به‌طور پیش‌فرض یک بزرگسال فرض نکنید؛ مقدار پیش‌فرض فقط بعداً و با انتخاب کاربر در برنامه اعمال می‌شود."
      ],
      "examples": [
        {{"input": "سه نفر هستیم", "output": {{"adults": 3, "children": 0, "infants": 0, "passenger_count_provided": true}}}},
        {{"input": "دو بزرگسال و یک کودک", "output": {{"adults": 2, "children": 1, "infants": 0, "passenger_count_provided": true}}}}
      ]
    }},
    "cabin_class": {{
      "rules": [
        " این فیلد اختیاری است و برنامه هرگز درباره‌اش از کاربر سؤال نمی‌پرسد."
        " فقط اگر کاربر صراحتاً اکونومی/بیزینس/فرست گفت → cabin_class مناسب و cabin_class_provided=true."
        " «فرقی نمی‌کند» → cabin_class="unspecified", cabin_class_provided=true."
        " چیزی گفته نشده → cabin_class=null, cabin_class_provided=false."
      ]
    }},
    "sort_by": {{
      "rules": [
        "فقط وقتی صراحتاً درباره‌ی ارزان‌ترین/زودترین/دیرترین/گران‌ترین چیزی گفته شده، sort_by را پر و sort_by_provided=true کنید.",
        "ذکر کلاس پرواز، تعداد مسافران یا تاریخ به‌تنهایی sort_by محسوب نمی‌شود."
      ],
      "examples": [
        {{"input": "ارزون‌ترین پرواز رو می‌خوام", "output": {{"sort_by": "cheapest", "sort_by_provided": true}}}},
        {{"input": "تهران مشهد سه روز دیگه یک نفر اکونومی", "output": {{"sort_by": null, "sort_by_provided": false}}}}
      ]
    }},
    "max_price_toman": {{
      "rules": [
        "چیزی گفته نشده → null.",
        "سقف/بودجه‌ی صریح به تومان → به عدد تومان (نه میلیون) تبدیل کنید.",
        "اگر فقط عدد گفته شد بدون واحد ولی از بافت روشن بود منظور میلیون تومان است، همان تبدیل را انجام دهید."
      ],
      "examples": [
        {{"input": "زیر ۱۵ میلیون تومان", "output": {{"max_price_toman": 15000000}}}},
        {{"input": "بودجه‌م حداکثر ۸ میلیونه", "output": {{"max_price_toman": 8000000}}}},
        {{"input": "زیر ۱۵", "output": {{"max_price_toman": 15000000}}}}
      ]
    }}
  }}
}}
"""
        ),
        (
            "human",
            "{user_request}"
        )
    ])
 
    return extraction_prompt | structured_llm


import re

ZWNJ = "\u200c"

KNOWN_CITIES = [
    "تهران","مشهد","اصفهان","شیراز","تبریز","کرج","اهواز","قم","کرمانشاه","ارومیه","رشت","زاهدان","کرمان","همدان","یزد","اردبیل","بندرعباس","اراک","زنجان","سنندج","قزوین","خرم‌آباد","گرگان","ساری","بجنورد","بیرجند","ایلام","شهرکرد","یاسوج","بوشهر","سمنان","کیش","قشم","آبادان","ماهشهر","چابهار","دزفول","بهبهان","سیرجان","رفسنجان","بم","طبس","خوی","مراغه","سبزوار","نیشابور","شاهرود","رامسر","نوشهر","عسلویه","لامرد","کنگان","پارس‌آباد","جهرم","فسا","اهر","گچساران","ایرانشهر","مسجدسلیمان","دوحه","دبی","ابوظبی","استانبول","آنکارا","آنتالیا","ازمیر","ایروان","تفلیس","باکو","مسکو","نجف","کربلا","بغداد","دمشق","بیروت","مسقط","کوالالامپور","بانکوک","پاریس","لندن","فرانکفورت","برلین","رم","میلان","آمستردام","تورنتو","دهلی","بمبئی","کراچی","کابل","تاشکند","دوشنبه","اشک‌آباد","قاهره","جده","مدینه",
]

_SORTED_CITIES = sorted(KNOWN_CITIES, key=len, reverse=True)


def _fa(text: str) -> str:
    return text.replace("ي", "ی").replace("ك", "ک")


def _norm(s: str) -> str:
    return _fa(s).replace(ZWNJ, "").replace(" ", "")


def _city_pattern(city: str) -> str:
    chars = city.replace(ZWNJ, "").replace(" ", "")
    return r"[\s\u200c]?".join(re.escape(c) for c in chars)


_CITY_ALT = "|".join(_city_pattern(c) for c in _SORTED_CITIES)
_CITY_BY_NORM = {_norm(c): c for c in KNOWN_CITIES}

_ORIGIN_RE = re.compile(rf"(?<!\w)از[\s\u200c]+({_CITY_ALT})(?!\w)")
_DEST_RE = re.compile(rf"(?<!\w)(?:به|تا)[\s\u200c]+({_CITY_ALT})(?!\w)")


def detect_route_from_text(text: str):
    text = _fa(text)
    m_o = _ORIGIN_RE.search(text)
    m_d = _DEST_RE.search(text)
    origin = _CITY_BY_NORM.get(_norm(m_o.group(1))) if m_o else None
    destination = _CITY_BY_NORM.get(_norm(m_d.group(1))) if m_d else None
    return origin, destination


def clean_city(value, user_message):
    """اگر مدل چیز اضافه چسبانده یا اسم را بریده، با فهرست اصلاح می‌کند."""
    if not value:
        return value
    v, msg = _norm(value), _norm(_fa(user_message))
    for city in _SORTED_CITIES:                 # «اصفهان برای پس‌فردا» → «اصفهان»
        if v.startswith(_norm(city)):
            return city
    for city in _SORTED_CITIES:                 # «شیر» → «شیراز» (اگر در پیام باشد)
        c = _norm(city)
        if len(v) >= 2 and c.startswith(v) and c in msg:
            return city
    return value


class InvalidDateError(Exception):
    """کاربر تاریخ مشخصی گفته، اما آن تاریخ نامعتبر یا در گذشته است.

    برخلاف برگرداندن None (که یعنی «هیچ تاریخی در متن پیدا نشد»)، این
    استثنا یعنی «تاریخی پیدا شد ولی قابل قبول نیست» — این تفاوت لازم است
    تا بتوانیم به کاربر دقیقاً بگوییم چرا تاریخش رد شده، نه اینکه فقط
    بی‌توضیح دوباره از او تاریخ بخواهیم.
    """

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


_PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")

PERSIAN_MONTHS = {
    "فروردین": 1, "اردیبهشت": 2, "خرداد": 3, "تیر": 4,
    "مرداد": 5, "شهریور": 6, "مهر": 7, "آبان": 8,
    "آذر": 9, "دی": 10, "بهمن": 11, "اسفند": 12,
}


def _jalali_to_gregorian_iso(year: int, month: int, day: int, today):
    """تاریخ شمسی را به میلادی تبدیل می‌کند؛ اگر روز/ماه واقعی نباشد یا
    تاریخ در گذشته باشد، InvalidDateError با دلیل مشخص پرتاب می‌کند."""

    try:
        j_date = jdatetime.date(year, month, day)
    except ValueError:
        raise InvalidDateError(
            f"«{year}/{month}/{day}» یک تاریخ معتبر نیست "
            "(روز یا ماه وارد شده وجود ندارد)."
        )

    g_date = j_date.togregorian()

    if g_date < today:
        raise InvalidDateError(
            f"تاریخ «{j_date.strftime('%Y/%m/%d')}» مربوط به گذشته است. "
            "لطفاً تاریخی از امروز به بعد بگویید."
        )

    return g_date.isoformat()


def validate_departure_date_iso(date_iso: str | None, today=None) -> str | None:
    """هر تاریخ میلادیِ نهایی (چه از resolve_departure_date، چه حدسِ مستقیمِ
    LLM) را قبل از استفاده اعتبارسنجی می‌کند.

    اگر تاریخ معتبر و از امروز به بعد باشد None برمی‌گرداند؛ در غیر این
    صورت متنِ توضیحِ خطا برای نمایش به کاربر برمی‌گرداند.
    """

    if not date_iso:
        return None

    if today is None:
        today = datetime.now(ZoneInfo("Asia/Tehran")).date()

    try:
        parsed = datetime.strptime(date_iso, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return f"تاریخ «{date_iso}» قابل تشخیص نیست."

    if parsed < today:
        return (
            f"تاریخ «{date_iso}» مربوط به گذشته است. "
            "لطفاً تاریخی از امروز به بعد بگویید."
        )

    return None


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

    if "دیروز" in text or "پریروز" in text:
        raise InvalidDateError(
            "تاریخ «دیروز» مربوط به گذشته است. "
            "لطفاً تاریخی از امروز به بعد بگویید."
        )

    # تاریخ عددیِ صریح شمسی، مثل «۱۴۰۳/۱/۵۰» یا «۱۴۰۳-۰۱-۰۵»
    numeric_text = text.translate(_PERSIAN_DIGITS)
    numeric_match = re.search(
        r"(\d{2,4})\s*[/\-]\s*(\d{1,2})\s*[/\-]\s*(\d{1,2})",
        numeric_text
    )
    if numeric_match:
        year, month, day = (int(g) for g in numeric_match.groups())
        if year < 100:
            year += 1400
        return _jalali_to_gregorian_iso(year, month, day, today)

    # فرمتِ «۵ فروردین» یا «۵ فروردین ۱۴۰۴»
    for month_name, month_num in PERSIAN_MONTHS.items():
        month_match = re.search(
            rf"(\d{{1,2}})\s*{month_name}(?:\s+(\d{{3,4}}))?",
            numeric_text
        )
        if month_match:
            day = int(month_match.group(1))
            explicit_year = month_match.group(2)

            if explicit_year:
                year = int(explicit_year)
            else:
                today_j = jdatetime.date.fromgregorian(date=today)
                year = today_j.year
                # اگر با سال امسال، این روز از ماه گذشته، سال بعد را در نظر بگیر
                try:
                    candidate = jdatetime.date(year, month_num, day)
                    if candidate.togregorian() < today:
                        year += 1
                except ValueError:
                    pass  # اجازه بده خطای «روز نامعتبر» پایین‌تر گزارش شود

            return _jalali_to_gregorian_iso(year, month_num, day, today)

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

CABIN_TEXT_KEYWORDS = [
    ("economy", ("اکونومی", "اقتصادی", "economy")),
    ("business", ("بیزینس", "business")),
    ("first", ("فرست", "first class")),
]

def detect_cabin_in_text(text: str):
    """کلاس پرواز را مستقیم از متن کاربر تشخیص می‌دهد (مستقل از LLM)."""
    t = (
        (text or "")
        .replace("\u200c", " ")
        .replace("ي", "ی")
        .replace("ك", "ک")
        .lower()
    )
    for key, words in CABIN_TEXT_KEYWORDS:
        if any(w in t for w in words):
            return key
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
    # کلاس پرواز مستقیم از متن کاربر هم تشخیص داده می‌شود (مستقل از LLM)؛
    # قبل از هر return زودهنگام (مثلاً خطای تاریخ) اجرا می‌شود.
    cabin_from_text = detect_cabin_in_text(user_text)
    if cabin_from_text:
        result.cabin_class = cabin_from_text
        result.cabin_class_provided = True
    elif result.cabin_class in ("economy", "business", "first"):
        result.cabin_class_provided = True

    text_origin, text_destination = detect_route_from_text(
        user_text
    )


    if text_origin:
        result.origin = text_origin


    if text_destination:
        result.destination = text_destination
    result.origin = clean_city(result.origin, user_text)
    result.destination = clean_city(result.destination, user_text)
    raw_date = result.departure_date_raw


    today_date = datetime.now(ZoneInfo("Asia/Tehran")).date()

    try:
        resolved_date = resolve_departure_date(
            raw_date
        )
    except InvalidDateError as error:
        # کاربر تاریخ مشخصی گفته ولی نامعتبر یا گذشته بود؛ به‌جای اینکه
        # departure_date خالی بماند و کاربر بی‌دلیل دوباره سؤال شود،
        # علتش را صریح نگه می‌داریم تا در مکالمه نمایش داده شود.
        result.departure_date = None
        result.date_error = error.reason
        return result

    if resolved_date is not None:
        result.departure_date = resolved_date

    # حتی اگر resolve_departure_date چیزی برنگردانده باشد، ممکن است خودِ LLM
    # مستقیماً یک departure_date حدس زده باشد (مثلاً از یک فرمت غیرمعمول)؛
    # آن را هم قبل از قبول کردن، برای گذشته‌نبودن بررسی می‌کنیم.
    date_error = validate_departure_date_iso(
        result.departure_date, today_date
    )
    if date_error:
        result.departure_date = None
        result.date_error = date_error
    return result
 
def merge_flight_state(new_request: FlightRequest):
 
    # اطلاعات قبلی را می‌گیریم
    current_state = st.session_state.get(
        "flight_state",
        {}
    ).copy()
 
    new_data = new_request.model_dump()
 
    # این دو فیلد را جدا مدیریت می‌کنیم
    current_state["is_flight_request"] = new_request.is_flight_request
    new_data.pop("is_flight_request", None)
    new_data.pop("passenger_count_provided", None)
    cabin_class_provided = new_data.pop("cabin_class_provided", False)
    sort_by_provided = new_data.pop("sort_by_provided", False)
    if not cabin_class_provided:
        new_data["cabin_class"] = None
 
    if not sort_by_provided:
        new_data["sort_by"] = None

    # date_error فقط مربوط به همین پیام است؛ نباید از نوبت‌های قبلی
    # باقی بماند و روی پیام درست بعدی هم نمایش داده شود.
    current_state["date_error"] = new_data.pop("date_error", None)
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