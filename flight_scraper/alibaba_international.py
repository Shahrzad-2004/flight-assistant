"""
اسکرپر بخش «پروازهای خارجی» علی‌بابا.

با بازرسی مستقیمِ سایت واقعی این موارد تأیید شده‌اند:
  - URL مسیرهای خارجی: alibaba.ir/international/{کد شهر مبدأ}ALL-{کد شهر
    مقصد}ALL (مثلاً THRALL-ISTALL برای تهران↔استانبول) — این تأییدشده‌ترین و
    قابل‌اعتمادترین راه رسیدن به صفحه‌ی یک مسیر است، پس مسیر اصلی این فایل
    مستقیم به همین URL می‌رود (بدون نیاز به تایپ در باکس مبدأ/مقصد)
  - ساختار متن کارت پرواز و قیمت (دو div برگ جدا) و برچسب‌های مرتب‌سازی

⚠️ نکاتی که هنوز باز/تخمینی‌اند:
  - select_origin_city/select_destination_city (فقط fallback برای شهرهای
    بدون کد شناخته‌شده) در تست واقعی هیچ‌چیز انتخاب نکردند؛ نیاز به سلکتور
    دقیق‌تر کانتینر دراپ‌داون پیشنهادها دارند
  - انتخاب روز در تقویم فقط بر اساس عدد روز است (بدون چک نام ماه)؛ برای
    تاریخ‌های چند ماه بعد ممکنه نیاز به منطق تشخیص ماه هم اضافه بشه
  - فرض هم‌ردیف‌بودن ترتیب کارت‌های «اطلاعات پرواز» و «قیمت» روی صفحه
  - وقتی مستقیم به URL مسیر می‌ریم، صفحه از قبل یک بخش «قیمت‌های ارزان»ی با
    تاریخ‌های پیش‌فرض نشون می‌ده که کارت‌هاش لزوماً شکل FLIGHT_CARD_PATTERN
    ندارن؛ بعد از ست‌کردن تاریخ و کلیک جستجو، نتایج واقعی (که پارس می‌کنیم)
    باید جایگزین/اضافه بشن - این رفتار روی سایت واقعی تست نشده
"""
from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import re
from datetime import datetime
import jdatetime
import streamlit as st

# نگاشت نام فارسی مقصدهای خارجی پرتقاضا به «کد شهر» (IATA). این کدها برای
# ساخت URL به‌فرمت {کد}ALL-{کد}ALL استفاده می‌شوند (یعنی «همه‌ی فرودگاه‌های
# شهر»)، که با مشاهده‌ی واقعی سایت (alibaba.ir/international/THRALL-ISTALL
# برای تهران↔استانبول) تأیید شده است. توجه: برای تهران کد «THR» (کد
# متروپلیتن/شهری، نه IKA که مخصوص فرودگاه امام خمینی است) درسته.
INTERNATIONAL_IATA_CODES = {
    # شهرهای مبدأ داخلی که پرواز خارجی هم دارند
    "تهران": "THR",
    "مشهد": "MHD",
    "شیراز": "SYZ",
    "اصفهان": "IFN",
    "تبریز": "TBZ",
    "کیش": "KIH",
    # مقصدهای خارجی پرتقاضا
    "دبی": "DXB",
    "استانبول": "IST",
    "آنتالیا": "AYT",
    "مسکو": "SVO",
    "باکو": "GYD",
    "ایروان": "EVN",
    "دوحه": "DOH",
    "کوالالامپور": "KUL",
    "بانکوک": "BKK",
    "پاریس": "CDG",
    "لندن": "LHR",
    "فرانکفورت": "FRA",
    "وین": "VIE",
    "رم": "FCO",
    "بارسلونا": "BCN",
    "دهلی نو": "DEL",
    "استانبول (صبیحه)": "SAW",
    "نجف": "NJF",
    "بغداد": "BGW",
    "دمشق": "DAM",
    "گوانگژو": "CAN",
}

