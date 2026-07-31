import streamlit as st
import feedparser
from bs4 import BeautifulSoup

# 1. قائمة الشاملة لكل الرياضات والمصادر
SPORTS_FEEDS = {
    "⚽ كرة القدم": {
        "Sky Sports Football": "https://www.skysports.com/rss/12040",
        "BBC Football": "http://feeds.bbci.co.uk/sport/football/rss.xml",
        "FilGoal (في الجول)": "https://www.filgoal.com/rss/news"
    },
    "🏀 كرة السلة": {
        "NBA News (Yahoo)": "https://sports.yahoo.com/nba/rss/",
        "Sky Sports Basketball": "https://www.skysports.com/rss/12040"  # يمكن إضافة روابط مخصصة
    },
    "🎾 التنس": {
        "BBC Tennis": "http://feeds.bbci.co.uk/sport/tennis/rss.xml",
        "Sky Sports Tennis": "https://www.skysports.com/rss/12110"
    },
    "🏎‍🟀 فورمولا 1 (Motorsport)": {
        "BBC Formula 1": "http://feeds.bbci.co.uk/sport/formula1/rss.xml",
        "Motorsport.com": "https://www.motorsport.com/rss/f1/news/"
    },
    "🥊 الفنون القتالية (UFC/Boxing)": {
        "BBC Boxing": "http://feeds.bbci.co.uk/sport/boxing/rss.xml",
        "MMA Fighting": "https://www.mmafighting.com/rss/index.xml"
    },
    "🌐 رياضة عامة (شاملة)": {
        "BBC Sport Main": "http://feeds.bbci.co.uk/sport/rss.xml",
        "Sky Sports News": "https://www.skysports.com/rss/12040"
    }
}

st.title("🏆 منصة الأخبار الرياضية الشاملة")
st.write("تابع أحدث التغطيات لجميع الرياضات فور صدورها.")

# 2. القوائم المنسدلة للترشيح
selected_sport = st.selectbox("📌 اختر الرياضة:", list(SPORTS_FEEDS.keys()))

# جلب المصادر الخاصة بالرياضة المحددة فقط
sources = SPORTS_FEEDS[selected_sport]
selected_source_name = st.selectbox("🌐 اختر المصدر:", list(sources.keys()))

# الحصول على رابط الـ RSS للمصدر المختار
feed_url = sources[selected_source_name]

# 3. عرض الأخبار
st.header(f"أخبار {selected_sport} - {selected_source_name}")

feed = feedparser.parse(feed_url)

if feed.entries:
    for entry in feed.entries[:10]: # عرض أول 10 أخبار
        st.subheader(entry.title)
        
        # تنظيف النص من الـ HTML
        summary_html = getattr(entry, 'summary', '')
        clean_text = BeautifulSoup(summary_html, "html.parser").get_text()
        
        st.write(clean_text)
        st.link_button("🔗 قراءة الخبر من المصدر", entry.link)
        st.divider()
else:
    st.warning("عذراً، تعذر جلب الأخبار من هذا المصدر حالياً.")
