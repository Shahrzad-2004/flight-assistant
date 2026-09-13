import streamlit as st
from .alibaba import search_alibaba
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

    future = executor.submit(
        search_alibaba,
        origin,
        destination,
        departure_date,
        adults,
        children,
        infants,
        sort_by=sort_by
    )

    flights = future.result()
    return flights