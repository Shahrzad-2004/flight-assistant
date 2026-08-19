"""
مدل‌های پای دنتیک برای ساختار اطلاعات پرواز.
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field


class FlightRequest(BaseModel):
    is_flight_request: bool = Field(
        description="آیا درخواست کاربر مربوط به جستجوی پرواز است؟"
    )

    origin: Optional[str] = Field(
        default=None,
        description="شهر یا فرودگاه مبدأ"
    )

    destination: Optional[str] = Field(
        default=None,
        description="شهر یا فرودگاه مقصد"
    )

    departure_date_raw: Optional[str] = Field(
        default=None,
        description="تاریخ رفت دقیقاً همان‌ طور که کاربر بیان کرده است"
    )

    departure_date: Optional[str] = Field(
        default=None,
        description="تاریخ رفت به فرمت YYYY-MM-DD"
    )

    return_date: Optional[str] = Field(
        default=None,
        description="تاریخ برگشت به فرمت YYYY-MM-DD"
    )

    trip_type: Optional[Literal["one_way", "round_trip"]] = Field(
        default=None,
        description="نوع سفر: یک‌ طرفه یا رفت‌ و برگشت"
    )

    adults: Optional[int] = Field(
        default=None,
        ge=1,
        description="تعداد مسافران بزرگسال"
    )

    children: Optional[int] = Field(
        default=None,
        ge=0,
        description="تعداد کودکان"
    )

    infants: Optional[int] = Field(
        default=None,
        ge=0,
        description="تعداد نوزادان"
    )
    passenger_count_provided: bool = Field(
        default=False,
        description=(
            "آیا کاربر تعداد مسافران را در درخواست خود "
            "به‌صورت واضح مشخص کرده است؟"
        )
    )
    cabin_class: Optional[
        Literal[
            "economy",
            "business",
            "first",
            "unspecified"
        ]
    ] = Field(
        default=None,
        description=(
            "کلاس پروازی کاربر؛ اگر کاربر کلاس را مشخص نکرده "
            "مقدار null و اگر گفت اهمیت ندارد unspecified باشد"
        )
    )

    max_price_toman: Optional[int] = Field(
        default=None,
        description="حداکثر بودجه کاربر به تومان"
    )

    preferred_airline: Optional[str] = Field(
        default=None,
        description="شرکت هواپیمایی موردنظر کاربر"
    )

    preferred_departure_time: Optional[
        Literal["morning", "afternoon", "evening", "night"]
    ] = Field(
        default=None,
        description="زمان ترجیحی حرکت"
    )

    direct_only: Optional[bool] = Field(
        default=None,
        description="آیا کاربر فقط پرواز مستقیم می‌خواهد؟"
    )

    sort_by: Optional[
        Literal["cheapest", "earliest", "shortest", "best"]
    ] = Field(
        default=None,
        description="معیار اصلی انتخاب پرواز"
    )
