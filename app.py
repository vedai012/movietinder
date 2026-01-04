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
    .sub-info { text-align: center; font-size: 15px !important; color: #FF4B4B; margin-bottom: 5px; font-weight: bold; }
    .star-rating { text-align: center; font-size: 28px; margin-bottom: 5px; }
    .summary-text { text-align: center; font-size: 16px !important; line-height: 1.4; color: #eee; margin-bottom: 15px; }
    .provider-text { text-align: center; font-size: 14px; color: #2ECC71; font-weight: bold; margin-bottom: 10px; }

    [data-testid="stHorizontalBlock"] {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important; 
        gap: 20px !important; 
        width: 100% !important;
        justify-items: center !important; 
        align-items: center !important;   
        padding: 0 10px !important;
    }

    div.stButton > button {
        border-radius: 15px !important; 
        width: 100px !important; 
        height: 80px !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4) !important;
        margin: 0 auto !important; 
    }

    div.stButton > button[key="skip_btn"] { background-color: #FF4B4B !important; }
    div.stButton > button[key="like_btn"] { background-color: #2ECC71 !important; }
    
    div.stButton > button p { font-size: 40px !important; margin: 0 !important; }
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

# ---------------- DATA FETCHING ----------------
def get_genres():
    url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={TMDB_API_KEY}"
    genres = requests.get(url).json().get("genres", [])
    return {g['name']: g['id'] for g in genres}

def load_content(genre_id=None):
    try:
        page = random.randint(1, 20)
        base_url = "https://api.themoviedb.org/3/discover/movie" if genre_id else "https://api.themoviedb.org/3/trending/all/week"
        params = f"?api_key={TMDB_API_KEY}&page={page}"
        if genre_id: params += f"&with_genres={genre_id}"
        
        res = requests.get(base_url + params, timeout=5).json()
        
        if res.get("results"):
            new_items = []
            for item in res["results"]:
                if item.get("media_type") == 'person': continue
                m_type = item.get("media_type", "movie")
                m_id = item.get("id")
                
                # Fetch Providers & Trailer
                d = requests.get(f"https://api.themoviedb.org/3/{m_type}/{m_id}?api_key={TMDB_API_KEY}&append_to_response=watch/providers,videos", timeout=5).json()
                
                # Providers (US region)
                providers = d.get("watch/providers", {}).get("results", {}).get("US", {}).get("flatrate", [])
                provider_names = ", ".join([p['provider_name'] for p in providers]) if providers else "Rent/Buy only"
                
                # Trailer
                video_list = d.get("videos", {}).get("results", [])
                trailer_key = next((v['key'] for v in video_list if v['type'] == 'Trailer'), None)
                trailer_url = f"https://www.youtube.com/watch?v={trailer_key}" if trailer_key else None

                if d.get('poster_path'):
                    stars = "⭐" * max(1, round(d.get('vote_average', 0) / 2))
                    new_items.append({
                        "title": d.get("title") or d.get("name"),
                        "poster": f"https://image.tmdb.org/t/p/w500{d.get('poster_path')}",
                        "summary": d.get("overview", ""),
                        "stars": stars,
                        "providers": provider_names,
                        "trailer": trailer_url,
                        "year": (d.get("release_date") or d.get("first_air_date") or " ")[0:4]
                    })
            st.session_state.media_list = new_items
            st.session_state.index = 0
    except: pass

# ---------------- UI ----------------
st.markdown('<h1 style="text-align:center;">❤️ Made for Annette</h1>', unsafe_allow_html=True)

# Genre Filter
genre_dict = get_genres()
selected_genre = st.selectbox("What mood are you in?", ["All"] + list(genre_dict.keys()))
if selected_genre != st.session_state.current_genre:
    st.session_state.current_genre = selected_genre
    load_content(genre_dict.get(selected_genre))
    st.rerun()

if not st.session_state.media_list:
    load_content()

if st.session_state.index < len(st.session_state.media_list):
    item = st.session_state.media_list[st.session_state.index]
    
    st.markdown(f'<div class="main-title">{item["title"]} ({item["year"]})</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="star-rating">{item["stars"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="provider-text">Streaming on: {item["providers"]}</div>', unsafe_allow_html=True)

    st.image(item["poster"], use_container_width=True)
    
    # Trailer Link
    if item["trailer"]:
        st.link_button("🎬 Watch Trailer", item["trailer"], use_container_width=True)

    st.markdown(f'<div class="summary-text">{item["summary"]}</div>', unsafe_allow_html=True)

    # Buttons
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

# Liked Section
if st.session_state.liked:
    st.divider()
    st.markdown("<h2 style='text-align:center;'>🫶 Liked so far</h2>", unsafe_allow_html=True)
    
    # Clear History Button
    if st.button("🗑️ Clear My Matches", use_container_width=True):
        st.session_state.liked = []
        st.rerun()

    cols = st.columns(2)
    for i, m in enumerate(reversed(st.session_state.liked)):
        with cols[i % 2]:
            st.image(m["poster"], caption=m["title"], use_container_width=True)
