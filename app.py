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

# 2. المصادر الرياضية العربية والعالمية المباشرة
SPORTS_FEEDS = {
    "⚽ الصحف والشبكات الرياضية (عربي وعالمي)": {
        "يلا كورة - أخبار كرة القدم": "https://www.yallakora.com/rss/news",
        "beIN Sports - أحدث الأخبار": "https://www.beinsports.com/ar/rss",
        "Sky Sports Football (إنجليزي)": "https://www.skysports.com/rss/12040",
        "BBC Sport - Football (إنجليزي)": "http://feeds.bbci.co.uk/sport/football/rss.xml",
        "Goal.com - أخبار كرة القدم": "https://www.goal.com/feeds/en/news"
    },
    "🏎️ سباقات السرعة والمحركات": {
        "BBC Sport - Formula 1": "http://feeds.bbci.co.uk/sport/formula1/rss.xml",
        "Motorsport.com F1": "https://www.motorsport.com/rss/f1/news/"
    },
    "🎾 التنس والرياضات الفردية": {
        "BBC Sport - Tennis": "http://feeds.bbci.co.uk/sport/tennis/rss.xml"
    },
    "🏀 كرة السلة والرياضات الأمريكية": {
        "Sky Sports Basketball": "https://www.skysports.com/rss/12040"
    }
}

# 3. دالة جلب الأخبار عبر خدمة وسيطة لتفادي الحظر تماماً
def fetch_feed_data(url):
    # استخدام خدمة rss2json الموثوقة لتجاوز حظر المواقع وجلب الأخبار فوراً
    api_url = f"https://api.rss2json.com/v1/api.json?rss_url={url}"
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'ok':
                # تحويل البيانات إلى هيكل مطابق لـ feedparser لعدم تغيير باقي الكود
                class Entry:
                    def __init__(self, item):
                        self.title = item.get('title', '')
                        self.link = item.get('link', '')
                        self.published = item.get('pubDate', '')
                        self.summary = item.get('description', '')
                        self.content = [{'value': item.get('content', '')}]
                        
                        # استخراج الصور إن وجدت
                        thumbnail = item.get('thumbnail', '')
                        enclosure = item.get('enclosure', {})
                        img_link = enclosure.get('link', '') if isinstance(enclosure, dict) else ''
                        
                        if thumbnail:
                            self.media_thumbnail = [{'url': thumbnail}]
                        elif img_link:
                            self.media_content = [{'url': img_link}]
                            
                class Feed:
                    def __init__(self, items):
                        self.entries = [Entry(item) for item in items]
                        
                return Feed(data.get('items', []))
    except Exception:
        pass
        
    # الطريقة الاحتياطية المباشرة
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return feedparser.parse(response.content)
    except Exception:
        pass
        
    return feedparser.parse(url)

# 4. فلتر ذكي لمنع أي كلمات سياسية وضمان الرياضة فقط
def is_sports_news(title, summary):
    forbidden_words = ["حماس", "سياسة", "حكومة", "انتخابات", "فلسطين", "غزة", "جيش", "رئيس", "وزير", "برلمان", "عسكري", "انفجار"]
    text = (title + " " + summary).lower()
    for word in forbidden_words:
        if word in text:
            return False
    return True

# 5. دالة استخراج الصور بدقة
def extract_image_url(entry):
    if hasattr(entry, 'media_content') and len(entry.media_content) > 0:
        return entry.media_content[0].get('url')
    if hasattr(entry, 'media_thumbnail') and len(entry.media_thumbnail) > 0:
        return entry.media_thumbnail[0].get('url')
    if hasattr(entry, 'links') and entry.links:
        for link in entry.links:
            if link.get('type', '').startswith('image/'):
                return link.get('href')
                
    content_to_search = getattr(entry, 'summary', '')
    soup = BeautifulSoup(content_to_search, 'html.parser')
    img_tag = soup.find('img')
    if img_tag and img_tag.get('src'):
        return img_tag['src']
        
    return None

# 6. واجهة التطبيق
st.title("⚽ المركز الرياضي الشامل - صحف عربية وعالمية")

col_info, col_btn = st.columns([3, 1])
with col_info:
    st.write("تغطية رياضية فورية ومحدثة لحظة بلحظة من الصحف العربية والعالمية الحصرية.")
with col_btn:
    if st.button("🔄 تحديث الأخبار الآن"):
        st.rerun()

tab_news, tab_videos = st.tabs(["📰 الأخبار الرياضية (عربي وعالمي)", "🎥 التغطيات المرئية والأهداف"])

with tab_news:
    col1, col2 = st.columns(2)
    with col1:
        selected_category = st.selectbox("📌 اختر القسم الرياضي:", list(SPORTS_FEEDS.keys()))
    with col2:
        sources = SPORTS_FEEDS[selected_category]
        selected_source_name = st.selectbox("🌐 اختر الصحيفة أو المصدر:", list(sources.keys()))

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
            st.warning("لا توجد أخبار جديدة مطابقة حالياً.")
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
    
    if video_option == "أبرز أهداف ومهارات كرة القدم ⚽":
        st.video("https://www.youtube.com/watch?v=3JZ_D3ELwOQ")
    elif video_option == "ملخصات سباقات الفورمولا 1 والسرعة 🏎️":
        st.video("https://www.youtube.com/watch?v=3JZ_D3ELwOQ")
    else:
        st.video("https://www.youtube.com/watch?v=3JZ_D3ELwOQ")
