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
st.markdown("""
<style>
/* Title */
.title {
    text-align: center;
    font-size: 40px;
    font-weight: bold;
    margin-bottom: 20px;
}

/* Poster centered */
.poster {
    display: flex;
    justify-content: center;
    margin-bottom: 10px;
}

/* Stars */
.stars {
    text-align: center;
    font-size: 28px;
    margin-top: 10px;
}

/* Genre & summary */
.info {
    text-align: center;
    font-size: 18px;
    margin-top: 5px;
}

/* Circular buttons */
.stButton>button#skip {
    background-color: #e74c3c !important;  /* Red */
    color: white !important;
    border-radius: 50% !important;
    width: 120px !important;
    height: 120px !important;
    font-size: 50px !important;
    font-weight: bold !important;
    border: none !important;
}
.stButton>button#like {
    background-color: #2ecc71 !important;  /* Green */
    color: white !important;
    border-radius: 50% !important;
    width: 120px !important;
    height: 120px !important;
    font-size: 50px !important;
    font-weight: bold !important;
    border: none !important;
}
.stButton>button:hover {
    transform: scale(1.1);
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown('<div class="title">🎬 app made for Annette</div>', unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "movies" not in st.session_state:
    st.session_state.movies = []
if "index" not in st.session_state:
    st.session_state.index = 0
if "liked" not in st.session_state:
    st.session_state.liked = []
if "skipped" not in st.session_state:
    st.session_state.skipped = []
if "movie_dict" not in st.session_state:
    st.session_state.movie_dict = {}

# ---------------- FUNCTION TO LOAD MOVIES ----------------
def load_movies():
    # Recommendation: use top genre from likes
    if st.session_state.liked:
        liked_genres = []
        for movie_title in st.session_state.liked:
            info = st.session_state.movie_dict.get(movie_title)
            if info:
                liked_genres.extend(info['Genre'].split(', '))
        if liked_genres:
            top_genre = Counter(liked_genres).most_common(1)[0][0]
            term = top_genre
        else:
            term = random.choice(SEARCH_TERMS)
    else:
        term = random.choice(SEARCH_TERMS)

    page = random.randint(1, 5)
    search_res = requests.get(
        "http://www.omdbapi.com/",
        params={
            "apikey": API_KEY,
            "s": term,
            "type": "movie",
            "page": page
        }
    ).json()

    if search_res.get("Search"):
        for m in search_res["Search"]:
            details = requests.get(
                "http://www.omdbapi.com/",
                params={
                    "apikey": API_KEY,
                    "i": m["imdbID"],
                    "plot": "short"
                }
            ).json()
            st.session_state.movies.append(details)
            st.session_state.movie_dict[details["Title"]] = details

# Load movies if list is short
if len(st.session_state.movies) < 3:
    load_movies()

# ---------------- CURRENT MOVIE ----------------
movie = st.session_state.movies[st.session_state.index]

title = movie.get("Title", "Unknown")
year = movie.get("Year", "")
poster = movie.get("Poster")
rating = movie.get("imdbRating", "N/A")
genre = movie.get("Genre", "N/A")
plot = movie.get("Plot", "No summary available.")

# ---------------- DISPLAY ----------------
st.markdown(f"<h2 style='text-align:center;'>{title} ({year})</h2>", unsafe_allow_html=True)

# Poster centered under title
if poster and poster != "N/A":
    st.markdown(f"""
    <div class="poster">
        <img src="{poster}" width="300">
    </div>
    """, unsafe_allow_html=True)

# Stars
if rating != "N/A":
    stars = round(float(rating)/2)
    st.markdown(
        f'<div class="stars">{"★"*stars}{"☆"*(5-stars)}<br>({rating}/10)</div>',
        unsafe_allow_html=True
    )

# Genre & summary
st.markdown(f'<div class="info"><b>Genre:</b> {genre}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="info">{plot}</div>', unsafe_allow_html=True)

# ---------------- CIRCULAR BUTTONS ----------------
col1, col2, col3 = st.columns([1,2,1])

with col1:
    if st.button("✖", key="skip"):
        st.session_state.skipped.append(title)
        st.session_state.index += 1
        st.rerun()

with col3:
    if st.button("✔", key="like"):
        st.session_state.liked.append(title)
        st.session_state.index += 1
        st.rerun()

# ---------------- LOAD MORE ----------------
if st.session_state.index >= len(st.session_state.movies) - 1:
    load_movies()
