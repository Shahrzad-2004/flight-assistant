from .alibaba import search_alibaba


def search_all_flights(
    origin,
    destination,
    departure_date,
    adults,
    children,
    infants,
    sort_by=None
):

    results = []

    alibaba_results = search_alibaba(
        origin,
        destination,
        departure_date,
        adults,
        children,
        infants
    )

    results.extend(alibaba_results)

    return results