"""
توابع رویدادی (callback) رابط کاربری: اسکرول خودکار، ثبت انتخاب کلاس
پرواز، ثبت گزینه تعداد مسافر و ذخیره تعداد مسافران وارد شده.

همه‌ی این توابع state چت را در st.session_state به‌روزرسانی می‌کنند
و Graph پروازها (flight_graph) را دوباره اجرا می‌کنند.
"""
import uuid
import traceback
import streamlit as st
import streamlit.components.v1 as components


from cookie_manager import cookies
from flight_graph import flight_graph
from chat_database import (
    save_message,
    load_messages,
    list_sessions,
    delete_session,
    set_session_pinned,
    set_session_archived,
    rename_session,
    MAX_TITLE_LENGTH,
)
WELCOME_MESSAGE = (
    "سلام من دستیارهوشمند رزرو بلیط هستم. "
    "چطور می توانم در رزرو بلیط کمکتان کنم ؟ "
)


def current_user_id():
    """آی‌دی کاربر لاگین‌شده، یا None اگر مهمان باشد."""
    return st.session_state.get("user", {}).get("id")


def _run_graph_step(current_state, user_message):
    """
    گراف پروازها را با state جدید اجرا می‌کند و پیام کاربر/پاسخ دستیار
    را ذخیره می‌کند.

    این تابع مرکزیِ مشترکِ همه‌ی دکمه‌های رابط کاربری است (کلاس پرواز،
    مرتب‌سازی، تعداد مسافران، تأیید/ویرایش پرواز و ...). قبلاً هرکدام از
    این callbackها مستقیماً flight_graph.invoke را صدا می‌زدند و اگر
    گراف خطای غیرمنتظره می‌داد (مثلاً کلید assistant_message وجود
    نداشت یا state ناقص بود)، کل اپ Streamlit کرش می‌کرد و کاربر یک
    traceback خام می‌دید.

    اینجا:
      ۱) پیام کاربر همیشه ذخیره می‌شود (خودش دلیل خطا نیست).
      ۲) invoke کردن گراف در try/except قرار می‌گیرد.
      ۳) اگر خطا رخ دهد، flight_state قبلی دست‌نخورده باقی می‌ماند
         (بازگردانی state جدید انجام نمی‌شود) تا کاربر بتواند دوباره
         تلاش کند، و یک پیام خطای قابل‌فهم فارسی نشان داده می‌شود،
         بدون لو رفتن جزئیات فنی خطا.
    """
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )
    save_message(
        st.session_state.session_id,
        "user",
        user_message,
        user_id=current_user_id()
    )

    try:
        
        graph_result = flight_graph.invoke(current_state)
        assistant_message = graph_result["assistant_message"]
    except Exception as error:
        print("GRAPH STEP ERROR:")
        print(traceback.format_exc())

        graph_result = None
        assistant_message = (
            "متأسفم، یک خطای غیرمنتظره پیش آمد.\n\n"
            f"`{type(error).__name__}: {error}`"
        )

    if graph_result is not None:
        st.session_state["flight_state"] = graph_result

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": assistant_message
        }
    )
    save_message(
        st.session_state.session_id,
        "assistant",
        assistant_message,
        user_id=current_user_id()
    )

    return graph_result


def scroll_to_bottom():

    components.html(
        """
        <script>
            setTimeout(function () {
                window.frameElement.scrollIntoView({
                    behavior: "smooth",
                    block: "end"
                });
            }, 400);
        </script>
        """,
        height=0
    )



def sort_flights_locally(sort_value):
    """پروازهایی که از قبل توسط search_flights برگردانده شده‌اند را فقط
    توی حافظه (session_state) دوباره مرتب می‌کند - بدون اسکرپ دوباره و
    بدون صدا زدن flight_graph. برخلاف select_cabin_class/... این تابع
    نه پیامی به چت اضافه می‌کند و نه گراف را دوباره اجرا می‌کند؛ چون
    مرتب‌سازی صرفاً یک تعامل UI روی نتایجِ همین جستجوست."""

    flight_state = st.session_state.get("flight_state", {}).copy()
    flights = list(flight_state.get("flights", []))

    if sort_value == "cheapest":
        flights.sort(key=lambda f: f.get("price_value", 0))

    elif sort_value == "priciest":
        flights.sort(key=lambda f: f.get("price_value", 0), reverse=True)

    elif sort_value == "earliest":
        flights.sort(key=lambda f: f.get("departure_time") or "99:99")

    elif sort_value == "latest":
        flights.sort(
            key=lambda f: f.get("departure_time") or "00:00",
            reverse=True
        )

    flight_state["flights"] = flights
    flight_state["sort_by"] = sort_value

    st.session_state["flight_state"] = flight_state
