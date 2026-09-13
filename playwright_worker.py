import concurrent.futures

_executor = None


def get_playwright_executor():
    global _executor
    if _executor is None:
        # فقط یک Worker Thread — همیشه همون یکی برای کل عمر برنامه
        _executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    return _executor