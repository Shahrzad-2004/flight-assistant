from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import re
from datetime import datetime
import jdatetime
 
# نگاشت نام فارسی شهرها به کد فرودگاه (IATA) برای ساخت لینک مستربلیط
# ⚠️ این کدها را حتماً با ساختار واقعی لینک‌های mrbilit.com چک کن،
# چون من به سایت زنده دسترسی ندارم و این بخش را بر اساس الگوی علی‌بابا تخمین زده‌ام.
IATA_CODES = {
    "تهران": "THR",
    "مشهد": "MHD",
    "شیراز": "SYZ",
    "اصفهان": "IFN",
    "تبریز": "TBZ",
    "اهواز": "AWZ",
    "کیش": "KIH",
    "کرمان": "KER",
    "اردبیل": "ADU",
    "یزد": "AZD",
    "بندرعباس": "BND",
    "رشت": "RAS",
    "ساری": "SRY",
    "زاهدان": "ZAH",
    "بوشهر": "BUZ",
    "همدان": "HDM",
    "کرمانشاه": "KSH",
    "ارومیه": "OMH",
    "گرگان": "GBT",
    "آبادان": "ABD",
    "خرم‌آباد": "KHD",
    "زنجان": "JWN",
    "قشم": "GSM",
    "چابهار": "ZBR",
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
    "cheapest": "کمترین قیمت",
    "earliest": "زود‌ترین زمان",
    "latest": "دیرترین زمان حرکت",
    "priciest": "گران‌ترین قیمت",
}
 
