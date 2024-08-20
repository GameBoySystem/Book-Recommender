import pickle
import streamlit as st
import numpy as np

st.header('Book Recommender System Using Machine Learning')

# Загрузка модели и данных
model = pickle.load(open('artifacts/model.pkl','rb'))
book_names = pickle.load(open('artifacts/book_names.pkl','rb'))
final_rating = pickle.load(open('artifacts/final_rating.pkl','rb'))
book_pivot = pickle.load(open('artifacts/book_pivot.pkl','rb'))

# Функция для получения постеров книг
def fetch_poster(suggestion):
    book_name = []
    ids_index = []
    poster_url = []

    for book_id in suggestion:
        book_name.append(book_pivot.index[book_id])

    for name in book_name[0]: 
        ids = np.where(final_rating['title'] == name)[0][0]
        ids_index.append(ids)

    for idx in ids_index:
        url = final_rating.iloc[idx]['image_url']
        poster_url.append(url)

    return poster_url

# Функция для получения рекомендаций
def recommend_books(selected_books):
    book_indices = []
    for book_name in selected_books:
        book_id = np.where(book_pivot.index == book_name)[0][0]
        book_indices.append(book_id)
    
    book_vectors = book_pivot.iloc[book_indices, :].values
    avg_book_vector = np.mean(book_vectors, axis=0).reshape(1, -1)
    
    distance, suggestions = model.kneighbors(avg_book_vector, n_neighbors=6)
    
    poster_url = fetch_poster(suggestions)
    recommended_books = [book_pivot.index[suggestion] for suggestion in suggestions[0]]
    
    return recommended_books, poster_url

# Выбор нескольких книг
selected_books = st.multiselect(
    "Type or select books from the dropdown",
    book_names
)

# Показ рекомендаций
if st.button('Show Recommendation') and selected_books:
    recommended_books, poster_url = recommend_books(selected_books)
    cols = st.columns(5)

    for i in range(1, 6):
        with cols[i - 1]:
            st.text(recommended_books[i])
            st.image(poster_url[i])
