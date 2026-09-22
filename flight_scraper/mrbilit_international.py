"""
اسکرپر بخش «پروازهای خارجی» مستربلیط (mrbilit.com/international-flights).

آنچه از تعامل واقعی ثبت‌شده (codegen) روی سایت مشخص است و در این فایل استفاده شده:
  - فیلد مبدأ/مقصد با placeholder های «فرودگاه مبدأ» / «فرودگاه مقصد» پیدا می‌شوند
  - هر گزینه‌ی دراپ‌داون یک div با متن «شهر + کد فرودگاه + کشور» است
    (مثلاً «تهرانIKAایران»)
  - فیلد تاریخ رفت: placeholder «رفت»
  - سلول هر روز در تقویم id دارد به‌شکل  سال-ماه(دو رقمی)-روز(بدون صفر اول)
    مثلاً id="1405-07-5" و id="1405-06-30"
    ⚠️ دقت کن: روز «بدون صفر ابتدایی» است (5 نه 05)، ولی ماه دو رقمی است.
  - متن «بزرگتر از ۱۲ سال» در پنل مسافران وجود دارد

⚠️ آنچه هنوز تأیید نشده و تخمینی است (سرور من به mrbilit.com دسترسی ندارد،
پس هیچ‌کدام از این بخش‌ها روی سایت واقعی تست نشده‌اند):
  - سلکتور دکمه‌ی «جستجو» در صفحه‌ی خارجی (فقط با نام/متن «جستجو» حدس زده شده)
  - نحوه‌ی باز شدن پنل مسافران و برچسب‌های کودک/نوزاد (فقط برچسب بزرگسال
    را از codegen داریم) و اینکه دکمه‌ی «+» کدام است
  - ساختار DOM صفحه‌ی نتایج: کارت‌ها با «لنگر قیمت» پیدا می‌شوند و متنشان
    خط‌به‌خط پارس می‌شود (مثل فایل داخلی مستربلیط ولی با تشخیص خودکار عمق کارت)
  - برچسب تب‌های مرتب‌سازی در صفحه‌ی خارجی (فعلاً از همان برچسب‌های داخلی)
  - دکمه‌ی ماه بعد در تقویم (فقط برای تاریخ‌هایی که در تقویم باز دیده نمی‌شوند)

برای اینکه تنظیمشان راحت باشد، DEBUG_PRINT_CARDS=True چند کارت اول را
خام چاپ می‌کند تا بشود الگوها را با متن واقعی تطبیق داد.
"""
from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import re
import time
from datetime import datetime
import jdatetime

MRBILIT_INTERNATIONAL_URL = "https://mrbilit.com/international-flights"

