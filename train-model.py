import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import pickle

def load_books(file_path):
    """
    Загрузить данные о книгах из CSV-файла.

    Аргументы:
        file_path (str): Путь к файлу CSV.

    Возвращает:
        DataFrame: Данные о книгах.
    """
    books = pd.read_csv(file_path, sep=",", on_bad_lines='skip', encoding='utf-8')
    books = books[['ID', 'Название', 'Автор(ы)', 'Год издания', 'Издатель', 'Обложка']]
    books.rename(columns={
        "ID": 'book_id',
        "Название": 'title', 
        'Автор(ы)': 'author', 
        "Год издания": 'year', 
        "Издатель": "publisher", 
        "Обложка": "image_url"
    }, inplace=True)
    return books

def load_users(file_path):
    """
    Загрузить данные о пользователях из CSV-файла.

    Аргументы:
        file_path (str): Путь к файлу CSV.

    Возвращает:
        DataFrame: Данные о пользователях.
    """
    users = pd.read_csv(file_path, sep=",", on_bad_lines='skip', encoding='utf-8')
    users.rename(columns={
        "ID": 'user_id', 
        'Last Name': 'last_name', 
        "Name": 'name'
    }, inplace=True)
    return users

def load_ratings(file_path):
    """
    Загрузить данные о рейтингах из CSV-файла.

    Аргументы:
        file_path (str): Путь к файлу CSV.

    Возвращает:
        DataFrame: Данные о рейтингах.
    """
    ratings = pd.read_csv(file_path, sep=",", on_bad_lines='skip', encoding='utf-8')
    ratings.rename(columns={
        "User Id": 'user_id', 
        "Book Id": 'book_id',
        'Rating': 'rating'
    }, inplace=True)
    return ratings

def filter_active_users(ratings, min_ratings=15):
    """
    Фильтрация активных пользователей на основе минимального количества рейтингов.

    Аргументы:
        ratings (DataFrame): Данные о рейтингах.
        min_ratings (int): Минимальное количество рейтингов для пользователя.

    Возвращает:
        DataFrame: Отфильтрованные данные о рейтингах.
    """
    user_counts = ratings['user_id'].value_counts()
    active_users = user_counts[user_counts > min_ratings].index
    return ratings[ratings['user_id'].isin(active_users)]

def prepare_final_ratings(ratings, books, min_book_ratings=50):
    """
    Подготовка окончательных данных о рейтингах.

    Аргументы:
        ratings (DataFrame): Данные о рейтингах.
        books (DataFrame): Данные о книгах.
        min_book_ratings (int): Минимальное количество рейтингов для книги.

    Возвращает:
        DataFrame: Окончательные данные о рейтингах.
    """
    ratings_with_books = ratings.merge(books, on='book_id')
    book_ratings_count = ratings_with_books.groupby('title')['rating'].count().reset_index()
    book_ratings_count.rename(columns={'rating': 'num_of_rating'}, inplace=True)
    final_ratings = ratings_with_books.merge(book_ratings_count, on='title')
    final_ratings = final_ratings[final_ratings['num_of_rating'] >= min_book_ratings]
    final_ratings.drop_duplicates(['user_id', 'title'], inplace=True)
    return final_ratings

def create_pivot_table(final_ratings):
    """
    Создание сводной таблицы для рекомендаций.

    Аргументы:
        final_ratings (DataFrame): Окончательные данные о рейтингах.

    Возвращает:
        DataFrame: Сводная таблица.
    """
    book_pivot = final_ratings.pivot_table(columns='user_id', index='title', values='rating')
    book_pivot.fillna(0, inplace=True)
    return book_pivot

def train_model(book_pivot):
    """
    Обучение модели рекомендаций.

    Аргументы:
        book_pivot (DataFrame): Сводная таблица.

    Возвращает:
        NearestNeighbors: Обученная модель.
    """
    book_sparse = csr_matrix(book_pivot)
    model = NearestNeighbors(algorithm='brute')
    model.fit(book_sparse)
    return model

def save_artifacts(model, book_pivot, final_ratings):
    """
    Сохранение артефактов модели и данных.

    Аргументы:
        model (NearestNeighbors): Обученная модель.
        book_pivot (DataFrame): Сводная таблица.
        final_ratings (DataFrame): Окончательные данные о рейтингах.
    """
    pickle.dump(model, open('artifacts/model.pkl', 'wb'))
    pickle.dump(book_pivot.index, open('artifacts/book_names.pkl', 'wb'))
    pickle.dump(final_ratings, open('artifacts/final_rating.pkl', 'wb'))
    pickle.dump(book_pivot, open('artifacts/book_pivot.pkl', 'wb'))

def main():
    """
    Основная функция для загрузки данных, подготовки и обучения модели.
    """
    books = load_books('data/Books.csv')
    users = load_users('data/Users.csv')
    ratings = load_ratings('data/Book-Ratings.csv')
    
    filtered_ratings = filter_active_users(ratings)
    final_ratings = prepare_final_ratings(filtered_ratings, books)
    book_pivot = create_pivot_table(final_ratings)
    model = train_model(book_pivot)
    save_artifacts(model, book_pivot, final_ratings)
    
    print("Model training and data preparation complete.")

if __name__ == "__main__":
    main()
