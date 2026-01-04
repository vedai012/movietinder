import streamlit as st
import requests
import random

# ---------------- CONFIG ----------------
TMDB_API_KEY = "94b6bc84983042915e04c3d723aab973"

st.set_page_config(page_title="Movie Matcher", layout="centered")

# ---------------- CSS ----------------
st.markdown("""
<style>
    .block-container { padding: 1rem !important; max-width: 450px; }
    .main-title { text-align: center; font-size: 26px !important; font-weight: 800; margin-bottom: 2px; }
    .star-rating { text-align: center; font-size: 28px; margin-bottom: 5px; }
    .provider-text { text-align: center; font-size: 14px; color: #2ECC71; font-weight: bold; margin-bottom: 10px; }
    .summary-text { text-align: center; font-size: 16px !important; line-height: 1.4; color: #eee; margin-bottom: 20px; }

    /* Main Thumb Buttons Grid */
    [data-testid="stHorizontalBlock"] {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important; 
        gap: 20px !important; 
        width: 100% !important;
        justify-items: center !important; 
        align-items: center !important;   
    }

    /* Thumb Button Styling */
    div.stButton > button {
        border-radius: 15px !important; 
        width: 110px !important; 
        height: 85px !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4) !important;
    }
    div.stButton > button[key="skip_btn"] { background-color: #FF4B4B !important; }
    div.stButton > button[key="like_btn"] { background-color: #2ECC71 !important; }
    div.stButton > button p { font-size: 45px !important; }

    /* SMALL SQUARE CLEAR BUTTON NEXT TO TITLE */
    div.stButton > button[key="clear_btn"] {
        width: 60px !important;
        height: 30px !important;
        background-color: #444 !important;
        border: none !important;
        color: white !important;
        font-size: 10px !important;
        border-radius: 5px !important;
        padding: 0 !important;
        margin-left: 10px !important;
    }
    div.stButton > button[key="clear_btn"] p {
        font-size: 11px !important;
        font-weight: bold !important;
    }

    /* Header Container for Title + Button */
    .liked-header {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 15px;
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
if "current_genre" not in st.session_state:
    st.session_state.current_genre = "All"

def get_genres():
    url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={TMDB_API_KEY}"
    try:
        return {g['name']: g['id'] for g in requests.get(url).json().get("genres", [])}
    except: return {}

def load_content(genre_id=None):
    try:
        page = random.randint(1, 40)
        base_url = "https://api.themoviedb.org/3/discover/movie" if genre_id else "https://api.themoviedb.org/3/trending/all/week"
        params = f"?api_key={TMDB_API_KEY}&page={page}"
        if genre_id: params += f"&with_genres={genre_id}"
        
        res = requests.get(base_url + params, timeout=5).json()
        if res.get("results"):
            new_items = []
            for item in res["results"]:
                m_type = item.get("media_type", "movie")
                m_id = item.get("id")
                d = requests.get(f"https://api.themoviedb.org/3/{m_type}/{m_id}?api_key={TMDB_API_KEY}&append_to_response=watch/providers,videos", timeout=5).json()
                
                prov = d.get("watch/providers", {}).get("results", {}).get("US", {}).get("flatrate", [])
                p_names = ", ".join([p['provider_name'] for p in prov]) if prov else "Rent/Buy"
                
                videos = d.get("videos", {}).get("results", [])
                t_key = next((v['key'] for v in videos if v['type'] == 'Trailer'), None)

                if d.get('poster_path'):
                    new_items.append({
                        "title": d.get("title") or d.get("name"),
                        "poster": f"https://image.tmdb.org/t/p/w500{d.get('poster_path')}",
                        "summary": d.get("overview", ""),
                        "stars": "⭐" * max(1, round(d.get('vote_average', 0) / 2)),
                        "providers": p_names,
                        "trailer": f"https://www.youtube.com/watch?v={t_key}" if t_key else None,
                        "year": (d.get("release_date") or d.get("first_air_date") or " ")[0:4]
                    })
            st.session_state.media_list = new_items
            st.session_state.index = 0
    except: pass

# ---------------- UI ----------------
st.markdown('<h1 style="text-align:center;">❤️ Made for Annette</h1>', unsafe_allow_html=True)

genre_dict = get_genres()
selected_genre = st.selectbox("Mood?", ["All"] + list(genre_dict.keys()))
if selected_genre != st.session_state.current_genre:
    st.session_state.current_genre = selected_genre
    load_content(genre_dict.get(selected_genre))
    st.rerun()

if not st.session_state.media_list: load_content()

if st.session_state.index < len(st.session_state.media_list):
    item = st.session_state.media_list[st.session_state.index]
    
    st.markdown(f'<div class="main-title">{item["title"]} ({item["year"]})</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="star-rating">{item["stars"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="provider-text">Streaming: {item["providers"]}</div>', unsafe_allow_html=True)

    st.image(item["poster"], use_container_width=True)
    
    if item["trailer"]:
        st.link_button("🎬 Watch Trailer", item["trailer"], use_container_width=True)

    st.markdown(f'<div class="summary-text">{item["summary"]}</div>', unsafe_allow_html=True)

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
else:
    st.button("Load More", on_click=lambda: load_content(genre_dict.get(selected_genre)))

# Matches Section
if st.session_state.liked:
    st.divider()
    
    # Title and Small Clear Button in one row
    head_col1, head_col2 = st.columns([3, 1])
    with head_col1:
        st.markdown("<h3 style='margin:0;'>🫶 Liked so far</h3>", unsafe_allow_html=True)
    with head_col2:
        if st.button("CLEAR", key="clear_btn"):
            st.session_state.liked = []
            st.rerun()

    # Back to 2 columns for medium-sized posters
    cols = st.columns(2)
    for i, m in enumerate(reversed(st.session_state.liked)):
        with cols[i % 2]:
            st.image(m["poster"], use_container_width=True)
            st.markdown(f"<p style='text-align:center; font-size:12px;'>{m['title']}</p>", unsafe_allow_html=True)
