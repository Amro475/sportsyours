import streamlit as st
import feedparser
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

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
    ui_page_label = "📍 اختر الصفحة:"
    ui_prev_btn = "◀ الصفحة السابقة"
    ui_next_btn = "الصفحة التالية ▶"
    
    categories = {
        "⚽ الرياضة": "الرياضة",
        "🏛️ السياسة": "السياسة",
        "💻 التكنولوجيا": "التكنولوجيا",
        "📈 الاقتصاد": "الاقتصاد"
    }
    
    NEWS_FEEDS = {
        "الرياضة": {
            "سكاي نيوز عربية - رياضة": "https://www.skynewsarabia.com/rss/sport.xml",
            "فرانس 24 - رياضة": "https://www.france24.com/ar/%D8%B1%D9%8A%D8%A7%D8%B6%D8%A9/rss",
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
    ui_page_label = "📍 Select Page:"
    ui_prev_btn = "◀ Previous Page"
    ui_next_btn = "Next Page ▶"
    
    categories = {
        "⚽ Sports": "الرياضة",
        "🏛️ Politics": "السياسة",
        "💻 Technology": "التكنولوجيا",
        "📈 Economy": "الاقتصاد"
    }
    
    NEWS_FEEDS = {
        "الرياضة": {
            "Sky News Arabic - Sports": "https://www.skynewsarabia.com/rss/sport.xml",
            "France 24 - Sports": "https://www.france24.com/ar/%D8%B1%D9%8A%D8%A7%D8%B6%D8%A9/rss",
            "BBC Sport Football": "http://feeds.bbci.co.uk/sport/football/rss.xml",
            "Sky Sports Football": "https://www.skysports.com/rss/12040"
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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    try:
        response = requests.get(url, headers=headers, timeout=12)
        if response.status_code == 200:
            parsed = feedparser.parse(response.content)
            if parsed.entries:
                return parsed
    except Exception:
        pass
    return feedparser.parse(url)

# 5. دالة استخراج الصور عالية الجودة
def extract_high_res_image(entry):
    if 'enclosures' in entry:
        for enc in entry.enclosures:
            if enc.get('type', '').startswith('image/'):
                return enc.get('href')
                
    if 'media_content' in entry and len(entry.media_content) > 0:
        for media in entry.media_content:
            if 'url' in media:
                return media['url']

    if 'links' in entry:
        for link in entry.links:
            if link.get('type', '').startswith('image/'):
                return link.get('href')

    content_to_search = getattr(entry, 'summary', '') + getattr(entry, 'content', [{'value': ''}])[0]['value']
    soup = BeautifulSoup(content_to_search, 'html.parser')
    img_tag = soup.find('img')
    if img_tag and img_tag.get('src'):
        src = img_tag['src']
        clean_src = src.split('?')[0] if 'http' in src else src
        return clean_src
        
    return None

# دالة الترجمة
def translate_text(text, target_lang):
    if not text or not text.strip():
        return ""
    try:
        target = 'ar' if target_lang == "العربية" else 'en'
        translated = GoogleTranslator(source='auto', target=target).translate(text)
        return translated if translated else text
    except Exception:
        return text

# دالة الترقيم المنسقة النظيفة بمرونة عالية
def render_clean_pagination(total_pages, key_prefix):
    col_prev, col_select, col_next = st.columns([1, 2, 1])
    
    # زر الصفحة السابقة
    with col_prev:
        if st.button(ui_prev_btn, key=f"{key_prefix}_prev", disabled=(st.session_state.current_page == 1), use_container_width=True):
            st.session_state.current_page -= 1
            st.rerun()
            
    # اختيار رقم الصفحة من قائمة منسدلة أنيقة
    with col_select:
        page_options = list(range(1, total_pages + 1))
        selected_p = st.selectbox(
            ui_page_label,
            options=page_options,
            index=st.session_state.current_page - 1,
            key=f"{key_prefix}_select",
            label_visibility="collapsed"
        )
        if selected_p != st.session_state.current_page:
            st.session_state.current_page = selected_p
            st.rerun()
            
    # زر الصفحة التالية
    with col_next:
        if st.button(ui_next_btn, key=f"{key_prefix}_next", disabled=(st.session_state.current_page == total_pages), use_container_width=True):
            st.session_state.current_page += 1
            st.rerun()

# 6. واجهة العرض الرئيسية
st.title(ui_title)
st.write(ui_desc)

if st.button(ui_btn_refresh):
    st.rerun()

st.divider()

# اختيار نوع الخبر
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

    # ضمان عدم تجاوز حدود الصفحات
    if st.session_state.current_page > total_pages:
        st.session_state.current_page = 1

    # شريط التنقل العلوي
    render_clean_pagination(total_pages, "top_p")
    st.divider()

    start_idx = (st.session_state.current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    current_page_entries = entries[start_idx:end_idx]

    for entry in current_page_entries:
        translated_title = translate_text(entry.title, lang_option)
        st.markdown(f"### {translated_title}")
        
        if hasattr(entry, 'published') and entry.published:
            st.caption(f"🕒 {entry.published}")
        
        img_url = extract_high_res_image(entry)
        if img_url:
            st.image(img_url, use_container_width=True)
            
        summary_html = getattr(entry, 'summary', '')
        clean_text = BeautifulSoup(summary_html, "html.parser").get_text().strip()
        
        if clean_text:
            translated_summary = translate_text(clean_text, lang_option)
            st.write(translated_summary)
            
        st.link_button(ui_read_more, entry.link)
        st.divider()
        
    # شريط التنقل السفلي
    render_clean_pagination(total_pages, "bottom_p")
else:
    st.warning(ui_error)
