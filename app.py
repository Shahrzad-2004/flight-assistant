import base64
import uuid
from pathlib import Path

import streamlit as st
from datetime import datetime
import jdatetime
from chat_database import create_tables, save_message,list_sessions
from authentication import handle_google_callback, get_google_auth_url
from user_database import create_users_table,get_user_by_id
from cookie_manager import cookies
from flight_graph import detect_cabin_key


from styles import (
    inject_background_style,
    inject_main_style,
    inject_cabin_and_passenger_style,
    inject_confirmation_style,
    inject_sidebar_style,
    render_header,
    inject_login_style,
    inject_auth_style,
    inject_user_box_style,
    inject_flight_ticket,
    inject_delete_popup_position,
    inject_hero_typing,
    inject_cabin_filter_panel_style,
    inject_search_loader
  


)
from ui_handlers import (
    scroll_to_bottom,
    sort_flights_locally,
    select_passenger_option,
    save_passenger_counts,
    confirm_flight,
    edit_flight,
    start_new_conversation,
    switch_session,
    remove_session,
    delete_session_dialog,
    toggle_sidebar,
    render_sidebar_main_view,
    render_sidebar_archive_view,
    logout_user,      

)
from chat_response import handle_user_prompt
@st.cache_resource
def initialize_database():
    create_users_table()
    create_tables()

