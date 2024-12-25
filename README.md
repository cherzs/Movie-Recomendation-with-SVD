# Movie-Recomendation-with-SVD
This project aims to build an accurate movie recommendation system using Kaggle data with a Collaborative Filtering and Content-Based Filtering approach.

---

## 🎥 **Movie Recommendation System**  

### 📜 **Description**  
This project aims to build an accurate and personalized movie recommendation system using data sourced from Kaggle. The system leverages **Collaborative Filtering** and **Content-Based Filtering** to suggest movies based on user preferences and movie metadata.  

### 📊 **Datasets**  
The project utilizes two primary datasets from Kaggle:  
1. **[The Movies Dataset](https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset)**: Contains metadata on movies, user ratings, and links to related data.  
2. **[TMDB Movie Metadata](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata)**: Provides detailed metadata about movies, including genres, keywords, and user ratings.  

### ⚙️ **Methodology**  
1. **Data Processing**:  
   - Combined and cleaned datasets to remove duplicates, null values, and inconsistencies.  
   - Preprocessed textual data for natural language-based similarity measures.  
2. **Model Development**:  
   - Implemented **Collaborative Filtering (SVD)** to predict user ratings.  
   - Used **Content-Based Filtering (TF-IDF)** to recommend movies based on metadata such as genres and descriptions.  
3. **Evaluation**:  
   - Evaluated model performance using **RMSE** for rating predictions and qualitative checks for relevance of recommendations.  

### 🔍 **Key Insights**  
- Combining user behavior and movie metadata provides richer recommendations.  
- Preprocessing and feature engineering significantly improved model accuracy.  

### 📂 **Repository**  
The source code, detailed documentation, and visualization of results are included in this repository for reproducibility and further development.  

---

Feel free to adjust details to fit your exact implementation. 😊
