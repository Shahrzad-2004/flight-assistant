# -*- coding: utf-8 -*-
"""
نحوه‌ی اجرا:
    python evaluate_scenarios.py --scenarios scenarios_sample.json --out eval_results
"""


import argparse
import csv
import json
import time
from pathlib import Path

import flight_graph
from flight_graph import validate_cities
from flight_logic import extract_flight_request
from flight_scraper.scraper_manager import search_all_flights_detailed

# ---------------------------------------------------------------------------
# تنظیمات
# ---------------------------------------------------------------------------

THRESHOLDS = {
    "extraction": 0.85,
    "search": 0.80,
    "time_min": 30,
    "time_max": 60,
}

FIELDS_TO_CHECK = [
    "origin",
    "destination",
    "departure_date",
    "sort_by",
    "adults",
    "children",
    "infants",
    "cabin_class",
    "max_price_toman",
]

# ---------------------------------------------------------------------------
# ابزارهای کمکی
# ---------------------------------------------------------------------------

def load_scenarios(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def effective_value(extracted, field):
    """مقدار فیلد را همان‌طور که سامانه واقعاً استفاده می‌کند برمی‌گرداند.
    (merge_flight_state در برنامه، sort_by و cabin_class را که کاربر صراحتاً
    نگفته باشد null می‌کند.)"""
    value = getattr(extracted, field, None)
    if field == "sort_by" and getattr(extracted, "sort_by_provided", True) is False:
        return None
    if field == "cabin_class" and getattr(extracted, "cabin_class_provided", True) is False:
        return None
    if field in ("adults", "children", "infants") and \
            getattr(extracted, "passenger_count_provided", True) is False:
        return None
    return value


def serialize_extracted(extracted) -> str:
    """کل خروجی خام LLM (آبجکت extracted) را برای ذخیره در CSV به JSON تبدیل می‌کند."""
    if hasattr(extracted, "model_dump"):       # pydantic v2
        data = extracted.model_dump()
    elif hasattr(extracted, "dict"):           # pydantic v1
        data = extracted.dict()
    elif hasattr(extracted, "__dict__"):
        data = vars(extracted)
    else:
        data = {"raw": str(extracted)}
    return json.dumps(data, ensure_ascii=False, default=str)


# ---------------------------------------------------------------------------
# ۱) استخراج
# ---------------------------------------------------------------------------

def check_extraction(expected: dict, extracted) -> dict:
    """فقط فیلدهایی که در سناریو مقدار مشخص برایشان تعیین شده مقایسه می‌شوند."""
    results = {}
    for field in FIELDS_TO_CHECK:
        if field not in expected:
            continue
        results[field] = (expected[field] == effective_value(extracted, field))
    return results


# ---------------------------------------------------------------------------
# اجرای هر سناریو
# ---------------------------------------------------------------------------

def run_scenario(scenario: dict) -> dict:
    scenario_id = scenario["id"]
    user_message = scenario["user_message"]
    expected = scenario.get("expected", {})
    is_valid = scenario.get("valid_scenario", True)

    row = {
        "id": scenario_id,
        "category": scenario.get("category", ""),
        "user_message": user_message,
        "valid_scenario": is_valid,
        "extraction_correct_fields": 0,
        "extraction_total_fields": 0,
        "extraction_accuracy": "",
        "search_success": False,
        "scenario_completed": False,
        "flight_count": 0,
        "raw_flight_count": "",
        "filter_wipeout": "",
        "sources_ok": "",
        "sources_status": "",
        "recommendation_correct": "",  # ستون خالی؛ دستی پر می‌شود
        "expected_availability": scenario.get("expected_availability", ""),
        "evaluator_note": (
            "" if scenario.get("expected_availability")
            else "وضعیت واقعیِ وجود پرواز تأیید دستی نشده"
        ),
    }

    t0 = time.time()

    # --- مرحله ۱: استخراج (مثل سامانه) ---
    try:
        extracted = extract_flight_request(user_message, {})
    except Exception as e:
        row["extraction_error"] = str(e)
        row["response_time_sec"] = round(time.time() - t0, 2)
        return row

    field_results = check_extraction(expected, extracted)
    row["extraction_correct_fields"] = sum(1 for v in field_results.values() if v)
    row["extraction_total_fields"] = len(field_results)
    if field_results:
        row["extraction_accuracy"] = round(row["extraction_correct_fields"] / len(field_results), 3)
    row["field_details"] = json.dumps(field_results, ensure_ascii=False)
    row["llm_extraction_raw"] = serialize_extracted(extracted)

    # --- مرحله ۲: نرمال‌سازی و اعتبارسنجی شهرها (مثل نود validate_cities) ---
    state = {
        "origin": extracted.origin,
        "destination": extracted.destination,
        "departure_date": extracted.departure_date,
        "adults": effective_value(extracted, "adults") or 1,
        "children": effective_value(extracted, "children") or 0,
        "infants": effective_value(extracted, "infants") or 0,
        "sort_by": effective_value(extracted, "sort_by"),
        "cabin_class": effective_value(extracted, "cabin_class"),
        "max_price_toman": effective_value(extracted, "max_price_toman"),
    }
    try:
        state = validate_cities(state)
    except Exception as e:
        row["search_error"] = f"validate_cities: {e}"
        row["response_time_sec"] = round(time.time() - t0, 2)
        return row

    can_search = (
        is_valid
        and state.get("current_step") != "invalid_city"
        and state.get("origin")
        and state.get("destination")
        and state.get("departure_date")
        and not getattr(extracted, "date_error", None)
    )

    # --- مرحله ۳ و ۴: جست‌وجو و پیشنهاد (خودِ نود search_flights سامانه) ---
    if can_search:
        captured = {}
        original = flight_graph.search_all_flights

        def capturing_search(*args, **kwargs):
            # همان جست‌وجوی سامانه، ولی نتیجه‌ی خام و وضعیت منابع را هم نگه می‌داریم
            detailed = search_all_flights_detailed(*args, **kwargs)
            captured["raw"] = detailed["flights"]
            captured["status"] = detailed["status"]
            return detailed["flights"]

        flight_graph.search_all_flights = capturing_search
        try:
            result = flight_graph.search_flights(state)
            # سرچ یعنی خودِ عملیات جست‌وجو بدون خطا اجرا و از منابع پاسخ گرفته شد؛
            # ربطی به این‌که چند تا پرواز نهایتاً پیدا شده ندارد.
            row["search_success"] = True
        except Exception as e:
            row["search_error"] = str(e)
            result = None
            row["search_success"] = False
        finally:
            flight_graph.search_all_flights = original

        status = captured.get("status", {})
        if status:
            row["sources_ok"] = sum(1 for s in status.values() if s["state"] == "ok")
            row["sources_status"] = json.dumps(
                {k: v["state"] for k, v in status.items()}, ensure_ascii=False
            )

        if result is not None:
            recs = result.get("flights", [])
            raw = captured.get("raw", [])
            row["flight_count"] = len(recs)
            row["raw_flight_count"] = len(raw)
            # کارت‌های نهایی: همان چیزی که پس از اعمال معیارها (کلاس پرواز،
            # بودجه، مرتب‌سازی و ...) واقعاً به کاربر نمایش داده می‌شود.
            row["recommended_cards"] = json.dumps(recs, ensure_ascii=False)
            if len(raw) > 0 and len(recs) == 0:
                sample_prices = [f.get("price_value") for f in raw[:5]]
                row["filter_wipeout"] = (
                    f"⚠️ {len(raw)} پرواز خام پیدا شد ولی فیلتر کلاس‌پرواز/بودجه همه را حذف کرد. "
                    f"نمونه price_value ها: {sample_prices}"
                )

            expected_avail = row["expected_availability"]

            if expected_avail == "unavailable":
                # بررسی دستی تأیید کرده پروازی وجود ندارد؛ خالی‌بودن نتیجه
                # همان رفتار درست است، نه شکست. سناریو کامل محسوب می‌شود اگر
                # هم سرچ درست اجرا شده باشد و هم نتیجه با انتظار (خالی) یکی باشد.
                row["availability_match"] = "بله" if len(recs) == 0 else "خیر"
                row["scenario_completed"] = row["search_success"] and len(recs) == 0
            elif expected_avail == "available":
                row["availability_match"] = "بله" if len(recs) > 0 else "خیر"
                row["scenario_completed"] = row["search_success"] and len(recs) > 0
            else:
                # وضعیت واقعیِ وجود پرواز تأیید دستی نشده، پس نمی‌توان صفر بودن
                # نتیجه را «شکست» یا «موفقیت» دانست. معیار تکمیل سناریو در این
                # حالت فقط اجرای موفق و بدون خطای فرآیند سرچ است.
                row["scenario_completed"] = row["search_success"]

    # زمان کل: از ثبت درخواست تا آماده شدن پیشنهاد نهایی
    row["response_time_sec"] = round(time.time() - t0, 2)
    return row


# ---------------------------------------------------------------------------
# گزارش کارت‌های نهایی (پروازهای پیشنهادی پس از اعمال معیارها)
# ---------------------------------------------------------------------------

def write_cards_report(rows: list[dict], out_dir: Path) -> None:
    """برای هر سناریو، کارت‌های پروازی که در نهایت (پس از فیلتر/مرتب‌سازی طبق
    معیارهای سامانه) به کاربر نشان داده می‌شوند را در یک فایل خوانا می‌نویسد."""
    lines = ["# گزارش کارت‌های نهایی پروازها\n"]
    for r in rows:
        lines.append(f"## {r['id']} — {r['user_message']}")
        lines.append(f"- تعداد کارت نهایی: {r.get('flight_count', 0)} "
                      f"(از {r.get('raw_flight_count', '?')} پرواز خام)")

        cards_raw = r.get("recommended_cards", "")
        if not cards_raw:
            note = r.get("filter_wipeout") or r.get("search_error") or "بدون نتیجه"
            lines.append(f"- وضعیت: {note}\n")
            continue

        try:
            cards = json.loads(cards_raw)
        except (json.JSONDecodeError, TypeError):
            lines.append("- خطا در خواندن کارت‌ها\n")
            continue

        for i, card in enumerate(cards, start=1):
            lines.append(f"\n**کارت {i}:**")
            if isinstance(card, dict):
                for k, v in card.items():
                    lines.append(f"  - {k}: {v}")
            else:
                lines.append(f"  - {card}")
        lines.append("")

    report_path = out_dir / "cards_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # نسخه‌ی JSON خام هم برای پردازش برنامه‌ای
    cards_json_path = out_dir / "cards_report.json"
    with open(cards_json_path, "w", encoding="utf-8") as f:
        json.dump(
            [
                {
                    "id": r["id"],
                    "user_message": r["user_message"],
                    "cards": json.loads(r["recommended_cards"]) if r.get("recommended_cards") else [],
                }
                for r in rows
            ],
            f, ensure_ascii=False, indent=2,
        )


# ---------------------------------------------------------------------------
# محاسبه‌ی معیارها
# ---------------------------------------------------------------------------

def _verdict(ok: bool) -> str:
    return "✅ قبول" if ok else "❌ رد"


def compute_summary(rows: list[dict]) -> dict:
    valid_rows = [r for r in rows if r["valid_scenario"]]
    n_valid = len(valid_rows)

    # 1) دقت استخراج -- کل فیلدهای درست ÷ کل فیلدهای ارزیابی‌شده (طبق پروپزال)
    total_fields = sum(r["extraction_total_fields"] for r in rows)
    correct_fields = sum(r["extraction_correct_fields"] for r in rows)
    extraction_acc = correct_fields / total_fields if total_fields else 0.0
    per_scenario = [r["extraction_accuracy"] for r in rows if r["extraction_accuracy"] != ""]
    extraction_macro = sum(per_scenario) / len(per_scenario) if per_scenario else 0.0

    # 2) نرخ موفقیت جست‌وجو -- سناریوهای انجام‌شده ÷ سناریوهای معتبر
    completed = sum(1 for r in valid_rows if r["scenario_completed"])
    search_rate = completed / n_valid if n_valid else 0.0

    # 3) زمان پاسخ -- فقط سناریوهای معتبر
    valid_times = [r["response_time_sec"] for r in valid_rows if r.get("response_time_sec") is not None]
    avg_time = sum(valid_times) / len(valid_times) if valid_times else 0.0
    if avg_time > THRESHOLDS["time_max"]:
        time_verdict = "❌ خارج از بازه (کندتر از هدف)"
    elif avg_time < THRESHOLDS["time_min"]:
        time_verdict = "✅ قبول (سریع‌تر از بازه‌ی هدف)"
    else:
        time_verdict = "✅ قبول (داخل بازه‌ی هدف)"

    # اطلاعات تکمیلی: حداقل ۲ منبع پاسخ‌گو (طبق پروپزال)
    with_sources = [r for r in valid_rows if r["sources_ok"] != ""]
    two_sources = sum(1 for r in with_sources if r["sources_ok"] >= 2)

    confirmed = [r for r in valid_rows if r["expected_availability"] in ("available", "unavailable")]
    unconfirmed = n_valid - len(confirmed)

    return {
        "تعداد کل سناریوها": len(rows),
        "تعداد سناریوهای معتبر": n_valid,

        "۱) دقت استخراج اطلاعات": f"{extraction_acc:.1%}",
        "   حد پذیرش": f"{THRESHOLDS['extraction']:.0%}",
        "   نتیجه": _verdict(extraction_acc >= THRESHOLDS["extraction"]),
        "   (میانگین سناریو به سناریو، برای مقایسه)": f"{extraction_macro:.1%}",

        "۲) نرخ موفقیت جست‌وجو": f"{search_rate:.1%}",
        "   حد پذیرش ": f"{THRESHOLDS['search']:.0%}",
        "   نتیجه ": _verdict(search_rate >= THRESHOLDS["search"]),

        "۳) میانگین زمان پاسخ‌گویی (ثانیه)": round(avg_time, 1),
        "   بازه‌ی هدف": f"{THRESHOLDS['time_min']} تا {THRESHOLDS['time_max']} ثانیه",
        "   نتیجه  ": time_verdict,
    }


def main():
    parser = argparse.ArgumentParser(description="ارزیابی مبتنی بر سناریو برای دستیار هوشمند بلیط")
    parser.add_argument("--scenarios", default="scenarios_sample.json", help="مسیر فایل JSON سناریوها")
    parser.add_argument("--out", default="eval_results", help="پوشه‌ی خروجی نتایج")
    args = parser.parse_args()

    scenarios = load_scenarios(args.scenarios)
    rows = []
    for sc in scenarios:
        print(f"در حال اجرای سناریوی {sc['id']} — {sc['user_message']!r} ...")
        rows.append(run_scenario(sc))

    out_dir = Path(args.out)
    out_dir.mkdir(exist_ok=True)

    csv_path = out_dir / "results_detailed.csv"
    fieldnames = [
        "id", "category", "user_message", "valid_scenario",
        "extraction_accuracy", "extraction_correct_fields", "extraction_total_fields", "field_details",
        "llm_extraction_raw",
        "search_success", "scenario_completed", "filter_wipeout",
        "sources_ok", "sources_status",
        "recommendation_correct",
        "expected_availability",
        "response_time_sec",
        "recommended_cards",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    write_cards_report(rows, out_dir)

    summary = compute_summary(rows)

    print("\n=== خلاصه نتایج ===")
    for k, v in summary.items():
        if k != "_numeric":
            print(f"{k}: {v}")

    with open(out_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()