"""
وقتی کاربر به‌جای شهر، اسم «کشور» می‌نویسد (مثلاً «ترکیه»)، سایت‌های اصلی
(علی‌بابا/مستربلیط) فهرستی از شهرها و فرودگاه‌های همان کشور نشان می‌دهند.
ما هم همین کار را می‌کنیم: به‌جای خطای «شهر پشتیبانی نمی‌شود»، گزینه‌ها را
به کاربر نشان می‌دهیم تا یکی را انتخاب کند.

هر گزینه:
    city     → دقیقاً یکی از کلیدهای SUPPORTED_CITIES (همان چیزی که اسکرپرها
               می‌فهمند؛ مثلاً «استانبول» = همه‌ی فرودگاه‌ها، «استانبول (صبیحه)» = SAW)
    title    → عنوان درشت دکمه
    subtitle → توضیح کوچک زیر آن (مثل «همه فرودگاه‌ها» در سایت اصلی)

⚠️ فقط شهرهایی اینجا هستند که کدشان در INTERNATIONAL_IATA_CODES هست.
برای اضافه‌کردن شهر تازه (مثلاً آنکارا، ازمیر) باید اول کدش را در
alibaba_international.INTERNATIONAL_IATA_CODES اضافه کنی، بعد یک خط اینجا.
"""
import re

_ARABIC_TO_PERSIAN = str.maketrans({"ي": "ی", "ك": "ک", "‌": " "})


def _normalize(text: str) -> str:
    text = (text or "").strip().translate(_ARABIC_TO_PERSIAN)
    return re.sub(r"\s+", " ", text).strip().lower()


COUNTRY_OPTIONS = {
    "ترکیه": [
        {"city": "استانبول", "title": "استانبول", "subtitle": "همه فرودگاه‌ها"},
        {"city": "استانبول (صبیحه)", "title": "استانبول", "subtitle": "فرودگاه صبیحه گوکچن (SAW)"},
        {"city": "آنکارا", "title": "آنکارا", "subtitle": "همه فرودگاه‌ها"},
        {"city": "ازمیر", "title": "ازمیر", "subtitle": "همه فرودگاه‌ها"},
        {"city": "آنتالیا", "title": "آنتالیا", "subtitle": "همه فرودگاه‌ها"},
        {"city": "ترابزون", "title": "ترابزون", "subtitle": "همه فرودگاه‌ها"},
        {"city": "دالامان", "title": "دالامان", "subtitle": "همه فرودگاه‌ها"},
        {"city": "بدروم", "title": "بدروم", "subtitle": "همه فرودگاه‌ها"},
        {"city": "رایز-آرتوین", "title": "رایز", "subtitle": "فرودگاه رایز (RZV)"},
        {"city": "چوکوروا (آدانا)", "title": "چوکوروا", "subtitle": "فرودگاه بین‌المللی چوکوروا (COV)"},
    ],
    "امارات": [
        {"city": "دبی", "title": "دبی", "subtitle": "همه فرودگاه‌ها"},
        {"city": "ابوظبی", "title": "ابوظبی", "subtitle": "همه فرودگاه‌ها"},
        {"city": "شارجه", "title": "شارجه", "subtitle": "همه فرودگاه‌ها"},
    ],
    "عراق": [
        {"city": "بغداد", "title": "بغداد", "subtitle": "همه فرودگاه‌ها"},
        {"city": "نجف", "title": "نجف", "subtitle": "همه فرودگاه‌ها"},
        {"city": "اربیل", "title": "اربیل", "subtitle": "همه فرودگاه‌ها"},
        {"city": "بصره", "title": "بصره", "subtitle": "همه فرودگاه‌ها"},
        {"city": "سلیمانیه", "title": "سلیمانیه", "subtitle": "همه فرودگاه‌ها"},
    ],
    "روسیه": [
        {"city": "مسکو", "title": "مسکو", "subtitle": "همه فرودگاه‌ها"},
        {"city": "سن‌پترزبورگ", "title": "سن‌پترزبورگ", "subtitle": "همه فرودگاه‌ها"},
    ],
    "جمهوری آذربایجان": [
        {"city": "باکو", "title": "باکو", "subtitle": "همه فرودگاه‌ها"},
        {"city": "نخجوان", "title": "نخجوان", "subtitle": "همه فرودگاه‌ها"},
        {"city": "گنجه", "title": "گنجه", "subtitle": "همه فرودگاه‌ها"},
    ],
    "ارمنستان": [
        {"city": "ایروان", "title": "ایروان", "subtitle": "همه فرودگاه‌ها"},
    ],
    "گرجستان": [
        {"city": "تفلیس", "title": "تفلیس", "subtitle": "همه فرودگاه‌ها"},
        {"city": "باتومی", "title": "باتومی", "subtitle": "همه فرودگاه‌ها"},
    ],
    "ایران": [
        {"city": "تهران", "title": "تهران", "subtitle": "همه فرودگاه‌ها"},
        {"city": "مشهد", "title": "مشهد", "subtitle": "همه فرودگاه‌ها"},
        {"city": "شیراز", "title": "شیراز", "subtitle": "همه فرودگاه‌ها"},
        {"city": "اصفهان", "title": "اصفهان", "subtitle": "همه فرودگاه‌ها"},
        {"city": "تبریز", "title": "تبریز", "subtitle": "همه فرودگاه‌ها"},
        {"city": "کیش", "title": "کیش", "subtitle": "همه فرودگاه‌ها"},
    ],
    "قطر": [
        {"city": "دوحه", "title": "دوحه", "subtitle": "همه فرودگاه‌ها"},
    ],
    "مالزی": [
        {"city": "کوالالامپور", "title": "کوالالامپور", "subtitle": "همه فرودگاه‌ها"},
    ],
    "تایلند": [
        {"city": "بانکوک", "title": "بانکوک", "subtitle": "همه فرودگاه‌ها"},
    ],
    "فرانسه": [
        {"city": "پاریس", "title": "پاریس", "subtitle": "همه فرودگاه‌ها"},
    ],
    "انگلیس": [
        {"city": "لندن", "title": "لندن", "subtitle": "همه فرودگاه‌ها"},
    ],
    "آلمان": [
        {"city": "فرانکفورت", "title": "فرانکفورت", "subtitle": "همه فرودگاه‌ها"},
    ],
    "اتریش": [
        {"city": "وین", "title": "وین", "subtitle": "همه فرودگاه‌ها"},
    ],
    "ایتالیا": [
        {"city": "رم", "title": "رم", "subtitle": "همه فرودگاه‌ها"},
    ],
    "اسپانیا": [
        {"city": "بارسلونا", "title": "بارسلونا", "subtitle": "همه فرودگاه‌ها"},
    ],
    "هند": [
        {"city": "دهلی نو", "title": "دهلی نو", "subtitle": "همه فرودگاه‌ها"},
    ],
    "سوریه": [
        {"city": "دمشق", "title": "دمشق", "subtitle": "همه فرودگاه‌ها"},
    ],
    "چین": [
        {"city": "گوانگژو", "title": "گوانگژو", "subtitle": "همه فرودگاه‌ها"},
    ],
}

