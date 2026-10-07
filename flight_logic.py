"""
منطق استخراج اطلاعات پرواز از پیام کاربر با LLM (QWEN) و ادغام آن
با وضعیت فعلی مکالمه.
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
 
import streamlit as st
import re
import jdatetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

 
from models import FlightRequest
from city_options import COUNTRY_NAMES
 
 
# ساخت ال ال ام استخراج‌کننده
@st.cache_resource
def create_flight_extractor():
 
    api_key = st.secrets.get("QWEN_API_KEY")
 
    if not api_key:
        raise RuntimeError(
            "کلید QWEN_API_KEY در فایل secrets.toml پیدا نشد."
        )
 
    llm = ChatOpenAI(
        model="qwen3.8-flash",
        api_key=api_key,
        base_url="https://api.avalai.ir/v1",
        max_retries=2,
        temperature=0
    )
    #ساختار پاسخ ال ال ام
    structured_llm = llm.with_structured_output(
    FlightRequest
)
 
    extraction_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
{{
  "role": "شما بخش استخراج اطلاعات یک دستیار هوشمند جستجوی بلیط پرواز هستید",
  "task": "وظیفه‌ی شما فقط و فقط استخراج ساخت‌یافته‌ی اطلاعات پرواز از متن «همین پیام فعلی» کاربر است. هیچ تصمیم دیگری نمی‌گیرید، هیچ پیشنهادی نمی‌دهید و هیچ پیامی مستقیم به کاربر نمی‌نویسید — فقط فیلدهای خروجی مشخص‌شده را پر می‌کنید.",
  "context": {{
    "today_in_iran": "{today}",
    "previous_conversation_state": "{current_state}",
    "note": "previous_conversation_state فقط برای فهمِ زمینه‌ی پیام فعلی است؛ مقدار هیچ فیلدی را مستقیماً و بدون دلیل از این‌جا کپی نکنید."
  }},
  "golden_rule": "فقط اطلاعاتی را برگردانید که از متنِ همین پیامِ کاربر (نه از previous_conversation_state) به‌طور مستقیم قابل‌استخراج است. اگر فیلدی در این پیام ذکر نشده، مقدارش را null بگذارید — حتی اگر در previous_conversation_state مقدار داشته باشد؛ برنامه خودش مقادیر قبلی را با مقادیر جدید ادغام می‌کند، پس هرگز مقدار قبلی را حدس نزنید یا دوباره برنگردانید. previous_conversation_state را فقط برای «فهمیدن زمینه‌ی» پیام فعلی به‌کار ببرید — مثلاً پیام «فردا» تنها زمانی به‌عنوان ادامه‌ی درخواست قبلی تفسیر می‌شود که از previous_conversation_state معلوم باشد کاربر وسط یک درخواست پرواز است.",
  "fields": {{
    "origin_and_destination": {{
      "known_cities": [
        "تهران","مشهد","اصفهان","شیراز","تبریز","کرج","اهواز","قم","کرمانشاه","ارومیه","رشت","زاهدان","کرمان","همدان","یزد","اردبیل","بندرعباس","اراک","زنجان","سنندج","قزوین","خرم‌آباد","گرگان","ساری","بجنورد","بیرجند","ایلام","شهرکرد","یاسوج","بوشهر","سمنان","کیش","قشم","آبادان","ماهشهر","چابهار","دزفول","بهبهان","سیرجان","رفسنجان","بم","طبس","خوی","مراغه","سبزوار","نیشابور","شاهرود","رامسر","نوشهر","عسلویه","لامرد","کنگان","پارس‌آباد","جهرم","فسا","اهر","گچساران","ایرانشهر","مسجدسلیمان","دوحه","دبی","ابوظبی","استانبول","آنکارا","آنتالیا","ازمیر","ایروان","تفلیس","باکو","مسکو","نجف","کربلا","بغداد","دمشق","بیروت","مسقط","کوالالامپور","بانکوک","پاریس","لندن","فرانکفورت","برلین","رم","میلان","آمستردام","تورنتو","دهلی","بمبئی","کراچی","کابل","تاشکند","دوشنبه","اشک‌آباد","قاهره","جده","مدینه"
      ],
      "rules": [
        "روش کار: ابتدا نام شهرهای موجود در پیام را پیدا کنید، سپس نقش هرکدام (مبدأ یا مقصد) را از روی نشانه‌های زیر یا ترتیب کلمات مشخص کنید.",
        "known_cities فهرست شهرهای شناخته‌شده است. اگر نام شهرِ پیام با یکی از آن‌ها مطابقت دارد، فقط و دقیقاً همان نامِ فهرست را برگردانید و هیچ کلمه‌ی دیگری از پیام به آن اضافه نکنید. املای محاوره‌ای یا جدا را به شکل استانداردِ فهرست تبدیل کنید (مثلاً «بندر عباس» → «بندرعباس»، «خرم آباد» → «خرم‌آباد»). غلط‌های تایپی رایج (مثل افتادگی یا جابه‌جاییِ یک حرف، «تهرون» به‌جای «تهران») را هم در صورت شباهت واضح به نزدیک‌ترین شهرِ فهرست تصحیح کنید.",
        "نام شهر را دقیقاً همان‌طور که کاربر نوشته برگردان. فقط املای ظاهری(مثل «ي»/«ك») را یکسان‌سازی کن و هرگز یک شهر را به شهر دیگری که شبیه آن است تبدیل نکن (مثلاً «قم» را «قشم» نکن).",
        "فهرست محدودکننده نیست: اگر شهری در فهرست نبود، همان نام را با رعایت قانون مرزبندی (فقط خودِ نام شهر، بدون تاریخ و فعل و کلمات اطراف) برگردانید.",
        "هرگز مقدار origin یا destination را با کلماتی مثل «امروز»، «فردا»، «پس‌فردا»، تاریخ، نام روز، «بلیط»، «پرواز»، «می‌خوام»، «میرم»، «رو» یا هر عبارت غیرشهری ادامه ندهید. کلماتی که بعد از اسم شهر می‌آیند مربوط به فیلدهای دیگرند (تاریخ، مرتب‌سازی، ...) نه بخشی از نام شهر.",
        "حرف‌اضافه‌ی «از» فقط وقتی نشانه‌ی مبدأ است که کلمه‌ی مستقلی قبل از نام شهر باشد. «از» داخل نام شهر (مثل شیراز، اهواز) جزو اسم است و نباید جدا شود.",
        "نشانه‌های مبدأ (origin): «از [شهر]»، «از طرف [شهر]»، «[شهر] هستم»/«ساکن [شهر]ام»/«اهل [شهر]» وقتی در ادامه‌ی جمله به رفتن به شهر دیگری اشاره شده، کلمات صریح «مبدا»/«مبدأم»/«مبدأ».",
        "نشانه‌های مقصد (destination) — این‌ها در هر دو ترتیبِ «نشانه + شهر» و «شهر + نشانه» معتبرند، پس هم «برای نجف پرواز می‌خوام» هم «دبی برای فردا» باید destination را پر کنند: «به [شهر]»، «تا [شهر]» (مثل «از تهران تا مشهد»)، «برم/میرم [شهر]» یا «[شهر] برم/میرم»، «برای [شهر]» یا «[شهر] برای ...»، «بلیط [شهر]» یا «پرواز [شهر]» (اشاره‌ی مستقیم بدون حرف‌اضافه، مثل «بلیط دبی می‌خوام»، «پرواز نجف دارید؟»)، «سفر به [شهر]»/«سفرم به [شهر]»، کلمات صریح «مقصد»/«مقصدم».",
        "اگر پیام دقیقاً دو اسم شهر را پشت‌سرهم و بدون حرف‌اضافه یا فعلی بین‌شان بیاورد (مثل «تهران مشهد»)، شهر اول origin و شهر دوم destination است.",
        "اگر پیام فقط اسم یک شهر باشد (بدون هیچ‌کدام از نشانه‌های بالا) و دقیقاً یکی از origin یا destination در previous_conversation_state از قبل پر و دیگری خالی باشد، آن شهر را برای فیلدِ خالی در نظر بگیرید.",
        "اگر هر دو فیلد خالی‌اند، هیچ قرینه‌ای در کار نیست و فقط یک شهر در پیام آمده، شهر را حدسی به مبدأ یا مقصد نسبت ندهید و مقدار نامشخص را null بگذارید.",
        "fallback معنایی (برای عبارت‌هایی که هیچ‌کدام از الگوهای بالا را عیناً ندارند): اگر فقط یک نام شهر در پیام آمده و از معنای کلی جمله («می‌خوام»، «لازم دارم»، «هست؟»، «دارید؟»، «چطور برم» و مشابه آن‌ها در کنار اشاره به بلیط/پرواز/سفر) روشن است که کاربر قصدِ رفتن/سفر به آن شهر را دارد نه آمدن از آن، آن شهر را destination در نظر بگیرید — در گفتار محاوره‌ای فارسی، ذکرِ تنهای مقصد (بدون مبدأ) بسیار رایج‌تر از ذکرِ تنهای مبدأ است."
      ],
      "examples": [
        {{"input": "ارزون‌ترین پرواز تهران به اصفهان برای پس‌فردا رو می‌خوام", "output": {{"origin": "تهران", "destination": "اصفهان", "departure_date_raw": "پس‌فردا"}}}},
        {{"input": "می‌خوام برم تهران", "output": {{"origin": null, "destination": "تهران"}}}},
        {{"input": "به تهران بلیط می‌خوام", "output": {{"origin": null, "destination": "تهران"}}}},
        {{"input": "از تبریز می‌خوام برم تهران", "output": {{"origin": "تبریز", "destination": "تهران"}}}},
        {{"input": "از تهران بلیط می‌خوام", "output": {{"origin": "تهران", "destination": null}}}},
        {{"input": "از تهران تا مشهد", "output": {{"origin": "تهران", "destination": "مشهد"}}}},
        {{"input": "تهران مشهد", "output": {{"origin": "تهران", "destination": "مشهد"}}}},
        {{"input": "می‌خوام مشهد برم", "output": {{"origin": null, "destination": "مشهد"}}}},
        {{"input": "از شیراز به اهواز", "output": {{"origin": "شیراز", "destination": "اهواز"}}}},
        {{"input": "استانبول ۱۰ آبان بلیط می‌خوام", "output": {{"origin": null, "destination": "استانبول"}}}},
        {{"input": "مشهد امروز میرم", "output": {{"origin": null, "destination": "مشهد"}}}},
        {{"input": "دبی برای فردا", "output": {{"origin": null, "destination": "دبی"}}}},
        {{"input": "بندر عباس", "output": {{"origin": null, "destination": null, "note": "فقط یک شهر و بدون قرینه؛ اگر previous_conversation_state یک فیلد خالی دارد به آن نسبت داده می‌شود"}}}},
        {{
          "input": "کرمان و برای فردا",
          "previous_conversation_state": {{"origin": null, "destination": "اردبیل"}},
          "output": {{"origin": "کرمان", "destination": null, "departure_date_raw": "فردا"}}
        }},
        {{"input": "برای نجف پرواز می‌خوام", "output": {{"origin": null, "destination": "نجف"}}}},
        {{"input": "برای کربلا بلیط لازم دارم", "output": {{"origin": null, "destination": "کربلا"}}}},
        {{"input": "بلیط دبی می‌خوام", "output": {{"origin": null, "destination": "دبی"}}}},
        {{"input": "پرواز نجف دارید؟", "output": {{"origin": null, "destination": "نجف"}}}},
        {{"input": "سفرم به استانبوله", "output": {{"origin": null, "destination": "استانبول"}}}},
        {{"input": "چطور از شیراز برم تهران", "output": {{"origin": "شیراز", "destination": "تهران"}}}},
        {{"input": "اهل مشهدم میخوام برم کیش", "output": {{"origin": "مشهد", "destination": "کیش"}}}},
        {{"input": "تهرونم، بلیط شیراز میخوام", "output": {{"origin": "تهران", "destination": "شیراز"}}}}
      ]
    }},
    "departure_date": {{
      "rules": [
        "departure_date_raw باید عیناً همان عبارت تاریخی باشد که کاربر گفته، بدون هیچ تغییری.",
        "departure_date باید همیشه به فرمت YYYY-MM-DD میلادی باشد، مگر این‌که کاربر اصلاً هیچ اشاره‌ای به تاریخ نکرده باشد — در آن صورت هر دو فیلد null می‌مانند.",
        "هرگز صرفاً به‌خاطر نبودن یک مثالِ دقیقاً مشابه، departure_date را خالی نگذارید؛ همیشه تلاش کنید بر اساس today آن را محاسبه کنید.",
        "امروز/فردا/پس‌فردا → نسبت به today محاسبه کنید.",
        "نام روز هفته (شنبه تا جمعه) → نزدیک‌ترین وقوعِ آینده‌ی همان روز نسبت به today.",
        "عبارات نسبیِ دیگر با بازه‌ی زمانی مشخص، مثل «N روز دیگه»، «هفته دیگه»/«یک هفته دیگه»، «ماه دیگه»/«یک ماه دیگه» → خودتان با جمع‌کردن همان بازه به today محاسبه کنید: «هفته دیگه» یعنی today + ۷ روز، «N روز دیگه» یعنی today + N روز، «ماه دیگه» یعنی today + ۳۰ روز.",
        "«همین هفته»/«هفته‌ی بعد»/«هفته بعد» را هم مثل «هفته دیگه» در نظر بگیرید (today + ۷ روز)، مگر این‌که «همین هفته» باشد که باید نزدیک‌ترین روزِ منطقی (فردا) را برگردانید.",
        "«آخر هفته» یعنی نزدیک‌ترین پنجشنبه یا جمعه‌ی پیشِ‌رو (هر کدام زودتر فرا می‌رسد). «اول هفته» یعنی نزدیک‌ترین شنبه‌ی پیشِ‌رو.",
        "«اول ماه» یعنی روز اولِ نزدیک‌ترین ماهِ شمسیِ بعدی؛ «وسط ماه» یعنی روز پانزدهمِ همان ماه؛ «آخر ماه» یعنی آخرین روزِ همان ماهِ شمسی.",
        "عبارات تقریبی مثل «یکی دو روز دیگه» یا «دو سه روز دیگه» → میانگینِ گرد‌شده‌ی بازه را به‌کار ببرید (مثلاً «یکی دو روز دیگه» یعنی today + ۲ روز).",
        "تاریخ‌های تقویمیِ دقیق (مثل «۱۵ آبان» یا «۱۴۰۵/۸/۱۵») را هم تا حد امکان به میلادی تبدیل و در departure_date قرار دهید؛ اگر از صحتِ تبدیل مطمئن نیستید همچنان بهترین حدس خود را بگذارید، نه null — یک بخش دیگر از برنامه این‌گونه تاریخ‌ها را جداگانه و به‌صورت قطعی هم دوباره محاسبه و در صورت لزوم جایگزین می‌کند."
      ],
      "examples": [
        {{"input": "فردا میرم", "today": "2026-09-26", "output": {{"departure_date_raw": "فردا", "departure_date": "2026-09-27"}}}},
        {{"input": "هفته دیگه", "today": "2026-09-26", "output": {{"departure_date_raw": "هفته دیگه", "departure_date": "2026-10-03"}}}},
        {{"input": "سه روز دیگه", "today": "2026-09-26", "output": {{"departure_date_raw": "سه روز دیگه", "departure_date": "2026-09-29"}}}}
      ]
    }},
    "is_flight_request": {{
      "rules": [
        "true: هر اشاره‌ای به بلیط، پرواز، سفر هوایی، مبدأ/مقصد، تاریخ پرواز، تعداد مسافران یا کلاس پرواز — حتی اگر ناقص باشد (مثلاً فقط تعداد مسافران، یا فقط اسم دو شهر).",
        "true: همچنین هر جمله‌ای که با فعل/عبارتِ قصد یا درخواست (نیاز دارم، لازم دارم، دنبال ... هستم، پیدا کن، هست؟، دارید؟، می‌تونم برم؟، چطور برم، میخوام) همراه با یک شهر یا کلمه‌ی سفر/پرواز/بلیط بیاید — ترتیب کلمات یا رسمی/محاوره‌ای بودن تاثیری در true بودن ندارد.",
        "true: اگر کاربر قصد رفتن/سفر به یک «کشور» را دارد (مثل «میخوام برم ترکیه»، «عراق میخوام برم»، «برم امارات»)، حتی بدون اسم شهر یا کلمه‌ی بلیط/پرواز، is_flight_request=true است؛ کشور فقط یک مقصد ناقص است.",
        "false: فقط وقتی پیام هیچ ربطی به جستجو/رزرو بلیط ندارد."
      ]
    }},
    "passenger_counts": {{
      "rules": [
        "چیزی گفته نشده → adults=children=infants=null, passenger_count_provided=false.",
        "فقط عدد کل گفته شده (بدون نوع) → همه را adults در نظر بگیرید، children=infants=0.",
        "نوع مسافران مشخص شده → دقیقاً مطابق متن.",
        "هرگز به‌طور پیش‌فرض یک بزرگسال فرض نکنید؛ مقدار پیش‌فرض فقط بعداً و با انتخاب کاربر در برنامه اعمال می‌شود.",
        "عدد می‌تواند رقمی («۳ نفر») یا به‌صورت حروف («سه نفر»، «دو تا بزرگسال») بیان شده باشد؛ هر دو را به عدد صحیح تبدیل کنید."
      ],
      "examples": [
        {{"input": "سه نفر هستیم", "output": {{"adults": 3, "children": 0, "infants": 0, "passenger_count_provided": true}}}},
        {{"input": "دو بزرگسال و یک کودک", "output": {{"adults": 2, "children": 1, "infants": 0, "passenger_count_provided": true}}}}
      ]
    }},
    "cabin_class": {{
      "rules": [
        " این فیلد اختیاری است و برنامه هرگز درباره‌اش از کاربر سؤال نمی‌پرسد."
        " فقط اگر کاربر صراحتاً اکونومی/بیزینس/فرست گفت → cabin_class مناسب و cabin_class_provided=true."
        " «فرقی نمی‌کند» → cabin_class="unspecified", cabin_class_provided=true."
        " چیزی گفته نشده → cabin_class=null, cabin_class_provided=false."
      ]
    }},
    "sort_by": {{
      "rules": [
        "فقط وقتی صراحتاً درباره‌ی ارزان‌ترین/زودترین/دیرترین/گران‌ترین چیزی گفته شده، sort_by را پر و sort_by_provided=true کنید.",
        "ذکر کلاس پرواز، تعداد مسافران یا تاریخ به‌تنهایی sort_by محسوب نمی‌شود."
      ],
      "examples": [
        {{"input": "ارزون‌ترین پرواز رو می‌خوام", "output": {{"sort_by": "cheapest", "sort_by_provided": true}}}},
        {{"input": "تهران مشهد سه روز دیگه یک نفر اکونومی", "output": {{"sort_by": null, "sort_by_provided": false}}}}
      ]
    }},
    "max_price_toman": {{
      "rules": [
        "چیزی گفته نشده → null.",
        "سقف/بودجه‌ی صریح به تومان → به عدد تومان (نه میلیون) تبدیل کنید.",
        "اگر فقط عدد گفته شد بدون واحد ولی از بافت روشن بود منظور میلیون تومان است، همان تبدیل را انجام دهید.",
        "عدد می‌تواند به‌صورت حروف هم بیان شده باشد (مثلاً «پونزده میلیون»، «حدود ده میلیون»)؛ آن را هم به عدد تومان تبدیل کنید. غلط‌های رایجِ واحد مثل «تومن»/«میلیون تومن»/«۱۵م» را هم به همان شکل تفسیر کنید."
      ],
      "examples": [
        {{"input": "زیر ۱۵ میلیون تومان", "output": {{"max_price_toman": 15000000}}}},
        {{"input": "بودجه‌م حداکثر ۸ میلیونه", "output": {{"max_price_toman": 8000000}}}},
        {{"input": "زیر ۱۵", "output": {{"max_price_toman": 15000000}}}}
      ]
    }}
  }}
}}
"""
        ),
        (
            "human",
            "{user_request}"
        )
    ])
 
    return extraction_prompt | structured_llm