AIRLINE_LOGOS = {
    "زاگرس": {
        "logo":"airlines/ZG.svg"
    },
    "ایران ایرتور": {
        "logo":"airlines/B99.svg"
    },
    "ایران ایر": {
        "logo":"airlines/B9.svg"
    },
    "آتا": {
            "logo":"airlines/I3.svg"
        },
    "معراج": {
            "logo":"airlines/MJ.svg"
        },
    "وارش": {
            "logo":"airlines/VR.svg"
        },
    "ماهان": {
            "logo":"airlines/W5.svg"
        },
    "سپهران ایر": {
            "logo":"airlines/SR.svg"
        },
    "کارون": {
            "logo":"airlines/NV.svg"
        },
    "جی اسکای": {
            "logo":"airlines/JS.png"
        },
    "تابان": {
            "logo":"airlines/HH.svg"
        },
    "آساجت": {
            "logo":"airlines/SJ.png"
        },
    "اطلس ایر": {
            "logo":"airlines/AT.svg"
        },
    "فلای کیش": {
            "logo":"airlines/FK.svg"
        },
    "کاسپین": {
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
    "ساها ایر": {
            "logo":"airlines/SA.svg"
        },
    "قشم ایر": {
            "logo":"airlines/QB.svg"
        },
    "سروش ایر": {
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
    "فلای پرشیا": {
            "logo":"airlines/FP.svg"
        },
}
 
 
def parse_price(price_text):
    numbers = re.sub(r"[^\d]", "", price_text)
    return int(numbers) if numbers else 0
 
 
def convert_to_jalali(date_str):
    gregorian_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    return jdatetime.date.fromgregorian(date=gregorian_date)
 
 
def build_mrbilit_url(
    origin: str,
    destination: str,
    departure_date: str,
    adults: int,
    children: int,
    infants: int,
) -> str:
    """آدرس صفحه‌ی جستجوی مستربلیط (با تاریخ و تعداد مسافر پرشده) را می‌سازد.
    ⚠️ الگوی مسیر (path) را با URL واقعی نتیجه‌ی جستجو در mrbilit.com مقایسه و در صورت نیاز اصلاح کن."""
 
    origin_code = IATA_CODES.get(origin)
    destination_code = IATA_CODES.get(destination)
 
    if not origin_code or not destination_code:
        return "https://mrbilit.com/plane-ticket"
 
    jalali_date = convert_to_jalali(departure_date)
    departure_date_param = f"{jalali_date.year}-{jalali_date.month:02d}-{jalali_date.day:02d}"
 
    return (
        f"https://mrbilit.com/flights/{origin_code}-{destination_code}"
        f"?departureDate={departure_date_param}"
        f"&adult={adults}&child={children}&infant={infants}"
    )
 
 
def apply_sort(page, sort_by):
    """در صورت وجود تب مرتب‌سازی کلیک می‌کند. این تب‌ها روی مستربلیط رادیو-باتن هستن
    (نه دکمه‌ی معمولی)، پس با متن خودشون پیداشون می‌کنیم."""
    if not sort_by:
        return
 
    label = SORT_TAB_LABELS.get(sort_by)
    if not label:
        return
 
    sort_option = page.get_by_text(label, exact=True)
 
    try:
        sort_option.click(timeout=5000)
        page.wait_for_timeout(1500)
    except PlaywrightTimeoutError:
        print(f"تب مرتب‌سازی «{label}» توی مستربلیط پیدا نشد - رد شدیم")
 
 
# --- تنظیمات پایداری پر کردن فرم ---
FORM_ATTEMPTS = 2            # چند بار کل فرم (با باز کردن دوباره‌ی صفحه) تلاش شود
VERIFY_CITY_INPUT_VALUE = True   # بعد از انتخاب شهر، پر بودن خودِ input هم چک شود.
                                 # اگر سایت مقدار را داخل input نگه نمی‌دارد و لاگ
                                 # مدام «مقدار داخل فیلد ثبت نشد» می‌دهد، False کن.
REQUIRE_PASSENGERS = True    # شکست در تنظیم مسافران = شکست فرم (و تلاش مجدد)


def wait_page_ready(page):
    """صبر تا صفحه واقعاً آماده‌ی تعامل شود (نه فقط DOM لود شده)."""
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except PlaywrightTimeoutError:
        pass  # بعضی سایت‌ها هیچ‌وقت idle نمی‌شن
    page.get_by_placeholder("فرودگاه مبدأ", exact=True).wait_for(
        state="visible", timeout=30000
    )
    page.wait_for_timeout(800)


def select_city(page, city, placeholder, timeout=25000, attempts=3):
    """انتخاب شهر مبدأ/مقصد با تایپ واقعی و تلاش مجدد.
    timeout به میلی‌ثانیه‌ست؛ روی نت کند مقدار بزرگ‌تری پاس بده."""
    field = page.get_by_placeholder(placeholder, exact=True)
    pattern = re.compile(rf"^\s*{re.escape(city.strip())}\s*$")

    for attempt in range(1, attempts + 1):
        try:
            field.click(timeout=timeout)
            field.fill("")                              # پاک‌کردن مقدار قبلی
            field.press_sequentially(city, delay=90)    # تایپ واقعی
            option = page.get_by_text(pattern).locator("visible=true").first
            option.wait_for(state="visible", timeout=8000)
            option.click(timeout=5000)
            page.wait_for_timeout(400)
            if not VERIFY_CITY_INPUT_VALUE or field.input_value().strip():
                return True                             # واقعاً ثبت شد
            print(f"مقدار داخل فیلد «{placeholder}» ثبت نشد")
        except PlaywrightTimeoutError:
            pass
        print(f"تلاش {attempt} برای «{city}» ناموفق بود")
        page.wait_for_timeout(700)

    return False


def _date_cell_ids(jalali_date):
    """id سلول روز در تقویم. طبق codegen ماه دو رقمی و روز بدون صفر اول است
    (مثل «1405-07-5»)؛ برای اطمینان حالت روز دورقمی هم امتحان می‌شود."""
    base = f"{jalali_date.year}-{jalali_date.month:02d}"
    ids = [f"{base}-{jalali_date.day}"]
    padded = f"{base}-{jalali_date.day:02d}"
    if padded not in ids:
        ids.append(padded)
    return ids


def select_departure_date(page, date_str, max_month_clicks=6):
    """باز کردن تقویم و انتخاب روز رفت با id سلول.
    اگر ماه موردنظر هنوز رندر نشده باشد، با دکمه‌ی «ماه بعد/بعدی» جلو می‌رود.
    در صورت پیدا نشدن روز، False برمی‌گرداند (رد‌شدن بی‌صدا ندارد)."""

    jalali_date = convert_to_jalali(date_str)
    day = jalali_date.day
    month_name = JALALI_MONTHS[jalali_date.month]

    page.get_by_placeholder("رفت").first.click()

    ids = _date_cell_ids(jalali_date)
    cell = page.locator(", ".join(f'[id="{i}"]' for i in ids)).locator(
        "visible=true"
    )

    for _ in range(max_month_clicks + 1):
        try:
            cell.first.wait_for(state="visible", timeout=2500)
            break
        except PlaywrightTimeoutError:
            next_button = page.get_by_role(
                "button", name=re.compile(r"ماه بعد|بعدی")
            )
            if next_button.count() == 0:
                print(
                    f"روز {day} {month_name} در تقویم دیده نشد و دکمه‌ی ماه بعد هم "
                    "پیدا نشد"
                )
                return False
            next_button.first.click()
            page.wait_for_timeout(400)
    else:
        print(f"روز {day} از ماه {month_name} در تقویم پیدا نشد")
        return False

    try:
        cell.first.get_by_text(str(day), exact=True).first.click(timeout=3000)
    except PlaywrightTimeoutError:
        # اگر متن روز جدا نبود، خود سلول را کلیک کن
        cell.first.click()
    confirm_button = page.get_by_role("button", name="تأیید")
    confirm_button.click()
    return True


def select_passengers(page, adults, children, infants):
    """باز کردن پنل مسافران و تنظیم تعداد بزرگسال/کودک/نوزاد.
    ⚠️ نام دکمه‌های افزایش/کاهش را با DOM واقعی مستربلیط چک کن.
    True یعنی تنظیم شد (یا نیازی به تغییر نبود)، False یعنی نشد."""

    if adults == 1 and children == 0 and infants == 0:
        return True  # پیش‌فرض، نیازی به کلیک نیست

    passenger_input = page.get_by_placeholder("انتخاب تعداد (اختیاری)")
    try:
        passenger_input.wait_for(state="visible", timeout=8000)
        passenger_input.click()
        add_buttons = page.get_by_role("button")
        add_buttons.nth(2).wait_for(state="visible", timeout=5000)
    except PlaywrightTimeoutError:
        print("پنل مسافران باز نشد")
        return False

    for _ in range(max(0, adults - 1)):
        add_buttons.nth(2).click()
    for _ in range(children):
        add_buttons.nth(4).click()
    for _ in range(infants):
        page.locator("div:nth-child(4) > .counter > button:nth-child(3)").click()
    return True


def fill_form(page, origin, destination, departure_date, adults, children, infants, city_timeout):
    """پر کردن کل فرم؛ اگر هر مرحله‌ی لازم شکست بخورد False برمی‌گرداند."""
    if not select_city(page, origin, "فرودگاه مبدأ", timeout=city_timeout):
        print(f"شهر مبدا در مستربلیط پیدا نشد: {origin}")
        return False

    if not select_city(page, destination, "فرودگاه مقصد", timeout=city_timeout):
        print(f"شهر مقصد در مستربلیط پیدا نشد: {destination}")
        return False

    if not select_departure_date(page, departure_date):
        print("انتخاب تاریخ در مستربلیط ناموفق بود")
        return False

    if not select_passengers(page, adults, children, infants):
        print("تنظیم تعداد مسافران در مستربلیط ناموفق بود")
        if REQUIRE_PASSENGERS:
            return False

    return True


def load_all_flights(page):
    """اسکرول تا انتهای صفحه برای بارگذاری همه‌ی پروازها (لود تنبل / بی‌نهایت).
    به‌جای کلاس خاصِ کارت (که روی مستربلیط معلوم نبود)، از شمارش خودِ قیمت‌ها استفاده می‌کنیم."""
    previous_count = 0
 
    while True:
        prices = page.get_by_text(
            re.compile(r"^\d{1,3}(?:,\d{3})+$"),
            exact=True,
        )
        current_count = prices.count()
 
        print("تعداد فعلی نتایج:", current_count)
 
        if current_count == previous_count:
            break
 
        previous_count = current_count
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1500)
 
 
def search_mrbilit(
    origin,
    destination,
    departure_date,
    adults,
    children,
    infants,
    sort_by=None,
    city_timeout=25000,
):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True,
                                    executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        page = browser.new_page()
        page.set_default_timeout(city_timeout)
 
        try:
            for attempt in range(1, FORM_ATTEMPTS + 1):
                try:
                    page.goto(
                        "https://mrbilit.com/plane-ticket",
                        wait_until="domcontentloaded",
                        timeout=90000,
                    )
                    wait_page_ready(page)
                except PlaywrightTimeoutError:
                    print(f"صفحه‌ی مستربلیط در تلاش {attempt} آماده نشد")
                    continue

                if fill_form(
                    page, origin, destination, departure_date,
                    adults, children, infants, city_timeout,
                ):
                    break
                print(f"پر کردن فرم در تلاش {attempt} ناموفق بود؛ صفحه رو دوباره باز می‌کنم")
            else:
                print("فرم مستربلیط بعد از چند تلاش پر نشد")
                return []
 
            page.get_by_role("button", name=re.compile("جستجو")).click()
            page.wait_for_timeout(5000)
            print("URL:", page.url)
 
            apply_sort(page, sort_by)
            load_all_flights(page)
 
            flights = []
 
            prices = page.get_by_text(
                re.compile(r"^\d{1,3}(?:,\d{3})+$"),
                exact=True,
            )
 
            print("تعداد قیمت:", prices.count())
 
            for i in range(prices.count()):
                try:
                    price = prices.nth(i)
 
                    card = price.locator("xpath=ancestor::div[4]")
 
                    lines = [
                        line.strip()
                        for line in card.inner_text().splitlines()
                        if line.strip()
                    ]
 
                    if not lines:
                        continue
 
                    airline = lines[0]
                    airline_info = AIRLINE_LOGOS.get(airline)
                    airline_logo = airline_info["logo"] if airline_info else None
 
                    time_pattern = re.compile(r"^\d{1,2}:\d{2}$")
                    times = [line for line in lines if time_pattern.match(line)]
 
                    departure_time = times[0] if len(times) > 0 else None
                    arrival_time = times[1] if len(times) > 1 else None
 
                    if departure_time is None or arrival_time is None:
                        continue
 
                    cabin_class = None
                    for line in lines:
                        if line in ["اکونومی", "بیزینس", "فرست"]:
                            cabin_class = line
                            break
 
                    aircraft = None
                    for line in lines:
                        if re.search(r"بوئینگ|ایرباس|ATR|فوکر", line):
                            aircraft = line
                            break
 
                    remaining_seats = None
                    for line in lines:
                        if "صندلی" in line:
                            remaining_seats = line
                            break
 
                    wheelchair_note = None
                    for line in lines:
                        if "ویلچر" in line:
                            wheelchair_note = line
                            break
 
                    flight_type = None
                    for line in lines:
                        if line in ("چارتری", "سیستمی"):
                            flight_type = line
                            break
 
                    price_text = price.inner_text().strip()
 
                    flight = {
                        "airline": airline,
                        "airline_logo": airline_logo,
                        "flight_type": flight_type,
                        "cabin_class": cabin_class,
                        "aircraft": aircraft,
                        "origin": origin,
                        "departure_time": departure_time,
                        "destination": destination,
                        "arrival_time": arrival_time,
                        "price": price_text,
                        "price_value": parse_price(price_text),
                        "remaining_seats": remaining_seats,
                        "wheelchair_note": wheelchair_note,
                        "source": "مستربلیط",
                        "source_url": build_mrbilit_url(
                            origin,
                            destination,
                            departure_date,
                            adults,
                            children,
                            infants,
                        ),
                    }
 
                    flights.append(flight)
 
                except Exception as e:
                    print("خطا در پردازش یک کارت مستربلیط:", e)
                    continue
 
            return flights
 
        except PlaywrightTimeoutError:
            print("زمان انتظار مستربلیط تمام شد")
            return []
 
        except Exception as e:
            print("خطا در جستجوی مستربلیط:", e)
            return []
 
        finally:
            if not page.is_closed():
                page.close()
            if browser.is_connected():
                browser.close()
 
 
if __name__ == "__main__":
    results = search_mrbilit(
        origin="تهران",
        destination="مشهد",
        departure_date="2026-10-08",
        adults=2,
        children=1,
        infants=0,
    )
 
    for flight in results:
        print("----------------")
        print(flight)