# اگر True باشد، متن خام چند کارت اول نتایج چاپ می‌شود (برای دیباگ الگوها)
DEBUG_PRINT_CARDS = True
DEBUG_CARDS_LIMIT = 3

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
AIRLINE_LOGOS = {
    "زاگرس": {
        "logo":"airlines/ZG.svg"
    },
    "ایران ایرتور": {
        "logo":"airlines/B9.svg"
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
}

# ⚠️ برچسب تب‌های مرتب‌سازی صفحه‌ی خارجی تأیید نشده؛ فعلاً همان برچسب‌های
# مستربلیط داخلی است. اگر پیدا نشد فقط پیام چاپ می‌شود و رد می‌شویم
# (مرتب‌سازی نهایی به‌هرحال در scraper_manager هم انجام می‌شود).
SORT_TAB_LABELS = {
    "cheapest": "کمترین قیمت",
    "earliest": "زود‌ترین زمان",
    "latest": "دیرترین زمان حرکت",
    "priciest": "گران‌ترین قیمت",
}

# فرودگاه ترجیحی برای شهرهایی که بیش از یک فرودگاه/کد در دراپ‌داون دارند.
# تهران در codegen با IKA (امام خمینی) انتخاب شده بود.
PREFERRED_AIRPORT_CODES = {
    "تهران": "IKA",
}

# برچسب ردیف‌های پنل مسافران. فقط برچسب بزرگسال از codegen مشخص است؛
# دو برچسب دیگر حدسی‌اند و باید با سایت چک شوند.
PASSENGER_LABELS = {
    "adult": "بزرگتر از ۱۲ سال",
    "child": "۲ تا ۱۲ سال",  # ⚠️ حدسی
    "infant": "کمتر از ۲ سال",  # ⚠️ حدسی
}

# قیمت: عدد با جداکننده‌ی هزارگان (انگلیسی/فارسی)، مثل 45,967,000
PRICE_RE = re.compile(r"(?<![\d:])\d{1,3}(?:[,٬،]\d{3})+(?![\d:])")
# برای get_by_text (کل متنِ عنصر باید قیمت باشد)
PRICE_ONLY_TEXT_RE = re.compile(
    r"^\s*[\d۰-۹٠-٩]{1,3}(?:[,٬،][\d۰-۹٠-٩]{3})+\s*(?:تومان)?\s*$"
)
# ساعت و کد فرودگاه ممکن است با متن دیگر در یک خط (inline) بیایند، مثل
# «19:05تهرانIKA»؛ پس به‌جای match کل خط، در کل متن جستجو می‌کنیم
TIME_RE = re.compile(r"(?<!\d)\d{1,2}:\d{2}(?!\d)")
AIRPORT_CODE_RE = re.compile(r"(?<![A-Za-z])[A-Z]{3}(?![A-Za-z])")
DURATION_RE = re.compile(r"\d+\s*ساعت(?:\s*و\s*\d+\s*دقیقه)?|\d+\s*دقیقه")
BAGGAGE_RE = re.compile(r"\d+\s*(?:KG|kg|Kg|کیلوگرم|کیلو)")
AIRCRAFT_RE = re.compile(r"بوئینگ|ایرباس|ATR|فوکر|Boeing|Airbus|Embraer", re.I)
CABIN_RE = re.compile(r"پریمیوم\s*اکونومی|اکونومی|بیزینس|فرست")
NO_RESULTS_RE = re.compile(r"یافت\s*نشد|موردی\s*پیدا\s*نشد|پروازی\s*وجود\s*ندارد")

# خطوطی که «نام ایرلاین» نیستند (برای تشخیص خط ایرلاین). علاوه بر کلمات
# مربوط به خود کارت پرواز، عبارات نوار مرتب‌سازی/هدر نتایج هم این‌جا اضافه
# شده‌اند: اگر به‌خاطر مرزبندی نادرستِ EXTRACT_CARDS_JS متن این نوار به یک
# کارت (معمولاً اولین کارت صفحه) بچسبد، نباید به‌جای اسم ایرلاین گرفته شود.
NON_AIRLINE_LINE_RE = re.compile(
    r"سیستمی|چارتری|اکونومی|بیزینس|فرست|تومان|ساعت|دقیقه|توقف|مستقیم|"
    r"صندلی|بار|KG|کیلو|جزئیات|انتخاب|ویلچر|قوانین|استرداد|بلیط|"
    r"مرتب‌سازی|مرتب سازی|بر اساس|ارزان‌ترین|زودترین|دیرترین|گران‌ترین|"
    r"پروازهای موجود|فیلتر|نتیجه|\d"
)

_DIGIT_TRANSLATION = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

# جاوااسکریپتی که «کارت‌ها» را از روی لنگر قیمت پیدا می‌کند. به‌جای ثابت
# گرفتن عمق والد (مثل ancestor::div[4] در فایل داخلی)، از قیمت شروع می‌کند و
# آن‌قدر بالا می‌رود تا والد بیش از یک قیمت (= کارت بعدی) را در خود جا بدهد؛
# سپس اگر هنوز دو ساعت (حرکت/رسیدن) داخلش نیست (مثلاً چون کارت قیمت خط‌خورده
# هم دارد) تا جایی که مجاز است بالاتر می‌رود.
EXTRACT_CARDS_JS = r"""
() => {
  const norm = (s) => s
    .replace(/[۰-۹]/g, d => String(d.charCodeAt(0) - 0x06F0))
    .replace(/[٠-٩]/g, d => String(d.charCodeAt(0) - 0x0660));
  const ownText = (el) => Array.from(el.childNodes)
    .filter(n => n.nodeType === 3)
    .map(n => n.textContent).join('').trim();
  const priceRe = /^\d{1,3}(?:[,٬،]\d{3})+(?:\s*تومان)?$/;
  const timeRe = /^\d{1,2}:\d{2}$/;
  const visible = (el) => el.getClientRects().length > 0;

  const all = Array.from(document.body.querySelectorAll('*'))
    .filter(el => !['SCRIPT', 'STYLE', 'NOSCRIPT'].includes(el.tagName));
  const priceEls = all.filter(el => visible(el) && priceRe.test(norm(ownText(el))));
  const timeEls = all.filter(el => visible(el) && timeRe.test(norm(ownText(el))));
  const countIn = (root, list) => list.filter(e => root.contains(e)).length;
  const isTop = (p) => !p || p === document.body || p === document.documentElement;

  const cards = new Set();
  for (const leaf of priceEls) {
    let node = leaf;
    for (let i = 0; i < 15; i++) {
      const p = node.parentElement;
      if (isTop(p)) break;
      if (countIn(p, priceEls) > 1) break;
      node = p;
    }
    for (let i = 0; i < 8 && countIn(node, timeEls) < 2; i++) {
      const p = node.parentElement;
      if (isTop(p)) break;
      if (countIn(p, priceEls) > 2) break;
      node = p;
    }
    if ((node.innerText || '').length <= 3000) cards.add(node);
  }
  return Array.from(cards).map(n => n.innerText);
}
"""


def convert_to_jalali(date_str):
    gregorian_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    return jdatetime.date.fromgregorian(date=gregorian_date)


def normalize_digits(text):
    """ارقام فارسی/عربی را به انگلیسی تبدیل می‌کند."""
    return text.translate(_DIGIT_TRANSLATION)


def parse_price(price_text):
    numbers = re.sub(r"[^\d]", "", normalize_digits(price_text))
    return int(numbers) if numbers else 0


# ---------------------------------------------------------------------------
# انتخاب مبدأ / مقصد
# ---------------------------------------------------------------------------


def _airport_option_locators(page, city, preferred_code=None):
    """لوکیتورهای ممکن برای گزینه‌ی دراپ‌داون یک شهر، به ترتیب اولویت.

    گزینه‌ها div هایی با متن «شهر + کد + کشور» هستند (مثلاً «تهرانIKAایران»).
    الگوی `[^A-Z]*` بعد از کد باعث می‌شود divهای والدی که چند گزینه
    (= چند کد فرودگاه) را با هم دارند match نشوند. `div:visible` هم
    گزینه‌های دراپ‌داون قبلی (مثلاً مبدأ) را که در DOM مانده ولی بسته‌اند
    کنار می‌گذارد — همان چیزی که در codegen باعث `.nth(2)` برای مقصد شده بود.
    """
    city_re = re.escape(city.strip())

    def option_re(code_pattern):
        return re.compile(rf"^\s*{city_re}\s*{code_pattern}\s*[^A-Z]*$")

    candidates = []

    if preferred_code:
        candidates.append(
            (
                f"{city} ({preferred_code})",
                page.locator("div:visible").filter(
                    has_text=option_re(re.escape(preferred_code))
                ),
            )
        )

    candidates.append(
        (
            f"{city} (هر کد فرودگاه)",
            page.locator("div:visible").filter(has_text=option_re(r"[A-Z]{3}")),
        )
    )

    # fallback شل‌تر: فقط متن دقیقِ نام شهر
    loose = page.get_by_text(re.compile(rf"^\s*{city_re}\s*$")).locator(
        "visible=true"
    )
    candidates.append((f"{city} (فقط نام)", loose))

    return candidates


def _click_first_available(candidates, page, timeout, loose_after=0.4):
    """تا timeout (میلی‌ثانیه) منتظر می‌ماند و روی اولین لوکیتور دارای نتیجه
    کلیک می‌کند. لوکیتور آخر (fallback شل) فقط بعد از loose_after از زمان
    کل بررسی می‌شود تا قبل از رسیدن گزینه‌ی دقیق، به یک متن نامرتبط کلیک نشود."""

    start = time.monotonic()
    deadline = start + timeout / 1000

    while time.monotonic() < deadline:
        elapsed_ratio = (time.monotonic() - start) / (timeout / 1000)

        for index, (name, locator) in enumerate(candidates):
            is_last = index == len(candidates) - 1
            if is_last and len(candidates) > 1 and elapsed_ratio < loose_after:
                continue

            try:
                if locator.count() > 0:
                    locator.first.click(timeout=3000)
                    return name
            except PlaywrightTimeoutError:
                continue

        page.wait_for_timeout(300)

    return None


def select_airport(page, city, placeholder, timeout=25000):
    """انتخاب فرودگاه مبدأ/مقصد: کلیک روی فیلد، تایپ نام شهر، کلیک روی گزینه."""

    field = page.get_by_placeholder(placeholder, exact=True)
    field.click(timeout=timeout)

    try:
        field.fill(city)
    except Exception:
        # اگر fill رویداد input را به‌درستی ایجاد نکرد، تایپ کاراکتر به کاراکتر
        field.press_sequentially(city, delay=80)

    candidates = _airport_option_locators(
        page, city, PREFERRED_AIRPORT_CODES.get(city.strip())
    )
    chosen = _click_first_available(candidates, page, timeout)

    if not chosen:
        print(f"گزینه‌ی فرودگاه در مستربلیط خارجی پیدا نشد: {city}")
        return False

    print(f"[{placeholder}] گزینه‌ی انتخاب‌شده: {chosen}")
    page.wait_for_timeout(500)
    return True


# ---------------------------------------------------------------------------
# تاریخ
# ---------------------------------------------------------------------------


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
    """باز کردن تقویم و انتخاب روز رفت با id سلول (مثل codegen).

    ⚠️ اگر ماه موردنظر هنوز در تقویم رندر نشده باشد، سعی می‌کنیم با دکمه‌ای
    که اسمش «ماه بعد/بعدی» است جلو برویم؛ این دکمه تأیید نشده."""

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

    return True


# ---------------------------------------------------------------------------
# مسافران
# ---------------------------------------------------------------------------


def _read_counter(row):
    """عدد شمارنده‌ی یک ردیف مسافر (المانِ برگی که فقط رقم دارد)؛ None اگر پیدا نشد."""
    counter = row.locator(
        "xpath=.//*[not(*)][normalize-space() and "
        "translate(normalize-space(), '0123456789۰۱۲۳۴۵۶۷۸۹', '')='']"
    )
    if counter.count() == 0:
        return None
    try:
        return int(normalize_digits(counter.first.inner_text().strip()))
    except ValueError:
        return None


def _increase_passenger(page, label, times):
    """روی ردیفی که برچسبش label است، «times» بار تعداد را زیاد می‌کند.

    ردیف = نزدیک‌ترین والدِ برچسب که دکمه دارد. چون نمی‌دانیم «+» اولین دکمه
    است یا دومی (RTL)، اولین کلیک را روی دکمه‌ی آخر می‌زنیم و از تغییر
    شمارنده می‌فهمیم درست بوده یا نه؛ اگر نه، دکمه‌ی اول را «+» می‌گیریم.
    """
    if times <= 0:
        return True

    label_el = page.get_by_text(label).locator("visible=true").first
    try:
        label_el.wait_for(state="visible", timeout=4000)
    except PlaywrightTimeoutError:
        print(f"برچسب مسافر «{label}» در پنل پیدا نشد")
        return False

    row = label_el.locator("xpath=ancestor::div[.//button][1]")
    buttons = row.get_by_role("button")

    if buttons.count() != 2:
        print(
            f"ردیف «{label}» {buttons.count()} دکمه دارد (انتظار ۲ تا) - "
            "نمی‌توانم «+» را مطمئن تشخیص دهم"
        )
        return False

    plus = buttons.last
    before = _read_counter(row)
    plus.click()
    after = _read_counter(row)

    if before is not None and after is not None and after <= before:
        # دکمه‌ی آخر «-» بوده؛ پس «+» دکمه‌ی اول است
        plus = buttons.first
        plus.click()

    for _ in range(times - 1):
        plus.click()

    return True


def select_passengers(page, adults, children, infants):
    """تنظیم تعداد مسافران. حالت پیش‌فرض (۱ بزرگسال) نیازی به کلیک ندارد.
    ⚠️ نحوه‌ی باز شدن پنل مسافران تأیید نشده؛ اگر برچسب بزرگسال دیده نشد
    سعی می‌کنیم روی فیلدی که «مسافر» در متن/placeholder دارد کلیک کنیم."""

    extra_adults = max(0, adults - 1)
    if extra_adults == 0 and children == 0 and infants == 0:
        return

    adult_label = page.get_by_text(PASSENGER_LABELS["adult"]).locator(
        "visible=true"
    )

    if adult_label.count() == 0:
        opener = page.get_by_placeholder(re.compile("مسافر"))
        if opener.count() == 0:
            opener = page.get_by_text(re.compile("مسافر")).locator("visible=true")
        if opener.count() > 0:
            opener.first.click()
            page.wait_for_timeout(500)

    _increase_passenger(page, PASSENGER_LABELS["adult"], extra_adults)
    _increase_passenger(page, PASSENGER_LABELS["child"], children)
    _increase_passenger(page, PASSENGER_LABELS["infant"], infants)


# ---------------------------------------------------------------------------
# جستجو، مرتب‌سازی، لود نتایج
# ---------------------------------------------------------------------------


def click_search(page, timeout=10000):
    """کلیک روی دکمه‌ی جستجو.
    ⚠️ سلکتور دقیق دکمه در صفحه‌ی خارجی تأیید نشده."""

    candidates = [
        (
            "دکمه‌ی جستجو",
            page.get_by_role("button", name=re.compile("جستجو")).locator(
                "visible=true"
            ),
        ),
        (
            "متن جستجو",
            page.get_by_text(re.compile(r"^\s*جستجو")).locator("visible=true"),
        ),
    ]

    chosen = _click_first_available(candidates, page, timeout, loose_after=0.5)
    if not chosen:
        print("دکمه‌ی جستجوی مستربلیط خارجی پیدا نشد")
        return False
    return True


def wait_for_results(page, timeout=60000):
    """منتظر می‌ماند تا یا قیمتی نمایش داده شود (True) یا پیام «پروازی یافت نشد»
    بیاید / زمان تمام شود (False)."""

    # ⚠️ count() روی get_by_text المان‌های مخفی را هم می‌شمارد؛ فقط
    # المان‌های قابل‌مشاهده را حساب می‌کنیم
    prices = page.get_by_text(PRICE_ONLY_TEXT_RE).locator("visible=true")
    no_results = page.get_by_text(NO_RESULTS_RE).locator("visible=true")
    deadline = time.monotonic() + timeout / 1000

    while time.monotonic() < deadline:
        if prices.count() > 0:
            return True

        if no_results.count() > 0:
            print("مستربلیط: پروازی برای این جستجو پیدا نشد")
            return False

        page.wait_for_timeout(500)

    print("مستربلیط: نتایج در زمان مجاز بارگذاری نشدند")
    return False


def apply_sort(page, sort_by):
    """کلیک روی تب/رادیوی مرتب‌سازی (اگر پیدا شد)."""

    if not sort_by:
        return

    label = SORT_TAB_LABELS.get(sort_by)
    if not label:
        return

    try:
        page.get_by_text(label, exact=True).first.click(timeout=5000)
        page.wait_for_timeout(1500)
    except PlaywrightTimeoutError:
        print(f"تب مرتب‌سازی «{label}» توی مستربلیط خارجی پیدا نشد - رد شدیم")


def load_all_flights(page, max_rounds=40):
    """اسکرول تا انتهای صفحه برای لود لیزی؛ تا وقتی تعداد قیمت‌ها ثابت شود."""

    previous_count = 0

    for _ in range(max_rounds):
        current_count = (
            page.get_by_text(PRICE_ONLY_TEXT_RE).locator("visible=true").count()
        )
        print("تعداد فعلی نتایج خارجی مستربلیط:", current_count)

        if current_count == previous_count:
            break

        previous_count = current_count
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1500)


