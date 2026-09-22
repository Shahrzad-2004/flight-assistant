import streamlit as st


def inject_background_style(background: str) -> None:
    """پس‌زمینه صفحه + فونت وزیرمتن + مخفی کردن منوهای پیش‌فرض استریم‌لیت."""
    # استایل
    
    st.markdown(
        f"""
    <style>
    
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800&display=swap');
    
    #MainMenu{{visibility:hidden;}}
    
    footer{{visibility:hidden;}}
    
    header{{visibility:hidden;}}
    
    html,
    body,
    [data-testid="stAppViewContainer"]{{
        background-image:url("data:image/jpeg;base64,{background}");
        background-size:cover;
        background-position:center;
        background-repeat:no-repeat;
        background-attachment:fixed;
    }}
    
    /* اجازه بده بکگراند از زیر نوار پایین هم دیده بشه */
    [data-testid="stBottom"],
    [data-testid="stBottom"] > div,
    [data-testid="stBottomBlockContainer"],
    [data-testid="stChatInputContainer"],
    .stBottom,
    .stBottomBlockContainer{{
        background:transparent !important;
        background-color:transparent !important;
    }}
    
    .block-container{{
        padding-top:25px;
        max-width:1050px;
    }}
    html,
    body,
    [data-testid="stAppViewContainer"],
    [data-testid="stMarkdownContainer"],
    textarea,
    button{{
    font-family:'Vazirmatn',sans-serif !important;
    }}
    
    </style>
    """,
        unsafe_allow_html=True,
    )


def inject_main_style() -> None:
    """استایل کارت اصلی، پیام‌های چت، کادر تایپ و دکمه‌ها."""
    st.markdown("""
    <style>
    
    /* کارت اصلی */
    /* جلوگیری از کم‌رنگ شدن پیام‌ها هنگام اجرای مجدد Streamlit */
    
    [data-testid="stChatMessage"] {
        opacity: 1 !important;
    }
    
    [data-testid="stChatMessage"] * {
        opacity: 1 !important;
        color: #111827 !important;
    }
    .main-card{
    
        background:rgba(255,255,255,.90);
    
        backdrop-filter:blur(18px);
    
        border-radius:28px;
    
        width:700px;
        max-width:calc(100vw - 40px);
        box-sizing:border-box;
        
        margin: 0 auto 30px auto;
        
        padding:50px;
    
        box-shadow:0 20px 40px rgba(0,0,0,.18);
    
        border:1px solid rgba(255,255,255,.75);
    
    }
    
    /* لوگو */
    
    .logo{
    
        font-size:60px;
    
        text-align:center;
    
        margin-bottom:8px;
    
    }
    
    /* عنوان */
    
    .title{
        text-align:center;
    
        font-size:40px;
    
        font-weight:800;
    
        color:#111827;
    
        letter-spacing:-1px;
    
    }
    
    /* زیرعنوان */
    
    .subtitle{
    
        text-align:center;
    
        font-size:15px;
    
        font-weight:500;
    
        color:#4B5563;
    }
    
    /* پیام‌های چت */
    
    [data-testid="stChatMessage"]{
    
        background:white;
    
        border-radius:18px;
    
        direction: rtl;
        text-align: right;
    
        padding:12px;
    
        margin-top:22px;
    
        margin-bottom:12px;
    
        box-shadow:0 4px 15px rgba(0,0,0,.06);
    
    }
    /* راست‌چین کردن متن داخل پیام */
    [data-testid="stChatMessage"]
    [data-testid="stMarkdownContainer"] {
        direction: rtl !important;
        text-align: right !important;
        width: 100%;
    }
    
    [data-testid="stChatMessage"] p {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* کادر تایپ */
    
    [data-testid="stChatInput"],
    [data-testid="stChatInput"] > div{
    
        background:white !important;
        background-color:white !important;
    
        border-radius:20px;
        
        direction: rtl;
        text-align: right;
    
        border:1px solid #d1d5db;
    
        box-shadow:0 5px 20px rgba(0,0,0,.08);
    
    }
    
    [data-testid="stChatInput"] textarea{
    
        color:#111827 !important;
        background-color:white !important;
    
    }
    
    [data-testid="stChatInput"] textarea::placeholder{
    
        color:#6b7280 !important;
    
    }
    /* متن حالت جستجو و لودینگ */
    
    [data-testid="stSpinner"] {
        direction: rtl !important;
        text-align: right !important;
    }
    
    [data-testid="stSpinner"] p,
    [data-testid="stSpinner"] span {
        color: #111827 !important;
        font-family: 'Vazirmatn', sans-serif !important;
        font-size: 16px !important;
        font-weight: 600 !important;
    }
    /* دکمه */
    
    button{
    
        background:#2563eb !important;
    
        color:white !important;
    
        border-radius:14px !important;
    
        border:none !important;
    
        transition:.3s;
    
    }
    
    button:hover{
    
        background:#1d4ed8 !important;
    
        transform:translateY(-2px);
    
    }
    
    </style>
    """, unsafe_allow_html=True)


