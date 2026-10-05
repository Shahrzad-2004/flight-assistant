import json

import streamlit as st
import streamlit.components.v1 as components


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

        /* شیشه‌ای ملایم (glassmorphism): نیمه‌شفاف، بلور، حاشیه‌ی نرم
           و سایه‌ی کم‌عمق؛ به‌اندازه‌ای مات که متن کاملاً خوانا بماند */
        background:linear-gradient(
            145deg,
            rgba(255,255,255,.78),
            rgba(255,255,255,.60)
        );

        backdrop-filter:blur(18px) saturate(140%);
        -webkit-backdrop-filter:blur(18px) saturate(140%);

        border-radius:28px;

        width:700px;
        max-width:calc(100vw - 40px);
        box-sizing:border-box;

        margin: 0 auto 30px auto;

        padding:50px;

        border:1px solid rgba(255,255,255,.78);

        box-shadow:
            0 18px 42px rgba(72,128,145,.16),
            0 2px 8px rgba(31,41,55,.05),
            inset 0 1px 0 rgba(255,255,255,.85);

    }

    /* مرورگرهایی که backdrop-filter ندارند: پس‌زمینه‌ی مات‌تر */
    @supports not ((backdrop-filter:blur(1px)) or (-webkit-backdrop-filter:blur(1px))){
        .main-card{
            background:rgba(255,255,255,.90);
        }
    }
    
    /* لوگو: مسیر پرواز نقطه‌چین از مبدا (A) تا مقصد (B) با یک حلقه‌ی کوچک وسط راه
       + هواپیمای متحرک روی مسیر. خود ✈️ داخل HTML باقی می‌ماند ولی مخفی است؛
       مسیر و هواپیما با CSS رسم می‌شوند. ابعاد ثابت است تا چیدمان کارت نپرد. */

    .logo{

        position:relative;

        width:320px;
        height:112px;

        margin:0 auto 8px auto;

        font-size:0;
        line-height:0;
        color:transparent;

        background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='320' height='112' viewBox='0 0 320 112'%3E%3Cpath d='M23.9 92.0 L25.2 91.9 L26.7 91.8 L28.4 91.6 L30.3 91.5 L32.3 91.3 L34.5 91.1 L36.8 91.0 L39.2 90.8 L41.7 90.6 L44.2 90.4 L46.8 90.2 L49.3 90.0 L51.9 89.8 L54.4 89.6 L56.9 89.4 L59.3 89.2 L61.6 89.0 L63.8 88.9 L65.9 88.7 L67.8 88.5 L69.6 88.4 L71.4 88.2 L73.2 88.1 L75.0 87.9 L76.7 87.8 L78.4 87.7 L80.1 87.6 L81.7 87.5 L83.4 87.4 L85.0 87.3 L86.6 87.3 L88.1 87.2 L89.7 87.2 L91.2 87.1 L92.7 87.1 L94.2 87.0 L95.7 86.9 L97.1 86.9 L98.6 86.8 L100.0 86.7 L101.5 86.6 L102.9 86.4 L104.2 86.2 L105.6 86.0 L106.9 85.8 L108.3 85.5 L109.6 85.2 L110.9 84.8 L112.2 84.5 L113.5 84.1 L114.8 83.6 L116.2 83.1 L117.5 82.6 L118.9 82.1 L120.3 81.5 L121.7 80.9 L123.1 80.3 L124.6 79.6 L126.1 78.9 L127.6 78.1 L129.3 77.4 L130.9 76.5 L132.6 75.6 L134.4 74.7 L136.2 73.7 L138.0 72.7 L139.8 71.6 L141.6 70.5 L143.4 69.4 L145.2 68.2 L147.0 67.0 L148.7 65.8 L150.4 64.6 L152.0 63.4 L153.5 62.1 L155.0 60.9 L156.4 59.7 L157.7 58.6 L158.9 57.5 L160.0 56.4 L161.0 55.3 L162.0 54.3 L162.8 53.3 L163.6 52.3 L164.3 51.4 L165.0 50.5 L165.6 49.6 L166.1 48.7 L166.6 47.8 L167.0 46.9 L167.4 46.1 L167.7 45.2 L167.9 44.4 L168.1 43.5 L168.2 42.6 L168.3 41.8 L168.4 40.9 L168.4 39.9 L168.3 39.0 L168.2 38.0 L168.1 37.0 L167.8 35.9 L167.5 34.8 L167.1 33.6 L166.6 32.5 L166.0 31.2 L165.4 30.0 L164.7 28.8 L164.0 27.6 L163.2 26.4 L162.4 25.2 L161.6 24.0 L160.8 22.8 L159.9 21.7 L159.1 20.6 L158.2 19.6 L157.4 18.7 L156.6 17.8 L155.8 17.0 L155.1 16.3 L154.3 15.6 L153.6 14.9 L152.9 14.3 L152.2 13.8 L151.5 13.3 L150.8 12.8 L150.1 12.3 L149.4 11.9 L148.7 11.5 L147.9 11.2 L147.2 10.9 L146.4 10.6 L145.7 10.4 L144.9 10.2 L144.1 10.0 L143.3 9.9 L142.5 9.8 L141.7 9.7 L140.9 9.7 L140.0 9.8 L139.1 9.8 L138.2 9.9 L137.2 10.1 L136.1 10.3 L135.1 10.5 L134.0 10.8 L132.9 11.1 L131.8 11.4 L130.7 11.8 L129.6 12.2 L128.5 12.7 L127.4 13.2 L126.3 13.7 L125.3 14.2 L124.3 14.8 L123.4 15.4 L122.4 16.1 L121.6 16.7 L120.8 17.4 L120.1 18.1 L119.4 18.8 L118.7 19.6 L118.0 20.4 L117.4 21.3 L116.8 22.2 L116.2 23.2 L115.6 24.1 L115.1 25.2 L114.6 26.2 L114.1 27.3 L113.7 28.4 L113.3 29.4 L113.0 30.5 L112.7 31.6 L112.4 32.7 L112.2 33.8 L112.0 34.9 L111.9 36.0 L111.8 37.0 L111.8 38.0 L111.8 39.0 L111.9 40.0 L112.0 41.1 L112.2 42.2 L112.4 43.3 L112.7 44.4 L113.0 45.5 L113.3 46.6 L113.7 47.6 L114.1 48.7 L114.6 49.8 L115.1 50.8 L115.6 51.9 L116.2 52.8 L116.8 53.8 L117.4 54.7 L118.0 55.6 L118.7 56.4 L119.4 57.2 L120.1 57.9 L120.8 58.6 L121.5 59.3 L122.3 59.9 L123.1 60.5 L123.9 61.0 L124.7 61.6 L125.6 62.1 L126.5 62.6 L127.5 63.0 L128.5 63.4 L129.5 63.8 L130.5 64.2 L131.6 64.5 L132.7 64.9 L133.8 65.2 L135.0 65.4 L136.2 65.7 L137.4 65.9 L138.7 66.1 L140.0 66.2 L141.3 66.4 L142.6 66.5 L143.9 66.6 L145.2 66.6 L146.5 66.6 L147.9 66.6 L149.2 66.6 L150.6 66.5 L152.0 66.4 L153.5 66.3 L155.0 66.1 L156.6 65.9 L158.2 65.7 L159.9 65.4 L161.6 65.1 L163.4 64.8 L165.3 64.4 L167.2 64.0 L169.2 63.5 L171.3 63.0 L173.4 62.5 L175.5 61.9 L177.7 61.3 L179.9 60.6 L182.0 59.9 L184.1 59.2 L186.2 58.4 L188.3 57.6 L190.3 56.8 L192.2 56.0 L194.1 55.2 L196.0 54.4 L197.7 53.6 L199.5 52.8 L201.2 52.0 L202.8 51.2 L204.4 50.5 L206.0 49.8 L207.5 49.1 L209.1 48.4 L210.7 47.7 L212.3 47.0 L214.0 46.3 L215.7 45.7 L217.5 45.0 L219.3 44.4 L221.2 43.7 L223.2 43.1 L225.2 42.4 L227.4 41.8 L229.5 41.2 L231.7 40.6 L234.0 40.0 L236.3 39.4 L238.6 38.8 L241.0 38.2 L243.3 37.6 L245.7 37.1 L248.1 36.5 L250.4 36.0 L252.8 35.5 L255.4 34.9 L258.0 34.3 L260.6 33.8 L263.4 33.2 L266.1 32.6 L268.9 32.0 L271.7 31.5 L274.4 30.9 L277.1 30.3 L279.8 29.8 L282.4 29.2 L284.8 28.7 L287.2 28.2 L289.4 27.8 L291.5 27.4 L293.4 27.0 L295.2 26.6 L296.7 26.3 L298.0 26.0' fill='none' stroke='%23488091' stroke-opacity='.6' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' stroke-dasharray='6 7'/%3E%3Ccircle cx='24' cy='92' r='5' fill='%23488091' fill-opacity='.8'/%3E%3Ccircle cx='298' cy='26' r='5' fill='white' fill-opacity='.95' stroke='%23488091' stroke-opacity='.8' stroke-width='2.2'/%3E%3C/svg%3E") center / 320px 112px no-repeat;

    }

    .logo::after{

        content:"";

        position:absolute;
        left:0;
        top:0;
        width:36px;
        height:36px;

        background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath transform='rotate(90 12 12)' fill='%23488091' d='M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z'/%3E%3C/svg%3E") center / contain no-repeat;
        filter:drop-shadow(0 2px 3px rgba(72,128,145,.30));

        /* دقیقاً همان مسیر خط‌چین داخل پس‌زمینه */
        offset-path:path("M23.9 92.0 L25.2 91.9 L26.7 91.8 L28.4 91.6 L30.3 91.5 L32.3 91.3 L34.5 91.1 L36.8 91.0 L39.2 90.8 L41.7 90.6 L44.2 90.4 L46.8 90.2 L49.3 90.0 L51.9 89.8 L54.4 89.6 L56.9 89.4 L59.3 89.2 L61.6 89.0 L63.8 88.9 L65.9 88.7 L67.8 88.5 L69.6 88.4 L71.4 88.2 L73.2 88.1 L75.0 87.9 L76.7 87.8 L78.4 87.7 L80.1 87.6 L81.7 87.5 L83.4 87.4 L85.0 87.3 L86.6 87.3 L88.1 87.2 L89.7 87.2 L91.2 87.1 L92.7 87.1 L94.2 87.0 L95.7 86.9 L97.1 86.9 L98.6 86.8 L100.0 86.7 L101.5 86.6 L102.9 86.4 L104.2 86.2 L105.6 86.0 L106.9 85.8 L108.3 85.5 L109.6 85.2 L110.9 84.8 L112.2 84.5 L113.5 84.1 L114.8 83.6 L116.2 83.1 L117.5 82.6 L118.9 82.1 L120.3 81.5 L121.7 80.9 L123.1 80.3 L124.6 79.6 L126.1 78.9 L127.6 78.1 L129.3 77.4 L130.9 76.5 L132.6 75.6 L134.4 74.7 L136.2 73.7 L138.0 72.7 L139.8 71.6 L141.6 70.5 L143.4 69.4 L145.2 68.2 L147.0 67.0 L148.7 65.8 L150.4 64.6 L152.0 63.4 L153.5 62.1 L155.0 60.9 L156.4 59.7 L157.7 58.6 L158.9 57.5 L160.0 56.4 L161.0 55.3 L162.0 54.3 L162.8 53.3 L163.6 52.3 L164.3 51.4 L165.0 50.5 L165.6 49.6 L166.1 48.7 L166.6 47.8 L167.0 46.9 L167.4 46.1 L167.7 45.2 L167.9 44.4 L168.1 43.5 L168.2 42.6 L168.3 41.8 L168.4 40.9 L168.4 39.9 L168.3 39.0 L168.2 38.0 L168.1 37.0 L167.8 35.9 L167.5 34.8 L167.1 33.6 L166.6 32.5 L166.0 31.2 L165.4 30.0 L164.7 28.8 L164.0 27.6 L163.2 26.4 L162.4 25.2 L161.6 24.0 L160.8 22.8 L159.9 21.7 L159.1 20.6 L158.2 19.6 L157.4 18.7 L156.6 17.8 L155.8 17.0 L155.1 16.3 L154.3 15.6 L153.6 14.9 L152.9 14.3 L152.2 13.8 L151.5 13.3 L150.8 12.8 L150.1 12.3 L149.4 11.9 L148.7 11.5 L147.9 11.2 L147.2 10.9 L146.4 10.6 L145.7 10.4 L144.9 10.2 L144.1 10.0 L143.3 9.9 L142.5 9.8 L141.7 9.7 L140.9 9.7 L140.0 9.8 L139.1 9.8 L138.2 9.9 L137.2 10.1 L136.1 10.3 L135.1 10.5 L134.0 10.8 L132.9 11.1 L131.8 11.4 L130.7 11.8 L129.6 12.2 L128.5 12.7 L127.4 13.2 L126.3 13.7 L125.3 14.2 L124.3 14.8 L123.4 15.4 L122.4 16.1 L121.6 16.7 L120.8 17.4 L120.1 18.1 L119.4 18.8 L118.7 19.6 L118.0 20.4 L117.4 21.3 L116.8 22.2 L116.2 23.2 L115.6 24.1 L115.1 25.2 L114.6 26.2 L114.1 27.3 L113.7 28.4 L113.3 29.4 L113.0 30.5 L112.7 31.6 L112.4 32.7 L112.2 33.8 L112.0 34.9 L111.9 36.0 L111.8 37.0 L111.8 38.0 L111.8 39.0 L111.9 40.0 L112.0 41.1 L112.2 42.2 L112.4 43.3 L112.7 44.4 L113.0 45.5 L113.3 46.6 L113.7 47.6 L114.1 48.7 L114.6 49.8 L115.1 50.8 L115.6 51.9 L116.2 52.8 L116.8 53.8 L117.4 54.7 L118.0 55.6 L118.7 56.4 L119.4 57.2 L120.1 57.9 L120.8 58.6 L121.5 59.3 L122.3 59.9 L123.1 60.5 L123.9 61.0 L124.7 61.6 L125.6 62.1 L126.5 62.6 L127.5 63.0 L128.5 63.4 L129.5 63.8 L130.5 64.2 L131.6 64.5 L132.7 64.9 L133.8 65.2 L135.0 65.4 L136.2 65.7 L137.4 65.9 L138.7 66.1 L140.0 66.2 L141.3 66.4 L142.6 66.5 L143.9 66.6 L145.2 66.6 L146.5 66.6 L147.9 66.6 L149.2 66.6 L150.6 66.5 L152.0 66.4 L153.5 66.3 L155.0 66.1 L156.6 65.9 L158.2 65.7 L159.9 65.4 L161.6 65.1 L163.4 64.8 L165.3 64.4 L167.2 64.0 L169.2 63.5 L171.3 63.0 L173.4 62.5 L175.5 61.9 L177.7 61.3 L179.9 60.6 L182.0 59.9 L184.1 59.2 L186.2 58.4 L188.3 57.6 L190.3 56.8 L192.2 56.0 L194.1 55.2 L196.0 54.4 L197.7 53.6 L199.5 52.8 L201.2 52.0 L202.8 51.2 L204.4 50.5 L206.0 49.8 L207.5 49.1 L209.1 48.4 L210.7 47.7 L212.3 47.0 L214.0 46.3 L215.7 45.7 L217.5 45.0 L219.3 44.4 L221.2 43.7 L223.2 43.1 L225.2 42.4 L227.4 41.8 L229.5 41.2 L231.7 40.6 L234.0 40.0 L236.3 39.4 L238.6 38.8 L241.0 38.2 L243.3 37.6 L245.7 37.1 L248.1 36.5 L250.4 36.0 L252.8 35.5 L255.4 34.9 L258.0 34.3 L260.6 33.8 L263.4 33.2 L266.1 32.6 L268.9 32.0 L271.7 31.5 L274.4 30.9 L277.1 30.3 L279.8 29.8 L282.4 29.2 L284.8 28.7 L287.2 28.2 L289.4 27.8 L291.5 27.4 L293.4 27.0 L295.2 26.6 L296.7 26.3 L298.0 26.0");
        offset-rotate:auto;
        offset-anchor:50% 50%;
        offset-distance:0%;

        opacity:0;
        will-change:offset-distance, opacity;
        animation:hero-plane-flight 10.5s linear infinite;

    }

    /* چرخه ≈ ۱۰٫۵ ثانیه (آهسته‌تر از قبل): پرواز حدود ۷٫۵ ثانیه (شامل حلقه‌ی بزرگ‌تر)، مکث حدود ۱ ثانیه
       در مقصد، محو شدن و شروع دوباره از مبدا. جهت هواپیما با شیب مسیر می‌چرخد */
    @keyframes hero-plane-flight{
        0%   { offset-distance:0%;   opacity:0; animation-timing-function:ease-out; }
        6%   { offset-distance:0%;   opacity:1; animation-timing-function:ease-in-out; }
        78%  { offset-distance:100%; opacity:1; }
        92%  { offset-distance:100%; opacity:1; }
        97%  { offset-distance:100%; opacity:0; }
        100% { offset-distance:0%;   opacity:0; }
    }

    /* صفحه‌های خیلی باریک: کل مسیر کمی کوچک می‌شود تا از کارت بیرون نزند */
    @media (max-width: 480px){
        .logo{
            zoom:.8;
        }
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
        direction:rtl;

        font-size:15px;

        font-weight:500;

        color:#374151;

        /* ارتفاع ثابت تا هنگام تایپ/پاک شدن متن، چیدمان نپرد */
        min-height:1.9em;
        line-height:1.9;

    }

    /* مکان‌نمای چشمک‌زن انتهای متن تایپ‌شونده */
    .hero-caret{
        display:inline-block;
        width:2px;
        height:1.15em;
        margin-inline-start:4px;
        vertical-align:text-bottom;
        border-radius:1px;
        background:#488091;
        animation:hero-caret-blink 1.1s steps(1, end) infinite;
    }

    @keyframes hero-caret-blink{
        0%, 55%   { opacity:.85; }
        56%, 100% { opacity:0;   }
    }

    /* اگر جاوااسکریپت اجرا نشد (یا کاربر کاهش حرکت خواسته)، جمله‌ی
       اول به‌صورت ثابت نمایش داده می‌شود. وقتی انیمیشن روشن شد
       (data-typing=on) این جمله‌ی پشتیبان کنار می‌رود */
    .hero-typed-text:empty::before{
        content:attr(data-fallback);
        opacity:0;
        animation:hero-fallback-in .01s linear 2.6s forwards;
    }

    .subtitle[data-typing="on"] .hero-typed-text:empty::before{
        content:"";
    }

    @keyframes hero-fallback-in{
        to{ opacity:1; }
    }

    @media (prefers-reduced-motion: reduce){
        .logo::after{ animation:none !important; opacity:1 !important; offset-distance:100% !important; }
        .hero-caret{ animation:none !important; opacity:0 !important; }
        .hero-typed-text:empty::before{
            animation:none !important;
            opacity:1 !important;
        }
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

    /* دکمه‌ی فلش ارسال (submit) داخل کادر چت - هم‌رنگ برند */
    [data-testid="stChatInputSubmitButton"]{
        background:#488091 !important;
        border-color:#488091 !important;
    }

    [data-testid="stChatInputSubmitButton"]:hover{
        background:#3d6d7b !important;
        border-color:#3d6d7b !important;
    }

    [data-testid="stChatInputSubmitButton"] svg{
        fill:#ffffff !important;
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
    

    /* ===== چک‌لیست نوع (کلاس) پرواز: متن مشکی ===== */

    [class*="st-key-cabin_filter_"],
    [class*="st-key-cabin_filter_"] label,
    [class*="st-key-cabin_filter_"] p,
    [class*="st-key-cabin_filter_"] span {
        color: #000000 !important;
        font-family: 'Vazirmatn', sans-serif !important;
        font-weight: 600 !important;
        direction: rtl !important;
    }

    /* تگ کلاس پرواز داخل کارت بلیط: مشکی */
    .flight-tags span.cabin-tag {
        color: #000000 !important;
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

    /* نوار کناری سمت راست (مناسب چیدمان راست‌به‌چپ).
       ظرف اصلی استریم‌لیت یک flex افقی است؛ معکوس کردن ترتیب آن
       نوار کناری را به راست می‌برد و محتوای اصلی خودکار با آن
       جمع و جور می‌شود */
    [data-testid="stAppViewContainer"]{{
        flex-direction:row-reverse !important;
    }}

    /* ظاهر کلی نوار کناری */
    [data-testid="stSidebar"]{{
        background:rgba(255,255,255,.92) !important;
        backdrop-filter:blur(16px);
        border-right:none !important;
        border-left:1px solid rgba(72,128,145,.18) !important;
        box-shadow:-6px 0 24px rgba(72,128,145,.08) !important;
    }}

    /* جلوگیری از اسکرول افقی هنگام انیمیشن گذار. عمداً clip (نه hidden):
       hidden یک scroll container می‌سازد و جای ردیف sticky «بایگانی»
       را به‌هم می‌ریزد؛ clip فقط برش می‌دهد */
    [data-testid="stSidebar"],
    [data-testid="stSidebarContent"],
    [data-testid="stSidebarUserContent"]{{
        overflow-x:clip !important;
    }}

    /* دستگیره‌ی تغییر عرض نوار کناری: چون نوار حالا سمت راست است،
       جهت کشیدنش برعکس می‌شد؛ عرض ثابت می‌ماند */
    [data-testid="stSidebar"] [data-testid*="esiz"],
    [data-testid="stSidebar"] [class*="esizer"]{{
        display:none !important;
    }}

    /* موبایل: اگر استریم‌لیت نوار را روی صفحه (fixed) می‌کشد، از راست بیاید */
    @media (max-width: 640px){{
        [data-testid="stSidebar"]{{
            left:auto !important;
            right:0 !important;
        }}
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
        right:14px;
        left:auto !important;
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

    /* سه‌نقطه‌ی هر گفتگو سمت چپ کارت؛ نام گفتگو سمت راست.
       (ردیف داخل کارت با rtl + row عادی چیده می‌شود: ستون اول = راست) */
    [data-testid="stSidebar"] [class*="st-key-chat_card_"] [data-testid="stHorizontalBlock"]{{
        flex-direction:row !important;
        direction:rtl !important;
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

    /* گزینه‌های پین / آرشیو / تغییر نام در منوی سه‌نقطه - هم‌قد و
       هم‌شکل دکمه‌ی حذف، ولی با رنگ خنثی و هماهنگ با برند */
    [class*="st-key-pin_option_"] button,
    [class*="st-key-archive_option_"] button,
    [class*="st-key-rename_option_"] button{{
        background:#f1f7f9 !important;
        color:#3d6d7b !important;
        border:1px solid var(--accent) !important;
        border-radius:10px !important;
        min-height:35px !important;
        box-shadow:none !important;
    }}

    [class*="st-key-pin_option_"] button p,
    [class*="st-key-archive_option_"] button p,
    [class*="st-key-rename_option_"] button p{{
        color:#3d6d7b !important;
    }}

    [class*="st-key-pin_option_"] button:hover,
    [class*="st-key-archive_option_"] button:hover,
    [class*="st-key-rename_option_"] button:hover{{
        background:#e2eef2 !important;
        border-color:var(--accent-hover) !important;
    }}

    /* فاصله‌ی جمع‌وجور بین گزینه‌های منو */
    div[data-baseweb="popover"]:has([class*="st-key-delete_option_"]) [data-testid="stVerticalBlock"]{{
        gap:.4rem !important;
    }}

    /* ورودی «بایگانی»: زیر لیست گفتگوها و بالای باکس کاربر، با خط جداکننده.
       اگر لیست طولانی باشد این ردیف بالای باکس کاربر می‌چسبد (sticky) تا
       همیشه در دسترس باشد؛ اگر sticky پشتیبانی نشود، ساده زیر لیست می‌ماند */
    .st-key-archive_entry_box{{
        position:sticky !important;
        bottom:104px;
        z-index:5;
        margin-top:14px !important;
        padding:10px 0 4px 0 !important;
        border-top:1px solid rgba(72,128,145,.25) !important;
        background:rgba(255,255,255,.96) !important;
    }}

    .st-key-archive_toggle_button button{{
        position:relative !important;
        background:rgba(255,255,255,.7) !important;
        color:#374151 !important;
        border:1px solid var(--soft-blue-border) !important;
        border-radius:14px !important;
        min-height:40px !important;
        box-shadow:none !important;
        direction:rtl !important;
        justify-content:flex-start !important;
        padding-inline:14px 30px !important;
    }}

    .st-key-archive_toggle_button button p{{
        color:#374151 !important;
        font-family:'Vazirmatn', sans-serif !important;
        font-size:14px !important;
        font-weight:600 !important;
    }}

    /* فلش کوچک سمت چپ = «ورود به بخش جدید» (نه لیست بازشونده) */
    .st-key-archive_toggle_button button::after{{
        content:"‹";
        position:absolute;
        left:14px;
        top:50%;
        transform:translateY(-52%);
        font-size:22px;
        line-height:1;
        color:#6b7280;
        transition:transform .2s ease, color .2s ease;
    }}

    .st-key-archive_toggle_button button:hover{{
        background:rgba(72,128,145,.10) !important;
        border-color:var(--accent) !important;
        transform:none !important;
    }}

    .st-key-archive_toggle_button button:hover::after{{
        color:var(--accent);
        transform:translate(-3px, -52%);
    }}

    /* کارت هدر نمای بایگانی: هم‌شکل کارت هدر نمای معمولی */
    .st-key-archive_header_box{{
        background:#ffffff !important;
        border:1px solid var(--soft-blue-border) !important;
        border-radius:18px !important;
        padding:16px 14px 14px 14px !important;
        margin-bottom:18px !important;
        box-shadow:0 4px 14px rgba(111,163,214,.12) !important;
    }}

    /* دکمه‌ی بازگشت: ساده و روشن، هم‌خانواده با دکمه‌های خنثی منو */
    .st-key-archive_back_button button{{
        background:#f1f7f9 !important;
        color:#3d6d7b !important;
        border:1px solid var(--accent) !important;
        border-radius:12px !important;
        min-height:38px !important;
        box-shadow:none !important;
        direction:rtl !important;
    }}

    .st-key-archive_back_button button p{{
        color:#3d6d7b !important;
        font-family:'Vazirmatn', sans-serif !important;
        font-weight:700 !important;
        font-size:14px !important;
    }}

    .st-key-archive_back_button button:hover{{
        background:#e2eef2 !important;
        border-color:var(--accent-hover) !important;
    }}

    /* گذار نرم بین نمای معمولی و نمای بایگانی.
       فقط روی همان rerunی که نما عوض شده اعمال می‌شود (کلید کانتینر
       عوض می‌شود). ورود به بایگانی از چپ، بازگشت از راست (RTL).
       fill-mode برابر backwards است تا بعد از پایان انیمیشن هیچ
       transform باقی نماند (transform باعث خراب شدن عناصر fixed می‌شود) */
    .st-key-sbview_anim_left{{
        animation:sb-view-in-left .34s cubic-bezier(.22,.8,.3,1) backwards;
    }}

    .st-key-sbview_anim_right{{
        animation:sb-view-in-right .34s cubic-bezier(.22,.8,.3,1) backwards;
    }}

    @keyframes sb-view-in-left{{
        from{{ opacity:0; transform:translateX(-34px); }}
        to{{   opacity:1; transform:translateX(0); }}
    }}

    @keyframes sb-view-in-right{{
        from{{ opacity:0; transform:translateX(34px); }}
        to{{   opacity:1; transform:translateX(0); }}
    }}

    @media (prefers-reduced-motion: reduce){{
        .st-key-sbview_anim_left,
        .st-key-sbview_anim_right{{
            animation:none !important;
        }}
    }}

    /* پنجره‌ی تغییر نام: چون متن‌های دیالوگ سفید است، ورودی متن باید
       پس‌زمینه‌ی روشن و متن تیره داشته باشد تا خوانا بماند */
    [class*="st-key-rename_input_"] input{{
        color:#1f2937 !important;
        -webkit-text-fill-color:#1f2937 !important;
        background:#ffffff !important;
        direction:rtl !important;
        text-align:right !important;
    }}

    [class*="st-key-rename_input_"] [data-baseweb="input"],
    [class*="st-key-rename_input_"] [data-baseweb="base-input"]{{
        background:#ffffff !important;
        border-radius:10px !important;
    }}

    /* دکمه‌های «ذخیره / انصراف» پنجره‌ی تغییر نام */
    [class*="st-key-rename_save_"] button,
    [class*="st-key-rename_cancel_"] button{{
        min-height:34px !important;
        padding:4px 6px !important;
        font-size:13px !important;
        border-radius:10px !important;
        box-shadow:none !important;
    }}

    [class*="st-key-rename_save_"] button{{
        background:#ffffff !important;
        border:none !important;
    }}

    [class*="st-key-rename_save_"] button,
    [class*="st-key-rename_save_"] button p{{
        color:#3d6d7b !important;
    }}

    [class*="st-key-rename_save_"] button:hover{{
        background:#eaf3f6 !important;
    }}

    [class*="st-key-rename_cancel_"] button{{
        background:transparent !important;
        border:1px solid rgba(255,255,255,.55) !important;
    }}

    [class*="st-key-rename_cancel_"] button:hover{{
        background:rgba(255,255,255,.14) !important;
    }}

    /* پس‌زمینه‌ی منوی سه‌نقطه: رنگ ساده‌ی #e4f6f6 (بدون گرادیانت
       تیل قبلی). رنگ روی همه‌ی لایه‌های پاپ‌آپ یکی است تا هیچ
       لایه‌ای رنگ دیگری نشان ندهد؛ فقط خودِ بدنه‌ی منو حاشیه و
       سایه‌ی ملایم دارد تا لایه‌ها دوبار قاب نشوند */
    div[data-baseweb="popover"]:has([class*="st-key-delete_option_"]),
    div[data-baseweb="popover"]:has([class*="st-key-delete_option_"]) > div,
    [data-testid="stPopoverBody"]:has([class*="st-key-delete_option_"]),
    div[role="dialog"]:has([class*="st-key-delete_option_"]){{
        background:#e4f6f6 !important;
        background-image:none !important;
        border:none !important;
        border-radius:14px !important;
        box-shadow:none !important;
        backdrop-filter:none !important;
        -webkit-backdrop-filter:none !important;

        /* کوتاه‌تر شدن عرض (قبلاً حدود ۳۲۰px بود). لبه‌ی چپ پاپ‌آپ
           همان قبلی می‌ماند و فقط از سمت راست کوتاه می‌شود.
           عرض برای جا شدن برچسب‌های منو (مثل «خارج کردن از بایگانی»)
           از ۱۴۰ به ۱۸۴px رسیده است */
        box-sizing:border-box !important;
        min-width:0 !important;
        width:184px !important;
        max-width:184px !important;
    }}

    [data-testid="stPopoverBody"]:has([class*="st-key-delete_option_"]){{
        border:1px solid rgba(72,128,145,.35) !important;
        box-shadow:0 8px 22px rgba(72,128,145,.22) !important;
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
    }}


    /* اصلاح hover سه نقطه */
    [data-testid="stPopover"] button:hover {{

        background:rgba(72,128,145,.15) !important;

        border-radius:10px !important;
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


    /* قانون موبایل نسخه‌ی دوستم (تا ۷۶۸px) - حفظ شده */
    @media (max-width: 768px){{
        [data-testid="stSidebar"]{{
            left:auto !important;
            right:0 !important;
        }}
    }}

    /* ---- نسخه‌ی قبلیِ استایل پاپ‌آپ (شیشه‌ای، عرض ۱۲۰px، translate ثابت) ----
       از فایل دوستم نگه داشته شده ولی غیرفعال است؛ جایش را استایل
       جدید پاپ‌آپ (#e4f6f6 با گزینه‌های پین / بایگانی / تغییر نام / حذف) گرفته.
       div[data-baseweb="popover"]:has([class*="st-key-delete_option_"]),
       div[data-baseweb="popover"]:has([class*="st-key-delete_option_"]) > div,
       [data-testid="stPopoverBody"]:has([class*="st-key-delete_option_"]),
       div[role="dialog"]:has([class*="st-key-delete_option_"]){{
       background:rgba(255,255,255,.55) !important;
       backdrop-filter:blur(14px) !important;
       -webkit-backdrop-filter:blur(14px) !important;
       border:1px solid rgba(255,255,255,.75) !important;
       box-shadow:0 8px 22px rgba(31,41,55,.14) !important;
       box-sizing:border-box !important;
       min-width:0 !important;
       width:120px !important;
       max-width:120px !important;
       translate: -100px 0px !important;
       }}
       
       div[data-baseweb="popover"]:has([class*="st-key-delete_option_"]) *{{
       background-color:transparent !important;
       }}
    */
    </style>
    """,
        unsafe_allow_html=True
    )

def inject_delete_popup_position() -> None:
    """جای منوی سه‌نقطه را برای هر ردیف گفتگو از روی جای واقعی سه‌نقطه‌ی
    همان ردیف حساب می‌کند (نه مختصات ثابت صفحه)، مثل منوی کشویی
    برنامه‌های چت: درست زیر سه‌نقطه و چسبیده به آن باز می‌شود؛
      - لبه‌ی منو با لبه‌ی همان سمتِ سه‌نقطه هم‌راستا است
      - اگر پایین صفحه جا نباشد، منو بالای سه‌نقطه باز می‌شود
      - منو همیشه داخل نوار کناری / صفحه می‌ماند
    پاپ‌آپ استریم‌لیت بیرون از ردیف رندر می‌شود، پس با یک اسکریپت
    کوچک و از روی getBoundingClientRect همان ردیف جابه‌جا می‌شود."""

    components.html(
        """
        <script>
        (function () {
            var win = window.parent;
            var doc = win.document;

            // فقط یک بار نصب شود (با هر rerun دوباره نصب نشود)
            if (win.__deletePopupPositionInstalled) { return; }
            win.__deletePopupPositionInstalled = true;

            var GAP_PX = 4;        // فاصله‌ی منو تا سه‌نقطه
            var EDGE_PX = 8;       // حداقل فاصله از لبه‌ی پنجره / نوار کناری

            var busy = false;
            var observer = null;

            function findPopup(del) {
                var pop = del.closest('[data-baseweb="popover"]');
                if (pop) { return pop; }
                var el = del.parentElement;
                while (el && el !== doc.body) {
                    var pos = win.getComputedStyle(el).position;
                    if (pos === "absolute" || pos === "fixed") { return el; }
                    el = el.parentElement;
                }
                return null;
            }

            function place() {
                var del = doc.querySelector(
                    '[class*="st-key-delete_option_"] button'
                );
                if (!del) { return; }

                var holder = del.closest('[class*="st-key-delete_option_"]');
                var m = /st-key-delete_option_([^ ]+)/.exec(holder.className);
                if (!m) { return; }

                // سه‌نقطه‌ی همان ردیفی که منویش باز شده
                var anchor = doc.querySelector(
                    '.st-key-menu_toggle_' + m[1] + ' button'
                );
                var pop = findPopup(del);
                if (!anchor || !pop) { return; }

                busy = true;

                // اندازه‌گیری از جای طبیعی پاپ‌آپ (بدون جابه‌جایی قبلی)
                pop.style.setProperty("translate", "0px 0px", "important");
                var a = anchor.getBoundingClientRect();
                var b = pop.getBoundingClientRect();

                // محدوده‌ی مجاز: نوار کناری (اگر هست) وگرنه کل پنجره
                var sb = doc.querySelector('[data-testid="stSidebar"]');
                var box = sb ? sb.getBoundingClientRect() : null;
                var minLeft = (box ? Math.max(box.left, 0) : 0) + EDGE_PX;
                var maxRight = (box ? Math.min(box.right, win.innerWidth)
                                    : win.innerWidth) - EDGE_PX;

                // افقی: لبه‌ی منو هم‌راستای لبه‌ی همان سمتِ سه‌نقطه
                var targetLeft;
                if (a.left + a.width / 2 < (minLeft + maxRight) / 2) {
                    targetLeft = a.left;              // سه‌نقطه سمت چپ
                } else {
                    targetLeft = a.right - b.width;   // سه‌نقطه سمت راست
                }
                if (targetLeft + b.width > maxRight) { targetLeft = maxRight - b.width; }
                if (targetLeft < minLeft) { targetLeft = minLeft; }

                // عمودی: درست زیر سه‌نقطه؛ اگر جا نبود بالای آن
                var targetTop = a.bottom + GAP_PX;
                if (targetTop + b.height > win.innerHeight - EDGE_PX) {
                    targetTop = a.top - GAP_PX - b.height;
                }
                if (targetTop < EDGE_PX) { targetTop = EDGE_PX; }

                var dx = targetLeft - b.left;
                var dy = targetTop - b.top;

                pop.style.setProperty(
                    "translate", dx + "px " + dy + "px", "important"
                );

                observer.takeRecords();
                busy = false;
            }

            observer = new win.MutationObserver(function () {
                if (!busy) { place(); }
            });

            observer.observe(doc.body, {
                childList: true,
                subtree: true,
                attributes: true,
                attributeFilter: ["style"]
            });

            win.addEventListener("resize", place);
        })();
        </script>
        """,
        height=0
    )


# جمله‌های چرخان زیر عنوان (تایپ‌شونده). جمله‌ی اول جمله‌ی پیش‌فرض/پشتیبان است.
HERO_TYPING_MESSAGES = [
    "هوشمندانه انتخاب کن، آسوده پرواز کن",
    "ارزان‌ترین پروازها را پیدا کن",
    "مقصدت را بگو، بقیه‌اش با من ✈️",
    "آماده‌ای پرواز کنیم؟",
]


def render_header() -> None:
    """رندر کارت اصلی، لوگو، عنوان ثابت و زیرعنوان تایپ‌شونده.
    عنوان اصلی ثابت است و فقط زیرعنوان با inject_hero_typing() متحرک می‌شود."""

    fallback = HERO_TYPING_MESSAGES[0]

    st.markdown(
        '<div class="main-card">'
        '<div class="logo">✈️</div>'
        '<div class="title">دستیار هوشمند بلیط</div>'
        '<div class="subtitle">'
        f'<span class="hero-typed-text" data-fallback="{fallback}"></span>'
        '<span class="hero-caret"></span>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )


def inject_hero_typing() -> None:
    """انیمیشن تایپ زیرعنوان (حرف‌به‌حرف، مکث، پاک کردن، جمله‌ی بعد).

    - عنوان اصلی دست‌نخورده می‌ماند؛ فقط span مخصوص زیرعنوان عوض می‌شود.
    - حلقه در هر tick عنصر را دوباره پیدا می‌کند، پس اگر Streamlit
      هنگام rerun آن را دوباره بسازد انیمیشن ادامه پیدا می‌کند.
    - وضعیت (جمله/حرف) روی window ذخیره می‌شود و یک watchdog تضمین
      می‌کند اگر iframe حذف و دوباره ساخته شد، حلقه از همان‌جا ادامه دهد.
    - اگر کاربر «کاهش حرکت» را خواسته باشد، هیچ انیمیشنی اجرا نمی‌شود
      و جمله‌ی اول ثابت نمایش داده می‌شود.
    """

    script = """
    <script>
    (function () {
        var win = window.parent;
        var doc = win.document;

        var MESSAGES = __MESSAGES__;

        var TYPE_MIN = 130, TYPE_MAX = 170;   // ms برای هر حرف هنگام تایپ (کندتر = عدد بزرگ‌تر)
        var DEL_MIN  = 28,  DEL_MAX  = 42;    // ms برای هر حرف هنگام پاک شدن
        var HOLD_MIN = 1500, HOLD_MAX = 2500; // مکث بعد از کامل شدن جمله
        var GAP_MS   = 450;                   // مکث بین پاک شدن و جمله‌ی بعد

        var reduce = win.matchMedia &&
            win.matchMedia("(prefers-reduced-motion: reduce)").matches;
        if (reduce) { return; }

        function rnd(a, b) { return a + Math.random() * (b - a); }

        // تقسیم به grapheme تا ایموجی‌ها (مثل ✈️) نیمه‌کاره نمایش داده نشوند
        function split(text) {
            try {
                if (win.Intl && win.Intl.Segmenter) {
                    var seg = new win.Intl.Segmenter("fa", { granularity: "grapheme" });
                    return Array.from(seg.segment(text), function (x) { return x.segment; });
                }
            } catch (e) {}
            return Array.from(text);
        }

        var chars = MESSAGES.map(split);

        // وضعیت مشترک؛ روی window می‌ماند تا با ساخته شدن دوباره‌ی iframe
        // انیمیشن از اول شروع نشود
        var st = win.__heroTyping || (win.__heroTyping = {
            msg: 0, pos: 0, phase: "type", beat: 0
        });

        var timer = null;

        // بیشترین فاصله‌ی دو tick (مکث ۲.۵ ثانیه‌ای) + حاشیه؛ بعد از آن
        // حلقه مرده حساب می‌شود و watchdog آن را دوباره راه می‌اندازد
        function alive() { return Date.now() - st.beat < 4500; }

        function render() {
            var el = doc.querySelector(".hero-typed-text");
            if (!el) { return; }

            var box = el.parentElement;
            if (box && box.getAttribute("data-typing") !== "on") {
                box.setAttribute("data-typing", "on");
            }

            var text = chars[st.msg].slice(0, st.pos).join("");
            if (el.textContent !== text) { el.textContent = text; }
        }

        function step() {
            st.beat = Date.now();
            var delay = 100;
            var len = chars[st.msg].length;

            if (st.phase === "type") {
                if (st.pos < len) {
                    st.pos += 1;
                    render();
                    delay = rnd(TYPE_MIN, TYPE_MAX);
                } else {
                    render();
                    st.phase = "hold";
                    delay = rnd(HOLD_MIN, HOLD_MAX);
                }
            } else if (st.phase === "hold") {
                st.phase = "delete";
                delay = 60;
            } else if (st.phase === "delete") {
                if (st.pos > 0) {
                    st.pos -= 1;
                    render();
                    delay = rnd(DEL_MIN, DEL_MAX);
                } else {
                    render();
                    st.phase = "gap";
                    delay = GAP_MS;
                }
            } else {
                st.msg = (st.msg + 1) % chars.length;
                st.pos = 0;
                st.phase = "type";
                delay = 120;
            }

            timer = setTimeout(step, delay);
        }

        function start() {
            if (alive()) { return; }
            st.beat = Date.now();
            step();
        }

        start();

        // اگر حلقه‌ی iframe دیگری مرده باشد، این نمونه ادامه‌اش را برمی‌دارد
        setInterval(start, 1000);
    })();
    </script>
    """.replace(
        "__MESSAGES__",
        json.dumps(HERO_TYPING_MESSAGES, ensure_ascii=False)
    )

    components.html(script, height=0)



def inject_delete_popup_position_legacy_3cm() -> None:
    """جای دکمه‌ی «حذف» را برای هر ردیف گفتگو از روی جای واقعی سه‌نقطه‌ی
    همان ردیف حساب می‌کند (نه مختصات ثابت صفحه):
      - دقیقاً هم‌تراز عمودی با سه‌نقطه‌ی همان ردیف
      - حدود ۳cm (≈۱۱۳px) فاصله‌ی افقی از سه‌نقطه، بیرون از کادر چت
    پاپ‌آپ استریم‌لیت بیرون از ردیف رندر می‌شود، پس با یک اسکریپت
    کوچک و از روی getBoundingClientRect همان ردیف جابه‌جا می‌شود.
    فقط جای دکمه عوض می‌شود؛ ظاهر آن دست‌نخورده است."""

    components.html(
        """
        <script>
        (function () {
            var win = window.parent;
            var doc = win.document;

            // فقط یک بار نصب شود (با هر rerun دوباره نصب نشود)
            if (win.__deletePopupPositionInstalled) { return; }
            win.__deletePopupPositionInstalled = true;

            var GAP_PX = 30;      // حدود ۳ سانتی‌متر
            var EDGE_PX = 8;       // حداقل فاصله از لبه‌ی پنجره

            var busy = false;
            var observer = null;

            function findPopup(del) {
                var pop = del.closest('[data-baseweb="popover"]');
                if (pop) { return pop; }
                var el = del.parentElement;
                while (el && el !== doc.body) {
                    var pos = win.getComputedStyle(el).position;
                    if (pos === "absolute" || pos === "fixed") { return el; }
                    el = el.parentElement;
                }
                return null;
            }

            function place() {
                var del = doc.querySelector(
                    '[class*="st-key-delete_option_"] button'
                );
                if (!del) { return; }

                var holder = del.closest('[class*="st-key-delete_option_"]');
                var m = /st-key-delete_option_([^ ]+)/.exec(holder.className);
                if (!m) { return; }

                // سه‌نقطه‌ی همان ردیفی که منویش باز شده
                var anchor = doc.querySelector(
                    '.st-key-menu_toggle_' + m[1] + ' button'
                );
                var pop = findPopup(del);
                if (!anchor || !pop) { return; }

                busy = true;

                // اندازه‌گیری از جای طبیعی پاپ‌آپ (بدون جابه‌جایی قبلی)
                pop.style.setProperty("translate", "0px 0px", "important");
                var a = anchor.getBoundingClientRect();
                var b = del.getBoundingClientRect();

                var dx = a.right + GAP_PX - b.left;
                var maxLeft = win.innerWidth - b.width - EDGE_PX;
                if (b.left + dx > maxLeft) { dx = maxLeft - b.left; }

                var dy = (a.top + a.height / 2) - (b.top + b.height / 2);

                pop.style.setProperty(
                    "translate", dx + "px " + dy + "px", "important"
                );

                observer.takeRecords();
                busy = false;
            }

            observer = new win.MutationObserver(function () {
                if (!busy) { place(); }
            });

            observer.observe(doc.body, {
                childList: true,
                subtree: true,
                attributes: true,
                attributeFilter: ["style"]
            });

            win.addEventListener("resize", place);
        })();
        </script>
        """,
        height=0
    )


def inject_cabin_filter_panel_style() -> None:
    """استایل پنل کوچک «کلاس پرواز» سمت چپ صفحه (نتایج پرواز).

    پنل یک st.container با کلید cabin_filter_panel است که با CSS
    ثابت (fixed) سمت چپ صفحه می‌نشیند و با یک انیمیشن نرم از چپ باز
    می‌شود. در صفحه‌های کوچک (موبایل / تبلت) ثابت نیست و ساده بالای
    کارت‌ها قرار می‌گیرد تا روی آن‌ها نیفتد."""

    st.markdown(
        """
    <style>

    /* ---------- پنل «کلاس پرواز» (فیلتر نتایج) ---------- */

    .cabin-filter-texts{
        display:flex;
        flex-direction:column;
        gap:1px;
        min-width:0;
    }

    .cabin-filter-title{
        font-family:'Vazirmatn', sans-serif !important;
        font-weight:800;
        font-size:15px;
        line-height:1.4;
        color:#1f2937;
        direction:rtl;
        text-align:right;
        margin:0;
    }

    .cabin-filter-sub{
        font-family:'Vazirmatn', sans-serif !important;
        font-weight:500;
        font-size:11.5px;
        line-height:1.4;
        color:#6b7280;
        direction:rtl;
        text-align:right;
    }

    /* پنل بیرونی فقط نگه‌دارنده است؛ هر بخش کارت جدا و مستقل دارد */
    .st-key-cabin_filter_panel{
        box-sizing:border-box;
        direction:rtl;
        background:transparent;
        border:none;
        padding:0 !important;
        margin-bottom:14px;
        gap:12px !important;
    }

    /* کارت‌های جدا (مثل عکس نمونه) */
    .st-key-cabin_filter_card_head,
    .st-key-cabin_filter_card_class,
    .st-key-cabin_filter_card_sort{
        box-sizing:border-box;
        direction:rtl;
        background:#ffffff;
        border:1px solid rgba(72,128,145,.14);
        border-radius:18px;
        padding:14px 14px 10px 14px !important;
        gap:.25rem !important;
        box-shadow:none !important;
        filter:none !important;
    }

    .st-key-cabin_filter_card_head{
        padding-bottom:12px !important;
    }

    /* رادیو باتن‌ها */
    .st-key-cabin_filter_panel [data-testid="stRadio"]{
        direction:rtl !important;
    }

    .st-key-cabin_filter_panel [data-testid="stRadio"] [role="radiogroup"]{
        gap:2px !important;
    }

    .st-key-cabin_filter_panel [data-testid="stRadio"] label{
        width:100%;
        direction:rtl !important;
        display:flex !important;
        align-items:center;
        gap:10px;
        padding:7px 4px;
        cursor:pointer;
    }

    /* دایره‌ی پیش‌فرض Streamlit (که قرمز/مشکی رندر می‌شد) مخفی می‌شود و
       دایره‌ی رادیو با ::before خودمان کشیده می‌شود تا به ساختار داخلی
       Streamlit وابسته نباشد */
    /* عنوان خالی ویجت (st.radio) هم یک label است؛ دایره‌ی اضافه نگیرد */
    .st-key-cabin_filter_panel [data-testid="stRadio"] [data-testid="stWidgetLabel"]{
        display:none !important;
    }

    /* هر عنصر داخل گزینه که متن نیست (دایره‌ی قرمز/مشکی Streamlit، در هر
       عمقی) مخفی می‌شود */
    .st-key-cabin_filter_panel [data-testid="stRadio"] label:has(input[type="radio"]) *:not(input):not(p):not(:has(p)):not(p *){
        display:none !important;
    }

    .st-key-cabin_filter_panel [data-testid="stRadio"] label:has(input[type="radio"])::before{
        content:"";
        flex:0 0 auto;
        box-sizing:border-box;
        width:20px;
        height:20px;
        border-radius:50%;
        background-color:#ffffff;
        border:1.5px solid #b6c9cf;
        transition:background-color .18s ease, border-color .18s ease;
    }

    .st-key-cabin_filter_panel [data-testid="stRadio"] label:has(input[type="radio"]):has(input:checked)::before{
        background-color:#3b82f6;
        border-color:#3b82f6;
        background-image:radial-gradient(circle, #ffffff 0 3.5px, transparent 4px);
    }

    .st-key-cabin_filter_panel [data-testid="stRadio"] label:has(input[type="radio"]):focus-within::before{
        box-shadow:0 0 0 3px rgba(59,130,246,.28);
    }

    .st-key-cabin_filter_panel [data-testid="stRadio"] p{
        font-family:'Vazirmatn', sans-serif !important;
        font-size:14px !important;
        font-weight:600 !important;
        color:#1f2937 !important;
        white-space:nowrap;
        margin:0;
    }

    .st-key-cabin_filter_panel [data-testid="stRadio"] label:has(input:checked) p{
        color:#2b5461 !important;
        font-weight:700 !important;
    }

    .st-key-cabin_filter_panel label,
    .st-key-cabin_filter_panel [data-testid="stCheckbox"]{
        direction:rtl !important;
    }

    /* هر گزینه یک ردیف قابل‌کلیک است؛ بدون کادر و پس‌زمینه‌ی جدا چون
       خود پنل یک کادر کلی دارد */
    .st-key-cabin_filter_panel [data-testid="stCheckbox"] label{
        width:100%;
        box-sizing:border-box;
        display:flex !important;
        align-items:center;
        gap:10px;
        padding:7px 4px;
        border:none !important;
        background:transparent !important;
        box-shadow:none !important;
        cursor:pointer;
    }

    .st-key-cabin_filter_panel [data-testid="stCheckbox"] label:hover p{
        color:#2b5461 !important;
    }

    /* عنوان بخش‌های داخل پنل («کلاس پرواز» / «مرتب‌سازی بر اساس») */
    .cabin-filter-section{
        direction:rtl;
        text-align:right;
        font-family:'Vazirmatn', sans-serif !important;
        font-weight:700;
        font-size:12.5px;
        line-height:1.5;
        color:#488091;
        margin:2px 4px 12px 4px;
    }

    .st-key-cabin_filter_card_class .cabin-filter-section{
        margin-bottom:18px;
    }

    .cabin-filter-section-sep{
        margin-top:8px;
        padding-top:10px;
        border-top:1px solid rgba(72,128,145,.18);
    }

    /* پیام‌های کوتاه نتایج (به‌جای st.info / st.warning) با متن خوانا */
    .cabin-notice{
        direction:rtl;
        text-align:right;
        font-family:'Vazirmatn', sans-serif !important;
        font-weight:600;
        font-size:14px;
        line-height:1.8;
        padding:12px 16px;
        border-radius:14px;
        margin:6px 0 10px 0;
    }

    .cabin-notice-warn{
        background:#fff4cc;
        border:1px solid #f0d27a;
        color:#6b4a00;
    }

    .cabin-notice-info{
        background:#e6f2f5;
        border:1px solid #b9d6de;
        color:#1f4a57;
    }

    /* مربع تیک (آبی). عنصر مربع = فرزند label که input و متن نیست،
       تا به ساختار HTML نسخه‌ی Streamlit وابسته نباشد */
    .st-key-cabin_filter_panel [data-testid="stCheckbox"] label > :not(input):not(:has(p)),
    .st-key-cabin_filter_panel [data-testid="stCheckbox"] label > span:first-of-type{
        flex:0 0 auto;
        width:20px !important;
        height:20px !important;
        border-radius:7px !important;
        background-color:#ffffff !important;
        border:1.5px solid #b6c9cf !important;
        transition:background-color .18s ease, border-color .18s ease;
    }

    .st-key-cabin_filter_panel [data-testid="stCheckbox"] label:has(input:checked) > :not(input):not(:has(p)),
    .st-key-cabin_filter_panel [data-testid="stCheckbox"] label:has(input:checked) > span:first-of-type{
        background-color:#3b82f6 !important;
        border-color:#3b82f6 !important;
    }

    .st-key-cabin_filter_panel [data-testid="stCheckbox"] label:focus-within > :not(input):not(:has(p)){
        box-shadow:0 0 0 3px rgba(59,130,246,.28) !important;
    }

    .st-key-cabin_filter_panel input[type="checkbox"],
    .st-key-cabin_filter_panel input[type="radio"]{
        accent-color:#3b82f6;
    }

    .st-key-cabin_filter_panel [data-testid="stCheckbox"] p{
        font-family:'Vazirmatn', sans-serif !important;
        font-size:14px !important;
        font-weight:600 !important;
        color:#1f2937 !important;
        white-space:nowrap;
        margin:0;
    }

    .st-key-cabin_filter_panel [data-testid="stCheckbox"] label:has(input:checked) p{
        color:#2b5461 !important;
        font-weight:700 !important;
    }

    /* صفحه‌ی عریض: پنل ثابت و کوچک سمت چپ + کمی فضا برای محتوا تا
       روی کارت‌های پرواز نیفتد */
    @media (min-width: 1280px){

        .st-key-cabin_filter_panel{
            position:fixed !important;
            left:44px;
            top:150px;
            width:210px !important;
            max-height:calc(100vh - 170px);
            overflow-y:auto;
            z-index:999;
            margin-bottom:0;

            /* fill-mode برابر backwards: بعد از پایان انیمیشن هیچ
               transform باقی نمی‌ماند (transform عناصر fixed را خراب می‌کند) */
            animation:cabin-panel-in .42s cubic-bezier(.22,.8,.3,1) backwards;
        }

        .block-container:has(.st-key-cabin_filter_panel),
        [data-testid="stMainBlockContainer"]:has(.st-key-cabin_filter_panel){
            padding-left:274px !important;
        }
    }

    @keyframes cabin-panel-in{
        from{ opacity:0; transform:translateX(-28px); }
        to{   opacity:1; transform:translateX(0); }
    }

    @media (prefers-reduced-motion: reduce){
        .st-key-cabin_filter_panel{ animation:none !important; }
    }

    </style>
        """,
        unsafe_allow_html=True
    )


# ---------------------------------------------------------------------
# لودر «در حال جستجوی پروازها»: حلقه‌ی نیم‌آبی / نیم‌نارنجی (خط‌چین) با دو
# هواپیمای آبی و نارنجی که روی حلقه می‌چرخند. به‌جای حالت «هنگ کردن»
# صفحه، تا پایان جستجو روی صفحه می‌ماند.
# ---------------------------------------------------------------------
_PLANE_PATH = (
    "M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5"
    "V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"
)

SEARCH_LOADER_SVG = (
    '<svg class="fsl-spin" viewBox="-60 -60 120 120" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
    # نیمه‌ی آبی (از بالا-چپ، ساعت‌گرد تا پایین-راست)
    '<path d="M-31.1 -31.1 A44 44 0 0 1 31.1 31.1" fill="none" stroke="#1b5a55" '
    'stroke-width="5" stroke-dasharray="11 6.27" stroke-linecap="butt"/>'
    # نیمه‌ی نارنجی (از پایین-راست، ساعت‌گرد تا بالا-چپ)
    '<path d="M31.1 31.1 A44 44 0 0 1 -31.1 -31.1" fill="none" stroke="#ff8a26" '
    'stroke-width="5" stroke-dasharray="11 6.27" stroke-linecap="butt"/>'
    # هواپیمای آبی (ابتدای نیمه‌ی آبی) و هواپیمای نارنجی (ابتدای نیمه‌ی نارنجی)؛
    # بدنه‌ی هواپیما در جهت حرکت (مماس بر حلقه) می‌چرخد
    '<g transform="rotate(225) translate(44 0)">'
    '<circle r="12.5" fill="#1b5a55"/>'
    f'<path transform="rotate(180) scale(.72) translate(-12 -12)" fill="#ffffff" d="{_PLANE_PATH}"/>'
    '</g>'
    '<g transform="rotate(45) translate(44 0)">'
    '<circle r="12.5" fill="#ff8a26"/>'
    f'<path transform="rotate(180) scale(.72) translate(-12 -12)" fill="#ffffff" d="{_PLANE_PATH}"/>'
    '</g>'
    '</svg>'
)

SEARCH_LOADER_TEXT = "در حال جستجوی پروازها…"

_SEARCH_LOADER_JS = """
<script>
(function () {
    // کد اصلی داخل صفحه‌ی والد (نه iframe) نصب می‌شود؛ چون iframe بعد از
    // هر rerun ممکن است حذف شود و تایمرهایش بمیرند
    function main() {
        var win = window, doc = document;
        if (win.__flightSearchLoader) { return; }
        win.__flightSearchLoader = true;

        // فقط دکمه‌ای که جستجوی واقعی پروازها را شروع می‌کند
        var TRIGGER = '.st-key-confirm_flight_button button';

        var ov = null;
        var shownAt = 0;
        var sawBusy = false;
        var idleSince = 0;
        var poll = null;

        function build() {
            if (ov && doc.body.contains(ov)) { return ov; }
            ov = doc.createElement('div');
            ov.id = 'flight-search-loader';
            ov.setAttribute('role', 'status');
            ov.setAttribute('aria-live', 'polite');
            ov.innerHTML = '<div class="fsl-box">' + '__SVG__' + '<div class="fsl-text">__TEXT__</div>' + '</div>';
            doc.body.appendChild(ov);
            return ov;
        }

        function scriptState() {
            var app = doc.querySelector('[data-testid="stApp"]');
            return app ? app.getAttribute('data-test-script-state') : null;
        }

        function stopPoll() {
            if (poll) { win.clearInterval(poll); poll = null; }
        }

        function hide() {
            stopPoll();
            if (ov) { ov.classList.remove('fsl-on'); }
            doc.body.classList.remove('fsl-searching');
        }

        function tick() {
            var s = scriptState();
            var age = Date.now() - shownAt;

            if (age > 180000) { hide(); return; }        // سقف ایمنی

            if (s === null) {                            // نسخه‌ای که نشانگر وضعیت ندارد
                if (age > 60000) { hide(); }
                return;
            }

            if (s === 'running' || s === 'rerunRequested') {
                sawBusy = true;
                idleSince = 0;
                return;
            }

            // اجرا تمام شده: کمی صبر می‌کنیم تا rerunِ پشت‌سرهم تمام شود
            if (sawBusy) {
                if (!idleSince) { idleSince = Date.now(); }
                if (Date.now() - idleSince > 450) { hide(); }
            } else if (age > 2500) {
                hide();                                  // اصلاً اجرایی شروع نشد
            }
        }

        // هم‌اندازه و هم‌جای کادر تایپ چت: اگر کادر تایپ در این حالت رندر
        // نشده باشد، از ظرف پایین صفحه‌ی Streamlit (که کادر تایپ همیشه داخل
        // آن می‌نشیند) اندازه و فاصله از پایین گرفته می‌شود
        function align() {
            if (!ov) { return; }

            var left = null, right = null, gap = null;

            var input = doc.querySelector('[data-testid="stChatInput"]');
            var cont = doc.querySelector('[data-testid="stBottomBlockContainer"]');

            if (input && input.offsetWidth > 0) {
                var ir = input.getBoundingClientRect();
                left = ir.left;
                right = ir.right;
                gap = win.innerHeight - ir.bottom;
            } else if (cont && cont.offsetWidth > 0) {
                var cs = win.getComputedStyle(cont);
                var cr = cont.getBoundingClientRect();
                left = cr.left + (parseFloat(cs.paddingLeft) || 0);
                right = cr.right - (parseFloat(cs.paddingRight) || 0);
                gap = win.innerHeight - cr.bottom + (parseFloat(cs.paddingBottom) || 0);
            } else {
                var m = doc.querySelector('[data-testid="stMain"]');
                if (!m) { return; }
                var mr = m.getBoundingClientRect();
                left = mr.left + 16;
                right = mr.right - 16;
                gap = 28;
            }

            // عرض افقی لودر هم‌اندازه‌ی محتوای اصلی (هم‌عرض کارت‌ها)
            var mainc = doc.querySelector('[data-testid="stMainBlockContainer"]')
                || doc.querySelector('.block-container');
            if (!(input && input.offsetWidth > 0) && mainc && mainc.offsetWidth > 0) {
                var mcs = win.getComputedStyle(mainc);
                var mcr = mainc.getBoundingClientRect();
                left = mcr.left + (parseFloat(mcs.paddingLeft) || 0);
                right = mcr.right - (parseFloat(mcs.paddingRight) || 0);
            }

            ov.style.paddingLeft = Math.max(left, 0) + 'px';
            ov.style.paddingRight = Math.max(win.innerWidth - right, 0) + 'px';
            ov.style.paddingBottom = Math.max(gap, 0) + 'px';
        }

        function show() {
            build();
            align();
            ov.classList.add('fsl-on');
            doc.body.classList.add('fsl-searching');
            shownAt = Date.now();
            sawBusy = false;
            idleSince = 0;
            stopPoll();
            poll = win.setInterval(tick, 200);
        }

        win.addEventListener('resize', align);

        doc.addEventListener('click', function (e) {
            var t = e.target;
            if (t && t.closest && t.closest(TRIGGER)) { show(); }
        }, true);
    }

    try {
        var parentDoc = window.parent.document;
        var tag = parentDoc.createElement('script');
        tag.textContent = '(' + main.toString() + ')();';
        parentDoc.head.appendChild(tag);
    } catch (err) {
        console.error('search loader install failed', err);
    }
})();
</script>
"""


def inject_search_loader() -> None:
    """لودر تمام‌صفحه‌ی جستجوی پرواز (حلقه‌ی نیم‌آبی/نیم‌نارنجی + دو هواپیما).

    با کلیک روی «تأیید و جستجوی پرواز» فوراً نمایش داده می‌شود و وقتی
    اجرای Streamlit تمام شد (نتایج آماده شد) خودکار محو می‌شود."""

    st.markdown(
        """
    <style>

    /* لودر جستجو: به‌جای وسط صفحه، مثل کادر تایپ کاربر پایین صفحه می‌نشیند و
       هواپیمای چرخان گوشه‌ی سمت چپ همان کادر است. لایه‌ی بیرونی شفاف است و فقط
       جلوی کلیک‌های اضافه را می‌گیرد */
    #flight-search-loader{
        position:fixed;
        top:0;
        bottom:0;
        left:0;
        right:0;
        z-index:2147483000;

        display:flex;
        align-items:flex-end;
        justify-content:center;
        box-sizing:border-box;
        padding:0 16px 28px 16px;   /* جای دقیق را align() در JS با اندازه‌ی کادر تایپ تنظیم می‌کند */

        background:transparent;

        opacity:0;
        visibility:hidden;
        pointer-events:none;
        transition:opacity .22s ease, visibility 0s linear .22s;
    }

    #flight-search-loader.fsl-on{
        opacity:1;
        visibility:visible;
        pointer-events:auto;
        transition:opacity .22s ease, visibility 0s;
    }

    #flight-search-loader .fsl-box{
        direction:ltr;
        display:flex;
        align-items:center;
        justify-content:space-between;
        gap:12px;

        width:100%;
        min-height:64px;
        box-sizing:border-box;
        padding:8px 14px 8px 12px;

        background:#ffffff;
        border:1px solid #d1d5db;
        border-radius:20px;
        box-shadow:0 5px 20px rgba(0,0,0,.08);
    }

    #flight-search-loader .fsl-spin{
        flex:0 0 auto;
        width:46px;
        height:46px;
        animation:fsl-rotate 2.4s linear infinite;
        filter:drop-shadow(0 3px 6px rgba(27,90,85,.18));
    }

    #flight-search-loader .fsl-text{
        flex:1 1 auto;
        font-family:'Vazirmatn', sans-serif;
        font-weight:700;
        font-size:15px;
        color:#1f2937;
        direction:rtl;
        text-align:right;
        animation:fsl-pulse 1.6s ease-in-out infinite;
    }

    /* در طول جستجو صفحه و نوار کناری کمرنگ/محو نشوند
       (استایل پیش‌فرض Streamlit برای عناصر «stale» هنگام rerun) */
    body.fsl-searching [data-stale="true"],
    body.fsl-searching .stale-element{
        opacity:1 !important;
        filter:none !important;
        transition:none !important;
    }

    @keyframes fsl-rotate{
        to{ transform:rotate(360deg); }
    }

    @keyframes fsl-pulse{
        0%, 100%{ opacity:.55; }
        50%{      opacity:1;   }
    }

    @media (prefers-reduced-motion: reduce){
        #flight-search-loader .fsl-spin{ animation-duration:7s; }
        #flight-search-loader .fsl-text{ animation:none; }
    }

    </style>
        """,
        unsafe_allow_html=True
    )

    script = (
        _SEARCH_LOADER_JS
        .replace("__SVG__", SEARCH_LOADER_SVG)
        .replace("__TEXT__", SEARCH_LOADER_TEXT)
    )

    components.html(script, height=0)



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

.guest-login-fixed{
    position:fixed !important;
    top:20px !important;
    left:30px !important;
    right:auto !important;
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
    right: 0 !important;
    left: auto !important;

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

min-width:0;

}

/* صفحه‌ی نتایج پرواز: کارت‌ها عرض بیشتری داشته باشند */
.block-container:has(.ticket-card),
[data-testid="stMainBlockContainer"]:has(.ticket-card){

max-width:1400px !important;

}



.ticket-header{

display:flex;

justify-content:space-between;

align-items:center;

flex-wrap:wrap;

gap:10px 16px;

}

.airline-name{
    display:flex;
    align-items:center;
    gap:12px;
    font-size:22px;
    font-weight:700;
    color:#488091;
    white-space:nowrap;
    flex:0 0 auto;
}

.airline-logo {
    width: 48px;
    height: 48px;

    object-fit: contain;

    border-radius: 8px;
}

.flight-tags{

    display:flex;

    flex-wrap:wrap;

    justify-content:flex-end;

    align-items:center;

    gap:6px;

    max-width:none;

    min-width:0;

}

@media (min-width: 900px){

    .flight-tags{

        flex-wrap:nowrap;

    }

}

.flight-tags span{

    background:rgba(72,128,145,0.15);

    color:#488091;

    padding:5px 12px;

    border-radius:20px;

    font-size:12px;

    font-weight:600;

    white-space:nowrap;

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