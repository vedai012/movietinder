import streamlit as st
import requests
import random
import streamlit.components.v1 as components

# ---------------- CONFIG ----------------
TMDB_API_KEY = "94b6bc84983042915e04c3d723aab973"

st.set_page_config(page_title="Movie Matcher", layout="centered")

# ---------------- CSS & SWIPE JAVASCRIPT ----------------
st.markdown("""
<style>
    /* Fix mobile squishing */
    .block-container { padding: 1rem !important; max-width: 500px; }
    
    /* Center everything */
    .main-title { text-align: center; font-size: 28px !important; font-weight: 800; margin-bottom: 2px; }
    .sub-info { text-align: center; font-size: 18px !important; color: #FF4B4B; margin-bottom: 10px; font-weight: bold; }
    .summary-text { text-align: center; font-size: 17px !important; line-height: 1.4; color: #ddd; }

    /* Flexbox fix for buttons to stop them from stacking */
    .button-row {
        display: flex !important;
        flex-direction: row !important;
        justify-content: center !important;
        gap: 30px !important;
        margin-top: 20px;
    }

    div.stButton > button {
        border-radius: 50% !important;
        width: 100px !important;
        height: 100px !important;
        border: none !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    button[key="skip_btn"] { background-color: #FF4B4B !important; }
    button[key="like_btn"] { background-color: #2ECC71 !important; }
    .stButton > button p { font-size: 45px !important; color: white !important; font-weight: bold !important; margin: 0 !important; }

    /* Card styling for swipe feel */
    .swipe-card {
        border-radius: 15px;
        overflow: hidden;
        touch-action: none;
        user-select: none;
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

# ---------------- DATA FETCHING ----------------
def load_content():
    try:
        page = random.randint(1, 15)
        url = f"https://api.themoviedb.org/3/trending/all/week?api_key={TMDB_API_KEY}&page={page}"
        res = requests.get(url, timeout=5).json()
        
        # Genre Mapping (TMDB uses IDs, we need names)
        genre_url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={TMDB_API_KEY}"
        genres_raw = requests.get(genre_url).json().get("genres", [])
        genre_map = {g['id']: g['name'] for g in genres_raw}

        if res.get("results"):
            for item in res["results"]:
                if item.get("media_type") == 'person': continue
                m_type = item.get("media_type")
                m_id = item.get("id")
                
                # Get detail for runtime/seasons
                d = requests.get(f"https://api.themoviedb.org/3/{m_type}/{m_id}?api_key={TMDB_API_KEY}", timeout=5).json()
                
                # Get the first genre name
                g_ids = item.get("genre_ids", [])
                genre_name = genre_map.get(g_ids[0], "General") if g_ids else "General"

                if d.get('poster_path') and d.get('overview'):
                    st.session_state.media_list.append({
                        "title": d.get("title") or d.get("name"),
                        "poster": f"https://image.tmdb.org/t/p/w500{d.get('poster_path')}",
                        "summary": d.get("overview"),
                        "type": m_type.upper(),
                        "genre": genre_name,
                        "rating": d.get("vote_average", 0),
                        "extra": f"{d.get('number_of_seasons')} Seasons" if m_type == 'tv' else f"{d.get('runtime')}m",
                        "year": (d.get("release_date") or d.get("first_air_date") or "    ")[0:4]
                    })
    except: pass

if not st.session_state.media_list:
    load_content()

# ---------------- UI ----------------
st.markdown('<h1 style="text-align:center; color:#FF4B4B;">🎬 app for Annette</h1>', unsafe_allow_html=True)

if st.session_state.index < len(st.session_state.media_list):
    item = st.session_state.media_list[st.session_state.index]
    
    st.markdown(f'<div class="main-title">{item["title"]} ({item["year"]})</div>', unsafe_allow_html=True)
    # Added Genre next to Type here:
    st.markdown(f'<div class="sub-info">{item["type"]} | {item["genre"]} • {item["extra"]} • ⭐ {round(item["rating"], 1)}</div>', unsafe_allow_html=True)

    # SWIPE COMPONENT (JavaScript injection)
    # This captures touch events on the phone
    swipe_js = f"""
    <script src="https://hammerjs.github.io/dist/hammer.min.js"></script>
    <div id="swipe-area" style="width: 100%; text-align: center;">
        <img src="{item['poster']}" style="width: 100%; border-radius: 15px; box-shadow: 0 10px 20px rgba(0,0,0,0.5);">
    </div>
    <script>
        var el = document.getElementById('swipe-area');
        var mc = new Hammer(el);
        mc.on("swipeleft", function(ev) {{
            window.parent.postMessage({{"type": "streamlit:setComponentValue", "value": "left"}}, "*");
        }});
        mc.on("swiperight", function(ev) {{
            window.parent.postMessage({{"type": "streamlit:setComponentValue", "value": "right"}}, "*");
        }});
    </script>
    """
    
    # Render the swipable image
    swipe_event = components.html(swipe_js, height=550)

    # Handle the swipe event
    # NOTE: Since Streamlit components are isolated, we use buttons as backup 
    # and the JS triggers the logic.
    
    st.markdown(f'<div class="summary-text">{item["summary"]}</div>', unsafe_allow_html=True)

    st.divider()

    # SIDE-BY-SIDE BUTTONS (Fixed CSS Row)
    st.markdown('<div class="button-row">', unsafe_allow_html=True)
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
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.index > len(st.session_state.media_list) - 3:
        load_content()
else:
    st.button("Reload", on_click=load_content)

# Matches Gallery
if st.session_state.liked:
    st.divider()
    st.markdown("<h2 style='text-align:center;'>❤️ Annette's Matches</h2>", unsafe_allow_html=True)
    cols = st.columns(2)
    for i, m in enumerate(st.session_state.liked):
        with cols[i % 2]:
            st.image(m["poster"], caption=m["title"], use_container_width=True)
