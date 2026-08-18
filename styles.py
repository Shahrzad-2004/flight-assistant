"""
استایل‌ها و ظاهر برنامه (CSS تزریق‌شده با st.markdown) و رندر هدر.
"""
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
    
        margin: 0 auto;
    
        padding:35px;
    
        box-shadow:0 20px 60px rgba(0,0,0,.18);
    
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
    
    
    /* استایل شیشه‌ای مخصوص چهار دکمه کلاس پرواز */
    
    .st-key-economy_button button,
    .st-key-business_button button,
    .st-key-first_button button,
    .st-key-unspecified_button button,
    .st-key-passenger_enter_button button,
    .st-key-passenger_default_button button,
    .st-key-save_passenger_counts_button button {
    
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
    .st-key-save_passenger_counts_button button p {
    
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
    .st-key-save_passenger_counts_button button:hover {
    
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
    .st-key-save_passenger_counts_button button:active {
    
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