# نام‌های جایگزین (فارسی رایج و لاتین) → کلید COUNTRY_OPTIONS
COUNTRY_ALIASES = {
    "georgia": "گرجستان", "iran": "ایران", "turkey": "ترکیه", "turkiye": "ترکیه", "türkiye": "ترکیه",
    "uae": "امارات", "emirates": "امارات", "united arab emirates": "امارات",
    "iraq": "عراق", "russia": "روسیه", "azerbaijan": "جمهوری آذربایجان",
    "آذربایجان": "جمهوری آذربایجان", "armenia": "ارمنستان", "qatar": "قطر",
    "malaysia": "مالزی", "thailand": "تایلند", "france": "فرانسه",
    "england": "انگلیس", "uk": "انگلیس", "britain": "انگلیس",
    "انگلستان": "انگلیس", "بریتانیا": "انگلیس",
    "germany": "آلمان", "austria": "اتریش", "italy": "ایتالیا",
    "spain": "اسپانیا", "india": "هند", "syria": "سوریه", "china": "چین",
    "ترکیه": "ترکیه", "امارات متحده عربی": "امارات",
}

_LOOKUP = {_normalize(k): k for k in COUNTRY_OPTIONS}
_LOOKUP.update({_normalize(k): v for k, v in COUNTRY_ALIASES.items()})

# برای اضافه‌شدن به KNOWN_CITIES در flight_logic (تشخیص «بلیط ترکیه»، «به ترکیه»)
COUNTRY_NAMES = list(COUNTRY_OPTIONS.keys())


def resolve_country(raw_name: str | None) -> str | None:
    """اگر ورودی اسم یک کشور بود کلید COUNTRY_OPTIONS را برمی‌گرداند، وگرنه None."""
    if not raw_name:
        return None
    return _LOOKUP.get(_normalize(raw_name))


def get_country_options(country: str) -> list[dict]:
    return [dict(option) for option in COUNTRY_OPTIONS.get(country, [])]