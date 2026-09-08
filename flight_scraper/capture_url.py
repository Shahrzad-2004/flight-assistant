"""
اسکریپت آزمایشی: فقط برای پیدا کردن الگوی URL علی‌بابا بعد از
پر کردن فرم (مبدأ، مقصد، تاریخ، تعداد مسافر) و زدن دکمه‌ی جستجو.

این فایل موقتی است و فقط برای بررسی و توسعه استفاده می‌شود؛
در جریان اصلی برنامه import یا استفاده نمی‌شود.

نحوه‌ی اجرا:
    python -m flight_scraper.capture_url
"""

from .alibaba import select_departure_date, select_passengers
from playwright.sync_api import sync_playwright
import re


def capture_search_url(
    origin="تهران",
    destination="مشهد",
    departure_date="2026-10-08",
    adults=2,
    children=1,
    infants=0
):

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://www.alibaba.ir")

        origin_input = page.get_by_role("textbox", name="مبدا (شهر)")
        origin_input.fill(origin)
        origin_option = page.locator("a").filter(
            has_text=re.compile(rf"^{re.escape(origin)}$")
        )
        origin_option.click()

        destination_input = page.get_by_role("textbox", name="مقصد (شهر)")
        destination_input.fill(destination)
        destination_option = page.locator("a").filter(
            has_text=re.compile(rf"^{re.escape(destination)}$")
        )
        destination_option.click()

        select_departure_date(page, departure_date)
        select_passengers(page, adults=adults, children=children, infants=infants)

        # همین‌جا (قبل از جستجو) هم آدرس را چاپ می‌کنیم چون ممکن است
        # علی‌بابا تاریخ/مسافر را در URL قبل از کلیک هم ثبت کند
        print("=" * 60)
        print("آدرس قبل از زدن دکمه‌ی جستجو:")
        print(page.url)

        search_button = page.get_by_role("button", name="جستجو")
        search_button.click()

        page.wait_for_timeout(4000)

        print("=" * 60)
        print("آدرس نهایی بعد از جستجو:")
        print(page.url)
        print("=" * 60)

        input("برای بستن مرورگر، اینتر را بزنید...")

        browser.close()


if __name__ == "__main__":
    capture_search_url()
