import streamlit as st
import feedparser
import requests
from bs4 import BeautifulSoup

# 1. إعدادات الصفحة والواجهة
st.set_page_config(
    page_title="المركز الرياضي الشامل",
    page_icon="⚽",
    layout="wide"
)

# محاذاة النص والاتجاة من اليمين لليسار (RTL)
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

# 2. مصادر أخبار رياضية دقيقة وخالصة
SPORTS_FEEDS = {
    "⚽ كرة القدم المحلية والعالمية": {
        "سكاي نيوز عربية - رياضة": "https://www.skynewsarabia.com/web/rss/sport",
        "الجزيرة - قسم الرياضة": "https://www.aljazeera.net/aljazeerarss/a7c18667-7117-4a45-b02e-0a0d0e677763/sport.xml",
        "Sky Sports Football": "https://www.skysports.com/rss/12040"
    },
    "🏎️ سباقات السرعة والمحركات": {
        "BBC Sport - Formula 1": "http://feeds.bbci.co.uk/sport/formula1/rss.xml"
    },
    "🎾 التنس والرياضات الفردية": {
        "BBC Sport - Tennis": "http://feeds.bbci.co.uk/sport/tennis/rss.xml"
    },
    "🏀 كرة السلة والرياضات الأمريكية": {
        "Sky Sports Basketball": "https://www.skysports.com/rss/12040"
    }
}

# 3. دالة جلب الأخبار الرياضية وتجاوز الحظر
def fetch_feed_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
    try:
        response = requests.get(url, headers=headers, timeout=12)
        if response.status_code == 200:
            return feedparser.parse(response.content)
        else:
            return feedparser.parse(url)
    except Exception:
        return feedparser.parse(url)

# 4. دالة استخراج الصور بدقة
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

# 5. واجهة التطبيق
st.title("⚽ المركز الرياضي الشامل - أخبار رياضية حصرياً")

col_info, col_btn = st.columns([3, 1])
with col_info:
    st.write("تغطية حصرية، فورية ومحدثة تلقائياً لأحدث البطولات والمباريات الرياضية.")
with col_btn:
    if st.button("🔄 تحديث الأخبار"):
        st.rerun()

tab_news, tab_videos = st.tabs(["📰 الأخبار والمقالات الرياضية", "🎥 التغطيات المرئية والأهداف"])

with tab_news:
    col1, col2 = st.columns(2)
    with col1:
        selected_category = st.selectbox("📌 اختر الرياضة / التصنيف:", list(SPORTS_FEEDS.keys()))
    with col2:
        sources = SPORTS_FEEDS[selected_category]
        selected_source_name = st.selectbox("🌐 اختر الشبكة أو المصدر الرياضي:", list(sources.keys()))

    feed_url = sources[selected_source_name]
    st.divider()

    st.header(f"آخر أحداث: {selected_source_name}")
    
    feed = fetch_feed_data(feed_url)

    if feed and feed.entries:
        for entry in feed.entries[:12]:
            st.subheader(entry.title)
            
            if hasattr(entry, 'published'):
                st.caption(f"🕒 وقت النشر: {entry.published}")
            
            img_url = extract_image_url(entry)
            if img_url:
                st.image(img_url, use_column_width=True)
                
            summary_html = getattr(entry, 'summary', '')
            clean_text = BeautifulSoup(summary_html, "html.parser").get_text().strip()
            
            if clean_text:
                st.write(clean_text)
                
            st.link_button("🔗 قراءة الخبر كاملاً من المصدر الرسمي", entry.link)
            st.divider()
    else:
        st.warning("جاري جلب أحدث الأخبار الرياضية... يرجى الضغط على زر التحديث في الأعلى.")

with tab_videos:
    st.header("🎬 مقاطع الفيديو والأهداف الرياضية المباشرة")
    video_option = st.selectbox(
        "📺 اختر نوع الفيديو:",
        [
            "أبرز أهداف ومهارات كرة القدم ⚽",
            "ملخصات سباقات الفورمولا 1 والسرعة 🏎️",
            "أفضل لقطات ومهارات كرة السلة NBA 🏀"
        ]
    )
    
    if video_option == "أبرز أهداف ومهارات كرة القدم ⚽":
        st.video("https://www.youtube.com/watch?v=3JZ_D3ELwOQ")
    elif video_option == "ملخصات سباقات الفورمولا 1 والسرعة 🏎️":
        st.video("https://www.youtube.com/watch?v=3JZ_D3ELwOQ")
    else:
        st.video("https://www.youtube.com/watch?v=3JZ_D3ELwOQ")
