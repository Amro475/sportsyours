import streamlit as st
import feedparser
from bs4 import BeautifulSoup
import re

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="منصة الأخبار الرياضية",
    page_icon="🏆",
    layout="wide"
)

# دعم اللغة العربية والاتجاه من اليمين لليسامر (RTL)
st.markdown("""
    <style>
    div[data-testid="stAppViewContainer"] {
        direction: rtl;
        text-align: right;
    }
    div[data-testid="stHeader"] {
        direction: rtl;
    }
    </style>
""", unsafe_allow_html=True)

# 2. مصادر الأخبار العربية لكل الرياضات
SPORTS_FEEDS = {
    "⚽ كرة القدم": {
        "في الجول (FilGoal)": "https://www.filgoal.com/rss/news",
        "يلا كورة (Yallakora)": "https://www.yallakora.com/rss/rssnews",
        "الجزيرة - رياضة": "https://www.aljazeera.net/aljazeerarss/a7c18667-7117-4a45-b02e-0a0d0e677763/sport.xml",
        "Sky Sports Football (إنجليزي)": "https://www.skysports.com/rss/12040"
    },
    "🏀 كرة السلة": {
        "الجزيرة - سلة وریاضات": "https://www.aljazeera.net/aljazeerarss/a7c18667-7117-4a45-b02e-0a0d0e677763/sport.xml",
        "Yahoo Basketball": "https://sports.yahoo.com/nba/rss/"
    },
    "🎾 التنس": {
        "الجزيرة - تنس": "https://www.aljazeera.net/aljazeerarss/a7c18667-7117-4a45-b02e-0a0d0e677763/sport.xml",
        "BBC Tennis": "http://feeds.bbci.co.uk/sport/tennis/rss.xml"
    },
    "🏎‍🟀 سباقات وفورمولا 1": {
        "BBC Formula 1": "http://feeds.bbci.co.uk/sport/formula1/rss.xml",
        "Motorsport F1": "https://www.motorsport.com/rss/f1/news/"
    },
    "🥊 رياضات قتالية (UFC / ملاكمة)": {
        "BBC Boxing": "http://feeds.bbci.co.uk/sport/boxing/rss.xml",
        "MMA Fighting": "https://www.mmafighting.com/rss/index.xml"
    }
}

# 3. دالة لاستخراج رابط الصورة من الخبر
def extract_image_url(entry):
    # محاولة 1: البحث في media_content أو media_thumbnail
    if 'media_content' in entry and len(entry.media_content) > 0:
        return entry.media_content[0].get('url')
    if 'media_thumbnail' in entry and len(entry.media_thumbnail) > 0:
        return entry.media_thumbnail[0].get('url')
    if 'links' in entry:
        for link in entry.links:
            if link.get('type', '').startswith('image/'):
                return link.get('href')
                
    # محاولة 2: البحث عن أي صورة <img src="..."> داخل نص الوصف (Summary/Content)
    content_to_search = getattr(entry, 'summary', '') + getattr(entry, 'content', [{'value': ''}])[0]['value']
    soup = BeautifulSoup(content_to_search, 'html.parser')
    img_tag = soup.find('img')
    if img_tag and img_tag.get('src'):
        return img_tag['src']
        
    return None

# 4. الواجهة الرئيسية
st.title("🏆 منصة الأخبار الرياضية الشاملة")
st.write("تابع أحدث التغطيات الرياضية بالصور وفور صدورها.")

col1, col2 = st.columns(2)
with col1:
    selected_sport = st.selectbox("📌 اختر الرياضة:", list(SPORTS_FEEDS.keys()))
with col2:
    sources = SPORTS_FEEDS[selected_sport]
    selected_source_name = st.selectbox("🌐 اختر المصدر:", list(sources.keys()))

feed_url = sources[selected_source_name]

st.divider()
st.header(f"أخبار {selected_sport} - {selected_source_name}")

# 5. جلب وعرض الأخبار
feed = feedparser.parse(feed_url)

if feed.entries:
    for entry in feed.entries[:10]:
        st.subheader(entry.title)
        
        # استخراج الصورة وعرضها إن وجدت
        img_url = extract_image_url(entry)
        if img_url:
            st.image(img_url, use_column_width=True)
            
        # تنظيف النص من الـ HTML
        summary_html = getattr(entry, 'summary', '')
        clean_text = BeautifulSoup(summary_html, "html.parser").get_text().strip()
        
        if clean_text:
            st.write(clean_text)
            
        st.link_button("🔗 قراءة الخبر كاملاً من المصدر", entry.link)
        st.divider()
else:
    st.warning("عذراً، تعذر جلب الأخبار من هذا المصدر حالياً.")