def select_passenger_option(option):

    current_state = st.session_state["flight_state"].copy()

    # کاربر می‌ خواهد خودش تعداد را وارد کند
    if option == "enter":

        current_state["passenger_status"] = "entering"

        user_message = "تعداد مسافران را وارد می‌کنم."

    # کاربر نمی‌خواهد تعداد را وارد کند
    else:

        current_state["adults"] = 1
        current_state["children"] = 0
        current_state["infants"] = 0

        current_state["passenger_status"] = "resolved"

        # برای سازگاری با ساختار فعلی گراف
        current_state["passengers_confirmed"] = True
        user_message = "تعداد مسافران را وارد نمی‌کنم."

    graph_result = _run_graph_step(current_state, user_message)

    print("PASSENGER OPTION RESULT:", graph_result)
def save_passenger_counts():

    current_state = st.session_state["flight_state"].copy()

    # دریافت مقادیر شمارنده‌ها
    current_state["adults"] = (st.session_state["adult_count"])
    current_state["children"] = (st.session_state["child_count"])
    current_state["infants"] = (st.session_state["infant_count"])

    # تعداد مسافران مشخص شده
    current_state["passenger_status"] = "resolved"

    # برای سازگاری با ساختار فعلی Graph
    current_state["passengers_confirmed"] = True

    user_message = (
        f"تعداد مسافران: "
        f"{current_state['adults']} بزرگسال، "
        f"{current_state['children']} کودک، "
        f"{current_state['infants']} نوزاد"
    )

    graph_result = _run_graph_step(current_state, user_message)

    print("PASSENGER COUNTER RESULT:", graph_result)
def confirm_flight():

    current_state = st.session_state["flight_state"].copy()

    current_state["confirmation_status"] = "confirmed"

    user_message = "اطلاعات پرواز را تأیید می‌کنم."

    _run_graph_step(current_state, user_message)


def edit_flight():

    current_state = st.session_state["flight_state"].copy()

    current_state["confirmation_status"] = "editing"

    user_message = "می‌خواهم اطلاعات پرواز را ویرایش کنم."

    _run_graph_step(current_state, user_message)
def toggle_sidebar():
    """باز یا بسته کردن نوار کناری کشویی با دکمه شناور بالای صفحه."""
    st.session_state.sidebar_open = not st.session_state.get(
        "sidebar_open",
        True
    )


def start_new_conversation():
    """ساخت یک گفتگوی تازه و خالی و فعال کردن آن."""
    st.session_state.session_id = str(uuid.uuid4())

    st.session_state.messages = [
        {
            "role": "assistant",
            "content": WELCOME_MESSAGE
        }
    ]

    st.session_state.flight_state = {}


def switch_session(session_id: str):
    """جابه‌جایی به یکی از گفتگوهای ذخیره‌شده و بارگذاری تاریخچه آن."""
    st.session_state.session_id = session_id

    messages = load_messages(session_id, user_id=current_user_id())

    if not messages:
        messages = [
            {
                "role": "assistant",
                "content": WELCOME_MESSAGE
            }
        ]

    st.session_state.messages = messages
    st.session_state.flight_state = {}


def remove_session(session_id: str):
    """حذف یک گفتگوی ذخیره‌شده از پایگاه داده (به‌صورت تکی)."""
    delete_session(session_id, user_id=current_user_id())

    # اگر گفتگوی فعلی حذف شد، یک گفتگوی جدید و خالی بساز
    if session_id == st.session_state.get("session_id"):
        start_new_conversation()

