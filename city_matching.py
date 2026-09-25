import re
from difflib import get_close_matches

ARABIC_TO_PERSIAN = str.maketrans({"ي": "ی", "ك": "ک", "‌": " "})  # نیم‌فاصله -> فاصله هم یکسان می‌شه

def _normalize(name: str) -> str:
    name = name.strip().translate(ARABIC_TO_PERSIAN)
    name = re.sub(r"\s+", " ", name).strip()
    return name

# alias هایی که مستقیم به کلید اصلی SUPPORTED_CITIES نگاشت می‌شن
CITY_ALIASES = {
    "tehran": "تهران", "mashhad": "مشهد", "shiraz": "شیراز",
    "isfahan": "اصفهان", "esfahan": "اصفهان", "tabriz": "تبریز",
    "ahvaz": "اهواز", "kish": "کیش", "kerman": "کرمان",
    "ardabil": "اردبیل", "yazd": "یزد", "bandar abbas": "بندرعباس",
    "rasht": "رشت", "sari": "ساری", "zahedan": "زاهدان",
    "bushehr": "بوشهر", "hamedan": "همدان", "kermanshah": "کرمانشاه",
    "urmia": "ارومیه", "gorgan": "گرگان", "abadan": "آبادان",
    "khorramabad": "خرم‌آباد", "zanjan": "زنجان", "qeshm": "قشم",
    "chabahar": "چابهار", "dubai": "دبی", "istanbul": "استانبول",
    "antalya": "آنتالیا", "moscow": "مسکو", "baku": "باکو",
    "yerevan": "ایروان", "doha": "دوحه", "kuala lumpur": "کوالالامپور",
    "bangkok": "بانکوک", "paris": "پاریس", "london": "لندن",
    "frankfurt": "فرانکفورت", "vienna": "وین", "rome": "رم",
    "barcelona": "بارسلونا", "new delhi": "دهلی نو", "delhi": "دهلی نو",
    "najaf": "نجف", "baghdad": "بغداد", "damascus": "دمشق",
    "guangzhou": "گوانگژو",
    # جایگزین‌های رایج فارسی که دقیقاً کلید نیستن
    "جزیره کیش": "کیش",
    "بندر عباس": "بندرعباس",
    "خرم آباد": "خرم‌آباد",
}

def resolve_city(raw_name: str, supported_cities: set, cutoff: float = 0.72) -> str | None:
    """اسم خام (فارسی/لاتین/با غلط املایی) رو به کلید معتبر SUPPORTED_CITIES تبدیل می‌کنه."""
    if not raw_name:
        return None

    normalized = _normalize(raw_name)
    lowered = normalized.lower()

    # ۱. مچ دقیق (حالت فعلی، سریع‌ترین مسیر)
    if normalized in supported_cities:
        return normalized

    # ۲. alias (لاتین یا نام‌های جایگزین رایج)
    if lowered in CITY_ALIASES:
        return CITY_ALIASES[lowered]
    if normalized in CITY_ALIASES:
        return CITY_ALIASES[normalized]

    # ۳. fuzzy matching برای غلط املایی (فقط روی فارسی معنا داره)
    matches = get_close_matches(normalized, supported_cities, n=1, cutoff=cutoff)
    if matches:
        return matches[0]

    return None