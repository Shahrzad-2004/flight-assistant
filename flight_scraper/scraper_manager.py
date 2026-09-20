from concurrent.futures import ThreadPoolExecutor, as_completed
 
from .alibaba import search_alibaba, IATA_CODES as DOMESTIC_IATA_CODES
from .mrbilit import search_mrbilit
from .mrbilit_international import search_mrbilit_international
from .alibaba_international import (
    search_alibaba_international,
    INTERNATIONAL_IATA_CODES,
)
from playwright_worker import get_playwright_executor
 
 
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
 
 
def search_all_flights(
    origin,
    destination,
    departure_date,
    adults,
    children,
    infants,
    sort_by=None
):
    executor = get_playwright_executor()
 
    if is_international_route(origin, destination):
        tasks = [
            executor.submit(
                search_alibaba_international,
                origin,
                destination,
                departure_date,
                adults,
                children,
                infants,
                sort_by=sort_by
            ),
            executor.submit(
                search_mrbilit_international,
                origin,
                destination,
                departure_date,
                adults,
                children,
                infants,
                sort_by=sort_by
            )
        ]
    else:
        tasks = [
            executor.submit(
                search_alibaba,
                origin,
                destination,
                departure_date,
                adults,
                children,
                infants,
                sort_by=sort_by
            ),
            executor.submit(
                search_mrbilit,
                origin,
                destination,
                departure_date,
                adults,
                children,
                infants,
                sort_by=sort_by
            )
        ]
 
    flights = []
 
    for task in as_completed(tasks):
        try:
            result = task.result()
            print("نتیجه‌ی یک منبع - تعداد:", len(result) if result else 0)
            if result:
                for f in result:
                    print("  ->", f.get("source"), f.get("airline"), f.get("departure_time"), f.get("price"))
                flights.extend(result)
        except Exception as e:
            print("خطا در یکی از سایت‌ها:", e)
 
    if sort_by == "cheapest":
        flights.sort(key=lambda x: x.get("price_value", 0))
 
    elif sort_by == "earliest":
        flights.sort(key=lambda x: x.get("departure_time") or "99:99")
 
    elif sort_by == "latest":
        flights.sort(
            key=lambda x: x.get("departure_time") or "00:00",
            reverse=True
        )
 
    elif sort_by == "priciest":
        flights.sort(
            key=lambda x: x.get("price_value", 0),
            reverse=True
        )
 
    return flights