import re

ZWNJ = "\u200c"

KNOWN_CITIES = [
    "تهران","مشهد","اصفهان","شیراز","تبریز","کرج","اهواز","قم","کرمانشاه","ارومیه","رشت","زاهدان","کرمان","همدان","یزد","اردبیل","بندرعباس","اراک","زنجان","سنندج","قزوین","خرم‌آباد","گرگان","ساری","بجنورد","بیرجند","ایلام","شهرکرد","یاسوج","بوشهر","سمنان","کیش","قشم","آبادان","ماهشهر","چابهار","دزفول","بهبهان","سیرجان","رفسنجان","بم","طبس","خوی","مراغه","سبزوار","نیشابور","شاهرود","رامسر","نوشهر","عسلویه","لامرد","کنگان","پارس‌آباد","جهرم","فسا","اهر","گچساران","ایرانشهر","مسجدسلیمان","دوحه","دبی","ابوظبی","استانبول","آنکارا","آنتالیا","ازمیر","ایروان","تفلیس","باکو","مسکو","نجف","کربلا","بغداد","دمشق","بیروت","مسقط","کوالالامپور","بانکوک","پاریس","لندن","فرانکفورت","برلین","رم","میلان","آمستردام","تورنتو","دهلی","بمبئی","کراچی","کابل","تاشکند","دوشنبه","اشک‌آباد","قاهره","جده","مدینه",
]

