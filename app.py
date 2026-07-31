import streamlit as st
import feedparser
import requests
from bs4 import BeautifulSoup

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="المركز الرياضي الشامل",
    page_icon="⚽",
    layout="wide"
)

# محاذاة النص والاتجاه (RTL)
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

# 2. المصادر الرياضية
SPORTS_FEEDS = {
    "⚽ كرة القدم - عربية ومصرية": {
        "روسيا اليوم - رياضة (RT Arabic)": "https://arabic.rt.com/rss/sport/",
        "فرانس 24 - رياضة": "https://www.france24.com/ar/%D8%B1%D9%8A%D8%A7%D8%B6%D8%A9/rss",
        "BBC العربي - رياضة": "https://feeds.bbci.co.uk/arabic/rss.xml",
        "Sky Sports Football": "https://www.skysports.com/rss/12040"
    },
    "🌍 الصحف العالمية": {
        "Sky Sports News": "https://www.skysports.com/rss/12040",
        "BBC Sport UK": "http://feeds.bbci.co.uk/sport/football/rss.xml",
        "Motorsport F1": "https://www.motorsport.com/rss/f1/news/"
    },
    "🏀 كرة السلة و NBA": {
        "Yahoo Sports NBA": "https://sports.yahoo.com/nba/rss/",
        "Sky Sports Basketball": "https://www.skysports.com/rss/12040"
    },
    "🎾 التنس والرياضات الأخرى": {
        "BBC Tennis": "http://feeds.bbci.co.uk/sport/tennis/rss.xml",
        "BBC Boxing": "http://feeds.bbci.co.uk/sport/boxing/rss.xml"
    }
}

# 3. دالة جلب البيانات بدون تخزين مؤقت (تحديث لحظي)
def fetch_feed_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Cache-Control': 'no-cache, no-store, must-revalidate',  # منع الكاش نهائياً
        'Pragma': 'no-cache'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return feedparser.parse(response.content)
        else:
            return feedparser.parse(url)
    except Exception:
        return feedparser.parse(url)

# 4. دالة استخراج الصور
def extract_image_url(entry):
    if 'media_content' in entry and len(entry.media_content) > 0:
        return entry.media_content[0].get('url')
    if 'media_thumbnail' in entry and len(entry.media_thumbnail) > 0:
        return entry.media_thumbnail[0].get('url')
    if 'links' in entry:
        for link in entry.links:
            if link.get('type', '').startswith('image/'):
                return link.get('href')
                
    content_to_search = getattr(entry, 'summary', '') + getattr(entry, 'content', [{'value': ''}])[0]['value']
    soup = BeautifulSoup(content_to_search, 'html.parser')
    img_tag = soup.find('img')
    if img_tag and img_tag.get('src'):
        return img_tag['src']
        
    return None

# 5. الواجهة
st.title("🌐 بوابة الأخبار والرياضة المتكاملة")

# زر التحديث اللحظي
col_title, col_btn = st.columns([3, 1])
with col_btn:
    if st.button("🔄 تحديث الأخبار الآن"):
        st.rerun()

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
    
    feed = fetch_feed_data(feed_url)

    if feed and feed.entries:
        for entry in feed.entries[:10]:
            st.subheader(entry.title)
            
            # عرض وقت نشر الخبر إن وجد
            if hasattr(entry, 'published'):
                st.caption(f"🕒 تاريخ النشر: {entry.published}")
            
            img_url = extract_image_url(entry)
            if img_url:
                st.image(img_url, use_column_width=True)
                
            summary_html = getattr(entry, 'summary', '')
            clean_text = BeautifulSoup(summary_html, "html.parser").get_text().strip()
            
            if clean_text:
                st.write(clean_text)
                
            st.link_button("🔗 قراءة المقال/الخبر كاملاً من المصدر الرسمي", entry.link)
            st.divider()
    else:
        st.warning("تعذر جلب الخلاصات حالياً، يرجى إعادة المحاولة أو تغيير المصدر.")

with tab_videos:
    st.header("🎬 التغطيات المرئية والفيديوهات الرياضية")
    video_option = st.selectbox(
        "📺 اختر التغطية المرئية:",
        [
            "أهداف ولقطات كروية مميزة ⚽",
            "ملخصات سباقات الفورمولا 1 🏎️",
            "أفضل لحظات كرة السلة NBA 🏀"
        ]
    )
    
    if video_option == "أهداف ولقطات كروية مميزة ⚽":
        st.video("https://youtu.be/3JZ_D3ELwOQ")
    elif video_option == "ملخصات سباقات الفورمولا 1 🏎️":
        st.video("https://youtu.be/3JZ_D3ELwOQ")
    else:
        st.video("https://youtu.be/3JZ_D3ELwOQ")
