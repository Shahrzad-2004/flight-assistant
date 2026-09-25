from typing import Optional, Literal
from pydantic import BaseModel, Field


class FlightRequest(BaseModel):
    is_flight_request: bool = Field(
        description="آیا درخواست کاربر مربوط به جستجوی پرواز است؟"
    )

    origin: Optional[str] = Field(
        default=None,
        description="شهر مبدأ"
    )

    destination: Optional[str] = Field(
        default=None,
        description="شهر مقصد"
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

    adults: Optional[int] = Field(
        default=None,
        ge=0,
        description=(
            "تعداد مسافران بزرگسال؛ حتی اگر کاربر عدد نامعتبر (مثلاً ۰) "
            "گفته باشد همان عدد باید برگردد تا برنامه خودش با پیام "
            "مناسب از کاربر اصلاح آن را بخواهد."
        )
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
    cabin_class_provided: bool = Field(
        default=False,
        description=(
            "آیا کاربر در همین پیام صراحتاً به کلاس پرواز "
            "اشاره کرده است؟"
        )
    )

    max_price_toman: Optional[int] = Field(
        default=None,
        description="حداکثر بودجه کاربر به تومان"
    )

    sort_by: Optional[
        Literal["cheapest", "earliest", "latest", "priciest"]
    ] = Field(
        default=None,
        description="معیار اصلی انتخاب پرواز"
    )

    sort_by_provided: bool = Field(
        default=False,
        description=(
            "آیا کاربر در همین پیام صراحتاً معیار مرتب‌سازی پروازها "
            "(ارزان‌ترین، زودترین، دیرترین، گران‌ترین) را مشخص کرده است؟"
        )
    )
    route_error: Optional[str] = Field(
        default=None,
        description="خطای مربوط به اعتبارسنجی مسیر پرواز"
    )