def inject_cabin_and_passenger_style() -> None:
    """استایل دکمه‌های کلاس پرواز و شمارنده‌های مسافر (بزرگسال/کودک/نوزاد)."""
    #استایل باتن های نوع پرواز
    st.markdown(
        """
    <style>
    
    /* عنوان انتخاب کلاس پرواز */
    
    .cabin-title {
        direction: rtl;
        text-align: right;
    
        font-family: 'Vazirmatn', sans-serif !important;
        font-size: 17px;
        font-weight: 700;
    
        color: #1f2937;
    
        margin-top: 20px;
        margin-bottom: 12px;
    }
    
    
    /* راست‌چین شدن ترتیب دکمه‌های کلاس پرواز */
    
    [data-testid="stHorizontalBlock"]:has(.st-key-economy_button) {
        direction: rtl !important;
        flex-direction: row-reverse !important;
        gap: 10px !important;
    }
    [data-testid="stHorizontalBlock"]:has(.st-key-cheapest_button) {
        direction: rtl !important;
        flex-direction: row-reverse !important;
        gap: 10px !important;
    }

    
    /* استایل شیشه‌ای مخصوص چهار دکمه کلاس پرواز */
    .st-key-economy_button button,
    .st-key-business_button button,
    .st-key-first_button button,
    .st-key-unspecified_button button,
    .st-key-passenger_enter_button button,
    .st-key-passenger_default_button button,
    .st-key-save_passenger_counts_button button,
    .st-key-cheapest_button button,
    .st-key-earliest_button button,
    .st-key-latest_button button,
    .st-key-priciest_button button {
    
        width: 100% !important;
        min-height: 48px !important;
    
        background: rgba(255, 255, 255, 0.45) !important;
    
        backdrop-filter: blur(14px) !important;
        -webkit-backdrop-filter: blur(14px) !important;
    
        border: 1px solid rgba(255, 255, 255, 0.75) !important;
        border-radius: 15px !important;
    
        box-shadow:
            0 5px 18px rgba(31, 41, 55, 0.10),
            inset 0 1px 0 rgba(255, 255, 255, 0.75) !important;
    
        color: #1f2937 !important;
    
        font-family: 'Vazirmatn', sans-serif !important;
        font-size: 14px !important;
        font-weight: 600 !important;
    
        direction: rtl !important;
        text-align: center !important;
    
        transition: all 0.25s ease !important;
    }
    
    
    /* فونت متن داخل دکمه‌ها */
    
    .st-key-economy_button button p,
    .st-key-business_button button p,
    .st-key-first_button button p,
    .st-key-unspecified_button button p,
    .st-key-passenger_enter_button button p,
    .st-key-passenger_default_button button p,
    .st-key-save_passenger_counts_button button p,
    .st-key-cheapest_button button p,
    .st-key-earliest_button button p,
    .st-key-latest_button button p,
    .st-key-priciest_button button p {
    
        font-family: 'Vazirmatn', sans-serif !important;
        color: #1f2937 !important;
    
        direction: rtl !important;
        text-align: center !important;
    }
    
    
    /* حالت قرار گرفتن موس روی دکمه */
    
    .st-key-economy_button button:hover,
    .st-key-business_button button:hover,
    .st-key-first_button button:hover,
    .st-key-unspecified_button button:hover,
    .st-key-passenger_enter_button button:hover,
    .st-key-passenger_default_button button:hover,
    .st-key-save_passenger_counts_button button:hover,
    .st-key-cheapest_button button:hover,
    .st-key-earliest_button button:hover,
    .st-key-latest_button button:hover,
    .st-key-priciest_button button:hover {
    
        background: rgba(37, 99, 235, 0.16) !important;
    
        border-color: rgba(37, 99, 235, 0.45) !important;
    
        box-shadow:
            0 8px 22px rgba(37, 99, 235, 0.16),
            inset 0 1px 0 rgba(255, 255, 255, 0.85) !important;
    
        transform: translateY(-2px) !important;
    }
    
    
    /* حالت کلیک */
    
    .st-key-economy_button button:active,
    .st-key-business_button button:active,
    .st-key-first_button button:active,
    .st-key-unspecified_button button:active,
    .st-key-passenger_enter_button button:active,
    .st-key-passenger_default_button button:active,
    .st-key-save_passenger_counts_button button:active,
    .st-key-cheapest_button button:active,
    .st-key-earliest_button button:active,
    .st-key-latest_button button:active,
    .st-key-priciest_button button:active {
    
        transform: translateY(0) scale(0.98) !important;
    }
    
    
    /* استایل شیشه‌ای و شیک شمارنده مسافران (بزرگسال/کودک/نوزاد) */
    
    .st-key-adult_count,
    .st-key-child_count,
    .st-key-infant_count {
    
        background: rgba(255, 255, 255, 0.45) !important;
    
        backdrop-filter: blur(14px) !important;
        -webkit-backdrop-filter: blur(14px) !important;
    
        border: 1px solid rgba(255, 255, 255, 0.75) !important;
        border-radius: 18px !important;
    
        padding: 10px 14px 14px 14px !important;
    
        box-shadow:
            0 5px 18px rgba(31, 41, 55, 0.10),
            inset 0 1px 0 rgba(255, 255, 255, 0.75) !important;
    
        transition: all 0.25s ease !important;
    }
    
    .st-key-adult_count:hover,
    .st-key-child_count:hover,
    .st-key-infant_count:hover {
    
        box-shadow:
            0 8px 22px rgba(37, 99, 235, 0.14),
            inset 0 1px 0 rgba(255, 255, 255, 0.85) !important;
    
        transform: translateY(-2px) !important;
    }
    
    /* برچسب بزرگسال / کودک / نوزاد */
    
    .st-key-adult_count label p,
    .st-key-child_count label p,
    .st-key-infant_count label p {
    
        font-family: 'Vazirmatn', sans-serif !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        color: #1f2937 !important;
    
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* ریست کامل هر پس‌زمینه تیره‌ای که خود streamlit روی */
    /* لایه‌های داخلی ورودی عدد ست می‌کند                */
    
    .st-key-adult_count *,
    .st-key-child_count *,
    .st-key-infant_count * {
    
        background-color: transparent !important;
        background-image: none !important;
        box-shadow: none !important;
        border-color: transparent !important;
    }
    
    /* بدنه ورودی عدد (باکس روشن شیشه‌ای دربرگیرنده عدد و دکمه‌ها) */
    
    .st-key-adult_count [data-testid="stNumberInputContainer"],
    .st-key-child_count [data-testid="stNumberInputContainer"],
    .st-key-infant_count [data-testid="stNumberInputContainer"],
    .st-key-adult_count [data-baseweb="input"],
    .st-key-child_count [data-baseweb="input"],
    .st-key-infant_count [data-baseweb="input"] {
    
        background: rgba(255, 255, 255, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.85) !important;
        border-radius: 14px !important;
        overflow: hidden !important;
    }
    
    .st-key-adult_count input,
    .st-key-child_count input,
    .st-key-infant_count input {
    
        background: transparent !important;
        color: #1f2937 !important;
    
        font-family: 'Vazirmatn', sans-serif !important;
        font-size: 16px !important;
        font-weight: 700 !important;
    
        text-align: center !important;
    }
    
    /* دکمه‌های + و − شمارنده - استایل شیشه‌ای ملایم */
    
    .st-key-adult_count button,
    .st-key-child_count button,
    .st-key-infant_count button {
    
        background: rgba(255, 255, 255, 0.7) !important;
        color: #2563eb !important;
    
        border: 1.5px solid rgba(37, 99, 235, 0.35) !important;
        border-radius: 50% !important;
    
        width: 30px !important;
        height: 30px !important;
        min-width: 30px !important;
    
        margin: 6px !important;
    
        box-shadow: 0 2px 8px rgba(31, 41, 55, 0.08) !important;
    
        transition: all 0.2s ease !important;
    }
    
    .st-key-adult_count button:hover,
    .st-key-child_count button:hover,
    .st-key-infant_count button:hover {
    
        background: rgba(37, 99, 235, 0.14) !important;
        border-color: rgba(37, 99, 235, 0.6) !important;
        transform: scale(1.08) !important;
    }
    
    .st-key-adult_count button:active,
    .st-key-child_count button:active,
    .st-key-infant_count button:active {
    
        transform: scale(0.92) !important;
    }
    
    .st-key-adult_count button svg,
    .st-key-child_count button svg,
    .st-key-infant_count button svg {
    
        fill: #2563eb !important;
    }
    
    /* فاصله یکنواخت بین سه ستون شمارنده */
    
    [data-testid="stHorizontalBlock"]:has(.st-key-adult_count) {
        gap: 12px !important;
    }
    
    </style>
    """,
        unsafe_allow_html=True
    )

