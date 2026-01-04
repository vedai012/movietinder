import streamlit as st
import requests
import random

# ---------------- CONFIG ----------------
TMDB_API_KEY = "94b6bc84983042915e04c3d723aab973"

st.set_page_config(page_title="Movie Matcher", layout="centered")

# ---------------- CSS FIXES ----------------
st.markdown("""
<style>
    /* Allow scrolling while keeping mobile layout tight */
    .block-container { padding: 1rem !important; max-width: 450px; }
    
    .main-title { text-align: center; font-size: 28px !important; font-weight: 800; margin-bottom: 2px; }
    .sub-info { text-align: center; font-size: 18px !important; color: #FF4B4B; margin-bottom: 15px; font-weight: bold; }
    
    /* Summary styling - now above buttons */
    .summary-text { 
        text-align: center; 
        font-size: 18px !important; 
        line-height: 1.5; 
        color: #eee; 
        margin-bottom: 20px;
        padding: 0 10px;
    }

    /* THE BUTTON FIX: Force side-by-side circles using a table container */
    .button-table {
        width: 100%;
        margin: 20px 0;
    }

    /* Target Streamlit buttons specifically to force them into circles */
    div.stButton > button {
        border-radius: 50% !important;
        width: 110px !important;
        height: 110px !important;
        border: none !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 auto !important;
        box-shadow: 0 6px 15px rgba(0,0,0,0.5) !important;
    }

    /* Red and Green colors */
    div.stButton > button[key="skip_btn"] { background-color: #FF4B4B !important; }
    div.stButton > button[key="like_btn"] { background-color: #2ECC71 !important; }

    /* X and Check icons */
    div.stButton > button p {
        font-size: 50px !important;
        color: white !important;
        font-weight: bold !important;
        margin: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "media_list" not in st.session_state:
    st.session_state.media_list = []
if "index" not in st.session_state:
    st.session_state.index = 0
if "liked" not in st.session_state:
    st.session_state.liked = []

# ---------------- DATA FETCH ----------------
def load_content():
    try:
        page = random.randint(1, 20)
        url = f"https://api.themoviedb.org/3/trending/all/week?api_key={TMDB_API_KEY}&page={page}"
        res = requests.get(url, timeout=5).json()
        
        g_url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={TMDB_API_KEY}"
        genre_map = {g['id']: g['name'] for g in requests.get(g_url).json().get("genres", [])}

        if res.get("results"):
            for item in res["results"]:
                if item.get("media_type") == 'person': continue
                m_type = item.get("media_type", "movie")
                m_id = item.get("id")
                
                d = requests.get(f"https://api.themoviedb.org/3/{m_type}/{m_id}?api_key={TMDB_API_KEY}", timeout=5).json()
                g_ids = item.get("genre_ids", [])
                genre = genre_map.get(g_ids[0], "Drama") if g_ids else "Drama"

                if d.get('poster_path'):
                    st.session_state.media_list.append({
                        "title": d.get("title") or d.get("name"),
                        "poster": f"https://image.tmdb.org/t/p/w500{d.get('poster_path')}",
                        "summary": d.get("overview", "No summary available."),
                        "type": m_type.upper(),
                        "genre": genre,
                        "extra": f"{d.get('number_of_seasons')} Seasons" if m_type == 'tv' else f"{d.get('runtime')}m",
                        "year": (d.get("release_date") or d.get("first_air_date") or " ")[0:4]
                    })
    except: pass

if not st.session_state.media_list:
    load_content()

# ---------------- UI ----------------
st.markdown('<h1 style="text-align:center; color:#FF4B4B;">🎬 for Annette</h1>', unsafe_allow_html=True)

if st.session_state.index < len(st.session_state.media_list):
    item = st.session_state.media_list[st.session_state.index]
    
    # 1. Header
    st.markdown(f'<div class="main-title">{item["title"]} ({item["year"]})</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-info">{item["type"]} | {item["genre"]} • {item["extra"]}</div>', unsafe_allow_html=True)

    # 2. Poster
    st.image(item["poster"], use_container_width=True)

    # 3. Summary (Now Above Buttons)
    st.markdown(f'<div class="summary-text">{item["summary"]}</div>', unsafe_allow_html=True)

    # 4. Circular Buttons (Using Columns but with CSS force)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✕", key="skip_btn"):
            st.session_state.index += 1
            st.rerun()
    with col2:
        if st.button("✔", key="like_btn"):
            st.session_state.liked.append(item)
            st.session_state.index += 1
            st.rerun()

    # Prefetch logic
    if st.session_state.index > len(st.session_state.media_list) - 3:
        load_content()
else:
    st.button("Reload Content", on_click=load_content)

# Matches Gallery
if st.session_state.liked:
    st.divider()
    st.markdown("<h2 style='text-align:center;'>❤️ Matches</h2>", unsafe_allow_html=True)
    cols = st.columns(2)
    for i, m in enumerate(st.session_state.liked):
        with cols[i % 2]:
            st.image(m["poster"], caption=m["title"], use_container_width=True)
