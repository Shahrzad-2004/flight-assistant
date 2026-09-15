from concurrent.futures import ThreadPoolExecutor, as_completed
 
from .alibaba import search_alibaba
from .mrbilit import search_mrbilit
from playwright_worker import get_playwright_executor
 
 
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