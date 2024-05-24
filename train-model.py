import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import pickle

# Загрузка данных
books = pd.read_csv('data/Books.csv', sep=",", on_bad_lines='skip', encoding='utf-8')
books = books[['ID', 'Название', 'Автор(ы)', 'Год издания', 'Издатель', 'Обложка']]
books.rename(columns={"ID": 'book_id',
                      "Название": 'title', 
                      'Автор(ы)': 'author', 
                      "Год издания": 'year', 
                      "Издатель": "publisher", 
                      "Обложка": "image_url"}, 
                      inplace=True)

users = pd.read_csv('data/Users.csv', sep=",", on_bad_lines='skip', encoding='utf-8')
users.rename(columns={"ID": 'user_id', 
                      'Last Name': 'last_name', 
                      "Name": 'name'}, 
                      inplace=True)

ratings = pd.read_csv('data/Book-Ratings.csv', sep=",", on_bad_lines='skip', encoding='utf-8')
ratings.rename(columns={"User Id": 'user_id', 
                        "Book Id": 'book_id',
                        'Rating': 'rating'}, 
                        inplace=True)

# Фильтрация данных
x = ratings['user_id'].value_counts() > 15
y = x[x].index
ratings = ratings[ratings['user_id'].isin(y)]

ratings_with_books = ratings.merge(books, on='book_id')
number_rating = ratings_with_books.groupby('title')['rating'].count().reset_index()
number_rating.rename(columns={'rating': 'num_of_rating'}, inplace=True)
final_rating = ratings_with_books.merge(number_rating, on='title')
final_rating = final_rating[final_rating['num_of_rating'] >= 50]
final_rating.drop_duplicates(['user_id', 'title'], inplace=True)

# Создание pivot-таблицы
book_pivot = final_rating.pivot_table(columns='user_id', index='title', values='rating')
book_pivot.fillna(0, inplace=True)

# Обучение модели
book_sparse = csr_matrix(book_pivot)
model = NearestNeighbors(algorithm='brute')
model.fit(book_sparse)

# Сохранение моделей и данных
pickle.dump(model, open('artifacts/model.pkl', 'wb'))
pickle.dump(book_pivot.index, open('artifacts/book_names.pkl', 'wb'))
pickle.dump(final_rating, open('artifacts/final_rating.pkl', 'wb'))
pickle.dump(book_pivot, open('artifacts/book_pivot.pkl', 'wb'))

print("Model training and data preparation complete.")