# شهرهای ایرانی‌ای که واقعاً می‌توانند «مبدأ» یک پرواز خارجی باشند. این زیرمجموعه‌ی
# صریح از INTERNATIONAL_IATA_CODES جداست چون آن دیکشنری مبدأ و مقصد را با هم قاطی
# دارد؛ بدون این ست، هر شهر ایرانیِ داخلی (مثلاً همدان) که فقط در IATA_CODES داخلی
# است هم به‌اشتباه به‌عنوان مبدأ خارجی معتبر پذیرفته می‌شود.
INTERNATIONAL_ORIGIN_CITIES = {
    "تهران",
    "مشهد",
    "شیراز",
    "اصفهان",
    "تبریز",
    "کیش",
}

JALALI_MONTHS = {
    1: "فروردین",
    2: "اردیبهشت",
    3: "خرداد",
    4: "تیر",
    5: "مرداد",
    6: "شهریور",
    7: "مهر",
    8: "آبان",
    9: "آذر",
    10: "دی",
    11: "بهمن",
    12: "اسفند",
}

SORT_TAB_LABELS = {
    "cheapest": "ارزان‌ترین",
    "fastest": "سریع‌ترین",
    "earliest": "زودترین",
    "latest": "دیرترین",
}
AIRLINE_LOGOS = {
    "Zagros Airline": {
        "logo":"airlines/ZG.svg"
    },
    "IRAN AIRTOUR": {
        "logo":"airlines/B99.svg"
    },
    "IranAir": {
        "logo":"airlines/B9.svg"
    },
    "Ata Airlines": {
            "logo":"airlines/I3.svg"
        },
    "Meraj Airlines": {
            "logo":"airlines/MJ.svg"
        },
    "Varesh": {
            "logo":"airlines/VR.svg"
        },
    "ماهان": {
            "logo":"airlines/W5.svg"
        },
    "Sepehran": {
            "logo":"airlines/SR.svg"
        },
    "کارون": {
            "logo":"airlines/NV.svg"
        },
    "جی اسکای": {
            "logo":"airlines/JS.png"
        },
    "Taban Air": {
            "logo":"airlines/HH.svg"
        },
    "آساجت": {
            "logo":"airlines/SJ.png"
        },
    "اطلس ایر": {
            "logo":"airlines/AT.svg"
        },
    "FlyKish": {
            "logo":"airlines/FK.svg"
        },
    "Caspian Airline": {
            "logo":"airlines/IV.svg"
        },
    "لاد": {
            "logo":"airlines/LD.svg"
        },
    "نسیم ایر": {
            "logo":"airlines/NA.svg"
        },
    "چابهار": {
            "logo":"airlines/RI.svg"
        },
    "Saha Airline": {
            "logo":"airlines/SA.svg"
        },
    "Qeshm Air": {
            "logo":"airlines/QB.svg"
        },
    "Soroush Air": {
            "logo":"airlines/SHR.svg"
        },
    "رایمون": {
            "logo":"airlines/RY.svg"
        },
    "آسمان": {
            "logo":"airlines/AS.svg"
        },
    "آوا ایر": {
            "logo":"airlines/AV.svg"
        },
}
# ساختار متن هر کارت پرواز (یک div برگ بدون فرزند div) روی صفحه‌ی خارجی،
# طبق نمونه‌ی واقعی مشاهده‌شده، همه چیز پشت‌سرهم و بدون جداکننده است، مثلاً:
# "IranAirسیستمیاکونومی19:05تهران IKA3 ساعت و 55 دقیقه22:30استانبول IST30 KG"
FLIGHT_CARD_PATTERN = re.compile(
    r"(?P<airline>[^\d\n]+?)\s*"
    r"(?P<flight_type>سیستمی|چارتری)\s*"
    r"(?P<cabin_class>(?:پرمیوم|پریمیوم)\s*اکونومی|اکونومی|بیزینس|فرست)\s*"
    r"(?P<departure_time>\d{1,2}:\d{2})\s*"
    r"(?P<origin_city>[^\d\n]+?)\s*(?P<origin_code>[A-Z]{3})\s*"
    r"(?P<duration>\d+\s*ساعت(?:\s*و\s*\d+\s*دقیقه)?)\s*"
    r"(?P<arrival_time>\d{1,2}:\d{2})\s*"
    r"(?P<destination_city>[^\d\n]+?)\s*(?P<destination_code>[A-Z]{3})\s*"
    r"(?P<baggage>\d+(?:\s*[×xX]\s*\d+)?\s*KG)"
)

