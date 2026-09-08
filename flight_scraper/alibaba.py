from playwright.sync_api import sync_playwright
import re
from datetime import datetime
import jdatetime

# نگاشت نام فارسی شهرها به کد فرودگاه (IATA) برای ساخت لینک علی‌بابا
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


def build_alibaba_url(
    origin: str,
    destination: str,
    departure_date: str,
    adults: int,
    children: int,
    infants: int
) -> str:
    """آدرس صفحه‌ی جستجوی علی‌بابا (با تاریخ و تعداد مسافر پرشده) را می‌سازد."""
 
    origin_code = IATA_CODES.get(origin)
    destination_code = IATA_CODES.get(destination)
 
    # اگر کد فرودگاه شهر پیدا نشد، به صفحه‌ی اصلی جستجو برمی‌گردیم
    if not origin_code or not destination_code:
        return "https://www.alibaba.ir/"
 
    jalali_date = convert_to_jalali(departure_date)
    departing = (
        f"{jalali_date.year}-"
        f"{jalali_date.month:02d}-"
        f"{jalali_date.day:02d}"
    )
 
    return (
        f"https://www.alibaba.ir/flights/{origin_code}-{destination_code}"
        f"?adult={adults}&child={children}&infant={infants}"
        f"&departing={departing}"
    )

def convert_to_jalali(date_str):

    gregorian_date = datetime.strptime(
        date_str,
        "%Y-%m-%d"
    ).date()

    jalali_date = jdatetime.date.fromgregorian(
        date=gregorian_date
    )

    return jalali_date
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
    12: "اسفند"
}
def select_departure_date(page, date_str):

    jalali_date = convert_to_jalali(date_str)

    month_name = JALALI_MONTHS[jalali_date.month]
    day = jalali_date.day

    print("MONTH:", month_name)
    print("DAY:", day)

    date_input = page.get_by_role(
        "textbox",
        name="تاریخ رفت"
    )

    date_input.click()

    month_box = page.locator(
        "div.calendar.is-jalali"
    ).filter(
        has=page.get_by_role(
            "heading",
            name=month_name
        )
    )

    day_cell = month_box.locator(
        "span.calendar-cell"
    ).filter(
        has=page.locator(
            "span.tooltip"
        ).filter(
            has_text=re.compile(
                rf"^{day}\b"
            )
        )
    )

    day_cell.click()
    confirm_button = page.get_by_role("button", name="تایید") 
    confirm_button.click()

def select_passengers(page, adults, children, infants):

    passenger_input = page.get_by_role(
        "textbox",
        name="مسافران"
    )

    passenger_input.click()

    add_buttons = page.get_by_role(
        "button",
        name="افزودن"
    )

    adult_add = add_buttons.first
    child_add = add_buttons.nth(1)
    infant_add = add_buttons.nth(2)

    # علی‌بابا معمولاً از قبل 1 بزرگسال دارد
    for _ in range(adults - 1):
        adult_add.click()

    for _ in range(children):
        child_add.click()

    for _ in range(infants):
        infant_add.click()
def load_all_flights(page):

            previous_count = 0

            while True:

                cards = page.locator(".available-card")

                current_count = cards.count()

                print("تعداد فعلی کارت‌ها:", current_count)

                if current_count == previous_count:
                    break

                previous_count = current_count

                page.evaluate(
                    "window.scrollTo(0, document.body.scrollHeight)"
                )

                page.wait_for_timeout(1500)
def search_alibaba(
    origin,
    destination,
    departure_date,
    adults,
    children,
    infants):

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        page = browser.new_page()

        page.goto(
            "https://www.alibaba.ir"
        )

        origin_input = page.get_by_role(
            "textbox",
            name="مبدا (شهر)"
        )

        origin_input.fill(origin)


        origin_option = page.locator("a").filter(has_text=re.compile(
        rf"^{re.escape(origin)}$"))
        origin_option.click()


        destination_input = page.get_by_role(
            "textbox", name="مقصد (شهر)")
        
        destination_input.fill(destination)
        destination_option = page.locator("a").filter(has_text=re.compile(rf"^{re.escape(destination)}$"))
        destination_option.click()

        select_departure_date(
            page,
            departure_date
        )
        select_passengers(
            page,
            adults=adults,
            children=children,
            infants=infants
        )
        search_button = page.get_by_role(
            "button",
            name="جستجو"
        )

        search_button.click()

        
        page.wait_for_timeout(5000)

        price_boxes = page.locator("span").filter(
            has_text=re.compile(
                r"^\s*\d{1,3}(?:,\d{3})+\s*تومان\s*$"
            )
        )
        flights = []

        for i in range(price_boxes.count()):

            try:
                price = price_boxes.nth(i)

                card = price.locator(
                    "xpath=ancestor::div[contains(@class,'a-card')][1]"
                )

                lines = [
                    line.strip()
                    for line in card.inner_text().splitlines()
                    if line.strip()
                ]

                if not lines:
                    continue

                airline = lines[0]

                time_pattern = re.compile(r"^\d{1,2}:\d{2}$")
                times = [line for line in lines if time_pattern.match(line)]

                departure_time = times[0] if len(times) > 0 else None
                arrival_time = times[1] if len(times) > 1 else None

                if departure_time is None or arrival_time is None:
                    continue

                remaining_seats = None
                for line in lines:
                    if "صندلی باقی مانده" in line:
                        remaining_seats = line
                        break

                wheelchair_note = None
                for line in lines:
                    if "ویلچر" in line:
                        wheelchair_note = line
                        break

                aircraft = None
                for line in lines:
                    if re.search(r"boeing|airbus|فوکر|ATR|CRJ", line, re.IGNORECASE):
                        aircraft = line
                        break

                cabin_class = None
                for line in lines:
                    if any(
                        keyword in line
                        for keyword in ["اکونومی", "بیزینس", "فرست"]
                    ):
                        cabin_class = line
                        break

                flight_type = None
                for line in lines:
                    if line in ("چارتری", "سیستمی"):
                        flight_type = line
                        break

                flight = {
                    "airline": airline,
                    "flight_type": flight_type,
                    "cabin_class": cabin_class,
                    "aircraft": aircraft,
                    "origin": origin,
                    "departure_time": departure_time,
                    "destination": destination,
                    "arrival_time": arrival_time,
                    "price": price.inner_text().strip(),
                    "remaining_seats": remaining_seats,
                    "wheelchair_note": wheelchair_note,
                    "source": "علی‌بابا",
                    "source_url": build_alibaba_url(
                        origin,
                        destination,
                        departure_date,
                        adults,
                        children,
                        infants
                    )
                }

                flights.append(flight)

            except Exception as e:
                print("خطا در پردازش یک کارت پرواز، رد شد:", e)
                continue
        
        browser.close()
        return flights


if __name__ == "__main__":

    results = search_alibaba(
        origin="تهران",
        destination="مشهد",
        departure_date="2026-10-08",
        adults=2,
        children=1,
        infants=0
    )

    for flight in results:

        print("----------------")

        print(flight)