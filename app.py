import streamlit as st
import feedparser
from bs4 import BeautifulSoup

# 1. إعدادات الصفحة والواجهة
st.set_page_config(
    page_title="المركز الرياضي الشامل",
    page_icon="⚽",
    layout="wide"
)

# دعم الاتجاه من اليمين لليسامر (RTL) وتنسيق بطاقات الأخبار
st.markdown("""
    <style>
    div[data-testid="stAppViewContainer"] {
        direction: rtl;
        text-align: right;
    }
    div[data-testid="stHeader"] {
        direction: rtl;
    }
    .stVideo {
        border-radius: 10px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. القائمة الشاملة للصحف والمصادر (مصرية، عربية، عالمية)
SPORTS_FEEDS = {
    "⚽ كرة القدم - صحف مصريـة وعربيـة": {
        "الجزيرة - رياضة (شامل)": "https://www.aljazeera.net/aljazeerarss/a7c18667-7117-4a45-b02e-0a0d0e677763/sport.xml",
        "روسيا اليوم (RT Arabic)": "https://arabic.rt.com/rss/sport/",
        "فرانس 24 (France 24)": "https://www.france24.com/ar/%DD8%B1%D9%8A%D8%A7%D8%B6%D8%A9/rss",
        "BBC العربي - رياضة": "https://feeds.bbci.co.uk/arabic/rss.xml",
        "يلا كورة (Yallakora)": "https://www.yallakora.com/rss/rssnews",
    },
    "🌍 كرة القدم - الصحف العالمية": {
        "Sky Sports Football": "https://www.skysports.com/rss/12040",
        "BBC Sport UK": "http://feeds.bbci.co.uk/sport/football/rss.xml",
        "Marca (ماركا الإسبانية)": "https://e00-marca.uecdn.es/rss/futbol/liga-bbva.xml"
    },
    "🏀 كرة السلة و NBA": {
        "Yahoo Sports NBA": "https://sports.yahoo.com/nba/rss/",
        "Sky Sports Basketball": "https://www.skysports.com/rss/12040",
        "الجزيرة - تغطيات السلة": "https://www.aljazeera.net/aljazeerarss/a7c18667-7117-4a45-b02e-0a0d0e677763/sport.xml"
    },
    "🎾 التنس و الرياضات الفردية": {
        "BBC Tennis": "http://feeds.bbci.co.uk/sport/tennis/rss.xml",
        "Sky Sports Tennis": "https://www.skysports.com/rss/12110"
    },
    "🏎‍🟀 سباقات ومحركات (Formula 1)": {
        "BBC Formula 1": "http://feeds.bbci.co.uk/sport/formula1/rss.xml",
        "Motorsport.com F1": "https://www.motorsport.com/rss/f1/news/"
    },
    "🥊 رياضات قتالية ومصارعة (UFC/Boxing)": {
        "BBC Boxing": "http://feeds.bbci.co.uk/sport/boxing/rss.xml",
        "MMA Fighting": "https://www.mmafighting.com/rss/index.xml"
    }
}

# 3. مكتبة الفيديوهات والتغطيات المرئية المباشرة
SPORTS_VIDEOS = {
    "أهداف وملخصات المبارايات (YouTube)": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", # رابط توضيحي يمكن استبداله بقنوات مثل OnTime Sports
    "ملخصات التنس والمحركات": "https://www.youtube.com/watch?v=3JZ_D3ELwOQ"
}

# 4. دالة متطورة لاستخراج أفضل صورة متاحة في الخبر
def extract_image_url(entry):
    # البحث فيوسائط Feedparser
    if 'media_content' in entry:
        for media in entry.media_content:
            if 'url' in media:
                return media['url']
    if 'media_thumbnail' in entry and len(entry.media_thumbnail) > 0:
        return entry.media_thumbnail[0].get('url')
    if 'links' in entry:
        for link in entry.links:
            if link.get('type', '').startswith('image/'):
                return link.get('href')
                
    # البحث في نص HTML الخاص بالخبر
    content_to_search = getattr(entry, 'summary', '') + getattr(entry, 'content', [{'value': ''}])[0]['value']
    soup = BeautifulSoup(content_to_search, 'html.parser')
    img_tag = soup.find('img')
    if img_tag and img_tag.get('src'):
        return img_tag['src']
        
    return None

# 5. واجهة التطبيق الرئيسية
st.title("🌐 بوابة الأخبار والرياضة المتكاملة")
st.write("تغطية شاملة لحظة بلحظة لكافة الرياضات، الصحف العربية والمصرية، الصور والتغطيات المرئية.")

# تبويبات لتنظيم المحتوى (أخبار نصية / فيديوهات ومقاطع)
tab_news, tab_videos = st.tabs(["📰 الصحف والمقالات", "🎥 الفيديوهات والتغطيات المرئية"])

with tab_news:
    col1, col2 = st.columns(2)
    with col1:
        selected_category = st.selectbox("📌 اختر القسم والرياضة:", list(SPORTS_FEEDS.keys()))
    with col2:
        sources = SPORTS_FEEDS[selected_category]
        selected_source_name = st.selectbox("🌐 اختر الصحيفة / المصدر:", list(sources.keys()))

    feed_url = sources[selected_source_name]
    st.divider()

    st.header(f"أحدث تغطيات: {selected_source_name}")
    
    # جلب الأخبار مع استخدام User-Agent لمنع الحظر
    feed = feedparser.parse(feed_url, agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")

    if feed.entries:
        for entry in feed.entries[:12]:
            st.subheader(entry.title)
            
            # عرض الصورة إن وجدت
            img_url = extract_image_url(entry)
            if img_url:
                st.image(img_url, use_column_width=True)
                
            # استخراج النص والتفاصيل الكاملة
            summary_html = getattr(entry, 'summary', '')
            clean_text = BeautifulSoup(summary_html, "html.parser").get_text().strip()
            
            if clean_text:
                st.write(clean_text)
                
            st.link_button("🔗 قراءة المقال/الخبر كاملاً من المصدر الرسمي", entry.link)
            st.divider()
    else:
        st.warning("تعذر جلب الخلاصات من هذا المصدر حالياً، يرجى اختيار صحيفة أخرى من القائمة.")

with tab_videos:
    st.header("🎬 التغطيات المرئية والفيديوهات الرياضية")
    st.write("متابعة ملخصات المباريات والتحليلات مباشرة:")
    
    # مشغل فيديو مدمج
    st.video("https://www.youtube.com/watch?v=2g811KoJBUo") # فيديو تجريبي ملخصات
    st.caption("تغطية ملخصات وتحليلات رياضية")
