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

# 3. جدول المصادر الإخبارية الشاملة (المفاتيح الموحدة)
NEWS_FEEDS = {
    "الرياضة": {
        "بي بي سي سبورت - كرة القدم": "http://feeds.bbci.co.uk/sport/football/rss.xml",
        "بطولات (عربي - رياضة)": "https://www.btolat.com/rss/news",
        "Sky Sports Football": "https://www.skysports.com/rss/12040",
        "Goal.com - أخبار كرة القدم": "https://www.goal.com/feeds/en/news"
    },
    "السياسة": {
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

# ضبط النصوص وقاموس الأزرار حسب اللغة المختارة
if lang_option == "العربية":
    ui_title = "🌍 المنصة الإخبارية الشاملة"
    ui_desc = "تغطية فورية ومباشرة لأحدث الأخبار العربية والعالمية في كافة المجالات لحظة بلحظة."
    ui_select_source = "🌐 اختر الصحيفة أو المصدر:"
    ui_btn_refresh = "🔄 تحديث الأخبار"
    ui_read_more = "🔗 قراءة الخبر كاملاً من المصدر الرسمي"
    ui_error = "تعذر جلب البيانات من هذا المصدر حالياً، يرجى اختيار مصدر آخر."
    ui_page_label = "📍 انتقل للصفحة:"
    categories_map = {
        "⚽ الرياضة": "الرياضة",
        "🏛️ السياسة": "السياسة",
        "💻 التكنولوجيا": "التكنولوجيا",
        "📈 الاقتصاد": "الاقتصاد"
    }
else:
    ui_title = "🌍 Global Comprehensive News Platform"
    ui_desc = "Instant and live coverage of the latest Arab and international news across all fields in real-time."
    ui_select_source = "🌐 Select Newspaper or Source:"
    ui_btn_refresh = "🔄 Refresh News"
    ui_read_more = "🔗 Read full story from official source"
    ui_error = "Could not fetch data from this source right now, please choose another source."
    ui_page_label = "📍 Go to page:"
    categories_map = {
        "⚽ Sports": "الرياضة",
        "🏛️ Politics": "السياسة",
        "💻 Technology": "التكنولوجيا",
        "📈 Economy": "الاقتصاد"
    }

# 4. دالة جلب الأخبار
def fetch_feed_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/rss+xml, application/xml, text/xml, */*'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return feedparser.parse(response.content)
    except Exception:
        pass
    return feedparser.parse(url)

# 5. دالة استخراج الصور
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

# اختيار نوع الخبر عبر الأزرار المباشرة (Segmented Control)
tab_options = list(categories_map.keys())
selected_tab = st.segmented_control("", tab_options, default=tab_options[0])

# في حال إلغاء التحديد نرجع إلى الخيار الأول تلقائياً
if not selected_tab:
    selected_tab = tab_options[0]

# الحصول على مفتاح NEWS_FEEDS الصحيح
selected_category = categories_map[selected_tab]

st.divider()

# قائمة اختيار المصدر التابعة للقسم المحدد
sources = NEWS_FEEDS.get(selected_category, {})
selected_source_name = st.selectbox(ui_select_source, list(sources.keys()))

feed_url = sources[selected_source_name]
st.divider()

st.subheader(f"📌 {selected_source_name}")

# جلب الأخبار وتطبيق نظام أرقام الصفحات (Pagination)
feed = fetch_feed_data(feed_url)

if feed and feed.entries:
    entries = feed.entries
    items_per_page = 5
    total_entries = len(entries)
    total_pages = max(1, (total_entries + items_per_page - 1) // items_per_page)
    
    # إدارة حالة الصفحة الحالية
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
        
    if 'last_source' not in st.session_state or st.session_state.last_source != selected_source_name:
        st.session_state.current_page = 1
        st.session_state.last_source = selected_source_name

    # عرض أرقام الصفحات بأزرار رقمية مباشرة (1, 2, 3...)
    st.write(f"**{ui_page_label}**")
    page_cols = st.columns(total_pages)
    for p in range(1, total_pages + 1):
        btn_type = "primary" if p == st.session_state.current_page else "secondary"
        if page_cols[p-1].button(str(p), key=f"top_p_{p}", type=btn_type):
            st.session_state.current_page = p
            st.rerun()

    st.divider()

    # تحديد الأخبار المعروضة بالصفحة
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
        
    # عرض أزرار الترقيم الرقمية في الأسفل أيضاً
    st.write(f"**{ui_page_label}**")
    bottom_page_cols = st.columns(total_pages)
    for p in range(1, total_pages + 1):
        btn_type = "primary" if p == st.session_state.current_page else "secondary"
        if bottom_page_cols[p-1].button(str(p), key=f"bottom_p_{p}", type=btn_type):
            st.session_state.current_page = p
            st.rerun()
else:
    st.warning(ui_error)
