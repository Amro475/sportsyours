import streamlit as st
import feedparser
from bs4 import BeautifulSoup

# 1. إعدادات الصفحة والواجهة
st.set_page_config(
    page_title="المركز الرياضي الشامل",
    page_icon="⚽",
    layout="wide"
)

# محاذاة النص والاتجاه من اليمين لليسامر (RTL)
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

# 2. القائمة الشاملة للمصادر الرياضية المصورة
SPORTS_FEEDS = {
    "⚽ كرة القدم - مصر والعالم العربي": {
        "يلا كورة (Yallakora)": "https://www.yallakora.com/rss/rssnews",
        "اليوم السابع - رياضة": "https://www.youm7.com/rss/SectionRss?SectionID=298",
        "Sky Sports Football": "https://www.skysports.com/rss/12040",
        "BBC العربي - رياضة": "https://feeds.bbci.co.uk/arabic/rss.xml"
    },
    "🌍 الصحف العالمية": {
        "Sky Sports News": "https://www.skysports.com/rss/12040",
        "BBC Sport UK": "http://feeds.bbci.co.uk/sport/football/rss.xml",
        "Motorsport.com F1": "https://www.motorsport.com/rss/f1/news/"
    },
    "🏀 كرة السلة و NBA": {
        "Yahoo Sports NBA": "https://sports.yahoo.com/nba/rss/",
        "Sky Sports Basketball": "https://www.skysports.com/rss/12040"
    },
    "🎾 التنس": {
        "BBC Tennis": "http://feeds.bbci.co.uk/sport/tennis/rss.xml",
        "Sky Sports Tennis": "https://www.skysports.com/rss/12110"
    },
    "🥊 رياضات قتالية": {
        "BBC Boxing": "http://feeds.bbci.co.uk/sport/boxing/rss.xml",
        "MMA Fighting": "https://www.mmafighting.com/rss/index.xml"
    }
}

# 3. دالة استخراج رابط الصورة من الخبر
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

# 4. واجهة التطبيق الرئيسية
st.title("🌐 بوابة الأخبار والرياضة المتكاملة")
st.write("تغطية شاملة لحظة بلحظة لكافة الرياضات، الصحف العربية والمصرية، الصور والتغطيات المرئية.")

tab_news, tab_videos = st.tabs(["📰 الصحف والمقالات", "🎥 الفيديوهات والتغطيات المرئية"])

with tab_news:
    col1, col2 = st.columns(2)
    with col1:
        selected_category = st.selectbox("📌 اختر القسم والرياضة:", list(SPORTS_FEEDS.keys()))
    with col2:
        sources = SPORTS_FEEDS[selected_category]
        selected_source_name = st.selectbox("🌐 اختر الصحيفة / المصدر:", list(sources.keys()))

    feed_url = sources[selected_source_name]
    st.divider()

    st.header(f"أحدث تغطيات: {selected_source_name}")
    
    feed = feedparser.parse(feed_url, agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")

    if feed.entries:
        for entry in feed.entries[:12]:
            st.subheader(entry.title)
            
            # عرض الصورة إذا توفرت
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
        st.warning("تعذر جلب الخلاصات من هذا المصدر حالياً، يرجى اختيار صحيفة أخرى من القائمة.")

with tab_videos:
    st.header("🎬 التغطيات المرئية والفيديوهات الرياضية")
    st.write("اختر الفيديو أو المقطع المرئي للمشاهدة المباشرة:")
    
    video_option = st.selectbox(
        "📺 اختر التغطية المرئية:",
        [
            "أبرز مهارات وأهداف كرة القدم ⚽",
            "ملخصات وسباقات الفورمولا 1 🏎‍🟀",
            "أفضل لقطات كرة السلة NBA 🏀"
        ]
    )
    
    if video_option == "أبرز مهارات وأهداف كرة القدم ⚽":
        st.video("https://www.youtube.com/watch?v=Lx9n8aC5s2g")
    elif video_option == "ملخصات وسباقات الفورمولا 1 🏎‍🟀":
        st.video("https://www.youtube.com/watch?v=3JZ_D3ELwOQ")
    else:
        st.video("https://www.youtube.com/watch?v=L_LUpnjgPso")
