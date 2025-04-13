import streamlit as st
import feedparser
import requests
from bs4 import BeautifulSoup
import unicodedata
import re
import json

st.set_page_config(page_title="Știrile Zilei", layout="wide")
st.title("🗞️ Știrile zilei pe gustul tău")

# Alegere interese din listă fixă
st.markdown("### ✅ Selectează interesele tale:")
all_interests = [
    "AI și tehnologie",
    "Economie și afaceri",
    "Politică din România",
    "Știri internaționale",
    "Memeuri & virale",
    "Șah",
    "Sport",
    "Evenimente locale"
]
interests = st.multiselect("Alege una sau mai multe categorii:", all_interests)

# City selection from list
city_options = ["Iași", "Cluj", "Timișoara", "București", "Brașov", "Constanța", "Sibiu"]
city = st.selectbox("🏙️ Alege orașul tău", city_options)

# Option to include local news
include_local = st.checkbox("🔎 Vreau să văd și știri locale din orașul selectat", value=True)

# Time of day selection
moment = st.selectbox("🕒 Alege momentul zilei", ["Dimineață", "Prânz", "Seară"])

# Surse preferate (doar cele românești)
all_sources = ["Hotnews", "Go4it", "ZF", "Stiripesurse", "Digi24", "Ziare locale", "Reddit","Adevarul","Realitatea"]
selected_sources = st.multiselect("🗂️ Alege sursele tale preferate de știri", all_sources, default=all_sources)

# RSS Catalog pe interese
rss_catalog = {
    "Hotnews": {
        "AI și tehnologie": "https://www.hotnews.ro/rss/stiinta",
        "Economie și afaceri": "https://www.hotnews.ro/rss/economie",
        "Politică din România": "https://www.hotnews.ro/rss/politica",
        "Știri internaționale": "https://www.hotnews.ro/rss"
    },
    "Go4it": {
        "AI și tehnologie": "https://www.go4it.ro/feed"
    },
    "ZF": {
        "Economie și afaceri": "https://www.zf.ro/rss"
    },
    "Stiripesurse": {
        "Politică din România": "https://www.stiripesurse.ro/rss"
    },
    "Digi24": {
        "Știri internaționale": "https://www.digi24.ro/rss",
        "Politică din România": "https://www.digi24.ro/rss/politica"
    },
    "Reddit": {
        "Memeuri & virale": "https://www.reddit.com/r/romania/top/.rss?t=day",
        "Șah": "https://www.reddit.com/r/sah/.rss"
    },
    "Adevarul": {
        "Politică din România": "https://adevarul.ro/rss/politica/index.xml"
    },
    "Realitatea": {
        "Politică din România": "https://www.realitatea.net/rss/politica"
    }
}

local_rss_map = {
    "iași": "https://www.ziaruldeiasi.ro/rss",
    "cluj": "https://www.monitorulcj.ro/rss",
    "timișoara": "https://www.opiniatimisoarei.ro/feed",
    "bucurești": "https://adevarul.ro/rss/locale/bucuresti/index.xml",
    "brașov": "https://www.bzb.ro/rss",
    "constanța": "https://www.ziuaconstanta.ro/rss",
    "sibiu": "https://www.turnulsfatului.ro/rss"
}

# Funcție utilitară pentru a curăța HTML tags și a încheia cu punct complet
def clean_summary(html):
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', html)
    sentences = re.split(r'(?<=[.!?]) +', text)
    return ' '.join(sentences[:2])

# Button to generate news
if st.button("🔘 Generează știrile"):
    if not interests:
        st.warning("Te rog selectează cel puțin un interes.")
    else:
        st.success(", ".join(interests))
        if include_local and city:
            location_info = f"în {city} ({moment.lower()})"
        else:
            location_info = f"la nivel general ({moment.lower()})"

        st.info(f"🔍 Vom căuta știri actuale despre: {', '.join(interests)} {location_info} din sursele: {', '.join(selected_sources)}")

        st.markdown("---")
        st.markdown("### 📰 Știri relevante")

        # === Știri generale ===
        for interest in interests:
            st.markdown(f"## 📌 {interest}")
            all_feeds = []
            for source in selected_sources:
                if source in rss_catalog and interest in rss_catalog[source]:
                    all_feeds.append(rss_catalog[source][interest])
            collected = []
            for url in all_feeds:
                feed = feedparser.parse(url)
                collected += feed.entries[:3]
            if collected:
                for entry in collected:
                    summary = clean_summary(entry.summary) if hasattr(entry, 'summary') else ""
                    st.markdown(f"**{entry.title}**")
                    st.markdown(f"{summary}")
                    st.markdown(f"[🔗 Citește mai mult]({entry.link})")
                    st.markdown("---")

        # === Știri locale ===
        if include_local and city:
            try:
                headers = {"User-Agent": "Mozilla/5.0"}

                rss_key = city.lower()
                if rss_key in local_rss_map:
                    rss_url = local_rss_map[rss_key]
                    feed = feedparser.parse(rss_url)
                    if feed.entries:
                        st.subheader(f"📰 Știri locale din {city}")
                        for entry in feed.entries[:5]:
                            summary = clean_summary(entry.summary) if hasattr(entry, 'summary') else ""
                            st.markdown(f"**{entry.title}**")
                            st.markdown(f"{summary}")
                            st.markdown(f"[🔗 Citește mai mult]({entry.link})")
                            st.markdown("---")
                    else:
                        st.info("Nu am găsit articole în presa locală.")
                else:
                    st.info("Nu avem încă o sursă locală asociată acestui oraș.")

            except Exception as e:
                st.error("Eroare la accesarea știrilor locale: " + str(e))