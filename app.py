import streamlit as st
import feedparser
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from io import BytesIO

# 1. إعدادات الصفحة والواجهة
st.set_page_config(
    page_title="المنصة الإخبارية الشاملة",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. تصميم وتنسيق عصري (Modern Theme CSS)
st.markdown("""
<style>
    /* خلفية الصفحة وتحسين الخطوط */
    .main {
        background-color: #f8f9fa;
    }
    
    /* تصميم بطاقات الأخبار */
    .news-card {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border: 1px solid #eef2f6;
        margin-bottom: 25px;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }
    .news-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
    }
    
    /* جعل زر القراءة متناسق */
    .stLinkButton>a {
        border-radius: 8px !important;
        font-weight: 600 !important;
        background: linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%) !important;
        color: white !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. القائمة الجانبية لإعدادات (اللغة)
with st.sidebar:
    st.markdown("### ⚙️ إعدادات / Settings")
    lang_option = st.selectbox(
        "اختر اللغة / Language",
        ["العربية", "English"]
    )
    st.divider()

# 4. توحيد مصادر الأخبار (لكي تظل هي نفسها دائماً وتترجم فقط عند تغيير اللغة)
NEWS_FEEDS = {
    "Sports": {
        "بي بي سي سبورت (BBC Sport)": "http://feeds.bbci.co.uk/sport/football/rss.xml",
        "سكاي سبورتس (Sky Sports)": "https://www.skysports.com/rss/12040",
        "إي إس بي إن (ESPN)": "https://www.espn.com/espn/rss/news"
    },
    "Politics": {
        "بي بي سي نيوز (BBC World)": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "الغارديان (The Guardian World)": "https://www.theguardian.com/world/rss",
        "سي إن إن (CNN World)": "http://rss.cnn.com/rss/edition_world.rss"
    },
    "Technology": {
        "تك كرانش (TechCrunch)": "https://techcrunch.com/feed/",
        "ذا فيرج (The Verge)": "https://www.theverge.com/rss/index.xml",
        "وايرد (Wired)": "https://www.wired.com/feed/rss"
    },
    "Economy": {
        "بي بي سي اقتصاد (BBC Business)": "http://feeds.bbci.co.uk/news/business/rss.xml",
        "فاينانشال تايمز (Financial Times)": "https://www.ft.com/?format=rss",
        "سي إن بي سي (CNBC)": "https://www.cnbc.com/id/100003114/device/rss/rss.html"
    },
    "Arts": {
        "بي بي سي فن وثقافة (BBC Arts)": "http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
        "أرت نيوز (ARTnews)": "https://www.artnews.com/feed/",
        "الغارديان ثقافة (The Guardian Culture)": "https://www.theguardian.com/culture/rss"
    }
}

# ضبط نصوص الواجهة بناءً على اللغة
if lang_option == "العربية":
    ui_title = "🌍 المنصة الإخبارية الشاملة"
    ui_desc = "تغطية فورية ومباشرة لأحدث الأخبار بأسلوب عصري ومترجم كلياً."
    ui_select_source = "🌐 اختر المصدر الإخباري:"
    ui_btn_refresh = "🔄 تحديث الأخبار"
    ui_read_more = "🔗 قراءة الخبر كاملاً من المصدر الأصلي"
    ui_error = "تعذر جلب البيانات من هذا المصدر حالياً، يرجى اختيار مصدر آخر."
    ui_prev_btn = "◀ الصفحة السابقة"
    ui_next_btn = "الصفحة التالية ▶"
    
    categories = {
        "⚽ الرياضة": "Sports",
        "🏛️ السياسة": "Politics",
        "💻 التكنولوجيا": "Technology",
        "📈 الاقتصاد": "Economy",
        "🎨 الفنون": "Arts"
    }
else:
    ui_title = "🌍 Comprehensive News Platform"
    ui_desc = "Live and instant coverage of the latest news with automatic translation."
    ui_select_source = "🌐 Select News Source:"
    ui_btn_refresh = "🔄 Refresh News"
    ui_read_more = "🔗 Read Full Story from Official Source"
    ui_error = "Could not fetch data from this source right now, please select another source."
    ui_prev_btn = "◀ Previous Page"
    ui_next_btn = "Next Page ▶"
    
    categories = {
        "⚽ Sports": "Sports",
        "🏛️ Politics": "Politics",
        "💻 Technology": "Technology",
        "📈 Economy": "Economy",
        "🎨 Arts": "Arts"
    }

# 5. دالة جلب خلاصة الأخبار
def fetch_feed_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
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

# 6. دالة استخراج وتجهيز الصورة بدقة HD
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_hd_og_image(article_url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(article_url, headers=headers, timeout=4)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, 'html.parser')
            og_tag = (soup.find('meta', property='og:image') or 
                      soup.find('meta', attrs={'name': 'og:image'}) or 
                      soup.find('meta', property='twitter:image:src') or
                      soup.find('meta', property='twitter:image'))
            if og_tag and og_tag.get('content'):
                return og_tag['content']
    except Exception:
        pass
    return None

def extract_best_hd_image(entry):
    if hasattr(entry, 'link') and entry.link:
        hd_url = fetch_hd_og_image(entry.link)
        if hd_url:
            return hd_url

    if 'media_content' in entry and len(entry.media_content) > 0:
        for media in entry.media_content:
            if 'url' in media:
                return media['url']

    if 'enclosures' in entry:
        for enc in entry.enclosures:
            if enc.get('type', '').startswith('image/'):
                return enc.get('href')

    content_to_search = getattr(entry, 'summary', '') + getattr(entry, 'content', [{'value': ''}])[0]['value']
    soup = BeautifulSoup(content_to_search, 'html.parser')
    img_tag = soup.find('img')
    if img_tag and img_tag.get('src'):
        return img_tag['src']

    return None

def display_hd_image(img_url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(img_url, headers=headers, timeout=5)
        if response.status_code == 200:
            image_bytes = BytesIO(response.content)
            st.image(image_bytes, use_container_width=True)
            return
    except Exception:
        pass
    
    try:
        st.image(img_url, use_container_width=True)
    except Exception:
        pass

# دالة الترجمة الذكية الكاش
@st.cache_data(ttl=86400, show_spinner=False)
def translate_text(text, target_lang):
    if not text or not text.strip():
        return ""
    try:
        target = 'ar' if target_lang == "العربية" else 'en'
        translated = GoogleTranslator(source='auto', target=target).translate(text)
        return translated if translated else text
    except Exception:
        return text

# دالة الترقيم المبسطة
def render_clean_pagination(total_pages, key_prefix):
    col_prev, col_info, col_next = st.columns([1, 1, 1])
    
    with col_prev:
        if st.button(ui_prev_btn, key=f"{key_prefix}_prev", disabled=(st.session_state.current_page == 1), use_container_width=True):
            st.session_state.current_page -= 1
            st.rerun()
            
    with col_info:
        st.markdown(f"<p style='text-align: center; margin-top: 8px; font-weight: bold; font-size: 1.1rem;'>{st.session_state.current_page} / {total_pages}</p>", unsafe_allow_html=True)
            
    with col_next:
        if st.button(ui_next_btn, key=f"{key_prefix}_next", disabled=(st.session_state.current_page == total_pages), use_container_width=True):
            st.session_state.current_page += 1
            st.rerun()

# 7. بناء الواجهة الرئيسية
st.title(ui_title)
st.write(ui_desc)

# تهيئة Session State للمرة الأولى
tab_names = list(categories.keys())
if 'selected_category_tab' not in st.session_state or st.session_state.selected_category_tab not in tab_names:
    st.session_state.selected_category_tab = tab_names[0]

if 'current_page' not in st.session_state:
    st.session_state.current_page = 1

# عند الضغط على زر التحديث: يعود تلقائياً لأول قسم ولأول خبر
if st.button(ui_btn_refresh):
    st.session_state.current_page = 1
    st.session_state.selected_category_tab = tab_names[0]
    if 'selected_source_index' in st.session_state:
        st.session_state.selected_source_index = 0
    st.rerun()

st.divider()

# عرض القائمة بشكل أفقي (Horizontal segmented control)
selected_tab = st.segmented_control(
    "",
    tab_names,
    default=st.session_state.selected_category_tab
)

if not selected_tab:
    selected_tab = tab_names[0]

st.session_state.selected_category_tab = selected_tab
selected_category_key = categories[selected_tab]

st.divider()

# جلب قائمة المصادر بناءً على القسم المحدد
sources = NEWS_FEEDS[selected_category_key]
source_names = list(sources.keys())

# عند ضبط التحديث يتم التمرير على أول مصدر تلقائياً
if 'selected_source_index' not in st.session_state or st.session_state.selected_source_index >= len(source_names):
    st.session_state.selected_source_index = 0

selected_source_name = st.selectbox(ui_select_source, source_names, index=st.session_state.selected_source_index)
feed_url = sources[selected_source_name]

st.divider()

st.subheader(f"📌 {selected_source_name}")

feed = fetch_feed_data(feed_url)

if feed and feed.entries:
    entries = feed.entries
    items_per_page = 5
    total_entries = len(entries)
    total_pages = max(1, (total_entries + items_per_page - 1) // items_per_page)
    
    # إعادة التصفير عند تغيير المصدر
    if 'last_source' not in st.session_state or st.session_state.last_source != selected_source_name:
        st.session_state.current_page = 1
        st.session_state.last_source = selected_source_name

    if st.session_state.current_page > total_pages:
        st.session_state.current_page = 1

    render_clean_pagination(total_pages, "top_p")
    st.divider()

    start_idx = (st.session_state.current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    current_page_entries = entries[start_idx:end_idx]

    for entry in current_page_entries:
        # ترجمة العنوان والمضمون لضمان المطابقة الكاملة
        translated_title = translate_text(entry.title, lang_option)
        
        st.markdown("<div class='news-card'>", unsafe_allow_html=True)
        st.markdown(f"### {translated_title}")
        
        if hasattr(entry, 'published') and entry.published:
            st.caption(f"🕒 {entry.published}")
        
        img_url = extract_best_hd_image(entry)
        if img_url:
            col_img, _ = st.columns([3, 1])
            with col_img:
                display_hd_image(img_url)
            
        summary_html = getattr(entry, 'summary', '')
        clean_text = BeautifulSoup(summary_html, "html.parser").get_text().strip()
        
        if clean_text:
            translated_summary = translate_text(clean_text, lang_option)
            st.write(translated_summary)
            
        st.link_button(ui_read_more, entry.link)
        st.markdown("</div>", unsafe_allow_html=True)
        
    render_clean_pagination(total_pages, "bottom_p")
else:
    st.warning(ui_error)
