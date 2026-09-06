from flight_scraper.scraper_manager import search_all_flights


results = search_all_flights(
    origin="تهران",
    destination="مشهد",
    departure_date="2026-10-08",
    adults=2,
    children=1,
    infants=0
)


for flight in results:
    print(flight)