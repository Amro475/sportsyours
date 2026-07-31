from bs4 import BeautifulSoup
import feedparser
import requests
import streamlit as st

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="منصة الأخبار الرياضية",
    page_icon="⚽",
    layout="wide",
)

# تنسيق مخصص يدعم العربية وسلس على الشاشات الصغيرة
st.markdown(
    """
    <style>
    div[data-testid="stAppViewContainer"] { 
        direction: rtl; 
        text-align: right; 
    }
    .stSelectbox label {
        font-size: 1.1rem;
        font-weight: bold;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- مصادر الأخبار ---
NEWS_FEEDS = {
    "⚽ كرة القدم": {
        "Sky Sports Football": "https://www.skysports.com/rss/12040",
        "BBC Football": "http://feeds.bbci.co.uk/sport/football/rss.xml",
    },
    "🏀 كرة السلة": {
        "ESPN NBA": "https://www.espn.com/espn/rss/nba/news",
        "Yahoo Sports NBA": "https://sports.yahoo.com/nba/rss.xml",
    },
    "🎾 كرة المضرب (تنس)": {
        "BBC Tennis": "http://feeds.bbci.co.uk/sport/tennis/rss.xml",
        "ESPN Tennis": "https://www.espn.com/espn/rss/tennis/news",
    },
    "🏎‍🟀 فورمولا 1": {
        "BBC Formula 1": "http://feeds.bbci.co.uk/sport/formula1/rss.xml",
        "ESPN F1": "https://www.espn.com/espn/rss/f1/news",
    },
}


def get_parsed_feed(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return feedparser.parse(response.content)
    except Exception:
        return feedparser.parse(url)


def extract_image(entry):
    if "media_thumbnail" in entry and len(entry.media_thumbnail) > 0:
        return entry.media_thumbnail[0].get("url")
    if "media_content" in entry and len(entry.media_content) > 0:
        return entry.media_content[0].get("url")
    if "enclosures" in entry and len(entry.enclosures) > 0:
        return entry.enclosures[0].get("href")

    if "summary" in entry:
        soup = BeautifulSoup(entry.summary, "html.parser")
        img = soup.find("img")
        if img and img.get("src"):
            return img["src"]

    return "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=600"


# --- الواجهة الرئيسية ---
st.title("🏆 منصة الأخبار الرياضية")
st.write("تابع أحدث التغطيات الرياضية فور صدورها.")

# اختيار الرياضة من قائمة منسدلة أعلى الصفحة بدلاً من القائمة الجانبية المزعجة
category = st.selectbox(
    "📌 اختر القسم الرياضي:", list(NEWS_FEEDS.keys()), index=0
)

st.divider()
st.header(f"أخبار {category}")

sources = NEWS_FEEDS[category]

for source_name, url in sources.items():
    st.subheader(f"🌐 المصدر: {source_name}")
    feed = get_parsed_feed(url)

    if not feed.entries:
        st.info(f"لا توجد تحديثات جديدة حالياً من {source_name}.")
        continue

    cols = st.columns(2)

    for idx, entry in enumerate(feed.entries[:4]):
        col = cols[idx % 2]
        img_url = extract_image(entry)

        with col:
            st.image(img_url, use_container_width=True)
            st.markdown(f"### [{entry.title}]({entry.link})")

            if "summary" in entry:
                clean_text = BeautifulSoup(
                    entry.summary, "html.parser"
                ).text.strip()
                if len(clean_text) > 130:
                    clean_text = clean_text[:130] + "..."
                st.write(clean_text)

            st.link_button("قراءة الخبر من المصدر 🔗", entry.link)
            st.write("")

    st.divider()