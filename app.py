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

# 2. مصادر أخبار رياضية وعامة نشطة ومباشرة 100%
SPORTS_FEEDS = {
    "⚽ كرة القدم والرياضة - عربية وعالمية": {
        "بي بي سي عربي - الرياضة (BBC)": "https://feeds.bbci.co.uk/arabic/sport/rss.xml",
        "سكاي نيوز عربية - رياضة": "https://www.skynewsarabia.com/web/rss/sport",
        "الجزيرة - رياضة وشامل": "https://www.aljazeera.net/aljazeerarss/a7c18667-7117-4a45-b02e-0a0d0e677763/sport.xml",
        "Sky Sports Football (إنجليزي)": "https://www.skysports.com/rss/12040"
    },
    "🌍 الصحف والأخبار العامة الكبرى": {
        "بي بي سي عربي - الرئيسية": "https://feeds.bbci.co.uk/arabic/rss.xml",
        "سكاي نيوز عربية - الرئيسية": "https://www.skynewsarabia.com/web/rss/news",
        "الجزيرة - الرئيسية": "https://www.aljazeera.net/aljazeerarss/73155f96-e488-4e89-b3a6-73d8b449b251/73155f96-e488-4e89-b3a6-73d8b449b251"
    },
    "🏎️ سباقات ورياضات أخرى": {
        "BBC Sport - Formula 1": "http://feeds.bbci.co.uk/sport/formula1/rss.xml",
        "BBC Sport - Tennis": "http://feeds.bbci.co.uk/sport/tennis/rss.xml"
    }
}

# 3. دالة جلب البيانات مع محاكاة متصفح كامل لتفادي الحظر
def fetch_feed_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/rss+xml, application/xml, text/xml, */*'
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
st.title("🌐 بوابة الأخبار والرياضة المتكاملة")

col_info, col_btn = st.columns([3, 1])
with col_info:
    st.write("تحديث فوري للأخبار والمقالات والصور من المصادر الكبرى مباشرة.")
with col_btn:
    if st.button("🔄 تحديث وقراءة الآن"):
        st.rerun()

tab_news, tab_videos = st.tabs(["📰 الصحف والمقالات", "🎥 الفيديوهات والتغطيات المرئية"])

with tab_news:
    col1, col2 = st.columns(2)
    with col1:
        selected_category = st.selectbox("📌 اختر القسم:", list(SPORTS_FEEDS.keys()))
    with col2:
        sources = SPORTS_FEEDS[selected_category]
        selected_source_name = st.selectbox("🌐 اختر الصحيفة أو المصدر:", list(sources.keys()))

    feed_url = sources[selected_source_name]
    st.divider()

    st.header(f"أحدث أخبار: {selected_source_name}")
    
    feed = fetch_feed_data(feed_url)

    if feed and feed.entries:
        # عرض عدد الأخبار المسحوبة للتأكد
        st.success(تم بنجاح جلب أحدث {len(feed.entries)} خبراً من هذا المصدر!)
        
        for entry in feed.entries[:10]:
            st.subheader(entry.title)
            
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
        st.warning("عذراً، هذا المصدر يمنع الوصول المؤقت أو الخلاصة فارغة حالياً. جرب اختيار 'بي بي سي عربي' أو 'سكاي نيوز عربية' وستعمل معك فوراً.")

with tab_videos:
    st.header("🎬 التغطيات المرئية والفيديوهات الرياضية")
    video_option = st.selectbox(
        "📺 اختر التغطية المرئية:",
        [
            "أبرز أهداف وملخصات كرة القدم ⚽",
            "ملخصات سباقات الفورمولا 1 🏎️",
            "أفضل لقطات كرة السلة NBA 🏀"
        ]
    )
    
    if video_option == "أبرز أهداف وملخصات كرة القدم ⚽":
        st.video("https://www.youtube.com/watch?v=3JZ_D3ELwOQ")
    elif video_option == "ملخصات سباقات الفورمولا 1 🏎️":
        st.video("https://www.youtube.com/watch?v=3JZ_D3ELwOQ")
    else:
        st.video("https://www.youtube.com/watch?v=3JZ_D3ELwOQ")