def inject_confirmation_style() -> None:
    """استایل باکس تأیید اطلاعات پرواز و دکمه‌های تأیید/ویرایش."""

    st.markdown(
        """
        <style>

        /* باکس اطلاعات پرواز */
        .confirmation-box {
            direction: rtl !important;
            text-align: right !important;

            width: 100%;
            box-sizing: border-box;

            background: rgba(255, 255, 255, 0.90) !important;

            backdrop-filter: blur(14px) !important;
            -webkit-backdrop-filter: blur(14px) !important;

            border: 1px solid rgba(255, 255, 255, 0.80);
            border-radius: 18px;

            padding: 18px 22px;
            margin-top: 10px;
            margin-bottom: 14px;

            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.06);

            font-family: 'Vazirmatn', sans-serif !important;
            color: #111827 !important;
        }


        /* هر خط از اطلاعات */
        .confirmation-row {
            display: flex;
            flex-direction: row;
            justify-content: flex-start;
            align-items: center;

            direction: rtl !important;

            gap: 8px;

            padding: 6px 0;

            font-family: 'Vazirmatn', sans-serif !important;
            font-size: 15px;
            color: #111827 !important;
        }


        /* عنوان هر فیلد مثل مبدأ، مقصد و ... */
        .confirmation-label {
            font-weight: 700;
            color: #111827 !important;
        }


        /* مقدار فیلد */
        .confirmation-value {
            font-weight: 500;
            color: #374151 !important;
        }


        /* قرار گرفتن دو دکمه کنار هم */
        [data-testid="stHorizontalBlock"]:has(.st-key-confirm_flight_button) {
            direction: rtl !important;
            flex-direction: row-reverse !important;
            gap: 10px !important;
        }


        /* دکمه تأیید و دکمه ویرایش */
        .st-key-confirm_flight_button button,
        .st-key-edit_flight_button button {

            width: 100% !important;
            min-height: 48px !important;

            background: rgba(255, 255, 255, 0.45) !important;

            backdrop-filter: blur(14px) !important;
            -webkit-backdrop-filter: blur(14px) !important;

            border: 1px solid rgba(255, 255, 255, 0.75) !important;
            border-radius: 15px !important;

            box-shadow:
                0 5px 18px rgba(31, 41, 55, 0.10),
                inset 0 1px 0 rgba(255, 255, 255, 0.75) !important;

            color: #1f2937 !important;

            font-family: 'Vazirmatn', sans-serif !important;
            font-size: 14px !important;
            font-weight: 600 !important;

            direction: rtl !important;
            text-align: center !important;

            transition: all 0.25s ease !important;
        }


        /* متن داخل دکمه */
        .st-key-confirm_flight_button button p,
        .st-key-edit_flight_button button p {

            font-family: 'Vazirmatn', sans-serif !important;
            color: #1f2937 !important;

            direction: rtl !important;
            text-align: center !important;
        }


        /* حالت hover */
        .st-key-confirm_flight_button button:hover,
        .st-key-edit_flight_button button:hover {

            background: rgba(37, 99, 235, 0.16) !important;

            border-color: rgba(37, 99, 235, 0.45) !important;

            box-shadow:
                0 8px 22px rgba(37, 99, 235, 0.16),
                inset 0 1px 0 rgba(255, 255, 255, 0.85) !important;

            transform: translateY(-2px) !important;
        }


        /* حالت کلیک */
        .st-key-confirm_flight_button button:active,
        .st-key-edit_flight_button button:active {

            transform: translateY(0) scale(0.98) !important;
        }

        </style>
        """,
        unsafe_allow_html=True
    )
