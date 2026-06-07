import streamlit as st
import pandas as pd
import numpy as np
import pickle
import requests
from sklearn.metrics.pairwise import cosine_similarity

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Netflix AI Clone", layout="wide")

# =========================
# LOAD DATA
# =========================
df = pickle.load(open("movies_dataframe.pkl", "rb"))
embeddings = pickle.load(open("movie_embeddings.pkl", "rb"))

df["movie_name"] = df["movie_name"].fillna("")
df["genre"] = df["genre"].fillna("")

df["movie_name_lower"] = df["movie_name"].str.lower().str.strip()

# =========================
# AI MODEL
# =========================
similarity_matrix = cosine_similarity(embeddings)

# =========================
# TMDB API KEY
# =========================
TMDB_API_KEY = "c835fa9931977fde5eb136086eedc9ad"

# =========================
# POSTER FUNCTION (ROBUST FIX)
# =========================
@st.cache_data
def get_poster(movie_name):

    try:
        query = movie_name.split("(")[0].strip()

        url = "https://api.themoviedb.org/3/search/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "query": query,
            "include_adult": False
        }

        res = requests.get(url, params=params, timeout=5).json()

        results = res.get("results", [])

        if results:
            for r in results:
                if r.get("poster_path"):
                    return "https://image.tmdb.org/t/p/w500" + r["poster_path"]

        return "https://via.placeholder.com/300x450?text=No+Image"

    except:
        return "https://via.placeholder.com/300x450?text=No+Image"

# =========================
# RECOMMEND FUNCTION
# =========================
def recommend(movie_name, top_n=10):

    movie_name = movie_name.lower().strip()

    if movie_name not in df["movie_name_lower"].values:
        return None

    idx = df[df["movie_name_lower"] == movie_name].index[0]

    scores = list(enumerate(similarity_matrix[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:top_n+1]

    results = []

    for i, score in scores:
        results.append({
            "title": df.iloc[i]["movie_name"],
            "genre": df.iloc[i]["genre"],
            "score": round(float(score), 3),
            "poster": get_poster(df.iloc[i]["movie_name"])
        })

    return results

# =========================
# HEADER UI
# =========================
st.markdown("""
    <h1 style='color:#E50914;'>🎬 Netflix AI Movie Recommender</h1>
    <p style='color:white;'>AI + TMDB Posters + Recommendation System</p>
""", unsafe_allow_html=True)

# =========================
# MOVIE SELECT
# =========================
movie_list = sorted(df["movie_name"].dropna().unique())
movie_name = st.selectbox("🔍 Search Movie", movie_list)

# =========================
# RECOMMEND BUTTON
# =========================
if st.button("Recommend 🚀"):

    results = recommend(movie_name)

    if results is None:
        st.error("Movie not found in dataset!")
    else:
        st.subheader("🔥 Top Recommendations")

        cols = st.columns(5)

        for i, movie in enumerate(results):

            with cols[i % 5]:
                st.image(movie["poster"], use_container_width=True)
                st.markdown(f"**{movie['title']}**")
                st.caption(movie["genre"])
                st.success(f"⭐ {movie['score']}")

# =========================
# TRENDING SECTION
# =========================
st.subheader("🔥 Trending Movies")

trending = df.sample(10)

cols = st.columns(5)

for i, row in enumerate(trending.itertuples()):

    with cols[i % 5]:
        st.image(get_poster(row.movie_name), use_container_width=True)
        st.caption(row.movie_name)