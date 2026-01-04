import streamlit as st
import requests
import random
import streamlit.components.v1 as components

# ---------------- CONFIG ----------------
TMDB_API_KEY = "94b6bc84983042915e04c3d723aab973"

st.set_page_config(page_title="Movie Matcher", layout="centered")

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
    /* Prevent iPhone squishing */
    .block-container { padding: 1rem !important; max-width: 450px; }
    
    /* Center text and make it look clean */
    .main-title { text-align: center; font-size: 26px !important; font-weight: 800; margin-bottom: 2px; }
    .sub-info { text-align: center; font-size: 16px !important; color: #FF4B4B; margin-bottom: 10px; font-weight: bold; }
    .summary-text { text-align: center; font-size: 16px !important; line-height: 1.4; color: #ccc; }

    /* THE FIX: Custom Flexbox Row to prevent button stacking */
    .button-container {
        display: flex !important;
        flex-direction: row !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 40px !important; /* Space between X and Check */
        margin: 20px 0 !important;
        width: 100%;
    }

    /* Style the buttons to be big circles */
    .circle-btn {
        width: 90px;
        height: 90px;
        border-radius: 50%;
        border: none;
        color: white;
        font-size: 40px;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 6px 15px rgba(0,0,0,0.4);
        cursor: pointer;
    }
    .btn-red { background-color: #FF4B4B; }
    .btn-green { background-color: #2ECC71; }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "media_list" not in st.session_state:
    st.session_state.media_list = []
if "index" not in st.session_state:
    st.session_state.index = 0
if "liked" not in st.session_state:
    st.session_state.liked = []

# ---------------- DATA FETCHING ----------------
def load_content():
    try:
        page = random.randint(1, 20)
        url = f"https://api.themoviedb.org/3/trending/all/week?api_key={TMDB_API_KEY}&page={page}"
        res = requests.get(url, timeout=5).json()
        
        # Get Genre Map
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
                        "year": (d.get("release_date") or d.get("first_air_date") or "2024")[0:4]
                    })
    except: pass

if not st.session_state.media_list:
    load_content()

# ---------------- UI & INTERACTION ----------------
st.markdown('<h1 style="text-align:center; color:#FF4B4B;">🎬 for Annette</h1>', unsafe_allow_html=True)

if st.session_state.index < len(st.session_state.media_list):
    item = st.session_state.media_list[st.session_state.index]
    
    st.markdown(f'<div class="main-title">{item["title"]} ({item["year"]})</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-info">{item["type"]} • {item["genre"]} • {item["extra"]}</div>', unsafe_allow_html=True)

    # SWIPE-SENSITIVE POSTER (JS Component)
    # This uses a simple touchstart/touchend logic to detect swipes
    swipe_html = f"""
    <div id="poster-card" style="width: 100%; touch-action: none;">
        <img src="{item['poster']}" style="width: 100%; border-radius: 15px; box-shadow: 0 8px 20px rgba(0,0,0,0.5);">
    </div>
    <script>
        let startX = 0;
        const card = document.getElementById('poster-card');
        card.addEventListener('touchstart', e => {{ startX = e.touches[0].clientX; }}, false);
        card.addEventListener('touchend', e => {{
            let endX = e.changedTouches[0].clientX;
            if (startX - endX > 80) window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'left'}}, '*');
            if (endX - startX > 80) window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'right'}}, '*');
        }}, false);
    </script>
    """
    event = components.html(swipe_html, height=520)

    # Fallback/Manual Buttons (Using raw HTML for Flexbox)
    # We use Streamlit buttons inside the custom CSS row to keep them side-by-side
    col_left, col_right = st.columns(2)
    with col_left:
        if st.button("✕", key="skip_btn", use_container_width=True):
            st.session_state.index += 1
            st.rerun()
    with col_right:
        if st.button("✔", key="like_btn", use_container_width=True):
            st.session_state.liked.append(item)
            st.session_state.index += 1
            st.rerun()

    st.markdown(f'<div class="summary-text">{item["summary"]}</div>', unsafe_allow_html=True)

    # Logic to handle the Swipe Value if it changes
    # (Note: In pure Streamlit this is tricky, so the buttons are the main drivers)

    if st.session_state.index > len(st.session_state.media_list) - 3:
        load_content()
else:
    st.button("Reload", on_click=load_content)

# Matches
if st.session_state.liked:
    st.divider()
    st.markdown("<h3 style='text-align:center;'>❤️ Liked</h3>", unsafe_allow_html=True)
    cols = st.columns(2)
    for i, m in enumerate(st.session_state.liked):
        with cols[i % 2]:
            st.image(m["poster"], caption=m["title"])