# اسم کشورها هم شناسایی شود (مثلاً «بلیط ترکیه»)؛ validate_cities بعداً گزینه‌ها را نشان می‌دهد
KNOWN_CITIES = KNOWN_CITIES + [c for c in COUNTRY_NAMES if c not in KNOWN_CITIES]

_SORTED_CITIES = sorted(KNOWN_CITIES, key=len, reverse=True)


def _fa(text: str) -> str:
    return text.replace("ي", "ی").replace("ك", "ک")


def _norm(s: str) -> str:
    return _fa(s).replace(ZWNJ, "").replace(" ", "")


def _city_pattern(city: str) -> str:
    chars = city.replace(ZWNJ, "").replace(" ", "")
    return r"[\s\u200c]?".join(re.escape(c) for c in chars)


_CITY_ALT = "|".join(_city_pattern(c) for c in _SORTED_CITIES)
_CITY_BY_NORM = {_norm(c): c for c in KNOWN_CITIES}

_ORIGIN_RE = re.compile(rf"(?<!\w)(?:از[\s\u200c]+طرف|از)[\s\u200c]+({_CITY_ALT})(?!\w)")
_DEST_RE = re.compile(
    rf"(?<!\w)(?:به|تا|برای|بلیط|پرواز|سفر(?:م)?[\s\u200c]+به)[\s\u200c]+({_CITY_ALT})(?!\w)"
)
# «برای»/«بلیط»/«پرواز» می‌توانند بعد از اسم شهر هم بیایند (مثل «دبی برای فردا»، «نجف بلیط میخوام»)
_DEST_RE_AFTER = re.compile(rf"(?<!\w)({_CITY_ALT})[\s\u200c]+(?:برای|بلیط|پرواز)(?!\w)")


