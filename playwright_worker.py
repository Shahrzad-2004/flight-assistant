import concurrent.futures

_executor = None

# هر جستجو همیشه ۲ اسکرِیپر رو هم‌زمان صدا می‌زنه (alibaba + mrbilit یا
# نسخه‌های international شون). با max_workers=1 این دو تا سریالی اجرا
# می‌شدن؛ حداقل باید برابر تعداد اسکرِیپرهای هر جستجو باشه تا واقعاً موازی
# اجرا بشن. عدد رو کمی بزرگ‌تر گرفتیم تا چند جستجوی هم‌زمان از کاربرهای
# مختلف هم صف نشن.
MAX_WORKERS = 4


def get_playwright_executor():
    global _executor
    if _executor is None:
        _executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=MAX_WORKERS
        )
    return _executor