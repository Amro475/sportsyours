import streamlit as st
import feedparser
import requests
from bs4 import BeautifulSoup

# 1. إعدادات الصفحة والواجهة
st.set_page_config(
    page_title="المنصة الإخبارية الشاملة",
    page_icon="🌍",
    layout="wide"
)

# 2. القائمة الجانبية لإعدادات القارئ (اللغة)
with st.sidebar:
    st.markdown("### ⚙️ إعدادات القارئ")
    lang_option = st.selectbox(
        "اختر اللغة / Language",
        ["العربية", "English"]
    )
    st.divider()

# ضبط النصوص حسب اللغة المختارة
if lang_option == "العربية":
    ui_title = "🌍 المنصة الإخبارية الشاملة"
    ui_desc = "تغطية فورية ومباشرة لأحدث الأخبار العربية، المصرية، والعالمية في كافة المجالات لحظة بلحظة."
    ui_select_source = "🌐 اختر الصحيفة أو المصدر:"
    ui_btn_refresh = "🔄 تحديث الأخبار"
    ui_read_more = "🔗 قراءة الخبر كاملاً من المصدر الرسمي"
    ui_error = "تعذر جلب البيانات من هذا المصدر حالياً، يرجى اختيار مصدر آخر."
    ui_prev_page = "◀️ الصفحة السابقة"
    ui_next_page = "الصفحة التالية ▶️"
    ui_page_text = "الصفحة"
    categories = {
        "⚽ الرياضة": "الرياضة",
        "🏛️ السياسة": "السياسة",
        "💻 التكنولوجيا": "التكنولوجيا",
        "📈 الاقتصاد": "الاقتصاد"
    }
else:
    ui_title = "🌍 Global Comprehensive News Platform"
    ui_desc = "Instant and live coverage of the latest Arab, Egyptian, and international news across all fields in real-time."
    ui_select_source = "🌐 Select Newspaper or Source:"
    ui_btn_refresh = "🔄 Refresh News"
    ui_read_more = "🔗 Read full story from official source"
    ui_error = "Could not fetch data from this source right now, please choose another source."
    ui_prev_page = "◀️ Previous Page"
    ui_next_page = "Next Page ▶️"
    ui_page_text = "Page"
    categories = {
        "⚽ Sports": "Sports",
        "🏛️ Politics": "Politics",
        "💻 Technology": "Technology",
        "📈 Economy": "Economy"
    }

# 3. جدول المصادر الإخبارية الشاملة متضمنة الصحف المصرية والعربية والعالمية
NEWS_FEEDS = {
    "الرياضة": {
        "يلا كورة (مصر - رياضة)": "https://www.yallakora.com/rss/news",
        "بطولات (عربي - رياضة)": "https://www.btolat.com/rss/news",
        "Sky Sports Football": "https://www.skysports.com/rss/12040",
        "Goal.com - أخبار كرة القدم": "https://www.goal.com/feeds/en/news"
    },
    "السياسة": {
        "اليوم السابع (مصر)": "https://www.youm7.com/rss/SectionRss?SecID=287",
        "بوابة الأهرام (مصر)": "https://gate.ahram.org.eg/RSS/1/0.aspx",
        "الجزيرة نت (عربي / سياسة)": "https://www.aljazeera.net/rss",
        "بي بي سي عربي - الرئيسية": "https://feeds.bbci.co.uk/arabic/rss.xml",
        "رويترز - أخبار سياسية وعامة": "https://www.reutersagency.com/feed/?best-regions=middle-east&post_type=best"
    },
    "التكنولوجيا": {
        "تكنولوجيا المعلومات (BBC)": "http://feeds.bbci.co.uk/arabic/scienceandtech/rss.xml",
        "TechCrunch": "https://techcrunch.com/feed/"
    },
    "الاقتصاد": {
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

# 6. واجهة العرض الرئيسية
st.title(ui_title)
st.write(ui_desc)

if st.button(ui_btn_refresh):
    st.rerun()

st.divider()

# اختيار نوع الخبر عبر الأزرار المباشرة
selected_tab_label = st.radio(
    "",
    options=list(categories.keys()),
    horizontal=True
)

selected_category = categories[selected_tab_label]

st.divider()

# قائمة اختيار المصدر التابعة للقسم المحدد
sources = NEWS_FEEDS[selected_category]
selected_source_name = st.selectbox(ui_select_source, list(sources.keys()))

feed_url = sources[selected_source_name]
st.divider()

st.subheader(f"📌 {selected_source_name}")

# جلب الأخبار وتطبيق نظام ترقيم الصفحات (Pagination)
feed = fetch_feed_data(feed_url)

if feed and feed.entries:
    entries = feed.entries
    items_per_page = 5  # عدد الأخبار في كل صفحة
    total_entries = len(entries)
    total_pages = max(1, (total_entries + items_per_page - 1) // items_per_page)
    
    # إدارة حالة الصفحات
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
        
    if 'last_source' not in st.session_state or st.session_state.last_source != selected_source_name:
        st.session_state.current_page = 1
        st.session_state.last_source = selected_source_name

    # أزرار التنقل بين الصفحات بالأعلى
    col_p1, col_p2, col_p3 = st.columns([1, 2, 1])
    with col_p1:
        if st.button(ui_prev_page) and st.session_state.current_page > 1:
            st.session_state.current_page -= 1
            st.rerun()
    with col_p2:
        st.markdown(f"<div style='text-align: center;'><b>{ui_page_text} {st.session_state.current_page} / {total_pages}</b></div>", unsafe_allow_html=True)
    with col_p3:
        if st.button(ui_next_page) and st.session_state.current_page < total_pages:
            st.session_state.current_page += 1
            st.rerun()

    st.divider()

    start_idx = (st.session_state.current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    current_page_entries = entries[start_idx:end_idx]

    for entry in current_page_entries:
        st.markdown(f"### {entry.title}")
        
        if hasattr(entry, 'published') and entry.published:
            st.caption(f"🕒 {entry.published}")
        
        img_url = extract_image_url(entry)
        if img_url:
            st.image(img_url, use_column_width=True)
            
        summary_html = getattr(entry, 'summary', '')
        clean_text = BeautifulSoup(summary_html, "html.parser").get_text().strip()
        
        if clean_text:
            st.write(clean_text)
            
        st.link_button(ui_read_more, entry.link)
        st.divider()
        
    # أزرار التنقل بالأسفل
    col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
    with col_b1:
        if st.button(ui_prev_page + " ") and st.session_state.current_page > 1:
            st.session_state.current_page -= 1
            st.rerun()
    with col_b2:
        st.markdown(f"<div style='text-align: center;'><b>{ui_page_text} {st.session_state.current_page} / {total_pages}</b></div>", unsafe_allow_html=True)
    with col_b3:
        if st.button(ui_next_page + "  ") and st.session_state.current_page < total_pages:
            st.session_state.current_page += 1
            st.rerun()
else:
    st.warning(ui_error)