@st.dialog("آیا می‌خواهید این چت حذف شود؟")
def delete_session_dialog(session_id: str):
    """پنجره‌ی تأیید حذف یک گفتگو - خارج از سایدبار و روی صفحه‌ی
    اصلی باز می‌شود (st.dialog)، با دو دکمه‌ی هم‌اندازه‌ی بله/خیر."""

    yes_col, no_col = st.columns(2)

    with yes_col:
        if st.button(
            "بله",
            key=f"confirm_delete_{session_id}",
            use_container_width=True
        ):
            remove_session(session_id)
            st.rerun()

    with no_col:
        if st.button(
            "خیر",
            key=f"cancel_delete_{session_id}",
            use_container_width=True
        ):
            st.rerun()


def toggle_pin_session(session_id: str, pinned: bool):
    """پین کردن (pinned=True) یا برداشتن پین یک گفتگو."""
    set_session_pinned(session_id, pinned, user_id=current_user_id())


def archive_session(session_id: str):
    """آرشیو کردن گفتگو؛ پیام‌ها در دیتابیس می‌مانند و فقط از لیست فعال
    خارج می‌شود. اگر گفتگوی فعلی آرشیو شد، یک گفتگوی تازه باز می‌شود."""
    set_session_archived(session_id, True, user_id=current_user_id())

    if session_id == st.session_state.get("session_id"):
        start_new_conversation()


def unarchive_session(session_id: str):
    """خارج کردن گفتگو از آرشیو و برگشت به لیست گفتگوهای اخیر."""
    set_session_archived(session_id, False, user_id=current_user_id())


def open_archive_view():
    """ورود به نمای «بایگانی» داخل نوار کناری.
    جهت انیمیشن ورود در session_state ذخیره می‌شود تا فقط همین یک
    rerun انیمیشن داشته باشد و rerunهای بعدی محتوا را دوباره حرکت ندهند."""
    st.session_state.show_archive = True
    st.session_state.sidebar_anim = "left"


def close_archive_view():
    """بازگشت از نمای «بایگانی» به نوار کناری معمولی."""
    st.session_state.show_archive = False
    st.session_state.sidebar_anim = "right"


@st.dialog("تغییر نام گفتگو")
def rename_session_dialog(session_id: str, current_title: str):
    """پنجره‌ی تغییر عنوان گفتگو؛ عنوان جدید در دیتابیس ذخیره می‌شود و
    بعد از Refresh یا اجرای دوباره‌ی برنامه هم باقی می‌ماند."""

    new_title = st.text_input(
        "عنوان جدید گفتگو",
        value=current_title[:MAX_TITLE_LENGTH],
        max_chars=MAX_TITLE_LENGTH,
        key=f"rename_input_{session_id}"
    )

    save_col, cancel_col = st.columns(2)

    with save_col:
        if st.button(
            "ذخیره",
            key=f"rename_save_{session_id}",
            use_container_width=True
        ):
            if new_title.strip():
                rename_session(
                    session_id,
                    new_title,
                    user_id=current_user_id()
                )
                st.rerun()
            else:
                st.markdown("⚠️ عنوان گفتگو نمی‌تواند خالی باشد.")

    with cancel_col:
        if st.button(
            "انصراف",
            key=f"rename_cancel_{session_id}",
            use_container_width=True
        ):
            st.rerun()


def render_session_card(session: dict, archived: bool = False):
    """رندر یک کارت گفتگو در نوار کناری: دکمه‌ی عنوان + منوی سه‌نقطه.
    برای گفتگوهای فعال: پین / آرشیو / تغییر نام / حذف.
    برای گفتگوهای بایگانی‌شده: خارج کردن از بایگانی / تغییر نام / حذف."""

    session_id = session["session_id"]
    is_active = session_id == st.session_state.session_id
    is_pinned = session.get("is_pinned", False) and not archived

    if is_active:
        icon = "📌🧳 " if is_pinned else "🧳 "
    elif is_pinned:
        icon = "📌 "
    else:
        icon = "💬 "

    # کل کارت هر گفتگو (نام + سه‌نقطه) داخل یک کانتینر واحد
    with st.container(key=f"chat_card_{session_id}"):

        row_label, row_menu = st.columns([5, 1])

        with row_label:
            st.button(
                icon + session["title"],
                key=f"session_{session_id}",
                use_container_width=True,
                on_click=switch_session,
                args=(session_id,)
            )

        with row_menu:

            with st.popover("⋮", key=f"menu_toggle_{session_id}"):

                if archived:
                    st.button(
                        "  خارج کردن از بایگانی",
                        key=f"archive_option_{session_id}",
                        use_container_width=True,
                        on_click=unarchive_session,
                        args=(session_id,)
                    )
                else:
                    st.button(
                        "📍 برداشتن پین" if is_pinned else "📌 پین کردن",
                        key=f"pin_option_{session_id}",
                        use_container_width=True,
                        on_click=toggle_pin_session,
                        args=(session_id, not is_pinned)
                    )

                    st.button(
                        "  بایگانی کردن",
                        key=f"archive_option_{session_id}",
                        use_container_width=True,
                        on_click=archive_session,
                        args=(session_id,)
                    )

                # دیالوگ فقط در همان اجرایی باز می‌شود که دکمه کلیک شده
                if st.button(
                    "  تغییر نام",
                    key=f"rename_option_{session_id}",
                    use_container_width=True
                ):
                    rename_session_dialog(
                        session_id,
                        session.get("full_title", session["title"])
                    )

                st.button(
                    "  حذف گفتگو",
                    key=f"delete_option_{session_id}",
                    use_container_width=True,
                    on_click=remove_session,
                    args=(session_id,)
                )


