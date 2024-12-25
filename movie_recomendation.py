# -*- coding: utf-8 -*-
"""Movie Recomendation.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1PW7bucmvdX1fQ165tiVnE682RtWb5Qyz

## Import Library
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')
from surprise import Reader, Dataset, SVD
from surprise.model_selection import cross_validate, GridSearchCV
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, request, jsonify
from surprise.model_selection import train_test_split
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer

# Load dataset
ratings_small = pd.read_csv('/content/drive/MyDrive/Project/Movie/ratings_small.csv')
tmdb_5000_credits = pd.read_csv('/content/drive/MyDrive/Project/Movie/tmdb_5000_credits.csv')
tmdb_5000_movies = pd.read_csv('/content/drive/MyDrive/Project/Movie/tmdb_5000_movies.csv')

tmdb_5000_credits.columns = ['id', 'title', 'cast', 'crew']
tmdb_5000_movies= tmdb_5000_movies.merge(tmdb_5000_credits,on='id')

tmdb_5000_movies = tmdb_5000_movies.rename(columns={'original_title': 'title'})
# Tampilkan 5 baris pertama
tmdb_5000_movies.head(5)

# Periksa beberapa baris pertama dari kolom yang diharapkan
tmdb_5000_movies.info()

tmdb_5000_credits.info()

C= tmdb_5000_movies['vote_average'].mean()
C

m= tmdb_5000_movies['vote_count'].quantile(0.9)
m

q_movies = tmdb_5000_movies.copy().loc[tmdb_5000_movies['vote_count'] >= m]
q_movies.shape

def weighted_rating(x, m=m, C=C):
    v = x['vote_count']
    R = x['vote_average']
    # Calculation based on the IMDB formula
    return (v/(v+m) * R) + (m/(m+v) * C)

# Define a new feature 'score' and calculate its value with `weighted_rating()`
q_movies['score'] = q_movies.apply(weighted_rating, axis=1)

#Sort movies based on score calculated above
q_movies = q_movies.sort_values('score', ascending=False)

#Print the top 15 movies
q_movies[['title', 'vote_count', 'vote_average', 'score']].head(10)

pop= tmdb_5000_movies.sort_values('popularity', ascending=False)
import matplotlib.pyplot as plt
plt.figure(figsize=(12,4))

plt.barh(pop['title'].head(6),pop['popularity'].head(6), align='center',
        color='skyblue')
plt.gca().invert_yaxis()
plt.xlabel("Popularity")
plt.title("Popular Movies")

tmdb_5000_movies['overview'].head(5)

#Import TfIdfVectorizer from scikit-learn
from sklearn.feature_extraction.text import TfidfVectorizer

#Define a TF-IDF Vectorizer Object. Remove all English stop words such as 'the', 'a'
tfidf = TfidfVectorizer(stop_words='english')

#Replace NaN with an empty string
tmdb_5000_movies['overview'] = tmdb_5000_movies['overview'].fillna('')

#Construct the required TF-IDF matrix by fitting and transforming the data
tfidf_matrix = tfidf.fit_transform(tmdb_5000_movies['overview'])

#Output the shape of tfidf_matrix
print(tfidf_matrix.shape)

# Import linear_kernel
from sklearn.metrics.pairwise import linear_kernel

# Compute the cosine similarity matrix
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

#Construct a reverse map of indices and movie titles
indices = pd.Series(tmdb_5000_movies.index, index=tmdb_5000_movies['title']).drop_duplicates()

# Function that takes in movie title as input and outputs most similar movies
def get_recommendations(title, cosine_sim=cosine_sim):
    # Get the index of the movie that matches the title
    idx = indices[title]

    # Get the pairwsie similarity scores of all movies with that movie
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort the movies based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores of the 10 most similar movies
    sim_scores = sim_scores[1:11]

    # Get the movie indices
    movie_indices = [i[0] for i in sim_scores]

    # Return the top 10 most similar movies
    return tmdb_5000_movies['title'].iloc[movie_indices]

get_recommendations('The Dark Knight Rises')

get_recommendations('The Avengers')

# Define the reader
reader = Reader()

data = Dataset.load_from_df(ratings_small[['userId', 'movieId', 'rating']], reader)

# Definisikan parameter grid
param_grid = {
    'n_factors': [50, 100, 150],
    'n_epochs': [20, 30],
    'lr_all': [0.002, 0.005],
    'reg_all': [0.02, 0.1]
}

# Lakukan Grid Search
gs = GridSearchCV(SVD, param_grid, measures=['rmse'], cv=3)
gs.fit(data)

# Cetak hasil terbaik
print(gs.best_score['rmse'])
print(gs.best_params['rmse'])

# Membagi data menjadi trainset dan testset
trainset, testset = train_test_split(data, test_size=0.25)

# Gunakan model terbaik
algo = gs.best_estimator['rmse']
algo.fit(trainset)

ratings_small[ratings_small['userId'] == 1]

algo.predict(1, 302, 3)

tmdb_5000_movies['overview_tokens'] = tmdb_5000_movies['overview'].apply(lambda x: x.split())

# Latih model Word2Vec
model = Word2Vec(sentences=tmdb_5000_movies['overview_tokens'], vector_size=100, window=5, min_count=1, workers=4)

# Mendapatkan vektor untuk setiap overview
def get_vector(tokens):
    # Filter out tokens not in the model's vocabulary
    valid_tokens = [word for word in tokens if word in model.wv]
    if not valid_tokens:
        # Return a zero vector if no valid tokens are found
        return np.zeros(model.vector_size)
    return np.mean([model.wv[word] for word in valid_tokens], axis=0)

tmdb_5000_movies['overview_vector'] = tmdb_5000_movies['overview_tokens'].apply(get_vector)

# Hitung cosine similarity berdasarkan vektor Word2Vec
overview_vectors = np.array(tmdb_5000_movies['overview_vector'].tolist())
cosine_sim_w2v = cosine_similarity(overview_vectors, overview_vectors)

# Fungsi rekomendasi menggunakan Word2Vec
def get_recommendations_w2v(title, cosine_sim=cosine_sim_w2v):
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    movie_indices = [i[0] for i in sim_scores]
    return tmdb_5000_movies['title'].iloc[movie_indices]

# Contoh penggunaan
get_recommendations_w2v('The Dark Knight Rises')

# Sort movies by popularity
popular_movies = tmdb_5000_movies.sort_values('popularity', ascending=False)

# Plot top 10 popular movies
plt.figure(figsize=(12, 6))
plt.barh(popular_movies['title'].head(10), popular_movies['popularity'].head(10), color='skyblue')
plt.xlabel('Popularity')
plt.title('Top 10 Most Popular Movies')
plt.gca().invert_yaxis()
plt.show()

plt.figure(figsize=(10, 6))
plt.hist(tmdb_5000_movies['vote_average'], bins=20, color='lightgreen', edgecolor='black')
plt.xlabel('Average Rating')
plt.ylabel('Number of Movies')
plt.title('Distribution of Movie Ratings')
plt.show()

# Generate word cloud for recommended movies
recommended_movies = get_recommendations('The Dark Knight Rises')
text = ' '.join(tmdb_5000_movies[tmdb_5000_movies['title'].isin(recommended_movies)]['overview'].fillna(''))

wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Word Cloud of Recommended Movies')
plt.show()

# Bagian 4: Trend Rating dari Waktu ke Waktu
# Assuming 'release_date' is available and in datetime format
tmdb_5000_movies['release_date'] = pd.to_datetime(tmdb_5000_movies['release_date'])
tmdb_5000_movies['year'] = tmdb_5000_movies['release_date'].dt.year

average_rating_per_year = tmdb_5000_movies.groupby('year')['vote_average'].mean()

plt.figure(figsize=(12, 6))
plt.plot(average_rating_per_year.index, average_rating_per_year.values, marker='o', linestyle='-')
plt.xlabel('Year')
plt.ylabel('Average Rating')
plt.title('Average Movie Rating Over Time')
plt.grid(True)
plt.show()

# Cetak hasil terbaik dari GridSearchCV
print("Best RMSE score from GridSearchCV:", gs.best_score['rmse'])

# Gunakan model terbaik untuk prediksi pada testset
predictions = algo.test(testset)

# Hitung RMSE pada testset
from surprise import accuracy
rmse = accuracy.rmse(predictions)
print("RMSE on testset:", rmse)

app = Flask(__name__)

@app.route('/recommend', methods=['GET'])
def recommend():
    title = request.args.get('title')
    recommendations = get_recommendations_w2v(title)
    return jsonify(recommendations.tolist())

if __name__ == '__main__':
    app.run(debug=True)