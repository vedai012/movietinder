import streamlit as st
import requests
import random
from collections import Counter

# ---------------- CONFIG ----------------
API_KEY = "c978ed19"

SEARCH_TERMS = [
    "love", "war", "future", "night", "dark",
    "hero", "life", "game", "dream", "world"
]

st.set_page_config(page_title="Movie Tinder", layout="centered")

# ---------------- CSS ----------------
# We target the 'stButton' container and the 'button' tag inside it
st.markdown("""
<style>
.title {
    text-align: center;
    font-size: 40px;
    font-weight: bold;
    margin-bottom: 20px;
}

.poster {
    display: flex;
    justify-content: center;
    margin-bottom: 10px;
}

.stars {
    text-align: center;
    font-size: 28px;
    margin-top: 10px;
}

.info {
    text-align: center;
    font-size: 18px;
    margin-top: 5px;
}

/* Styling the actual Streamlit buttons to be circles */
div.stButton > button {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    font-size: 50px !important;
    color: white !important;
    border: none !important;
    transition: transform 0.2s;
}

div.stButton > button:hover {
    transform: scale(1.1);
    color: white !important;
}

/* Specific colors for Skip and Like */
div.stButton > button[kind="secondary"]:nth-child(1) { 
    /* This targets buttons generally, we will use unique keys */
}

/* We use the key names to apply specific colors */
button[key="skip_btn"] {
    background-color: #e74c3c !important;
}

button[key="like_btn"] {
    background-color: #2ecc71 !important;
}

/* Centering the button container */
.stColumn {
    display: flex;
    justify-content: center;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "movies" not in st.session_state:
    st.session_state.movies = []
if "index" not in st.session_state:
    st.session_state.index = 0
if "liked" not in st.session_state:
    st.session_state.liked = []
if "movie_dict" not in st.session_state:
    st.session_state.movie_dict = {}

# ---------------- FUNCTIONS ----------------
def load_movies():
    if st.session_state.liked:
        liked_genres = []
        for movie_title in st.session_state.liked:
            info = st.session_state.movie_dict.get(movie_title)
            if info:
                liked_genres.extend(info['Genre'].split(', '))
        term = Counter(liked_genres).most_common(1)[0][0] if liked_genres else random.choice(SEARCH_TERMS)
    else:
        term = random.choice(SEARCH_TERMS)

    page = random.randint(1, 10)
    try:
        search_res = requests.get(
            "http://www.omdbapi.com/",
            params={"apikey": API_KEY, "s": term, "type": "movie", "page": page}
        ).json()

        if search_res.get("Search"):
            for m in search_res["Search"]:
                details = requests.get(
                    "http://www.omdbapi.com/",
                    params={"apikey": API_KEY, "i": m["imdbID"], "plot": "short"}
                ).json()
                if details["Title"] not in st.session_state.movie_dict:
                    st.session_state.movies.append(details)
                    st.session_state.movie_dict[details["Title"]] = details
    except:
        st.error("Failed to fetch movies. Check API Key or Connection.")

def handle_click(action, title):
    if action == "like":
        st.session_state.liked.append(title)
    st.session_state.index += 1
    # Check if we need more movies
    if st.session_state.index >= len(st.session_state.movies) - 2:
        load_movies()

# Initial Load
if not st.session_state.movies:
    load_movies()

# ---------------- DISPLAY ----------------
st.markdown('<div class="title">🎬 app made for Annette</div>', unsafe_allow_html=True)

if st.session_state.index < len(st.session_state.movies):
    movie = st.session_state.movies[st.session_state.index]
    
    title = movie.get("Title", "Unknown")
    year = movie.get("Year", "")
    poster = movie.get("Poster")
    rating = movie.get("imdbRating", "N/A")
    genre = movie.get("Genre", "N/A")
    plot = movie.get("Plot", "No summary available.")

    st.markdown(f"<h2 style='text-align:center;'>{title} ({year})</h2>", unsafe_allow_html=True)

    if poster and poster != "N/A":
        st.markdown(f'<div class="poster"><img src="{poster}" width="300"></div>', unsafe_allow_html=True)

    if rating != "N/A":
        stars = round(float(rating)/2)
        st.markdown(f'<div class="stars">{"★"*stars}{"☆"*(5-stars)}<br>({rating}/10)</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="info"><b>Genre:</b> {genre}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info" style="padding: 0 50px;">{plot}</div>', unsafe_allow_html=True)

    # ---------------- CIRCULAR BUTTONS ----------------
    # Use columns to position them like the UI design
    col1, col2 = st.columns(2)

    with col1:
        # We use custom CSS inside the button labels or via the style block above
        if st.button("✖", key="skip_btn", help="Skip"):
            handle_click("skip", title)
            st.rerun()

    with col2:
        if st.button("✔", key="like_btn", help="Like"):
            handle_click("like", title)
            st.rerun()
else:
    st.write("Loading more movies...")
    load_movies()
    st.rerun()
