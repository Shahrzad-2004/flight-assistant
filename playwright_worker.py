import concurrent.futures
import os
import threading

_executor = None
_lock = threading.Lock()

# هر جستجو همیشه ۲ اسکرِیپر رو هم‌زمان صدا می‌زنه (alibaba + mrbilit یا
# نسخه‌های international شون). با max_workers=1 این دو تا سریالی اجرا
# می‌شدن؛ حداقل باید برابر تعداد اسکرِیپرهای هر جستجو باشه تا واقعاً موازی
# اجرا بشن. عدد رو کمی بزرگ‌تر گرفتیم تا چند جستجوی هم‌زمان از کاربرهای
# مختلف هم صف نشن. (هر worker یک پنجره‌ی Chrome باز می‌کنه، پس بی‌جهت
# زیادش نکن.) برای تغییر بدون دست‌بردن به کد: PLAYWRIGHT_MAX_WORKERS
MAX_WORKERS = int(os.environ.get("PLAYWRIGHT_MAX_WORKERS", 2))


def get_playwright_executor():
    global _executor
    if _executor is None:
        # در Streamlit چند session هم‌زمان می‌توانند اولین بار همین تابع را
        # صدا بزنند؛ بدون قفل ممکن بود دو executor (و ۲×MAX_WORKERS مرورگر) ساخته شود.
        with _lock:
            if _executor is None:
                _executor = concurrent.futures.ThreadPoolExecutor(
                    max_workers=MAX_WORKERS,
                    thread_name_prefix="playwright",
                )
    return _executor