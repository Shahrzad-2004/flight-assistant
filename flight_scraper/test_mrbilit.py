from mrbilit import search_mrbilit


result = search_mrbilit(
    origin="تهران",
    destination="مشهد",
    departure_date="2026-09-20",
    adults=1,
    children=1,
    infants=0
)


print("تعداد نتایج:", len(result))