initialize_database()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True
# تنظیمات صفحه
st.set_page_config(
    page_title="دستیار هوشمند بلیط",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# خواندن عکس
BASE_DIR = Path(__file__).parent

@st.cache_data
def get_base64(file_name):
    path = BASE_DIR / file_name
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def get_plane_image():

    path = Path("plane.jpg")

    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    return f"data:image/jpeg;base64,{encoded}"

def get_airline_logo_base64(logo_path):
    if not logo_path:
        return ""
    path = BASE_DIR / logo_path
    if not path.exists():
        return ""
    mime = "image/svg+xml" if path.suffix.lower() == ".svg" else "image/png"
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{encoded}"

def to_jalali(date_str):

    if not date_str:
        return "-"

    try:
        gregorian_date = datetime.strptime(
            str(date_str),"%Y-%m-%d").date()

        jalali_date = jdatetime.date.fromgregorian(
            date=gregorian_date
        )

        return jalali_date.strftime("%Y/%m/%d")

    except (ValueError, TypeError):
        return str(date_str)

CABIN_FILTER_OPTIONS = [
    ("economy", "اکونومی"),
    ("business", "بیزینس"),
    ("first", "فرست کلاس"),
    ("unspecified", "اهمیت ندارد"),
]

# گزینه‌های پنل کوچک «کلاس پرواز» سمت چپ (نتایج پرواز)
CABIN_PANEL_OPTIONS = [
    ("first", "فرست کلاس"),
    ("economy", "اکونومی"),
    ("business", "بیزینس"),
]
def get_cabin_label(cabin_class):

    cabin_labels = {
        "economy": "اکونومی",
        "business": "بیزینس",
        "first": "فرست کلاس",
        "unspecified": "اهمیت ندارد"
    }

    return cabin_labels.get(cabin_class, "همه کلاس‌ها")

def get_sort_label(sort_by):

    sort_labels = {
        "cheapest": "ارزان‌ترین",
        "earliest": "زودترین",
        "latest": "دیرترین",
        "priciest": "گران‌ترین"
    }

    return sort_labels.get(
        sort_by,
        "-"
    )
background = get_base64("ee.jpg")

# استایل‌ها
inject_background_style(background)
inject_main_style()
inject_cabin_and_passenger_style()
inject_confirmation_style()
inject_sidebar_style(st.session_state.sidebar_open)
inject_login_style()
inject_auth_style()
inject_user_box_style()
inject_flight_ticket()
inject_cabin_filter_panel_style()



handle_google_callback()


# بازیابی کاربر از Cookie

if "user" not in st.session_state and not st.session_state.get("just_logged_out"):

    if "user_id" in cookies:

        user = get_user_by_id(
            int(cookies["user_id"])
        )

        if user:
            st.session_state.user = user

# فلگ خروج فقط برای همون یک rerun بلافاصله بعد از کلیک لازمه
st.session_state["just_logged_out"] = False

if "user" not in st.session_state:

    google_url = get_google_auth_url()

    st.markdown(
        f'<a href="{google_url}" target="_self" class="guest-login-fixed">ورود / ثبت‌ نام</a>',
        unsafe_allow_html=True
    )


# دکمه شناور باز و بسته کردن نوار کناری 

st.button(
    "☰",
    key="sidebar_toggle_button",
    on_click=toggle_sidebar
)


# نوار کناری: گفتگوی جدید و فهرست گفتگوهای اخیر

with st.sidebar:

    current_user_id = st.session_state.get("user", {}).get("id")

    # جهت انیمیشن گذار (فقط برای همان rerunی که بین دو نما جابه‌جا شده)
    sidebar_anim = st.session_state.pop("sidebar_anim", None)

    view_key = {
        "left": "sbview_anim_left",     # ورود به بایگانی
        "right": "sbview_anim_right"    # بازگشت از بایگانی
    }.get(sidebar_anim, "sbview_static")

    # محتوای نوار کناری: یا نمای معمولی، یا نمای کامل «بایگانی».
    # باکس کاربر عمداً بیرون از این کانتینر است (ثابت پایین می‌ماند و
    # انیمیشن روی آن اثر نمی‌گذارد)
    with st.container(key=view_key):

        if st.session_state.get("show_archive", False):
            render_sidebar_archive_view(current_user_id)
        else:
            render_sidebar_main_view(current_user_id)

    # باکس کاربر: کل باکس کلیک‌پذیره (details/summary) و منوی خروج را باز می‌کند
    if "user" in st.session_state:

        with st.container(key="user_box_container"):

            user = st.session_state.user
            name = user.get("name") or "کاربر"
            email = user.get("email") or "-"
            avatar_url = user.get("picture")

            if avatar_url:
                avatar_html = f'<img src="{avatar_url}" class="user-avatar-img" />'
            else:
                initial = (name[0] if name else "?").upper()
                avatar_html = f'<div class="user-avatar-fallback">{initial}</div>'

            st.markdown(
                f"""
                <details class="user-details">
                <summary class="user-summary">
                {avatar_html}
                <div class="user-box-text">
                <div class="user-box-name">{name}</div>
                <div class="user-box-email">{email}</div>
                </div>
                <span class="user-chevron">▾</span>
                </summary>
                </details>
                """,
                unsafe_allow_html=True
            )

            st.button(
                "🚪 خروج از حساب",
                key="logout_button",
                use_container_width=True,
                on_click=logout_user
            )

    else:

        with st.container(key="user_box_container"):

            st.markdown(
            """
            <div class="user-details guest-user-details">
            <div class="user-summary guest-user-summary">
            <div class="user-avatar-fallback">👤</div>

            <div class="user-box-text">
            <div class="user-box-name">مهمان</div>
            </div>
            </div>
            </div>
                """,
                unsafe_allow_html=True
            )
# هدر
render_header()


if "messages" not in st.session_state:

    st.session_state.messages = [

        {
            "role": "assistant",
            "content": "سلام من دستیارهوشمند رزرو بلیط هستم. چطور می توانم در رزرو بلیط کمکتان کنم ؟ "
        }

    ]

# ساخت باکس برای پیام ها و نمایش پیام ها در صفحه چت

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# بررسی نوع رابطی که لنگ گراف درخواست کرده و ورودی کاربر
# یعنی رابط کاربری فعلی مثلا الان داره شمارنده مسافران رو نشون میده یا باتن های نوع پرواز یا ....
current_ui = st.session_state.get(
    "flight_state",{}).get("ui_type")
print("current_ui",current_ui)


def known_or_empty(value, render):
    """اگه مقدار خالی/None یا «نامشخص» باشه، رشته‌ی خالی برمی‌گردونه؛
    وگرنه render(value) رو صدا می‌زنه. برای این استفاده می‌شه که فیلدهای
    نامشخص (مثل ظرفیت، نوع پرواز، کلاس پرواز و ...) اصلاً توی کارت پرواز
    نمایش داده نشن، به‌جای این‌که به‌شکل «نامشخص» نشون داده بشن."""
    if not value or str(value).strip() == "نامشخص":
        return ""
    return render(value)


def render_flight_ticket(flight):
    plane_img = get_plane_image()
    airline_logo_data = get_airline_logo_base64(flight.get("airline_logo"))
    wheelchair_badge = ""
    if flight.get("wheelchair_note"):
        wheelchair_badge = f'<span>{flight["wheelchair_note"]}</span>'

    flight_type_badge = known_or_empty(
        flight.get("flight_type"), lambda v: f"<span>{v}</span>"
    )
    cabin_class_badge = known_or_empty(
        flight.get("cabin_class"), lambda v: f'<span class="cabin-tag">{v}</span>'
    )
    aircraft_badge = known_or_empty(
        flight.get("aircraft"), lambda v: f"<span>{v}</span>"
    )
    seat_info = known_or_empty(
        flight.get("remaining_seats"),
        lambda v: f'<div class="seat-info">ظرفیت: {v}</div>',
    )

    st.markdown(
f"""
<div class="ticket-card">

<div class="ticket-content">


<div class="flight-section">


<div class="ticket-header">

<div class="airline-name">


<img class="airline-logo"
src="{ airline_logo_data }" >

<span>{ flight["airline"] }</span>

</div>


<div class="flight-tags">

{flight_type_badge}
{cabin_class_badge}
{aircraft_badge}
{wheelchair_badge}

</div>

</div>



<div class="route-section">


<div class="airport">

<div class="city">
{flight["origin"]}
</div>

<div class="time">
{flight["departure_time"]}
</div>

</div>



<div class="flight-line">

<div class="line"></div>

<img class="plane-icon" src="{plane_img}">

<div class="line"></div>

</div>



<div class="airport">

<div class="city">
{flight["destination"]}
</div>

<div class="time">
{flight["arrival_time"]}
</div>

</div>


</div>

</div>




<div class="price-section">



<div class="ticket-price">
{flight["price"]}
</div>


{seat_info}

<a href="{flight.get("source_url", "#")}" target="_blank" class="select-flight">
انتخاب پرواز
</a>

<span class="flight-source">
    منبع: {flight.get("source", "نامشخص")}
</span>

</div>



</div>

</div>
""",
unsafe_allow_html=True
)

if current_ui == "passenger_choice":

    st.markdown(
        """
        <div class="cabin-title">
            آیا می‌خواهید تعداد مسافران را مشخص کنید؟
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    col1.button(
        "وارد می‌کنم",
        key="passenger_enter_button",
        use_container_width=True,
        on_click=select_passenger_option,
        args=("enter",)
    )

    col2.button(
        "وارد نمی‌کنم",
        key="passenger_default_button",
        use_container_width=True,
        on_click=select_passenger_option,
        args=("default",)
    )

    scroll_to_bottom()
    # در این مرحله کادر چت نمایش داده نشود
    prompt = None

elif current_ui == "passenger_counter":

    st.markdown(
        """
        <div class="cabin-title">
            تعداد مسافران را مشخص کنید:
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.number_input(
            "بزرگسال",
            min_value=1,
            value=1,
            step=1,
            key="adult_count"
        )

    with col2:

        st.number_input(
            "کودک",
            min_value=0,
            value=0,
            step=1,
            key="child_count"
        )

    with col3:

        st.number_input(
            "نوزاد",
            min_value=0,
            value=0,
            step=1,
            key="infant_count"
        )

    st.button(
        "ثبت تعداد مسافران",
        key="save_passenger_counts_button",
        use_container_width=True,
        on_click=save_passenger_counts
    )

    scroll_to_bottom()
    prompt = None


elif current_ui == "confirmation":

    flight_state = st.session_state["flight_state"]

    st.markdown(
        """
    <div class="cabin-title">
    لطفاً اطلاعات پرواز را بررسی کنید:
    </div>
    """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
    <div class="confirmation-box">
    <div class="confirmation-row">
    <span class="confirmation-label">مبدأ:</span>
    <span class="confirmation-value">{flight_state.get("origin") or "-"}</span>
    </div>

    <div class="confirmation-row">
    <span class="confirmation-label">مقصد:</span>
    <span class="confirmation-value">{flight_state.get("destination") or "-"}</span>
    </div>

    <div class="confirmation-row">
    <span class="confirmation-label">تاریخ حرکت:</span>
    <span class="confirmation-value">{to_jalali(flight_state.get("departure_date"))}</span>
    </div>

    <div class="confirmation-row">
    <span class="confirmation-label">بزرگسال:</span>
    <span class="confirmation-value">{flight_state.get("adults", 0)}</span>
    </div>

    <div class="confirmation-row">
    <span class="confirmation-label">کودک:</span>
    <span class="confirmation-value">{flight_state.get("children", 0)}</span>
    </div>

    <div class="confirmation-row">
    <span class="confirmation-label">نوزاد:</span>
    <span class="confirmation-value">{flight_state.get("infants", 0)}</span>
    </div>

    <div class="confirmation-row">
    <span class="confirmation-label">کلاس پرواز:</span>
    <span class="confirmation-value">{get_cabin_label(flight_state.get("cabin_class"))}</span>
    </div>
    </div>

    </div>
    """,
        unsafe_allow_html=True
    )
    col1, col2 = st.columns(2)

    col1.button(
        "تأیید و جستجوی پرواز",
        key="confirm_flight_button",
        use_container_width=True,
        on_click=confirm_flight
    )

    col2.button(
        "ویرایش اطلاعات",
        key="edit_flight_button",
        use_container_width=True,
        on_click=edit_flight
    )

    scroll_to_bottom()

    prompt = None

elif current_ui == "search":

    flight_state = st.session_state["flight_state"]

    flights = flight_state.get(
        "flights",
        []
    )


    if flights:
        departure_date = flight_state.get("departure_date")
        date_label = ""

        if departure_date:
            gregorian_date = datetime.strptime(
                departure_date,
                "%Y-%m-%d"
            ).date()

            jalali_date = jdatetime.date.fromgregorian(
                date=gregorian_date
            )

            date_label = jalali_date.strftime("%Y/%m/%d")

        st.markdown(
            f"""
            <div class="cabin-title">
                پروازهای موجود{f" ({date_label})" if date_label else ""}:
            </div>
            """,
            unsafe_allow_html=True
        )
        current_sort = flight_state.get("sort_by")
        sort_col1, sort_col2, sort_col3, sort_col4 = st.columns(4)

        sort_col1.button(
            "ارزان‌ترین" + (" ✓" if current_sort == "cheapest" else ""),
            key="local_sort_cheapest",
            use_container_width=True,
            on_click=sort_flights_locally,
            args=("cheapest",)
        )

        sort_col2.button(
            "زودترین" + (" ✓" if current_sort == "earliest" else ""),
            key="local_sort_earliest",
            use_container_width=True,
            on_click=sort_flights_locally,
            args=("earliest",)
        )

        sort_col3.button(
            "دیرترین" + (" ✓" if current_sort == "latest" else ""),
            key="local_sort_latest",
            use_container_width=True,
            on_click=sort_flights_locally,
            args=("latest",)
        )

        sort_col4.button(
            "گران‌ترین" + (" ✓" if current_sort == "priciest" else ""),
            key="local_sort_priciest",
            use_container_width=True,
            on_click=sort_flights_locally,
            args=("priciest",)
        )
        counts = {}
        for f in flights:
            k = detect_cabin_key(f)
            counts[k] = counts.get(k, 0) + 1

        present = [(k, l) for k, l in CABIN_FILTER_OPTIONS if k in counts]
        preferred = flight_state.get("cabin_class")
        search_id = flight_state.get("search_id", "")

        # اگر کاربر کلاسی گفته و در نتایج هست، فقط همان تیک می‌خورد؛ وگرنه همه
        preferred_available = preferred in counts
        if preferred and preferred != "unspecified" and not preferred_available:
            st.info("پروازی با کلاس درخواستی پیدا نشد؛ سایر کلاس‌ها نمایش داده می‌شوند.")

        # پنل کوچک سمت چپ: هر سه کلاس را می‌شود هم‌زمان، دوتایی یا تکی
        # تیک زد. کلاسی که در نتایج پروازی ندارد غیرفعال نمایش داده می‌شود
        selected = set()

        with st.container(key="cabin_filter_panel"):

            st.markdown(
                '<div class="cabin-filter-head">'
                '<div class="cabin-filter-icon">✈</div>'
                '<div class="cabin-filter-texts">'
                '<div class="cabin-filter-title">کلاس پرواز</div>'
                '<div class="cabin-filter-sub">نتایج را فیلتر کنید</div>'
                '</div></div>',
                unsafe_allow_html=True
            )

            for key, label in CABIN_PANEL_OPTIONS:
                count = counts.get(key, 0)
                default = count > 0 and (
                    (not preferred_available) or preferred == key
                )

                if st.checkbox(
                    f"{label}  ({count})",
                    value=default,
                    key=f"cabin_filter_{search_id}_{key}",
                    disabled=(count == 0),
                ):
                    selected.add(key)

        visible = [f for f in flights if detect_cabin_key(f) in selected]

        if not visible:
            st.warning("حداقل یک نوع پرواز را انتخاب کنید.")
        for flight in visible:
            render_flight_ticket(flight)



    prompt = None
else:
    prompt = st.chat_input(
        "درخواست خود را بنویسید"
    )

st.markdown(
    "</div>",
    unsafe_allow_html=True
)

# جای دکمه‌ی «حذف» نسبت به سه‌نقطه‌ی همان ردیف گفتگو
inject_delete_popup_position()
inject_hero_typing()
inject_search_loader()


if prompt:

    # پیام کاربر ذخیره شود
    #پیام ابتدا در حافظه موقت سپس در دیتابیس ذخیره می شود
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )
    save_message(
    st.session_state.session_id,
    "user",
    prompt,
    user_id=st.session_state.get("user", {}).get("id")
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    handle_user_prompt(prompt)

    st.rerun()