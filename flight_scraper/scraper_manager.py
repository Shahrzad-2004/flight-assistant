import time
from concurrent.futures import as_completed
from concurrent.futures import TimeoutError as FuturesTimeoutError

# حداکثر زمانی که منتظر می‌مونیم بدون هیچ هشداری. بعضی از منابع
# (مخصوصاً نسخه‌ی خارجی مستربلیط که چندین مرحله‌ی فرم/کلیک/صبر داره و
# روی مرورگر واقعی هم اجرا می‌شه) معمولاً بیشتر از این طول می‌کشن؛ برای
# همین یک SEARCH_GRACE_SECONDS هم داریم که به‌جای cancel کردن بی‌فایده‌ی
# تسک‌های درحال‌اجرا (که اصلاً واقعاً متوقفشون نمی‌کنه)، صبر می‌کنیم تا
# نتیجه‌شون - اگه نزدیکه - از دست نره.
SEARCH_TIMEOUT_SECONDS = 30
# مهلت اضافه بعد از SEARCH_TIMEOUT_SECONDS. مجموع این دو، سقف کل انتظاره.
SEARCH_GRACE_SECONDS = 30

# اگر True باشد، تک‌تک پروازهای برگشتی هر منبع چاپ می‌شود (برای دیباگ)
DEBUG_PRINT_FLIGHTS = False

from .alibaba import search_alibaba, IATA_CODES as DOMESTIC_IATA_CODES
from .mrbilit import search_mrbilit
from .mrbilit_international import search_mrbilit_international
from .alibaba_international import (
    search_alibaba_international,
    INTERNATIONAL_IATA_CODES,
)
from playwright_worker import get_playwright_executor

# (نام منبع، تابع اسکرپر). نام‌ها با فیلد "source" خروجی هر اسکرپر یکی است.
DOMESTIC_SOURCES = (
    ("علی‌بابا", search_alibaba),
    ("مستربلیط", search_mrbilit),
)
INTERNATIONAL_SOURCES = (
    ("علی‌بابا (خارجی)", search_alibaba_international),
    ("مستربلیط (خارجی)", search_mrbilit_international),
)


def is_international_route(origin, destination):
    """اگر مقصد (یا مبدأ) جزو مقصدهای خارجی باشد و در فهرست شهرهای صرفاً
    داخلی نباشد، مسیر را خارجی در نظر می‌گیریم."""
    origin_domestic = origin in DOMESTIC_IATA_CODES
    destination_domestic = destination in DOMESTIC_IATA_CODES

    if origin_domestic and destination_domestic:
        return False

    origin_known = origin in INTERNATIONAL_IATA_CODES or origin_domestic
    destination_known = (
        destination in INTERNATIONAL_IATA_CODES or destination_domestic
    )

    return origin_known and destination_known


