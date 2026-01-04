import streamlit as st
import requests
import random

# ---------------- CONFIG ----------------
TMDB_API_KEY = "94b6bc84983042915e04c3d723aab973"

st.set_page_config(page_title="Movie & TV Matcher", layout="centered")

# ---------------- THE "ANTI-STACK" CSS ----------------
st.markdown("""
<style>
    /* 1. Force buttons to stay in a horizontal row on mobile */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 20px !important; /* Space between the circles */
    }

    /* 2. Standardize button size and shape */
    div.stButton > button {
        border-radius: 50% !important;
        width: 110px !important;
        height: 110px !important;
        border: none !important;
        box-shadow: 0 8px 15px rgba(0,0,0,0.3) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0 !important;
    }

    /* Red Circle */
    button[key="skip_btn"] { background-color: #FF4B4B !important; }
    /* Green Circle */
    button[key="like_btn"] { background-color: #2ECC71 !important; }

    /* Icons inside buttons */
    .stButton > button p {
        font-size: 50px !important;
        color: white !important;
        font-weight: bold !important;
        margin: 0 !important;
        line-height: 1 !important;
    }

    /* Typography fixes for mobile */
    .main-title { text-align: center; font-size: 28px !important; font-weight: 800; margin-bottom: 5px; }
    .sub-info { text-align: center; font-size: 18px !important; color: #FF4B4B; margin-bottom: 10px; }
    .summary-text { text-align: center; font-size: 18px !important; line-height: 1.4; }
</style>
""", unsafe_allow_html=True)

# ---------------- DATA & STATE ----------------
if "media_list" not in st.session_state:
    st.session_state.media_list = []
if "index" not in st.session_state:
    st.session_state.index = 0
if "liked" not in st.session_state:
    st.session_state.liked = []

def load_content():
    try:
        page = random.randint(1, 10)
        url = f"https://api.themoviedb.org/3/trending/all/week?api_key={TMDB_API_KEY}&page={page}"
        res = requests.get(url, timeout=5).json()
        if res.get("results"):
            for item in res["results"]:
                if item.get("media_type") == 'person': continue
                m_type = item.get("media_type")
                m_id = item.get("id")
                d = requests.get(f"https://api.themoviedb.org/3/{m_type}/{m_id}?api_key={TMDB_API_KEY}", timeout=5).json()
                if d.get('poster_path') and d.get('overview'):
                    st.session_state.media_list.append({
                        "title": d.get("title") or d.get("name"),
                        "poster": f"https://image.tmdb.org/t/p/w500{d.get('poster_path')}",
                        "summary": d.get("overview"),
                        "type": m_type,
                        "rating": d.get("vote_average", 0),
                        "extra": f"{d.get('number_of_seasons')} Seasons" if m_type == 'tv' else f"{d.get('runtime')}m",
                        "year": (d.get("release_date") or d.get("first_air_date") or "    ")[0:4]
                    })
    except: pass

if not st.session_state.media_list:
    load_content()

# ---------------- UI ----------------
st.markdown('<h1 style="text-align:center; color:#FF4B4B;">🎬 for Annette</h1>', unsafe_allow_html=True)

if st.session_state.index < len(st.session_state.media_list):
    item = st.session_state.media_list[st.session_state.index]
    
    st.markdown(f'<div class="main-title">{item["title"]} ({item["year"]})</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-info">{item["type"].upper()} • {item["extra"]} • ⭐ {round(item["rating"], 1)}</div>', unsafe_allow_html=True)

    st.image(item["poster"], use_container_width=True)
    st.markdown(f'<div class="summary-text">{item["summary"]}</div>', unsafe_allow_html=True)

    st.divider()

    # Fixed: No more stacking. These stay side-by-side.
    btn_col_1, btn_col_2 = st.columns(2)
    with btn_col_1:
        if st.button("✕", key="skip_btn"):
            st.session_state.index += 1
            st.rerun()
    with btn_col_2:
        if st.button("✔", key="like_btn"):
            st.session_state.liked.append(item)
            st.session_state.index += 1
            st.rerun()

    if st.session_state.index > len(st.session_state.media_list) - 3:
        load_content()
else:
    st.button("Reload", on_click=load_content)

# Matches
if st.session_state.liked:
    st.divider()
    st.markdown("<h2 style='text-align:center;'>❤️ Matches</h2>", unsafe_allow_html=True)
    cols = st.columns(2)
    for i, m in enumerate(st.session_state.liked):
        with cols[i % 2]:
            st.image(m["poster"], caption=m["title"], use_container_width=True)
