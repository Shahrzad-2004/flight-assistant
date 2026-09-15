from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import re


def parse_price(price_text):
    numbers = re.sub(r"[^\d]", "", price_text)
    return int(numbers) if numbers else 0


def search_mrbilit(
    origin,
    destination,
    departure_date,
    adults,
    children,
    infants,
    sort_by=None
):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            page.goto(
                "https://mrbilit.com/plane-ticket",
                wait_until="domcontentloaded",
                timeout=60000
            )

            # انتخاب مبدأ
            page.get_by_placeholder(
                "فرودگاه مبدأ",
                exact=True
            ).click()

            page.get_by_text(
                origin,
                exact=True
            ).first.click()


            # انتخاب مقصد
            page.get_by_placeholder(
                "فرودگاه مقصد",
                exact=True
            ).click()

            page.get_by_text(
                destination,
                exact=True
            ).nth(1).click()

            page.get_by_placeholder("رفت").first.click()
            page.locator("[id=\"1405-06-30\"]").get_by_text("30").click()

            # انتخاب تاریخ و مسافران را مطابق ساختار واقعی سایت اضافه کن

            page.get_by_role("button", name=re.compile("جستجو")).click()
            page.wait_for_timeout(5000)
            print("URL:", page.url)



            flights = []

            prices = page.get_by_text(
                re.compile(r"^\d{1,3}(?:,\d{3})+$"),
                exact=True
            )

            print("تعداد قیمت:", prices.count())


            for i in range(prices.count()):

                price = prices.nth(i)

                card = price.locator(
                    "xpath=ancestor::div[4]"
                )

                lines = [
                    line.strip()
                    for line in card.inner_text().splitlines()
                    if line.strip()
                ]

                airline = lines[0]

                time_pattern = re.compile(r"^\d{1,2}:\d{2}$")

                times = [
                    line for line in lines
                    if time_pattern.match(line)
                ]

                departure_time = times[0] if len(times) > 0 else None
                arrival_time = times[1] if len(times) > 1 else None


                cabin_class = None
                for line in lines:
                    if line in ["اکونومی", "بیزینس", "فرست"]:
                        cabin_class = line
                        break


                aircraft = None
                for line in lines:
                    if re.search(
                        r"بوئینگ|ایرباس|ATR|فوکر",
                        line
                    ):
                        aircraft = line
                        break


                remaining_seats = None
                for line in lines:
                    if "صندلی" in line:
                        remaining_seats = line
                        break


                price_text = price.inner_text().strip()

                flight = {
                    "airline": airline,
                    "airline_logo": None,
                    "flight_type": None,
                    "cabin_class": cabin_class,
                    "aircraft": aircraft,
                    "origin": origin,
                    "departure_time": departure_time,
                    "destination": destination,
                    "arrival_time": arrival_time,
                    "price": price_text,
                    "price_value": int(
                        re.sub(
                            r"[^\d]",
                            "",
                            price_text
                        )
                    ),
                    "remaining_seats": remaining_seats,
                    "wheelchair_note": None,
                    "source": "مستربلیط",
                    "source_url": page.url
                }

                flights.append(flight)
            return flights


        except PlaywrightTimeoutError:
            print("زمان انتظار مستربلیط تمام شد")
            return []


        except Exception as e:
            print("خطا در جستجوی مستربلیط:", e)
            return []


        finally:
            browser.close()