def inject_sidebar_style(sidebar_open: bool = True) -> None:
    """استایل نوار کناری کشویی: دکمه شناور باز/بسته، کارت هدر نوار،
    فهرست گفتگوهای اخیر (با رفع مشکل خارج زدن متن از کادر) و
    رنگ‌آمیزی نرم‌تر آواتار پیام‌های ربات و کاربر.
    """

    # وقتی کاربر نوار کناری را بسته باشد، به‌طور کامل مخفی می‌شود
    # اما دکمه‌ی شناور باز کردن، همیشه در دسترس باقی می‌ماند
    hide_sidebar_rule = "" if sidebar_open else """
    [data-testid="stSidebar"]{
        display:none !important;
    }
    """

    st.markdown(
        f"""
    <style>

    :root{{
        --soft-blue:#6fa3d6;
        --soft-blue-hover:#5c93c9;
        --soft-blue-border:#a9cdf0;
        --soft-blue-bg:#eaf3fc;
        --soft-user-color:#a8b6e8;
        --accent:#488091;
        --accent-hover:#3d6d7b;
    }}

    {hide_sidebar_rule}

    /* ظاهر کلی نوار کناری */
    [data-testid="stSidebar"]{{
        background:rgba(255,255,255,.92) !important;
        backdrop-filter:blur(16px);
    }}

    [data-testid="stSidebar"] > div{{
        padding-top:20px;
    }}

    /* مخفی کردن دکمه‌های داخلی و پیش‌فرض خود Streamlit برای
       باز/بسته کردن نوار کناری، تا فقط دکمه شناور سفارشی ما
       (sidebar_toggle_button) این کار را انجام دهد و با هم تداخل
       نکنند (باگ بسته‌ماندن نوار کناری دقیقاً از همینجا بود) */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="baseButton-headerNoPadding"],
    button[title="Collapse sidebar"],
    button[title="Expand sidebar"],
    button[aria-label="Collapse sidebar"],
    button[aria-label="Expand sidebar"]{{
        display:none !important;
        visibility:hidden !important;
        pointer-events:none !important;
    }}

    /* دکمه شناور باز/بسته کردن نوار کناری - همیشه در دسترس */
    .st-key-sidebar_toggle_button button{{
        position:fixed !important;
        top:14px;
        left:14px;
        z-index:999999 !important;

        width:46px !important;
        height:46px !important;
        min-width:46px !important;

        border-radius:50% !important;

        background:var(--accent) !important;
        color:white !important;

        font-size:20px !important;
        line-height:1 !important;

        border:none !important;
        box-shadow:0 6px 18px rgba(72,128,145,.45) !important;
    }}

    .st-key-sidebar_toggle_button button:hover{{
        background:var(--accent-hover) !important;
        transform:translateY(-2px);
    }}

    /* کارت هدر نوار کناری: عنوان + دکمه گفتگوی جدید */
    .st-key-sidebar_header_box{{
        background:#ffffff !important;
        border:1px solid var(--soft-blue-border) !important;
        border-radius:18px !important;
        padding:16px 14px 14px 14px !important;
        margin-bottom:18px !important;
        box-shadow:0 4px 14px rgba(111,163,214,.12) !important;
    }}

    .sidebar-title{{
        font-family:'Vazirmatn', sans-serif !important;
        font-weight:800;
        font-size:18px;
        color:#1f2937;
        text-align:center;
        margin-bottom:12px;
    }}

    /* دکمه گفتگوی جدید */
    .st-key-new_chat_button button{{
        background:var(--accent) !important;
    }}

    .st-key-new_chat_button button:hover{{
        background:var(--accent-hover) !important;
    }}

    /* عنوان بخش گفتگوهای اخیر */
    .sidebar-section-title{{
        font-family:'Vazirmatn', sans-serif !important;
        font-weight:700;
        font-size:14px;
        color:#374151;
        direction:rtl;
        text-align:right;
        margin:6px 4px 10px 4px;
    }}

    .sidebar-empty{{
        font-family:'Vazirmatn', sans-serif !important;
        font-size:13px;
        color:#9ca3af;
        direction:rtl;
        text-align:right;
        margin:4px;
    }}

    /* ردیف هر گفتگوی ذخیره‌شده - راست‌چین کردن ترتیب دکمه نام/حذف */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]{{
        gap:6px !important;
        align-items:center !important;
        direction:rtl !important;
        flex-direction:row-reverse !important;
    }}

    /* کارت واحد هر گفتگو: نام + سه‌نقطه (و در صورت باز بودن،
       منوی زیرش) همه داخل یک قاب یکپارچه‌اند. حاشیه و پس‌زمینه
       فقط روی خودِ این کانتینر است، نه روی دکمه‌های داخلش */
    [class*="st-key-chat_card_"]{{
        background:rgba(255,255,255,.6) !important;
        border:1px solid var(--accent) !important;
        border-radius:14px !important;
        margin-bottom:8px !important;
        padding:4px 8px !important;
        overflow:hidden !important;
        transition:background .18s ease, border-color .18s ease !important;
    }}

    [class*="st-key-chat_card_"]:hover{{
        background:rgba(72,128,145,.10) !important;
        border-color:var(--accent-hover) !important;
    }}
    [class*="st-key-delete_option_"] button{{
        background:#fcf2f3 !important;
        color:#ef4444 !important;
        border:1px solid #ef4444 !important;
        border-radius:10px !important;
        min-height:35px !important;
        box-shadow:none !important;
    }}

    [class*="st-key-delete_option_"] button p{{
        color:#ef4444 !important;
    }}

    [class*="st-key-delete_option_"] button:hover{{
        background:#fbe6e8 !important;
        border-color:#ef4444 !important;
    }}

    /* حذف کامل کادر آبی (گرادیانت تیل) دور دکمه حذف - فقط خود دکمه
       می‌ماند. اندازه و جای پاپ‌آپ (padding و ...) دست‌نخورده است */
    div[data-baseweb="popover"]:has([class*="st-key-delete_option_"]),
    div[data-baseweb="popover"]:has([class*="st-key-delete_option_"]) > div,
    [data-testid="stPopoverBody"]:has([class*="st-key-delete_option_"]),
    div[role="dialog"]:has([class*="st-key-delete_option_"]){{
        background:transparent !important;
        border:none !important;
        box-shadow:none !important;
        backdrop-filter:none !important;
        -webkit-backdrop-filter:none !important;

        /* کوتاه‌تر شدن عرض (قبلاً حدود ۳۲۰px بود). لبه‌ی چپ پاپ‌آپ
           همان قبلی می‌ماند و فقط از سمت راست کوتاه می‌شود */
        box-sizing:border-box !important;
        min-width:0 !important;
        width:140px !important;
        max-width:140px !important;
    }}
    /* حذف فلش کنار دکمه popover */
    [data-testid="stPopover"] button svg {{
        display:none !important;
    }}

    /* ظاهر خود سه نقطه */
    /* تنظیم جای سه نقطه */
    [data-testid="stPopover"] button {{

        background:transparent !important;
        color:#6b7280 !important;

        border:none !important;
        box-shadow:none !important;

        width:32px !important;
        min-width:32px !important;
        height:32px !important;

        padding:0 !important;

        font-size:18px !important;

        transform:translateX(-10px) !important;
    }}


    /* اصلاح hover سه نقطه */
    [data-testid="stPopover"] button:hover {{

        background:rgba(72,128,145,.15) !important;

        border-radius:10px !important;

        transform:translateX(-10px) !important;
    }}

    /* حذف سایه‌ی پیش‌فرض همه‌ی دکمه‌های داخل کارت گفتگو، تا هیچ
       دکمه‌ای قاب/برجستگی جدا از خودِ کارت نداشته باشد */
    [class*="st-key-chat_card_"] [data-testid="stButton"] button{{
        box-shadow:none !important;
    }}

    /* دکمه‌ی نام گفتگو - بدون حاشیه یا پس‌زمینه‌ی جدا */
    [class*="st-key-session_"] button{{
        background:transparent !important;
        color:#1f2937 !important;
        border:none !important;

        overflow:hidden !important;
        text-overflow:ellipsis !important;
        white-space:nowrap !important;
        display:block !important;

        text-align:right !important;
        direction:rtl !important;

        /* نزدیک‌تر شدن متن به سه‌نقطه (پیش‌فرض حدود ۱۲px بود) */
        padding-right:4px !important;
    }}

    [class*="st-key-session_"] button > div,
    [class*="st-key-session_"] button [data-testid="stMarkdownContainer"]{{
        display:flex !important;
        justify-content:flex-start !important;
        width:100% !important;
        text-align:right !important;
        direction:rtl !important;
    }}

    [class*="st-key-session_"] button p{{
        display:block !important;
        width:100% !important;
        text-align:right !important;
        overflow:hidden !important;
        text-overflow:ellipsis !important;
        white-space:nowrap !important;
        max-width:100% !important;
    }}

    /* دکمه‌ی سه‌نقطه - فقط یک آیکون ساده، دقیقاً داخل همان کارت */
    [class*="st-key-menu_toggle_"] button{{
        background:transparent !important;
        border:none !important;
        color:#6b7280 !important;
        min-width:26px !important;
        width:26px !important;
        padding:0 !important;
        font-size:18px !important;
        font-weight:700 !important;
        line-height:1 !important;
    }}

    [class*="st-key-menu_toggle_"] button p{{
        color:#6b7280 !important;
    }}

    [class*="st-key-menu_toggle_"] button:hover{{
        color:#1f2937 !important;
        background:rgba(72,128,145,.15) !important;
        border-radius:8px !important;
    }}

    /* دکمه‌های «بله / انصراف» در تأیید حذف (تکی یا گروهی) -
       جمع‌وجور و شکیل به‌جای بلوک‌های بزرگ قبلی */
    [class*="st-key-confirm_delete_"] button,
    [class*="st-key-cancel_delete_"] button{{
        min-height:30px !important;
        padding:4px 6px !important;
        font-size:12.5px !important;
        border-radius:9px !important;
    }}

    [class*="st-key-confirm_delete_"] button{{
        background:#ef4444 !important;
        color:white !important;
        border:none !important;
    }}

    [class*="st-key-confirm_delete_"] button:hover{{
        background:#dc2626 !important;
    }}

    [class*="st-key-cancel_delete_"] button{{
        background:rgba(255,255,255,.8) !important;
        color:#374151 !important;
        border:1px solid rgba(209,213,219,.9) !important;
    }}

    [class*="st-key-cancel_delete_"] button:hover{{
        background:rgba(243,244,246,.9) !important;
    }}

    /* پنجره‌ی تأیید حذف (st.dialog) - همیشه خارج از سایدبار و
       روی صفحه‌ی اصلی باز می‌شود؛ ظاهر شیشه‌ای با رنگ برند
       (همان تیل هواپیماهای پس‌زمینه) و حرفه‌ای */
    [data-testid="stDialog"],
    div[role="dialog"]:not(:has([class*="st-key-delete_option_"])){{
        direction:rtl !important;
        font-family:'Vazirmatn', sans-serif !important;

        background:linear-gradient(
            135deg,
            rgba(72,128,145,.92),
            rgba(43,84,97,.95)
        ) !important;
        backdrop-filter:blur(24px) saturate(160%) !important;
        -webkit-backdrop-filter:blur(24px) saturate(160%) !important;
        border:1px solid rgba(255,255,255,.22) !important;
        border-radius:22px !important;
        box-shadow:0 24px 70px rgba(10,30,38,.45) !important;
    }}

    /* متن پیش‌فرض داخل دیالوگ (عنوان و...) سفید و خوانا؛ رنگ
       اختصاصی دکمه‌های بله/خیر پایین‌تر همچنان برتری دارد */
    [data-testid="stDialog"] *,
    div[role="dialog"]:not(:has([class*="st-key-delete_option_"])) *{{
        color:#ffffff !important;
    }}

    [data-testid="stDialog"] [data-testid="stHorizontalBlock"],
    div[role="dialog"]:not(:has([class*="st-key-delete_option_"])) [data-testid="stHorizontalBlock"]{{
        direction:rtl !important;
        flex-direction:row-reverse !important;
        gap:10px !important;
    }}

    /* آواتار پیام دستیار (ربات) - آبی ملایم به‌جای نارنجی */
    [data-testid="stChatMessageAvatarAssistant"]{{
        background-color:var(--soft-blue) !important;
    }}

    /* آواتار پیام کاربر - رنگی هماهنگ با آواتار ربات */
    [data-testid="stChatMessageAvatarUser"]{{
        background-color:var(--soft-user-color) !important;
        color:#1f2a4d !important;
    }}
    /* حذف فلش پیش فرض Streamlit Popover */
    [data-testid="stPopover"] button > div > svg,
    [data-testid="stPopover"] button svg,
    [data-testid="stPopover"] button [data-testid="stIconMaterial"] {{
        display:none !important;
    }}


    /* تنظیم دوباره دکمه سه نقطه */
    [data-testid="stPopover"] button {{

        background:transparent !important;
        color:#6b7280 !important;

        border:none !important;
        box-shadow:none !important;

        width:28px !important;
        min-width:28px !important;
        height:28px !important;

        padding:0 !important;

        font-size:18px !important;

        position:relative !important;
    }}



    /* حذف فضای خالی اطراف آیکون */
    [data-testid="stPopover"] button div {{
        gap:0 !important;
    }}

    /* حرف «⋮» مخفی می‌شود (فونت آن را به لبه‌ی کادر می‌چسباند) و
       به‌جایش سه نقطه با CSS دقیقاً وسط کادر هاور رسم می‌شود */
    [data-testid="stPopover"] button > *{{
        visibility:hidden !important;
    }}

    [data-testid="stPopover"] button::after{{
        content:"";
        position:absolute;
        top:50%;
        left:50%;
        width:2.5px;
        height:2.5px;
        margin:-1.25px 0 0 -1.25px;
        border-radius:50%;
        background:#6b7280;
        box-shadow:0 -5px 0 #6b7280, 0 5px 0 #6b7280;
        pointer-events:none;
    }}

    [data-testid="stPopover"] button:hover::after{{
        background:#1f2937;
        box-shadow:0 -5px 0 #1f2937, 0 5px 0 #1f2937;
    }}

    </style>
    """,
        unsafe_allow_html=True
    )
