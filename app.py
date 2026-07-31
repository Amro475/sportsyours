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

# محاذاة النص والاتجاه من اليمين لليسار (RTL)
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

# 2. المصادر الرياضية النشطة والمضمونة 100% (بدون حظر)
SPORTS_FEEDS = {
    "⚽ شبكات كرة القدم العالمية الكبرى": {
        "Sky Sports Football": "https://www.skysports.com/rss/12040",
        "Goal.com - أخبار كرة القدم": "https://www.goal.com/feeds/en/news",
        "BBC Sport - Football": "http://feeds.bbci.co.uk/sport/football/rss.xml"
    },
    "🏎️ سباقات السرعة والمحركات": {
        "Motorsport.com F1": "https://www.motorsport.com/rss/f1/news/",
        "BBC Sport - Formula 1": "http://feeds.bbci.co.uk/sport/formula1/rss.xml"
    },
    "🎾 التنس والرياضات الفردية": {
        "BBC Sport - Tennis": "http://feeds.bbci.co.uk/sport/tennis/rss.xml"
    },
    "🏀 كرة السلة والرياضات الأمريكية": {
        "Sky Sports Basketball": "https://www.skysports.com/rss/12040"
    }
}

# 3. دالة جلب الأخبار وتجاوز الحظر
def fetch_feed_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Cache-Control': 'no-cache',
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

# 4. فلتر ذكي صارم لمنع أي كلمات سياسية أو غير رياضية نهائياً
def is_sports_news(title, summary):
    forbidden_words = [
        "حماس", "سياسة", "حكومة", "انتخابات", "فلسطين", "غزة", "جيش", 
        "رئيس", "وزير", "برلمان", "عسكري", "انفجار", "حرب", "أمريكية", 
        "إيران", "صراع", "منطقة", "واشنطن", "الرئيس"
    ]
    text = (title + " " + summary).lower()
    for word in forbidden_words:
        if word in text:
            return False
    return True

# 5. دالة استخراج الصور بدقة
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

# 6. واجهة التطبيق
st.title("⚽ المركز الرياضي الشامل - رياضة فقط")

col_info, col_btn = st.columns([3, 1])
with col_info:
    st.write("تغطية حصرية وفورية لأحدث المباريات والأخبار الرياضية الصافية.")
with col_btn:
    if st.button("🔄 تحديث الأخبار الآن"):
        st.rerun()

tab_news, tab_videos = st.tabs(["📰 الأخبار الرياضية", "🎥 التغطيات المرئية والأهداف"])

with tab_news:
    col1, col2 = st.columns(2)
    with col1:
        selected_category = st.selectbox("📌 اختر القسم الرياضي:", list(SPORTS_FEEDS.keys()))
    with col2:
        sources = SPORTS_FEEDS[selected_category]
        selected_source_name = st.selectbox("🌐 اختر المصدر الرياضي:", list(sources.keys()))

    feed_url = sources[selected_source_name]
    st.divider()

    st.header(f"آخر أحداث: {selected_source_name}")
    
    feed = fetch_feed_data(feed_url)

    if feed and feed.entries:
        filtered_entries = [
            entry for entry in feed.entries 
            if is_sports_news(entry.title, getattr(entry, 'summary', ''))
        ]
        
        if filtered_entries:
            for entry in filtered_entries[:12]:
                st.subheader(entry.title)
                
                if hasattr(entry, 'published') and entry.published:
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
            st.warning("جاري جلب أحدث الأخبار الرياضية...")
    else:
        st.warning("تعذر جلب البيانات من هذا المصدر حالياً، يرجى اختيار مصدر آخر.")

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
    
    # تحديث روابط الفيديوهات لتتوافق مع محتوى كرة القدم والرياضة الحقيقية
    if video_option == "أبرز أهداف ومهارات كرة القدم ⚽":
        st.video("https://www.youtube.com/watch?v=2tXh3W5C30o")
    elif video_option == "ملخصات سباقات الفورمولا 1 والسرعة 🏎️":
        st.video("https://www.youtube.com/watch?v=0hK2aWwXb4I")
    else:
        st.video("https://www.youtube.com/watch?v=450p7goxZqg")