# متن کارت قیمت (هم div برگِ جدا)، مثلاً:
# "45,967,000تومان جزئیات پرواز و خرید 8صندلی باقی مانده"
# ⚠️ بخش «N صندلی باقی مانده» ظاهراً همیشه نمایش داده نمی‌شه (شاید فقط وقتی
# صندلی کم مونده)، پس اختیاری در نظر گرفته شده.
PRICE_CARD_PATTERN = re.compile(
    r"(?P<price>[\d,]{4,})\s*تومان"
    r"(?:.*?(?P<seats_left>\d+)\s*صندلی\s*باقی\s*مانده)?"
)

# برای پیدا کردن این دو نوع div با has_text (که substring/regex search است،
# نه match کامل)، از یک الگوی کوتاه‌تر و بدون anchor استفاده می‌کنیم:
FLIGHT_CARD_HINT = re.compile(r"(سیستمی|چارتری).*(اکونومی|بیزینس|فرست)")
PRICE_CARD_HINT = re.compile(r"[\d,]{4,}\s*تومان")


def get_airline_logo(airline_name):
    """نام ایرلاین (فارسی) را با کلیدهای AIRLINE_LOGOS مقایسه می‌کند و در صورت
    تطابق، مسیر لوگو را برمی‌گرداند؛ در غیر این صورت None."""
    if not airline_name:
        return None
    for name, logo in AIRLINE_LOGOS.items():
        if name in airline_name:
            return logo["logo"]
    return None


def convert_to_jalali(date_str):
    gregorian_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    return jdatetime.date.fromgregorian(date=gregorian_date)


def parse_price(price_text):
    numbers = re.sub(r"[^\d]", "", price_text)
    return int(numbers) if numbers else 0


def build_alibaba_international_url(origin: str, destination: str) -> str | None:
    """آدرس صفحه‌ی مسیر خارجی را می‌سازد، مثلاً برای تهران↔استانبول:
    https://www.alibaba.ir/international/THRALL-ISTALL
    این فرمت با مشاهده‌ی واقعی روی سایت تأیید شده. اگر کد شهر در
    INTERNATIONAL_IATA_CODES نباشد None برمی‌گرداند."""

    origin_code = INTERNATIONAL_IATA_CODES.get(origin)
    destination_code = INTERNATIONAL_IATA_CODES.get(destination)

    if not origin_code or not destination_code:
        return None

    return f"https://www.alibaba.ir/international/{origin_code}ALL-{destination_code}ALL"


def login_if_required(page, timeout=15000):


    password_login_button = page.get_by_role(
        "button", name="ورود با کلمه عبور"
    )

    try:
        password_login_button.wait_for(state="visible", timeout=timeout)
    except PlaywrightTimeoutError:
        # مودال ورود باز نشده - نیازی به لاگین نیست
        return True

    phone = st.secrets.get("ALIBABA_PHONE")
    password = st.secrets.get("ALIBABA_PASSWORD")

    if not phone or not password:
        print(
            "مودال ورود علی‌بابا باز شد ولی ALIBABA_PHONE/ALIBABA_PASSWORD "
            "توی secrets.toml تنظیم نشدن - نمی‌تونم لاگین کنم"
        )
        return False

    try:
        password_login_button.click(timeout=timeout)

        page.get_by_role(
            "textbox", name="آدرس ایمیل یا شماره موبایل"
        ).fill(phone)

        page.get_by_role("textbox", name="کلمه عبور").fill(password)

        page.get_by_role("button", name="ورود به علی‌بابا").click(
            timeout=timeout
        )

        page.wait_for_timeout(3000)
        return True

    except PlaywrightTimeoutError:
        print("لاگین به علی‌بابا با تایم‌اوت مواجه شد")
        return False
    except Exception as e:
        print("خطا در لاگین به علی‌بابا:", e)
        return False