def render_header() -> None:
    """رندر کارت اصلی، لوگو، عنوان و زیرعنوان."""
    # هدر
    st.markdown("""
    
    <div class="main-card">
    
    <div class="logo">✈️</div>
    
    <div class="title">
    
    دستیار هوشمند بلیط
    
    </div>
    
    <div class="subtitle">
    
    ✨✈️ هوشمندانه انتخاب کن، آسوده پرواز کن 
    
    </div>
    
    """, unsafe_allow_html=True)

def inject_login_style():

    st.markdown(
    """
    <style>


    .email-login-card{

        background:rgba(255,255,255,0.45);

        backdrop-filter:blur(15px);
        -webkit-backdrop-filter:blur(15px);

        border:1px solid rgba(255,255,255,0.7);

        border-radius:22px;

        padding:25px;

        margin:25px auto;

        width:400px;

        box-shadow:
        0 10px 35px rgba(0,0,0,0.15);

    }


    .email-login-title{

        text-align:center;

        font-size:24px;

        font-weight:800;

        color:#111827;

        font-family:'Vazirmatn';

    }


    div[data-testid="stTextInput"] input{

        background:rgba(255,255,255,0.6)!important;

        border-radius:14px!important;

        border:1px solid rgba(255,255,255,0.8)!important;

        font-family:'Vazirmatn'!important;

    }


    .st-key-email_submit button,
    .st-key-email_login_button button{

        background:rgba(255,255,255,0.45)!important;

        backdrop-filter:blur(12px);

        color:#111827!important;

        border-radius:15px!important;

        border:1px solid rgba(255,255,255,0.7)!important;

        font-weight:700!important;

    }


    </style>
    """,
    unsafe_allow_html=True
    )


