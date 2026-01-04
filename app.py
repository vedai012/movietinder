import streamlit as st
import requests
import random

# ---------------- CONFIG ----------------
TMDB_API_KEY = "94b6bc84983042915e04c3d723aab973"

st.set_page_config(page_title="Movie Matcher", layout="centered")

# ---------------- THE "ANTI-STACK" GRID CSS ----------------
# ---------------- THE "WIDE GRID" CSS ----------------
st.markdown("""
<style>
    .block-container { padding: 1rem !important; max-width: 450px; }
    
    .main-title { text-align: center; font-size: 28px !important; font-weight: 800; margin-bottom: 2px; }
    .sub-info { text-align: center; font-size: 16px !important; color: #FF4B4B; margin-bottom: 5px; font-weight: bold; }
    .star-rating { text-align: center; font-size: 32px; margin-bottom: 10px; }
    .summary-text { text-align: center; font-size: 17px !important; line-height: 1.4; color: #eee; margin-bottom: 20px; }

    /* THE FIX: space-between pushes buttons to the far left and far right */
    [data-testid="stHorizontalBlock"] {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important; 
        gap: 40px !important; /* Increased gap to push them apart */
        width: 100% !important;
        justify-content: space-between !important; 
        align-items: center !important;
        padding: 0 10px !important; /* Prevents buttons from touching the very edge of the screen */
    }

    /* Square Button Style */
    div.stButton > button {
        border-radius: 15px !important; 
        width: 100% !important;
        height: 85px !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4) !important;
    }

    /* Colors */
    div.stButton > button[key="skip_btn"] { background-color: #FF4B4B !important; }
    div.stButton > button[key="like_btn"] { background-color: #2ECC71 !important; }

    /* Thumb Emojis */
    div.stButton > button p {
        font-size: 45px !important;
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

def load_content():
    try:
        page = random.randint(1, 40)
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
                    # Stars logic
                    raw_rating = d.get('vote_average', 0)
                    star_count = max(1, round(raw_rating / 2))
                    stars = "⭐" * star_count

                    st.session_state.media_list.append({
                        "title": d.get("title") or d.get("name"),
                        "poster": f"https://image.tmdb.org/t/p/w500{d.get('poster_path')}",
                        "summary": d.get("overview", ""),
                        "type": m_type.upper(),
                        "genre": genre,
                        "stars": stars,
                        "extra": f"{d.get('number_of_seasons', 0)} Seasons" if m_type == 'tv' else f"{d.get('runtime', 0)}m",
                        "year": (d.get("release_date") or d.get("first_air_date") or " ")[0:4]
                    })
    except: pass

if not st.session_state.media_list:
    load_content()

# ---------------- UI ----------------
st.markdown('<h1 style="text-align:center;">❤️ Made for Annette</h1>', unsafe_allow_html=True)

if st.session_state.index < len(st.session_state.media_list):
    item = st.session_state.media_list[st.session_state.index]
    
    # Header
    st.markdown(f'<div class="main-title">{item["title"]} ({item["year"]})</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-info">{item["type"]} | {item["genre"]} • {item["extra"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="star-rating">{item["stars"]}</div>', unsafe_allow_html=True)

    # Poster
    st.image(item["poster"], use_container_width=True)
    
    # Summary
    st.markdown(f'<div class="summary-text">{item["summary"]}</div>', unsafe_allow_html=True)

    # TWO BUTTONS: Now using Grid to stay perfectly centered and side-by-side
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👎", key="skip_btn"):
            st.session_state.index += 1
            st.rerun()
    with col2:
        if st.button("👍", key="like_btn"):
            st.session_state.liked.append(item)
            st.session_state.index += 1
            st.rerun()

    if st.session_state.index > len(st.session_state.media_list) - 3:
        load_content()
else:
    st.button("Reload", on_click=load_content)

# Match History
if st.session_state.liked:
    st.divider()
    st.markdown("<h2 style='text-align:center;'>🫶 Liked so far</h2>", unsafe_allow_html=True)
    cols = st.columns(2)
    for i, m in enumerate(st.session_state.liked):
        with cols[i % 2]:
            st.image(m["poster"], caption=m["title"], use_container_width=True)