def detect_route_from_text(text: str):
    text = _fa(text)
    m_o = _ORIGIN_RE.search(text)
    m_d = _DEST_RE.search(text) or _DEST_RE_AFTER.search(text)
    origin = _CITY_BY_NORM.get(_norm(m_o.group(1))) if m_o else None
    destination = _CITY_BY_NORM.get(_norm(m_d.group(1))) if m_d else None
    return origin, destination


def clean_city(value, user_message):
    """اگر مدل چیز اضافه چسبانده یا اسم را بریده، با فهرست اصلاح می‌کند."""
    if not value:
        return value
    v, msg = _norm(value), _norm(_fa(user_message))
    for city in _SORTED_CITIES:                 # «اصفهان برای پس‌فردا» → «اصفهان»
        if v.startswith(_norm(city)):
            return city
    for city in _SORTED_CITIES:                 # «شیر» → «شیراز» (اگر در پیام باشد)
        c = _norm(city)
        if len(v) >= 2 and c.startswith(v) and c in msg:
            return city
    return value


class InvalidDateError(Exception):
    """کاربر تاریخ مشخصی گفته، اما آن تاریخ نامعتبر یا در گذشته است.

    برخلاف برگرداندن None (که یعنی «هیچ تاریخی در متن پیدا نشد»)، این
    استثنا یعنی «تاریخی پیدا شد ولی قابل قبول نیست» — این تفاوت لازم است
    تا بتوانیم به کاربر دقیقاً بگوییم چرا تاریخش رد شده، نه اینکه فقط
    بی‌توضیح دوباره از او تاریخ بخواهیم.
    """

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


_PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")

PERSIAN_MONTHS = {
    "فروردین": 1, "اردیبهشت": 2, "خرداد": 3, "تیر": 4,
    "مرداد": 5, "شهریور": 6, "مهر": 7, "آبان": 8,
    "آذر": 9, "دی": 10, "بهمن": 11, "اسفند": 12,
}


def _jalali_to_gregorian_iso(year: int, month: int, day: int, today):
    """تاریخ شمسی را به میلادی تبدیل می‌کند؛ اگر روز/ماه واقعی نباشد یا
    تاریخ در گذشته باشد، InvalidDateError با دلیل مشخص پرتاب می‌کند."""

    try:
        j_date = jdatetime.date(year, month, day)
    except ValueError:
        raise InvalidDateError(
            f"«{year}/{month}/{day}» یک تاریخ معتبر نیست "
            "(روز یا ماه وارد شده وجود ندارد)."
        )

    g_date = j_date.togregorian()

    if g_date < today:
        raise InvalidDateError(
            f"تاریخ «{j_date.strftime('%Y/%m/%d')}» مربوط به گذشته است. "
            "لطفاً تاریخی از امروز به بعد بگویید."
        )

    return g_date.isoformat()


def validate_departure_date_iso(date_iso: str | None, today=None) -> str | None:
    """هر تاریخ میلادیِ نهایی (چه از resolve_departure_date، چه حدسِ مستقیمِ
    LLM) را قبل از استفاده اعتبارسنجی می‌کند.

    اگر تاریخ معتبر و از امروز به بعد باشد None برمی‌گرداند؛ در غیر این
    صورت متنِ توضیحِ خطا برای نمایش به کاربر برمی‌گرداند.
    """

    if not date_iso:
        return None

    if today is None:
        today = datetime.now(ZoneInfo("Asia/Tehran")).date()

    try:
        parsed = datetime.strptime(date_iso, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return f"تاریخ «{date_iso}» قابل تشخیص نیست."

    if parsed < today:
        return (
            f"تاریخ «{date_iso}» مربوط به گذشته است. "
            "لطفاً تاریخی از امروز به بعد بگویید."
        )

    return None



_NUMBER_WORDS = {
    "یک": 1, "یکی": 1, "یه": 1, "دو": 2, "سه": 3, "چهار": 4, "پنج": 5,
    "شش": 6, "شیش": 6, "هفت": 7, "هشت": 8, "نه": 9, "ده": 10,
    "یازده": 11, "دوازده": 12, "سیزده": 13, "چهارده": 14,
    "پانزده": 15, "پونزده": 15, "شانزده": 16, "هفده": 17, "هجده": 18,
    "نوزده": 19, "بیست": 20, "سی": 30,
}
_NUM_TOKEN = r"(?:\d+|" + "|".join(
    sorted(_NUMBER_WORDS, key=len, reverse=True)
) + r")"
_NUM_PHRASE = rf"{_NUM_TOKEN}(?:\s+و\s+{_NUM_TOKEN})?"
_REL_SUFFIX = r"\s*(?:دیگه|دیگر|بعد|بعدی)(?!\w)"


def _to_number(phrase: str):
    """«سه»، «۳»، «بیست و پنج» → عدد؛ اگر نشد None."""
    total = 0
    for part in re.split(r"\s+و\s+", phrase.strip()):
        part = part.translate(_PERSIAN_DIGITS)
        if part.isdigit():
            total += int(part)
        elif part in _NUMBER_WORDS:
            total += _NUMBER_WORDS[part]
        else:
            return None
    return total


def parse_relative_offset_days(text: str):
    """«سه روز دیگه»، «۳ روز دیگه»، «دو سه روز دیگه»، «یک هفته دیگه»،
    «بیست و پنج روز دیگه» → تعداد روز از امروز؛ اگر الگو نبود None."""
    t = text.translate(_PERSIAN_DIGITS)

    # بازه‌ی کلمه‌ای: «دو سه روز دیگه»، «یکی دو روز دیگه»
    pair = re.search(
        rf"(?<!\w)({_NUM_TOKEN})\s+({_NUM_TOKEN})\s+روز{_REL_SUFFIX}", t
    )
    if pair:
        lo, hi = _to_number(pair.group(1)), _to_number(pair.group(2))
        if lo is not None and hi is not None:
            return round((lo + hi) / 2)

    single = re.search(
        rf"(?<!\w)({_NUM_PHRASE})\s+(روز|هفته|ماه){_REL_SUFFIX}", t
    )
    if single:
        n = _to_number(single.group(1))
        if n is not None:
            unit = {"روز": 1, "هفته": 7, "ماه": 30}[single.group(2)]
            return n * unit
    return None


def resolve_departure_date(raw_date: str | None):
 
    if not raw_date:
        return None
 
    # یکسان‌سازی متن فارسی
    text = (
        raw_date
        .strip()
        .replace("\u200c", " ")
        .replace("ي", "ی")
        .replace("ك", "ک")
    )
 
    text = " ".join(text.split())
 
    today = datetime.now(
        ZoneInfo("Asia/Tehran")
    ).date()
 
    # پس‌فردا باید قبل از فردا بررسی شود
    if "پس فردا" in text:
        return (today + timedelta(days=2)).isoformat()
 
    if "فردا" in text:
        return (today + timedelta(days=1)).isoformat()
 
    if "امروز" in text:
        return today.isoformat()

    if "دیروز" in text or "پریروز" in text:
        raise InvalidDateError(
            "تاریخ «دیروز» مربوط به گذشته است. "
            "لطفاً تاریخی از امروز به بعد بگویید."
        )

    # بازه‌های تقریبی مثل «یکی دو روز دیگه» یا «دو سه روز دیگه» → میانگینِ گردشده
    approx_match = re.search(
        r"(\d)\s*(?:تا|،|,)?\s*(\d)\s*روز\s*دیگه",
        text.translate(_PERSIAN_DIGITS)
    )
    if approx_match:
        lo, hi = int(approx_match.group(1)), int(approx_match.group(2))
        avg_days = round((lo + hi) / 2)
        return (today + timedelta(days=avg_days)).isoformat()

    # «سه روز دیگه»، «یک هفته دیگه»، «دو سه روز دیگه» (عدد یا کلمه)
    offset_days = parse_relative_offset_days(text)
    if offset_days is not None:
        return (today + timedelta(days=offset_days)).isoformat()

    # «آخر هفته» باید قبل از «هفته» بررسی شود
    if "آخر هفته" in text or "اخر هفته" in text:
        # نزدیک‌ترین پنجشنبه (weekday=3) یا جمعه (weekday=4)، هرکدام زودتر برسد
        days_to_thu = (3 - today.weekday()) % 7
        days_to_fri = (4 - today.weekday()) % 7
        days_ahead = min(d for d in (days_to_thu, days_to_fri) if d > 0) if today.weekday() not in (3, 4) else 0
        return (today + timedelta(days=days_ahead)).isoformat()

    if "اول هفته" in text:
        # نزدیک‌ترین شنبه‌ی پیشِ‌رو (weekday=5)
        days_ahead = (5 - today.weekday()) % 7
        return (today + timedelta(days=days_ahead)).isoformat()

    if "همین هفته" in text:
        return (today + timedelta(days=1)).isoformat()

    if "هفته بعد" in text or "هفته‌ی بعد" in text or "هفته ی بعد" in text:
        return (today + timedelta(days=7)).isoformat()

    if "وسط ماه" in text:
        today_j = jdatetime.date.fromgregorian(date=today)
        year, month = today_j.year, today_j.month
        if today_j.day > 15:
            month += 1
            if month > 12:
                month, year = 1, year + 1
        return _jalali_to_gregorian_iso(year, month, 15, today)

    if "اول ماه" in text:
        today_j = jdatetime.date.fromgregorian(date=today)
        year, month = today_j.year, today_j.month + 1
        if month > 12:
            month, year = 1, year + 1
        return _jalali_to_gregorian_iso(year, month, 1, today)

    if "آخر ماه" in text or "اخر ماه" in text:
        today_j = jdatetime.date.fromgregorian(date=today)
        year, month = today_j.year, today_j.month
        next_month = month + 1
        next_year = year
        if next_month > 12:
            next_month, next_year = 1, year + 1
        first_of_next = jdatetime.date(next_year, next_month, 1)
        last_day = (first_of_next.togregorian() - timedelta(days=1))
        last_day_j = jdatetime.date.fromgregorian(date=last_day)
        return _jalali_to_gregorian_iso(last_day_j.year, last_day_j.month, last_day_j.day, today)

    # تاریخ عددیِ صریح شمسی، مثل «۱۴۰۳/۱/۵۰» یا «۱۴۰۳-۰۱-۰۵»
    numeric_text = text.translate(_PERSIAN_DIGITS)
    numeric_match = re.search(
        r"(\d{2,4})\s*[/\-]\s*(\d{1,2})\s*[/\-]\s*(\d{1,2})",
        numeric_text
    )
    if numeric_match:
        year, month, day = (int(g) for g in numeric_match.groups())
        if year < 100:
            year += 1400
        return _jalali_to_gregorian_iso(year, month, day, today)

    # فرمتِ «۵ فروردین» یا «۵ فروردین ۱۴۰۴»
    for month_name, month_num in PERSIAN_MONTHS.items():
        month_match = re.search(
            rf"(\d{{1,2}})\s*{month_name}(?:\s+(\d{{3,4}}))?",
            numeric_text
        )
        if month_match:
            day = int(month_match.group(1))
            explicit_year = month_match.group(2)

            if explicit_year:
                year = int(explicit_year)
            else:
                today_j = jdatetime.date.fromgregorian(date=today)
                year = today_j.year
                # اگر با سال امسال، این روز از ماه گذشته، سال بعد را در نظر بگیر
                try:
                    candidate = jdatetime.date(year, month_num, day)
                    if candidate.togregorian() < today:
                        year += 1
                except ValueError:
                    pass  # اجازه بده خطای «روز نامعتبر» پایین‌تر گزارش شود

            return _jalali_to_gregorian_iso(year, month_num, day, today)

    weekdays = {
        "دوشنبه": 0,
        "دو شنبه": 0,
 
        "سه شنبه": 1,
        "سه‌شنبه": 1,
 
        "چهارشنبه": 2,
        "چهار شنبه": 2,
 
        "پنجشنبه": 3,
        "پنج شنبه": 3,
 
        "جمعه": 4,
 
        "شنبه": 5,
 
        "یکشنبه": 6,
        "یک شنبه": 6,
    }
 
    for day_name, target_weekday in sorted(
        weekdays.items(),
        key=lambda item: len(item[0]),
        reverse=True
    ):
 
        if day_name in text:
 
            days_ahead = (
                target_weekday - today.weekday()
            ) % 7
 
            target_date = today + timedelta(
                days=days_ahead
            )
 
            return target_date.isoformat()
 
    return None

CABIN_TEXT_KEYWORDS = [
    ("economy", ("اکونومی", "اقتصادی", "economy")),
    ("business", ("بیزینس", "business")),
    ("first", ("فرست", "first class")),
]

def detect_cabin_in_text(text: str):
    """کلاس پرواز را مستقیم از متن کاربر تشخیص می‌دهد (مستقل از LLM)."""
    t = (
        (text or "")
        .replace("\u200c", " ")
        .replace("ي", "ی")
        .replace("ك", "ک")
        .lower()
    )
    for key, words in CABIN_TEXT_KEYWORDS:
        if any(w in t for w in words):
            return key
    return None

_LONE_CITY_RE = re.compile(rf"(?<!\w)(?:{_CITY_ALT})(?!\w)")
_EXPLICIT_ROLE_RE = re.compile(
    r"(?<!\w)(?:از|به|تا|برای)(?!\w)|برم|میرم|می‌رم|مقصد|مبدا|مبدأ|مبدآ|بلیط|پرواز|سفر"
)


def fill_missing_city_from_lone_message(user_text: str, current_state: dict):
    """وقتی ربات فقط «مبدأ» (یا فقط «مقصد») را پرسیده و کاربر فقط اسم یک
    شهر نوشته، آن شهر قطعاً برای همان فیلدِ خالی است؛ این کار را به‌جای
    LLM مستقیم در کد انجام می‌دهیم (LLM اسم تنها را معمولاً «مقصد» می‌گذاشت
    و مقصد قبلی را خراب می‌کرد).

    خروجی: ("origin" | "destination", نام شهر) یا None."""

    if current_state.get("current_step") not in ("ask_required_fields", "city_choice", "invalid_route"):
        return None

    has_origin = bool(current_state.get("origin"))
    has_destination = bool(current_state.get("destination"))

    # فقط وقتی دقیقاً یکی از این دو خالی است
    if has_origin == has_destination:
        return None

    text = _fa(user_text or "")

    # اگر کاربر خودش نقش شهر را گفته (از/به/تا/برم/مقصد/مبدأ)، دخالت نمی‌کنیم
    if _EXPLICIT_ROLE_RE.search(text.replace(ZWNJ, " ")):
        return None

    cities = {
        _CITY_BY_NORM[_norm(m.group(0))]
        for m in _LONE_CITY_RE.finditer(text)
        if _norm(m.group(0)) in _CITY_BY_NORM
    }

    if len(cities) != 1:
        return None

    field = "destination" if has_origin else "origin"
    return field, cities.pop()



_COUNTRY_RE = re.compile(
    rf"(?<!\w)(?:{'|'.join(_city_pattern(c) for c in sorted(COUNTRY_NAMES, key=len, reverse=True))})(?!\w)"
)


def apply_country_mentions(user_text: str, result, current_state: dict | None = None) -> None:
    """وقتی کاربر اسم «کشور» نوشته (مثلاً «عراق»)، LLM گاهی یک شهر از فهرست
    را حدس می‌زند (مثلاً «کربلا») و کاربر را با شهری که نگفته روبه‌رو می‌کند.
    اینجا اسم کشور مستقیم از متن خودِ کاربر گرفته می‌شود تا بعداً
    validate_cities گزینه‌های آن کشور را نشان بدهد."""
    text = _fa(user_text or "").replace(ZWNJ, " ")
    norm_text = _norm(text)

    for match in _COUNTRY_RE.finditer(text):
        country = _CITY_BY_NORM.get(_norm(match.group(0)))
        if not country:
            continue

        # قبلاً (از LLM یا regex) همین کشور ثبت شده است
        if country in (result.origin, result.destination):
            continue

        before = text[:match.start()].rstrip()
        explicit = True
        if before.endswith(("از", "طرف")):
            field = "origin"
        elif before.endswith(("به", "تا", "برای")):
            field = "destination"
        elif country == "ایران":
            field, explicit = "origin", False   # «ایران ...» بدون حرف اضافه معمولاً مبدأ است
        else:
            field, explicit = "destination", False

        current = getattr(result, field)
        # بدون حرف اضافه: اگر شهری که LLM گفته واقعاً در متن کاربر هست، دستکاری نمی‌کنیم
        if not explicit and current and _norm(current) in norm_text:
            continue

        setattr(result, field, country)

        # مقدار حدسیِ طرف دیگر (شهری که نه در متن است و نه از قبل در state بوده) پاک شود
        other = "destination" if field == "origin" else "origin"
        other_value = getattr(result, other)
        known_before = (current_state or {}).get(other)
        if (
            other_value
            and other_value != known_before
            and _norm(other_value) not in norm_text
        ):
            setattr(result, other, None)



def _relative_date_from_user_text(user_text: str):
    """وقتی LLM مقدار departure_date_raw را خالی گذاشته (مثلاً پیام «ایران سه روز
    دیگه» که اول آن اسم کشور است)، تاریخ‌های نسبی را مستقیم از خود متن
    کاربر می‌خوانیم: «N روز/هفته دیگه»، فردا، پس‌فردا، امروز."""
    text = " ".join(
        (user_text or "").replace(ZWNJ, " ").replace("ي", "ی").replace("ك", "ک").split()
    )
    if (
        parse_relative_offset_days(text) is not None
        or any(w in text for w in ("پس فردا", "فردا", "امروز"))
    ):
        return resolve_departure_date(text)
    return None


def extract_flight_request(user_text: str,current_state: dict | None = None) -> FlightRequest:
 
    today = datetime.now(ZoneInfo("Asia/Tehran")).date().isoformat()
 
    extractor = create_flight_extractor()
    print("===== QWEN CALL =====")
    print("USER:", user_text)
    if current_state is None:
        current_state = {}
    result = extractor.invoke({
        "user_request": user_text,
        "today": today,
        "current_state": current_state
    })
    # کلاس پرواز مستقیم از متن کاربر هم تشخیص داده می‌شود (مستقل از LLM)؛
    # قبل از هر return زودهنگام (مثلاً خطای تاریخ) اجرا می‌شود.
    cabin_from_text = detect_cabin_in_text(user_text)
    if cabin_from_text:
        result.cabin_class = cabin_from_text
        result.cabin_class_provided = True
    elif result.cabin_class in ("economy", "business", "first"):
        result.cabin_class_provided = True

    text_origin, text_destination = detect_route_from_text(
        user_text
    )


    if text_origin:
        result.origin = text_origin


    if text_destination:
        result.destination = text_destination

    # اسم کشور (عراق، ترکیه، ...) → دقیقاً همان، نه شهری که LLM حدس زده
    apply_country_mentions(user_text, result, current_state)

    # LLM گاهی برای «برم ترکیه» is_flight_request=false می‌دهد، در حالی که کد
    # بالا مقصد را از متن پیدا کرده؛ اگر مبدأ/مقصدی داریم و در خودِ پیام
    # نشانه‌ی قصد سفر (برم/میرم/از/به/تا/برای/بلیط/پرواز/سفر/میخوام) هست،
    # پیام قطعاً پروازی است و نباید به مسیر non_flight برود.
    if (not result.is_flight_request) and (result.origin or result.destination):
        _intent_text = _fa(user_text or "").replace(ZWNJ, " ")
        if _EXPLICIT_ROLE_RE.search(_intent_text) or re.search(r"می ?خوام|می ?خواهم|میخام", _intent_text):
            result.is_flight_request = True

    # فقط اسم یک شهر، بعد از سؤال «مبدأ/مقصد را مشخص کنید» → برای فیلد خالی
    lone_city = fill_missing_city_from_lone_message(
        user_text, current_state
    )
    if lone_city:
        field, city = lone_city
        if field == "origin":
            result.origin = city
            result.destination = None   # مقصد قبلی دست‌نخورده می‌ماند
        else:
            result.destination = city
            result.origin = None

    result.origin = clean_city(result.origin, user_text)
    result.destination = clean_city(result.destination, user_text)
    raw_date = result.departure_date_raw


    today_date = datetime.now(ZoneInfo("Asia/Tehran")).date()

    try:
        resolved_date = resolve_departure_date(
            raw_date
        )
        if resolved_date is None and not result.departure_date:
            resolved_date = _relative_date_from_user_text(user_text)
    except InvalidDateError as error:
        # کاربر تاریخ مشخصی گفته ولی نامعتبر یا گذشته بود؛ به‌جای اینکه
        # departure_date خالی بماند و کاربر بی‌دلیل دوباره سؤال شود،
        # علتش را صریح نگه می‌داریم تا در مکالمه نمایش داده شود.
        result.departure_date = None
        result.date_error = error.reason
        return result

    if resolved_date is not None:
        result.departure_date = resolved_date

    # حتی اگر resolve_departure_date چیزی برنگردانده باشد، ممکن است خودِ LLM
    # مستقیماً یک departure_date حدس زده باشد (مثلاً از یک فرمت غیرمعمول)؛
    # آن را هم قبل از قبول کردن، برای گذشته‌نبودن بررسی می‌کنیم.
    date_error = validate_departure_date_iso(
        result.departure_date, today_date
    )
    if date_error:
        result.departure_date = None
        result.date_error = date_error
    return result
 
def merge_flight_state(new_request: FlightRequest):
 
    # اطلاعات قبلی را می‌گیریم
    current_state = st.session_state.get(
        "flight_state",
        {}
    ).copy()
 
    new_data = new_request.model_dump()
 
    # این دو فیلد را جدا مدیریت می‌کنیم
    current_state["is_flight_request"] = new_request.is_flight_request
    new_data.pop("is_flight_request", None)
    new_data.pop("passenger_count_provided", None)
    cabin_class_provided = new_data.pop("cabin_class_provided", False)
    sort_by_provided = new_data.pop("sort_by_provided", False)
    if not cabin_class_provided:
        new_data["cabin_class"] = None
 
    if not sort_by_provided:
        new_data["sort_by"] = None

    # date_error فقط مربوط به همین پیام است؛ نباید از نوبت‌های قبلی
    # باقی بماند و روی پیام درست بعدی هم نمایش داده شود.
    current_state["date_error"] = new_data.pop("date_error", None)
    # فقط اطلاعاتی که در پیام جدید وجود دارند
    # روی اطلاعات قبلی نوشته می‌شوند
    for key, value in new_data.items():
        if value is not None:
            current_state[key] = value
 
    # اگر کاربر خودش تعداد مسافران را گفته باشد
    if new_request.passenger_count_provided:
 
        # اگر کودک یا نوزاد ذکر نشده، صفر در نظر گرفته شود
        if current_state.get("children") is None:
            current_state["children"] = 0
 
        if current_state.get("infants") is None:
            current_state["infants"] = 0
 
        current_state["passenger_status"] = "resolved"
 
    else:
 
        # فقط بار اول ساخته شود
        current_state.setdefault(
            "passenger_status",
            "unknown"
        )
 
    return current_state