def apply_sort(page, sort_by):
    """کلیک روی تب مرتب‌سازی.
    نام دکمه‌ها ثابت نیست؛ قیمت/زمان هم به اسم accessibility اضافه می‌شود
    (مثلاً «ارزان‌ترین 34.2 میلیون - 02:...»)، پس با regex فقط پیشوند برچسب
    را match می‌کنیم."""

    if not sort_by:
        return

    label = SORT_TAB_LABELS.get(sort_by)
    if not label:
        return

    try:
        page.get_by_role(
            "button", name=re.compile(rf"^{re.escape(label)}")
        ).first.click(timeout=5000)
        page.wait_for_timeout(1500)
    except PlaywrightTimeoutError:
        print(f"تب مرتب‌سازی «{label}» توی پروازهای خارجی پیدا نشد - رد شدیم")


def select_origin_city(page, city, timeout=25000):
    """[Fallback] انتخاب فرودگاه مبدأ از طریق تایپ در باکس، برای شهرهایی که
    کدشان در INTERNATIONAL_IATA_CODES نیست (مسیر اصلی از build_alibaba_international_url
    استفاده می‌کند و این تابع را صدا نمی‌زند).

    ⚠️ این تابع در تست واقعی جواب نداد (فیلد خالی موند). گمان می‌کنم چون
    `page.locator("a").filter(has_text=city)` به کل صفحه اسکوپ داره، نه فقط
    باکس پیشنهادهای زیر ورودی، ممکنه یا هیچی پیدا نکنه (و timeout بخوره) یا
    به یک لینک نامرتبط جای دیگه‌ی صفحه کلیک کنه. برای دقیق‌شدنش نیاز به
    سلکتور کانتینر دراپ‌داون واقعی (مثلاً یک role="listbox" یا کلاس مشخص)
    داریم که باید از DevTools/codegen گرفته بشه."""

    city_input = page.get_by_role(
        "textbox", name="مبدا (شهر، فرودگاه)"
    )
    city_input.click(timeout=timeout)
    city_input.fill("")
    city_input.fill(city)

    option = page.locator("a").filter(has_text=city).first

    try:
        option.wait_for(state="visible", timeout=timeout)
        option.click(timeout=timeout)
        return True
    except PlaywrightTimeoutError:
        print(f"گزینهٔ فرودگاه مبدأ خارجی پیدا نشد: {city}")
        return False


def select_destination_city(page, city, timeout=25000):
    """[Fallback] همان توضیح select_origin_city، برای فیلد مقصد."""

    city_input = page.get_by_role(
        "textbox", name="مقصد (شهر، فرودگاه)"
    )
    city_input.click(timeout=timeout)
    city_input.fill("")
    city_input.fill(city)

    option = page.locator("a").filter(has_text=city).first

    try:
        option.wait_for(state="visible", timeout=timeout)
        option.click(timeout=timeout)
        return True
    except PlaywrightTimeoutError:
        print(f"گزینهٔ مقصد خارجی پیدا نشد: {city}")
        return False


def select_departure_date(page, date_str):
    """باز کردن تقویم و انتخاب روز رفت.
    ⚠️ این تابع فقط بر اساس عدد روز کلیک می‌کند (get_by_text(day).first)،
    دقیقاً مثل تعامل واقعی ثبت‌شده روی سایت. یعنی فرض می‌شود روزِ موردنظر در
    اولین/بالاترین چیزی است که با آن متن مطابقت دارد — روی تاریخ‌های دورتر
    (چند ماه بعد) که چند عدد روزِ یکسان در تقویم دیده می‌شود، ممکن است لازم
    باشد ابتدا با نام ماه (JALALI_MONTHS) به بخش درست تقویم اسکرول/ناوبری
    شود."""

    jalali_date = convert_to_jalali(date_str)
    day = jalali_date.day

    date_input = page.get_by_role("textbox", name="تاریخ رفت")
    date_input.click()

    try:
        page.get_by_text(str(day)).first.click()
    except PlaywrightTimeoutError:
        print(f"روز {day} در تقویم پروازهای خارجی پیدا نشد")


