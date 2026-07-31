import streamlit as st
import feedparser
import requests
from bs4 import BeautifulSoup

# 1. إعدادات الصفحة والواجهة
st.set_page_config(
    page_title="المنصة الإخبارية الشاملة",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. القائمة الجانبية لإعدادات القارئ (اللغة والسمات)
st.sidebar.header("⚙️ إعدادات القارئ والتحكم")

# اختيار اللغة
lang_option = st.sidebar.selectbox(
    "🌐 اختر اللغة / Language",
    ["العربية", "English"]
)

# ضبط الاتجاه حسب اللغة
if lang_option == "العربية":
    direction = "rtl"
    align = "right"
    ui_title = "🌍 المنصة الإخبارية الشاملة - لحظة بلحظة"
    ui_desc = "تغطية فورية ومباشرة لأحدث الأخبار العربية والعالمية في كافة المجالات."
    ui_select_cat = "📌 اختر التصنيف الإخباري:"
    ui_select_source = "🌐 اختر الصحيفة أو المصدر:"
    ui_btn_refresh = "🔄 تحديث الأخبار الآن"
    ui_read_more = "🔗 قراءة الخبر كاملاً من المصدر الرسمي"
    ui_loading = "جاري جلب أحدث الأخبار الفورية..."
    ui_error = "تعذر جلب البيانات من هذا المصدر حالياً، يرجى اختيار مصدر آخر."
else:
    direction = "ltr"
    align = "left"
    ui_title = "🌍 Global Comprehensive News Platform - Real-time"
    ui_desc = "Instant and live coverage of the latest Arab and international news across all fields."
    ui_select_cat = "📌 Select News Category:"
    ui_select_source = "🌐 Select Newspaper or Source:"
    ui_btn_refresh = "🔄 Refresh News Now"
    ui_read_more = "🔗 Read full story from official source"
    ui_loading = "Fetching latest breaking news..."
    ui_error = "Could not fetch data from this source right now, please choose another source."

# تطبيق اتجاه الصفحة (RTL / LTR) بدون أخطاء برمجية
st.markdown(
    f"""
    <style>
    div[data-testid="stAppViewContainer"] {{
        direction: {direction};
        text-align: {align};
    }
    div[data-testid="stHeader"] {{
        direction: {direction};
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 3. جدول المصادر الإخبارية الشاملة (رياضة، سياسة، تكنولوجيا، اقتصاد)
NEWS_FEEDS = {
    "⚽ الرياضة / Sports": {
        "Sky Sports Football": "https://www.skysports.com/rss/12040",
        "Goal.com - أخبار كرة القدم": "https://www.goal.com/feeds/en/news",
        "BBC Sport - Football": "http://feeds.bbci.co.uk/sport/football/rss.xml"
    },
    "🏛️ السياسة / Politics": {
        "بي بي سي عربي - الرئيسية": "https://feeds.bbci.co.uk/arabic/rss.xml",
        "رويترز - أخبار سياسية وعامة": "https://www.reutersagency.com/feed/?best-regions=middle-east&post_type=best"
    },
    "💻 التكنولوجيا / Technology": {
        "تكنولوجيا المعلومات (BBC)": "http://feeds.bbci.co.uk/arabic/scienceandtech/rss.xml",
        "TechCrunch": "https://techcrunch.com/feed/"
    },
    "📈 الاقتصاد والأعمال / Economy": {
        "بي بي سي عربي - الاقتصاد": "http://feeds.bbci.co.uk/arabic/business/rss.xml"
    }
}

# 4. دالة جلب الأخبار فور صدورها مع تجاوز الحظر
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

# 5. دالة استخراج الصور بدقة لتظهر بشكل جذاب ومريح للقارئ
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

# 6. واجهة العرض الرئيسية
st.title(ui_title)

col_info, col_btn = st.columns([3, 1])
with col_info:
    st.write(ui_desc)
with col_btn:
    if st.button(ui_btn_refresh):
        st.rerun()

st.divider()

# القوائم المنفصلة لاختيار التصنيف والصحيفة بكل مرونة
col1, col2 = st.columns(2)
with col1:
    selected_category = st.selectbox(ui_select_cat, list(NEWS_FEEDS.keys()))
with col2:
    sources = NEWS_FEEDS[selected_category]
    selected_source_name = st.selectbox(ui_select_source, list(sources.keys()))

feed_url = sources[selected_source_name]
st.divider()

st.header(f"📌 {selected_source_name}")

# جلب الأخبار فوراً
feed = fetch_feed_data(feed_url)

if feed and feed.entries:
    for entry in feed.entries[:15]:
        st.subheader(entry.title)
        
        if hasattr(entry, 'published') and entry.published:
            st.caption(f"🕒 {entry.published}")
        
        # عرض الصورة المرفقة إذا وجدت بشكل جذاب ومتناسق
        img_url = extract_image_url(entry)
        if img_url:
            st.image(img_url, use_column_width=True)
            
        summary_html = getattr(entry, 'summary', '')
        clean_text = BeautifulSoup(summary_html, "html.parser").get_text().strip()
        
        if clean_text:
            st.write(clean_text)
            
        st.link_button(ui_read_more, entry.link)
        st.divider()
else:
    st.warning(ui_error)