# ---------------------------------------------------------------------------
# پارس کارت
# ---------------------------------------------------------------------------


def parse_card_text(card_text):
    """متن یک کارت را (خط‌به‌خط) به فیلدهای پرواز تبدیل می‌کند.
    اگر ساعت حرکت/رسیدن یا قیمت پیدا نشد None برمی‌گرداند."""

    text = normalize_digits(card_text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    if not lines:
        return None

    times = TIME_RE.findall(text)
    prices = [parse_price(m.group()) for m in PRICE_RE.finditer(text)]
    prices = [p for p in prices if p > 0]

    if len(times) < 2 or not prices:
        return None

    # ممکن است کارت قیمت اصلی و تخفیف‌خورده را با هم داشته باشد؛ کمتر را می‌گیریم
    price_value = min(prices)

    flight_type_index = next(
        (i for i, l in enumerate(lines) if l in ("سیستمی", "چارتری")), None
    )

    airline = None
    if flight_type_index is not None:
        # نام ایرلاین همیشه بلافاصله قبل از خط نوع پرواز (سیستمی/چارتری)
        # می‌آید؛ این لنگر خیلی مطمئن‌تر از «اولین خط مجاز در کل متن کارت»
        # است، چون اگر متنِ نامرتبطی (مثل هدر/نوار مرتب‌سازی) به ابتدای
        # کارت چسبیده باشد، جست‌وجوی سراسری ممکن است همان را به‌جای
        # ایرلاین بگیرد؛ جست‌وجوی رو به عقب از این لنگر چنین ریسکی ندارد.
        for line in reversed(lines[:flight_type_index]):
            if not NON_AIRLINE_LINE_RE.search(line) and re.search(
                r"[A-Za-z\u0600-\u06FF]", line
            ):
                airline = line
                break

    if airline is None:
        # Fallback: وقتی «سیستمی/چارتری» پیدا نشد (یا لنگر بی‌نتیجه بود)،
        # همان روش قبلی (اولین خط مجاز در کل متن) را امتحان کن.
        for line in lines:
            if not NON_AIRLINE_LINE_RE.search(line) and re.search(
                r"[A-Za-z\u0600-\u06FF]", line
            ):
                airline = line
                break

    airline_logo = None
    if airline:
        for name, logo in AIRLINE_LOGOS.items():
            if name in airline:
                airline_logo = logo["logo"]
                break

    # مدل هواپیما (مثل ATR) را قبل از جستجوی کد فرودگاه حذف می‌کنیم
    codes = AIRPORT_CODE_RE.findall(AIRCRAFT_RE.sub(" ", text))

    def first_match(pattern):
        for line in lines:
            m = pattern.search(line)
            if m:
                return m.group().strip()
        return None

    def first_line_with(keyword):
        for line in lines:
            if keyword in line:
                return line
        return None

    flight_type = lines[flight_type_index] if flight_type_index is not None else None

    seats_line = first_line_with("صندلی")
    seats_match = re.search(r"\d+", seats_line) if seats_line else None

    stops = None
    for line in lines:
        if re.search(r"بدون\s*توقف|مستقیم", line):
            stops = "بدون توقف"
            break
        if "توقف" in line:
            stops = line
            break

    return {
        "airline": airline or "نامشخص",
        "airline_logo": airline_logo,
        "flight_type": flight_type or "نامشخص",
        "cabin_class": first_match(CABIN_RE) or "نامشخص",
        "aircraft": first_match(AIRCRAFT_RE) or "نامشخص",
        "wheelchair_note": first_line_with("ویلچر"),
        "origin_code": codes[0] if len(codes) > 0 else None,
        "destination_code": codes[1] if len(codes) > 1 else None,
        "departure_time": times[0],
        "arrival_time": times[1],
        "duration": first_match(DURATION_RE) or "نامشخص",
        "baggage": first_match(BAGGAGE_RE) or "نامشخص",
        "stops": stops or "نامشخص",
        "remaining_seats": seats_match.group() if seats_match else "نامشخص",
        "price_value": price_value,
        "price": f"{price_value:,} تومان",
    }


# ---------------------------------------------------------------------------
# تابع اصلی
# ---------------------------------------------------------------------------


def search_mrbilit_international(
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
        browser = p.chromium.launch(
            headless=False,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        )
        page = browser.new_page()
        page.set_default_timeout(city_timeout)

        try:
            page.goto(
                MRBILIT_INTERNATIONAL_URL,
                wait_until="domcontentloaded",
                timeout=90000,
            )

            if not select_airport(page, origin, "فرودگاه مبدأ", timeout=city_timeout):
                print(f"مبدا در مستربلیط خارجی پیدا نشد: {origin}")
                return []

            if not select_airport(
                page, destination, "فرودگاه مقصد", timeout=city_timeout
            ):
                print(f"مقصد در مستربلیط خارجی پیدا نشد: {destination}")
                return []

            if not select_departure_date(page, departure_date):
                return []

            select_passengers(
                page, adults=adults, children=children, infants=infants
            )

            if not click_search(page):
                return []

            if not wait_for_results(page):
                return []

            print("URL نتایج:", page.url)
            results_url = page.url

            apply_sort(page, sort_by)
            load_all_flights(page)

            card_texts = page.evaluate(EXTRACT_CARDS_JS)
            print("تعداد کارت‌های شناسایی‌شده:", len(card_texts))

            if DEBUG_PRINT_CARDS:
                for i, sample in enumerate(card_texts[:DEBUG_CARDS_LIMIT]):
                    print(f"--- نمونه‌ی خام کارت {i} ---")
                    print(repr(sample))

            flights = []
            seen = set()
            rejected_printed = 0

            for card_text in card_texts:
                try:
                    info = parse_card_text(card_text)

                    if info is None:
                        if rejected_printed < 3:
                            print(
                                "کارتی با الگوی مورد انتظار (۲ ساعت + قیمت) جور نشد:",
                                repr(card_text[:300]),
                            )
                            rejected_printed += 1
                        continue

                    # جلوگیری از تکرار (یک کارت از دو لنگر قیمت پیدا شده باشد)
                    key = (
                        info["airline"],
                        info["departure_time"],
                        info["arrival_time"],
                        info["price_value"],
                    )
                    if key in seen:
                        continue
                    seen.add(key)

                    flights.append(
                        {
                            "airline": info["airline"],
                            "airline_logo": info["airline_logo"],
                            "flight_type": info["flight_type"],
                            "cabin_class": info["cabin_class"],
                            "aircraft": info["aircraft"],
                            "wheelchair_note": info["wheelchair_note"],
                            "origin": origin,
                            "origin_code": info["origin_code"],
                            "departure_time": info["departure_time"],
                            "destination": destination,
                            "destination_code": info["destination_code"],
                            "arrival_time": info["arrival_time"],
                            "duration": info["duration"],
                            "baggage": info["baggage"],
                            "stops": info["stops"],
                            "remaining_seats": info["remaining_seats"],
                            "price": info["price"],
                            "price_value": info["price_value"],
                            "source": "مستربلیط (خارجی)",
                            "source_url": results_url
                            or MRBILIT_INTERNATIONAL_URL,
                        }
                    )

                except Exception as e:
                    print("خطا در پردازش یک کارت مستربلیط خارجی:", e)
                    continue

            return flights

        except PlaywrightTimeoutError:
            print("زمان انتظار مستربلیط (خارجی) تمام شد")
            return []

        except Exception as e:
            print("خطا در جستجوی مستربلیط (خارجی):", e)
            return []

        finally:
            if not page.is_closed():
                page.close()
            if browser.is_connected():
                browser.close()


if __name__ == "__main__":
    results = search_mrbilit_international(
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