def select_passengers(page, adults, children, infants):
    passenger_input = page.get_by_role("textbox", name="مسافران")
    if passenger_input.count() == 0:
        return

    passenger_input.click()

    add_buttons = page.get_by_role("button", name="افزودن")
    if add_buttons.count() < 3:
        return

    adult_add = add_buttons.first
    child_add = add_buttons.nth(1)
    infant_add = add_buttons.nth(2)

    # علی‌بابا معمولاً از قبل ۱ بزرگسال دارد
    for _ in range(max(0, adults - 1)):
        adult_add.click()

    for _ in range(children):
        child_add.click()

    for _ in range(infants):
        infant_add.click()


def load_all_flights(page):
    """با اسکرول تا انتهای صفحه، لود لیزی همه‌ی کارت‌های پرواز را کامل می‌کند.
    از FLIGHT_CARD_HINT به‌جای کلاس ".available-card" (که برای صفحه‌ی خارجی
    تأیید نشده) برای شمارش کارت‌ها استفاده می‌شود."""

    previous_count = 0

    while True:
        cards = page.locator("div:not(:has(div))").filter(
            has_text=FLIGHT_CARD_HINT
        )
        current_count = cards.count()

        print("تعداد فعلی کارت‌های خارجی:", current_count)

        if current_count == previous_count:
            break

        previous_count = current_count
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1500)