def inject_auth_style() -> None:
    st.markdown(
        """
        <style>

        .auth-btn-link{
            display:flex !important;
            align-items:center;
            justify-content:center;
            width:100%;
            height:58px;
            box-sizing:border-box;

            text-decoration:none !important;

            background: rgba(255, 255, 255, 0.45) !important;
            backdrop-filter: blur(14px) !important;
            -webkit-backdrop-filter: blur(14px) !important;

            border: 1px solid rgba(255, 255, 255, 0.75) !important;
            border-radius: 18px !important;

            box-shadow:
                0 5px 18px rgba(31, 41, 55, 0.10),
                inset 0 1px 0 rgba(255, 255, 255, 0.75) !important;

            color: #1f2937 !important;
            font-family: 'Vazirmatn', sans-serif !important;
            font-size: 16px !important;
            font-weight: 700 !important;

            transition: all 0.25s ease !important;
        }
        .st-key-email_login_button button p{
            font-family:'Vazirmatn', sans-serif !important;
            font-size:16px !important;
            font-weight:700 !important;
            color:#1f2937 !important;
            text-align:center !important;
        }
        .auth-button-link{
            font-weight:700 !important;
        }
        .auth-btn-link:hover{
            background: rgba(37, 99, 235, 0.16) !important;
            border-color: rgba(37, 99, 235, 0.45) !important;
            box-shadow:
                0 8px 22px rgba(37, 99, 235, 0.16),
                inset 0 1px 0 rgba(255, 255, 255, 0.85) !important;
            transform: translateY(-2px) !important;
        }

        .st-key-email_login_button button{
            width:100% !important;
            min-height:58px !important;

            background: rgba(255, 255, 255, 0.45) !important;
            backdrop-filter: blur(14px) !important;
            -webkit-backdrop-filter: blur(14px) !important;

            border: 1px solid rgba(255, 255, 255, 0.75) !important;
            border-radius: 18px !important;

            box-shadow:
                0 5px 18px rgba(31, 41, 55, 0.10),
                inset 0 1px 0 rgba(255, 255, 255, 0.75) !important;

            color: #1f2937 !important;
            font-family: 'Vazirmatn', sans-serif !important;
            font-size: 16px !important;
            font-weight: 700 !important;

            transition: all 0.25s ease !important;
        }

        .st-key-email_login_button button:hover{
            background: rgba(37, 99, 235, 0.16) !important;
            border-color: rgba(37, 99, 235, 0.45) !important;
            box-shadow:
                0 8px 22px rgba(37, 99, 235, 0.16),
                inset 0 1px 0 rgba(255, 255, 255, 0.85) !important;
            transform: translateY(-2px) !important;
        }

        .st-key-email_login_button button p{
            font-family: 'Vazirmatn', sans-serif !important;
            color: #1f2937 !important;
            text-align:center !important;
        }


        /* دکمه ورود / ثبت نام مهمان */

/* دکمه ورود / ثبت نام مهمان */

.guest-login-fixed{
    position:fixed !important;
    top:20px !important;
    right:30px !important;
    z-index:999999 !important;

    display:flex !important;
    align-items:center !important;
    justify-content:center !important;

    width:180px !important;
    min-height:42px !important;
    box-sizing:border-box !important;

    background:rgba(255,255,255,0.35) !important;

    backdrop-filter:blur(14px) !important;
    -webkit-backdrop-filter:blur(14px) !important;

    border:1px solid rgba(255,255,255,0.75) !important;
    border-radius:16px !important;

    box-shadow:
        0 5px 18px rgba(31,41,55,.10),
        inset 0 1px 0 rgba(255,255,255,.8) !important;

    color:#1f2937 !important;
    text-decoration:none !important;

    font-family:'Vazirmatn',sans-serif !important;
    font-size:14px !important;
    font-weight:700 !important;

    transition:.25s ease !important;
    cursor:pointer;
}

.guest-login-fixed:hover{
    background:rgba(37,99,235,.15) !important;
    transform:translateY(-2px);
}
        .st-key-guest_login_button .guest-login-link{

    display:flex !important;
    align-items:center !important;
    justify-content:center !important;

    width:180px !important;
    min-height:42px !important;
    box-sizing:border-box !important;

    background:rgba(255,255,255,0.35) !important;

    backdrop-filter:blur(14px) !important;
    -webkit-backdrop-filter:blur(14px) !important;

    border:1px solid rgba(255,255,255,0.75) !important;
    border-radius:16px !important;

    box-shadow:
    0 5px 18px rgba(31,41,55,.10),
    inset 0 1px 0 rgba(255,255,255,.8) !important;

    color:#1f2937 !important;
    text-decoration:none !important;

    font-family:'Vazirmatn',sans-serif !important;
    font-size:14px !important;
    font-weight:700 !important;

    transition:.25s ease !important;
    cursor:pointer;
}

.st-key-guest_login_button .guest-login-link:hover{
    background:rgba(37,99,235,.15) !important;
    transform:translateY(-2px);
}

        </style>
        """,
        unsafe_allow_html=True
    )