# متن دکمه‌ی بازگشت. در چیدمان راست‌به‌چپ فلش «بازگشت» به سمت راست
# (سمت شروع) است؛ اگر فلش چپ (←) را ترجیح می‌دهید فقط همین ثابت را عوض کنید.
ARCHIVE_BACK_LABEL = "→ بازگشت"


def render_sidebar_main_view(user_id: int | None):
    """نمای معمولی نوار کناری: گفتگوی جدید، گفتگوهای اخیر و ورودی «بایگانی»."""

    with st.container(key="sidebar_header_box"):

        st.markdown(
            '<div class="sidebar-title">✈️ دستیار هوشمند بلیط</div>',
            unsafe_allow_html=True
        )

        st.button(
            "گفتگوی جدید",
            key="new_chat_button",
            use_container_width=True,
            on_click=start_new_conversation
        )

    st.markdown(
        '<div class="sidebar-section-title">گفتگوهای اخیر</div>',
        unsafe_allow_html=True
    )

    sessions = list_sessions(user_id=user_id)

    if not sessions:

        st.markdown(
            '<div class="sidebar-empty">هنوز گفتگویی ذخیره نشده است.</div>',
            unsafe_allow_html=True
        )

    for session in sessions:
        render_session_card(session)

    # ورودی بایگانی: زیر لیست گفتگوها و بالای باکس کاربر.
    # با کلیک، کل نوار کناری به نمای بایگانی تبدیل می‌شود (نه لیست بازشونده)
    with st.container(key="archive_entry_box"):

        st.button(
            "  بایگانی",
            key="archive_toggle_button",
            use_container_width=True,
            on_click=open_archive_view
        )


def render_sidebar_archive_view(user_id: int | None):
    """نمای «بایگانی» داخل نوار کناری: دکمه‌ی بازگشت، عنوان و گفتگوهای
    واقعیِ بایگانی‌شده‌ی همین کاربر (از دیتابیس)."""

    with st.container(key="archive_header_box"):

        st.markdown(
            '<div class="sidebar-title">  بایگانی</div>',
            unsafe_allow_html=True
        )

        st.button(
            ARCHIVE_BACK_LABEL,
            key="archive_back_button",
            use_container_width=True,
            on_click=close_archive_view
        )

    st.markdown(
        '<div class="sidebar-section-title">گفتگوهای بایگانی‌شده</div>',
        unsafe_allow_html=True
    )

    archived_sessions = list_sessions(user_id=user_id, archived=True)

    if not archived_sessions:

        st.markdown(
            '<div class="sidebar-empty">بایگانی خالی است.</div>',
            unsafe_allow_html=True
        )

    for session in archived_sessions:
        render_session_card(session, archived=True)


def logout_user():
    """خروج کاربر از حساب: پاک کردن session و کوکی."""
    st.session_state.pop("user", None)
    st.session_state["just_logged_out"] = True
    st.session_state.pop("show_archive", None)

    try:
        del cookies["user_id"]
        cookies.save()
    except KeyError:
        pass

    # بعد از خروج، یک گفتگوی تازه و خالی نشان داده شود
    start_new_conversation()