def search_alibaba_international(
    origin,
    destination,
    departure_date,
    adults,
    children,
    infants,
    sort_by=None,
):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        )
        page = browser.new_page()

        try:
            route_url = build_alibaba_international_url(origin, destination)

            if route_url:
                # مسیر اصلی و قابل‌اعتماد: رفتن مستقیم به URL تأییدشده‌ی مسیر
                page.goto(route_url)
            else:
                # Fallback: کد شهر نداریم، پس از صفحه‌ی اصلی و تایپ استفاده کن
                # ⚠️ این مسیر در تست واقعی جواب نداده - نگاه کن به توضیحات
                # select_origin_city/select_destination_city
                page.goto("https://www.alibaba.ir/iranout")

                if not select_origin_city(page, origin):
                    print(f"شهر مبدا در پروازهای خارجی پیدا نشد: {origin}")
                    return []

                if not select_destination_city(page, destination):
                    print(f"شهر مقصد در پروازهای خارجی پیدا نشد: {destination}")
                    return []

            select_departure_date(page, departure_date)
            select_passengers(page, adults=adults, children=children, infants=infants)

            # روی صفحه‌ی مسیر (/international/...) دکمه «جستجوی پرواز» است؛
            # روی صفحه‌ی اصلی (/iranout) فقط «جستجو» - هر دو را امتحان می‌کنیم
            search_button = page.get_by_role(
                "button", name=re.compile(r"^جستجو")
            ).first
            search_button.click()

            page.wait_for_timeout(3000)
            login_if_required(page)
            page.wait_for_timeout(2000)

            apply_sort(page, sort_by)
            load_all_flights(page)

            # هر کارت پرواز از چند div برگِ جدا تشکیل شده (ایرلاین، نوع/کلاس،
            # ساعت‌ها، قیمت هرکدوم توی div خودشون‌اند، نه یکی). برای همین از
            # کوچیک‌ترین و مشخص‌ترین‌شون (نوع‌پرواز+کلاس کابین) به‌عنوان لنگرِ
            # هر کارت استفاده می‌کنیم و با XPath می‌ریم بالا تا نزدیک‌ترین
            # والدی که «تومان» هم توش هست - یعنی کل کارت شامل قیمت.
            anchor_divs = page.locator("div:not(:has(div))").filter(
                has_text=FLIGHT_CARD_HINT
            )
            anchor_count = anchor_divs.count()

            print("تعداد کارت‌های شناسایی‌شده (بر اساس لنگر نوع/کلاس):", anchor_count)

            flights = []
            debug_samples_printed = 0

            for i in range(anchor_count):
                try:
                    anchor = anchor_divs.nth(i)
                    card = anchor.locator(
                        "xpath=ancestor::div[contains(., 'تومان')][1]"
                    )

                    if card.count() == 0:
                        print(f"[کارت {i}] والد حاوی قیمت پیدا نشد - رد شد")
                        continue

                    card_text = card.first.inner_text().strip()

                    # اگه والد انتخابی بیش‌ازحد بزرگ بوده و بیش از یک کارت رو
                    # توی خودش جا داده (چند بار «اکونومی»/«بیزینس» و... توش
                    # هست)، مطمئن نیستیم کدوم قیمت مال کدوم پرواز است - رد شو
                    marker_occurrences = len(
                        list(FLIGHT_CARD_HINT.finditer(card_text))
                    )
                    if marker_occurrences > 1:
                        print(
                            f"[کارت {i}] والد انتخابی چند کارت رو با هم گرفته "
                            f"({marker_occurrences} بار) - رد شد"
                        )
                        continue

                    info_match = FLIGHT_CARD_PATTERN.search(card_text)
                    price_match = PRICE_CARD_PATTERN.search(card_text)

                    if not info_match:
                        if debug_samples_printed < 5:
                            print(
                                "متن کارت با الگوی مورد انتظار جور نشد:",
                                repr(card_text[:400]),
                            )
                            debug_samples_printed += 1
                        continue

                    if not price_match:
                        if debug_samples_printed < 5:
                            print(
                                "قیمت توی متن کارت پیدا نشد:",
                                repr(card_text[:400]),
                            )
                            debug_samples_printed += 1
                        continue

                    info = info_match.groupdict()
                    price_info = price_match.groupdict()

                    price_value = int(price_info["price"].replace(",", ""))

                    airline_name = info["airline"].strip()

                    flight = {
                        "airline": airline_name,
                        "airline_logo": get_airline_logo(airline_name),
                        "flight_type": info["flight_type"],
                        "cabin_class": info["cabin_class"],
                        "aircraft": "نامشخص",
                        "wheelchair_note": None,
                        "origin": origin,
                        "origin_city": info["origin_city"].strip(),
                        "origin_code": info["origin_code"],
                        "departure_time": info["departure_time"],
                        "destination": destination,
                        "destination_city": info["destination_city"].strip(),
                        "destination_code": info["destination_code"],
                        "arrival_time": info["arrival_time"],
                        "duration": info["duration"],
                        "baggage": info["baggage"],
                        "remaining_seats": price_info.get("seats_left") or "نامشخص",
                        "price": f"{price_info['price']} تومان",
                        "price_value": price_value,
                        "source": "علی‌بابا (خارجی)",
                        "source_url": route_url or build_alibaba_international_url(
                            origin, destination
                        ) or "https://www.alibaba.ir/iranout",
                    }

                    flights.append(flight)

                except Exception as e:
                    print("خطا در پردازش یک کارت پرواز خارجی:", e)
                    continue

            return flights

        except PlaywrightTimeoutError:
            print("زمان انتظار پروازهای خارجی علی‌بابا تمام شد")
            return []

        except Exception as e:
            print("خطا در جستجوی پروازهای خارجی:", e)
            return []

        finally:
            if not page.is_closed():
                page.close()
            if browser.is_connected():
                browser.close()


if __name__ == "__main__":
    results = search_alibaba_international(
        origin="تهران",
        destination="استانبول",
        departure_date="2026-10-08",
        adults=1,
        children=0,
        infants=0,
    )

    for flight in results:
        print("----------------")
        print(flight)