def search_all_flights_detailed(
    origin,
    destination,
    departure_date,
    adults,
    children,
    infants,
    sort_by=None,
):
    """هر دو منبع را هم‌زمان (روی executor مرورگر) اجرا می‌کند.

    خروجی: {"flights": [...], "status": {نام منبع: {...}}}
    status برای هر منبع یکی از این حالت‌هاست: ok / empty / error / timeout
    (به‌همراه تعداد نتایج، مدت اجرا و در صورت خطا متن خطا) تا رابط کاربری
    بتواند مثلاً بگوید «مستربلیط جواب نداد» به‌جای اینکه بی‌صدا فقط نتایج
    یک سایت را نشان بدهد.
    """
    executor = get_playwright_executor()
    sources = (
        INTERNATIONAL_SOURCES
        if is_international_route(origin, destination)
        else DOMESTIC_SOURCES
    )

    started = time.monotonic()
    futures = {
        executor.submit(
            fn,
            origin,
            destination,
            departure_date,
            adults,
            children,
            infants,
            sort_by=sort_by,
        ): name
        for name, fn in sources
    }

    flights = []
    status = {}

    # نتیجه‌ها همان لحظه‌ای که آماده می‌شوند جمع می‌شوند (نه بعد از اتمام
    # همه)، و سقف کل انتظار TIMEOUT + GRACE است.
    try:
        for task in as_completed(
            futures, timeout=SEARCH_TIMEOUT_SECONDS + SEARCH_GRACE_SECONDS
        ):
            name = futures[task]
            elapsed = round(time.monotonic() - started, 1)
            try:
                result = task.result() or []
            except Exception as e:
                print(f"خطا در {name}:", e)
                status[name] = {
                    "state": "error",
                    "count": 0,
                    "seconds": elapsed,
                    "error": str(e),
                }
                continue

            print(f"{name}: {len(result)} نتیجه در {elapsed} ثانیه")
            if DEBUG_PRINT_FLIGHTS:
                for f in result:
                    print(
                        "  ->",
                        f.get("source"),
                        f.get("airline"),
                        f.get("departure_time"),
                        f.get("price"),
                    )
            flights.extend(result)
            status[name] = {
                "state": "ok" if result else "empty",
                "count": len(result),
                "seconds": elapsed,
            }
    except FuturesTimeoutError:
        pass

    for task, name in futures.items():
        if name not in status:
            # cancel فقط روی تسکی که هنوز شروع نشده اثر دارد؛ تسک درحال‌اجرا
            # تا پایان کارش (یا تایم‌اوت داخلی Playwright) ادامه می‌دهد.
            task.cancel()
            print(f"هشدار: {name} تا سقف مجاز جواب نداد؛ ادامه با نتایج موجود.")
            status[name] = {
                "state": "timeout",
                "count": 0,
                "seconds": round(time.monotonic() - started, 1),
            }

    return {"flights": _apply_sort(flights, sort_by), "status": status}


def search_all_flights(
    origin,
    destination,
    departure_date,
    adults,
    children,
    infants,
    sort_by=None,
):
    """نسخه‌ی سازگار با قبل: فقط لیست پروازها را برمی‌گرداند."""
    return search_all_flights_detailed(
        origin,
        destination,
        departure_date,
        adults,
        children,
        infants,
        sort_by=sort_by,
    )["flights"]


def _time_key(flight, default):
    """ساعت حرکت را برای مقایسه‌ی رشته‌ای هم‌طول می‌کند: «9:05» باید قبل از
    «19:05» بیاید، ولی به‌صورت رشته‌ی خام «9:05» > «19:05» می‌شد."""
    value = flight.get("departure_time")
    return value.zfill(5) if isinstance(value, str) and value else default


def _apply_sort(flights, sort_by):
    if sort_by in ("cheapest", "priciest"):
        return _sort_by_price(flights, reverse=(sort_by == "priciest"))

    if sort_by == "earliest":
        return sorted(flights, key=lambda x: _time_key(x, "99:99"))

    if sort_by == "latest":
        return sorted(flights, key=lambda x: _time_key(x, "00:00"), reverse=True)

    return flights


def _has_valid_price(flight):
    """True فقط وقتی price_value یک عدد واقعی (int/float) باشد.

    قبلاً از x.get("price_value", 0) مستقیم استفاده می‌شد که دو مشکل داشت:
    ۱) اگر price_value صراحتاً None بود (نه غایب)، .get() مقدار پیش‌فرض
       را برنمی‌گرداند و مقایسه‌ی None با int در flights.sort() با
       TypeError کرش می‌کرد.
    ۲) اگر price_value اصلاً وجود نداشت، صفر در نظر گرفته می‌شد و آن
       پرواز به‌اشتباه به‌عنوان «ارزان‌ترین» (قیمت صفر تومان) در صدر
       پیشنهاد به کاربر نمایش داده می‌شد.
    """
    value = flight.get("price_value")
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _sort_by_price(flights, reverse=False):
    """پروازهای دارای قیمت معتبر را طبق قیمت مرتب می‌کند و پروازهای بدون
    قیمت معتبر (None یا غایب) را همیشه ته لیست می‌گذارد - چه برای
    ارزان‌ترین چه برای گران‌ترین - تا هرگز به‌اشتباه به‌عنوان بهترین
    گزینه به کاربر پیشنهاد نشوند."""
    priced = [f for f in flights if _has_valid_price(f)]
    unpriced = [f for f in flights if not _has_valid_price(f)]
    priced.sort(key=lambda x: x["price_value"], reverse=reverse)
    return priced + unpriced