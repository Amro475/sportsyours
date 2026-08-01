import streamlit as st
import feedparser
import requests
from bs4 import BeautifulSoup
from googletrans import Translator

# إعداد مترجم جوجل
translator = Translator()

# 1. إعدادات الصفحة والواجهة
st.set_page_config(
    page_title="المنصة الإخبارية الشاملة",
    page_icon="🌍",
    layout="wide"
)

# 2. القائمة الجانبية لإعدادات (اللغة)
with st.sidebar:
    st.markdown("### ⚙️ إعدادات / Settings")
    lang_option = st.selectbox(
        "اختر اللغة / Language",
        ["العربية", "English"]
    )
    st.divider()

# ضبط جميع نصوص الواجهة والأقسام بناءً على اللغة
if lang_option == "العربية":
    ui_title = "🌍 المنصة الإخبارية الشاملة"
    ui_desc = "تغطية فورية ومباشرة لأحدث الأخبار العربية والعالمية في كافة المجالات لحظة بلحظة."
    ui_select_source = "🌐 اختر الصحيفة أو المصدر:"
    ui_btn_refresh = "🔄 تحديث الأخبار"
    ui_read_more = "🔗 قراءة الخبر كاملاً من المصدر الرسمي"
    ui_error = "تعذر جلب البيانات من هذا المصدر حالياً، يرجى اختيار مصدر آخر."
    ui_page_label = "📍 انتقل للصفحة:"
    
    categories = {
        "⚽ الرياضة": "الرياضة",
        "🏛️ السياسة": "السياسة",
        "💻 التكنولوجيا": "التكنولوجيا",
        "📈 الاقتصاد": "الاقتصاد"
    }
    
    NEWS_FEEDS = {
        "الرياضة": {
            "بطولات (عربي)": "https://www.btolat.com/rss/news",
            "بي بي سي سبورت": "http://feeds.bbci.co.uk/sport/football/rss.xml",
            "سكاي سبورتس": "https://www.skysports.com/rss/12040"
        },
        "السياسة": {
            "الجزيرة نت": "https://www.aljazeera.net/rss",
            "بي بي سي عربي": "https://feeds.bbci.co.uk/arabic/rss.xml"
        },
        "التكنولوجيا": {
            "تكنولوجيا (BBC عربي)": "http://feeds.bbci.co.uk/arabic/scienceandtech/rss.xml",
            "تك كرانش": "https://techcrunch.com/feed/"
        },
        "الاقتصاد": {
            "اقتصاد (BBC عربي)": "http://feeds.bbci.co.uk/arabic/business/rss.xml"
        }
    }
else:
    ui_title = "🌍 Global News Platform"
    ui_desc = "Live and instant coverage of the latest Arab and international news across all fields."
    ui_select_source = "🌐 Select Newspaper or Source:"
    ui_btn_refresh = "🔄 Refresh News"
    ui_read_more = "🔗 Read Full Story from Official Source"
    ui_error = "Could not fetch data from this source right now, please select another source."
    ui_page_label = "📍 Go to Page:"
    
    categories = {
        "⚽ Sports": "الرياضة",
        "🏛️ Politics": "السياسة",
        "💻 Technology": "التكنولوجيا",
        "📈 Economy": "الاقتصاد"
    }
    
    NEWS_FEEDS = {
        "الرياضة": {
            "BBC Sport Football": "http://feeds.bbci.co.uk/sport/football/rss.xml",
            "Sky Sports Football": "https://www.skysports.com/rss/12040",
            "Btolat Sports": "https://www.btolat.com/rss/news"
        },
        "السياسة": {
            "Al Jazeera Net": "https://www.aljazeera.net/rss",
            "BBC Arabic News": "https://feeds.bbci.co.uk/arabic/rss.xml"
        },
        "التكنولوجيا": {
            "BBC Tech News": "http://feeds.bbci.co.uk/arabic/scienceandtech/rss.xml",
            "TechCrunch": "https://techcrunch.com/feed/"
        },
        "الاقتصاد": {
            "BBC Economy": "http://feeds.bbci.co.uk/arabic/business/rss.xml"
        }
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

# دالة لترجمة المحتوى تلقائياً
def translate_text(text, target_lang):
    if not text:
        return ""
    try:
        dest = 'ar' if target_lang == "العربية" else 'en'
        translated = translator.translate(text, dest=dest)
        return translated.text
    except Exception:
        return text  # في حال تعذر الترجمة يتم إرجاع النص كما هو

# 6. واجهة العرض الرئيسية
st.title(ui_title)
st.write(ui_desc)

if st.button(ui_btn_refresh):
    st.rerun()

st.divider()

# اختيار نوع الخبر باستخدام أزرار التبويب المباشرة (Tabs)
tab_names = list(categories.keys())
selected_tab = st.segmented_control("", tab_names, default=tab_names[0])

if not selected_tab:
    selected_tab = tab_names[0]

selected_category = categories[selected_tab]

st.divider()

sources = NEWS_FEEDS[selected_category]
selected_source_name = st.selectbox(ui_select_source, list(sources.keys()))

feed_url = sources[selected_source_name]
st.divider()

st.subheader(f"📌 {selected_source_name}")

feed = fetch_feed_data(feed_url)

if feed and feed.entries:
    entries = feed.entries
    items_per_page = 5
    total_entries = len(entries)
    total_pages = max(1, (total_entries + items_per_page - 1) // items_per_page)
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
        
    if 'last_source' not in st.session_state or st.session_state.last_source != selected_source_name:
        st.session_state.current_page = 1
        st.session_state.last_source = selected_source_name

    # أزرار الترقيم الرقمية في الأعلى
    st.write(f"**{ui_page_label}**")
    page_cols = st.columns(total_pages)
    for p in range(1, total_pages + 1):
        btn_type = "primary" if p == st.session_state.current_page else "secondary"
        if page_cols[p-1].button(str(p), key=f"top_p_{p}", type=btn_type):
            st.session_state.current_page = p
            st.rerun()

    st.divider()

    start_idx = (st.session_state.current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    current_page_entries = entries[start_idx:end_idx]

    for entry in current_page_entries:
        # ترجمة العنوان والملخص بناءً على اللغة المختارة
        translated_title = translate_text(entry.title, lang_option)
        st.markdown(f"### {translated_title}")
        
        if hasattr(entry, 'published') and entry.published:
            st.caption(f"🕒 {entry.published}")
        
        img_url = extract_image_url(entry)
        if img_url:
            st.image(img_url, use_column_width=True)
            
        summary_html = getattr(entry, 'summary', '')
        clean_text = BeautifulSoup(summary_html, "html.parser").get_text().strip()
        
        if clean_text:
            translated_summary = translate_text(clean_text, lang_option)
            st.write(translated_summary)
            
        st.link_button(ui_read_more, entry.link)
        st.divider()
        
    # أزرار الترقيم الرقمية في الأسفل
    st.write(f"**{ui_page_label}**")
    bottom_page_cols = st.columns(total_pages)
    for p in range(1, total_pages + 1):
        btn_type = "primary" if p == st.session_state.current_page else "secondary"
        if bottom_page_cols[p-1].button(str(p), key=f"bottom_p_{p}", type=btn_type):
            st.session_state.current_page = p
            st.rerun()
else:
    st.warning(ui_error)