def inject_user_box_style() -> None:
    """باکس کاربر به‌صورت فیکس در پایین سایدبار."""
    st.markdown(
        """
    <style>

    /* جای خالی ته لیست گفتگوها تا زیر باکس کاربر قایم نشه */
/* جا برای باکس پایین سایدبار */
[data-testid="stSidebarUserContent"]{
    padding-bottom: 90px !important;
}


/* باکس کاربر همیشه پایین سایدبار */
.st-key-user_box_container{
    position: fixed !important;

    bottom: 0 !important;
    left: 0 !important;

    width: 21rem !important;
padding: 10px 16px 30px 16px !important;

    box-sizing: border-box !important;

    background: rgba(255,255,255,.97) !important;

    backdrop-filter: blur(16px);

    z-index: 999998 !important;
}

    .user-details{
        width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
        background:#ffffff;
        border:1px solid var(--soft-blue-border, #a9cdf0);
        border-radius:16px;
        padding:10px 14px;
        box-shadow:0 4px 14px rgba(111,163,214,.12);
    }

    .user-summary{
        display:flex;
        align-items:center;
        gap:10px;
        cursor:pointer;
        list-style:none;
        direction:rtl;
        outline:none;
    }

    .user-summary::-webkit-details-marker{ display:none; }
    .user-summary::marker{ content:""; }

    .user-chevron{
        margin-right:auto;
        font-size:12px;
        color:#9ca3af;
        transition: transform .2s ease;
    }

    .user-details[open] .user-chevron{
        transform: rotate(180deg);
    }

    .user-avatar-img{
        width:40px;
        height:40px;
        border-radius:50%;
        object-fit:cover;
        border:1px solid var(--soft-blue-border, #a9cdf0);
        flex-shrink:0;
    }

    .user-avatar-fallback{
        width:40px;
        height:40px;
        border-radius:50%;
        background:var(--soft-blue, #6fa3d6);
        color:white;
        font-family:'Vazirmatn', sans-serif !important;
        font-weight:800;
        font-size:16px;
        display:flex;
        align-items:center;
        justify-content:center;
        flex-shrink:0;
    }

    .user-box-text{ overflow:hidden; text-align:right; }

    .user-box-name{
        font-family:'Vazirmatn', sans-serif !important;
        font-weight:700;
        font-size:14px;
        color:#1f2937;
        white-space:nowrap;
        overflow:hidden;
        text-overflow:ellipsis;
    }

    .user-box-email{
        font-family:'Vazirmatn', sans-serif !important;
        font-weight:400;
        font-size:12px;
        color:#6b7280;
        white-space:nowrap;
        overflow:hidden;
        text-overflow:ellipsis;
        direction:ltr;
        text-align:right;
    }

    .st-key-logout_button{
        display:none !important;
        margin-top:10px !important;
    }

    .st-key-user_box_container:has(.user-details[open]) .st-key-logout_button{
        display:block !important;
    }

    .st-key-logout_button button{
        width:100% !important;
        background: rgba(239,68,68,.10) !important;
        color:#ef4444 !important;
        border:1px solid rgba(239,68,68,.35) !important;
    }

    .st-key-logout_button button:hover{
        background: rgba(239,68,68,.20) !important;
    }

    .st-key-logout_button button p{
        color:#ef4444 !important;
        font-weight:700 !important;
    }

    </style>
    """,
        unsafe_allow_html=True,
    )



