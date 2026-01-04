import streamlit as st
import requests
import random

# ---------------- CONFIG ----------------
TMDB_API_KEY = "94b6bc84983042915e04c3d723aab973"

st.set_page_config(page_title="Movie & TV Matcher", layout="centered")

# ---------------- MOBILE-FIRST CSS (STAYING THE SAME) ----------------
st.markdown("""
<style>
    .block-container { padding: 1rem !important; max-width: 500px; }
    .main-title { text-align: center; font-size: 32px !important; font-weight: 800 !important; line-height: 1.1; margin-bottom: 5px; }
    .sub-info { text-align: center; font-size: 20px !important; color: #FF4B4B; font-weight: bold; margin-bottom: 15px; }
    .summary-text { text-align: center; font-size: 19px !important; line-height: 1.4; margin-top: 15px; }
    .stButton > button { border-radius: 50% !important; width: 120px !important; height: 120px !important; border: none !important; box-shadow: 0 10px 20px rgba(0,0,0,0.4) !important; display: flex !important; align-items: center !important; justify-content: center !important; }
    button[key="skip_btn"] { background-color: #FF4B4B !important; }
    button[key="like_btn"] { background-color: #2ECC71 !important; }
    .stButton > button p { font-size: 60px !important; color: white !important; font-weight: bold !important; margin: 0 !important; }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "media_list" not in st.session_state:
    st.session_state.media_list = []
if "index" not in st.session_state:
    st.session_state.index = 0
if "liked" not in st.session_state:
    st.session_state.liked = []

# ---------------- DATA FETCHING (FIXED & SAFER) ----------------
def load_trending_content():
    try:
        # Increase the page number slightly to get fresh results
        page = random.randint(1, 10)
        url = f"https://api.themoviedb.org/3/trending/all/week?api_key={TMDB_API_KEY}&page={page}"
        res = requests.get(url, timeout=5).json()
        
        if res.get("results"):
            results = res["results"]
            random.shuffle(results)
            
            for item in results:
                try:
                    media_type = item.get("media_type")
                    media_id = item.get("id")
                    if not media_type or not media_id: continue
                    
                    # Skip 'person' results from trending all
                    if media_type == 'person': continue

                    detail_url = f"https://api.themoviedb.org/3/{media_type}/{media_id}?api_key={TMDB_API_KEY}"
                    d = requests.get(detail_url, timeout=5).json()
                    
                    # Only add if it has a poster and summary
                    if d.get('poster_path') and d.get('overview'):
                        st.session_state.media_list.append({
                            "title": d.get("title") or d.get("name"),
                            "poster": f"https://image.tmdb.org/t/p/w500{d.get('poster_path')}",
                            "summary": d.get("overview"),
                            "type": media_type,
                            "rating": d.get("vote_average", 0),
                            "extra_info": f"{d.get('number_of_seasons')} Seasons" if media_type == 'tv' else f"{d.get('runtime')} mins",
                            "year": (d.get("release_date") or d.get("first_air_date") or "    ")[0:4]
                        })
                except Exception:
                    continue # If one specific movie fails, just move to the next
    except Exception as e:
        st.error(f"Connection error: {e}")

# Initial load
if not st.session_state.media_list:
    load_trending_content()

# ---------------- UI DISPLAY ----------------
st.markdown('<h1 style="text-align:center; color:#FF4B4B;">💕 app made for Annette👌</h1>', unsafe_allow_html=True)

# Check if we have items to show
if st.session_state.index < len(st.session_state.media_list):
    item = st.session_state.media_list[st.session_state.index]
    
    st.markdown(f'<div class="main-title">{item["title"]} ({item["year"]})</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-info">{item["type"].upper()} • {item["extra_info"]} • ⭐ {round(item["rating"], 1)}</div>', unsafe_allow_html=True)

    if item["poster"]:
        st.image(item["poster"], use_container_width=True)

    st.markdown(f'<div class="summary-text">{item["summary"]}</div>', unsafe_allow_html=True)

    st.divider()

    l_space, btn_x, btn_check, r_space = st.columns([1, 2, 2, 1])
    with btn_x:
        if st.button("✕", key="skip_btn"):
            st.session_state.index += 1
            st.rerun()

    with btn_check:
        if st.button("✔", key="like_btn"):
            st.session_state.liked.append(item)
            st.session_state.index += 1
            st.rerun()

    # Pre-fetch more when running low
    if st.session_state.index > len(st.session_state.media_list) - 5:
        load_trending_content()

else:
    # This triggers if the initial load failed or we ran out
    if st.button("Reload Movies"):
        load_trending_content()
        st.rerun()
    st.info("Loading fresh movies... click reload if it takes more than 5 seconds.")

# ---------------- MATCH GALLERY ----------------
if st.session_state.liked:
    st.divider()
    st.markdown("<h2 style='text-align:center;'>❤️ Annette's Matches</h2>", unsafe_allow_html=True)
    cols = st.columns(2)
    for i, m in enumerate(st.session_state.liked):
        with cols[i % 2]:
            st.image(m["poster"], caption=m["title"], use_container_width=True)