def inject_flight_ticket():

    st.markdown(
"""
<style>


.ticket-card{

    background: rgba(255,255,255,0.92);

    border-radius:28px;

    padding:20px;

    margin-bottom:25px;

    box-shadow:
    0 10px 35px rgba(0,0,0,0.10);

    backdrop-filter:blur(12px);

    direction:rtl;


}

.seat-info{

margin:20px 0;

font-size:16px;

color:#444 !important;

opacity:1 !important;

}

.flight-source{

font-size:13px;

color:#444 !important;

opacity:1 !important;

display:block;

margin-top:6px;

}

.plane-icon{

width:35px;

height:35px;

object-fit:contain;

opacity:0.55;

}

.ticket-content{

display:flex;

flex-direction:row;

gap:20px;

}



.flight-section{

flex:1;

}



.ticket-header{

display:flex;

justify-content:space-between;

align-items:center;

}

.airline-name{
    display:flex;
    align-items:center;
    gap:12px;
    font-size:22px;
    font-weight:700;
    color:#488091;
}

.airline-logo {
    width: 48px;
    height: 48px;

    object-fit: contain;

    border-radius: 8px;
}

.flight-tags span{

    background:rgba(72,128,145,0.15);

    color:#488091;

    padding:7px 18px;

    border-radius:20px;

    font-size:14px;

    margin-left:8px;

    font-weight:600;

}



.route-section{

display:flex;

justify-content:center;

align-items:center;

gap:30px;

margin:20px 0;

}



.airport{

text-align:center;

}



.airline-name{

    font-size:22px;

    font-weight:700;

    color:#488091;

}

.city{

    font-size:18px;

    color:#333;

}


.time{

    font-size:32px;

    font-weight:700;

    color:#488091;

}



.flight-line{

display:flex;

align-items:center;

gap:10px;

color:#888;

}



.line{

width:70px;

border-top:2px dashed #ccc;

}



.flight-details{

    display:flex;

    justify-content:space-around;

    background:#6fa3d6;

    color:#444;

    border-radius:18px;

    padding:15px;

    text-align:center;

}



.price-section{

width:230px;

border-right:1px solid #ddd;

display:flex;

flex-direction:column;

justify-content:center;

align-items:center;

}



.price-title{

font-size:14px;

color:#777;

}



.ticket-price{

font-size:27px;

font-weight:bold;

color:#488091;

margin:15px 0;

}


/* دکمه «انتخاب پرواز» - این کلاسیه که واقعاً در HTML رندر می‌شود */
.select-flight{

background:#488091 !important;

color:white !important;

border:none;

padding:13px 35px;

border-radius:14px;

display:inline-block;

text-decoration:none !important;

font-weight:700;

transition:background .2s ease;
}

.select-flight:hover{

background:#3d6d7b !important;
}

/* این سلکتور در نسخه‌ی فعلی HTML استفاده نمی‌شود (چون دکمه یک
   تگ <a class="select-flight"> است نه <button>)؛ برای سازگاری با
   نسخه‌های احتمالی دیگر پروژه نگه داشته شده است */
[class*="st-key-select_flight_"] button {

 background:#488091 !important;

color:white !important;

border:none;

padding:13px 35px;

border-radius:14px;

display:inline-block;

text-decoration:none !important;
}



</style>
""",
unsafe_allow_html=True
)