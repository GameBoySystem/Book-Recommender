from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import pickle
import numpy as np
import uvicorn
import pandas as pd

# Создаем приложение FastAPI
app = FastAPI()

# Настройка шаблонов Jinja2
templates = Jinja2Templates(directory="templates")

# Включение CORS middleware для клиентских запросов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Укажите домены, если это необходимо
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Загрузка модели и данных
model = pickle.load(open('artifacts/model.pkl', 'rb'))
book_names = pickle.load(open('artifacts/book_names.pkl', 'rb'))
final_rating = pickle.load(open('artifacts/final_rating.pkl', 'rb'))
book_pivot = pickle.load(open('artifacts/book_pivot.pkl', 'rb'))

# Загрузка данных книг из CSV
books_df = pd.read_csv('data/Books.csv')

# Определение модели запроса
class BookRequest(BaseModel):
    selected_books: list

@app.get("/")
def index(request: Request):
    """
    Отображение шаблона index.html на корневом маршруте.

    Аргументы:
        request (Request): Объект запроса.

    Возвращает:
        TemplateResponse: Отрендеренный шаблон.
    """
    return templates.TemplateResponse("index.html", context={"request": request})

@app.get("/books")
def get_books():
    """
    Получение списка всех названий книг.

    Возвращает:
        JSONResponse: JSON-ответ, содержащий список названий книг.
    """
    book_names_list = [name for name in book_names]
    return JSONResponse(book_names_list)

@app.post("/recommend/")
def get_recommendations(request: BookRequest):
    """
    Получение рекомендаций книг на основе выбранных книг.

    Аргументы:
        request (BookRequest): Объект запроса, содержащий выбранные книги.

    Возвращает:
        dict: Словарь, содержащий рекомендованные книги и URL-адреса их обложек.

    Вызывает:
        HTTPException: Если произошла ошибка в процессе рекомендации.
    """
    try:
        recommended_books, poster_url, authors, publisher = recommend_books(request.selected_books)
        return {"recommended_books": recommended_books, "poster_url": poster_url, "authors": authors, "publisher": publisher}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/search")
def search_books(query: str):
    """
    Поиск книг по названию.

    Аргументы:
        query (str): Строка поискового запроса.

    Возвращает:
        JSONResponse: JSON-ответ, содержащий результаты поиска.
    """
    matching_books = books_df[books_df['Название'].str.contains(query, case=False, na=False)]
    search_results = matching_books[['Название', 'Обложка']].to_dict(orient='records')
    return JSONResponse(search_results)

def fetch_poster(suggestion):
    """
    Получение URL-адресов обложек для предложенных книг.

    Аргументы:
        suggestion (list): Список индексов предложенных книг.

    Возвращает:
        list: Список URL-адресов обложек для предложенных книг.
    """
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

def recommend_books(selected_books):
    """
    Рекомендация книг на основе выбранных книг.

    Аргументы:
        selected_books (list): Список названий выбранных книг.

    Возвращает:
        tuple: Кортеж, содержащий список рекомендованных названий книг и URL-адресов их обложек.
    """
    book_indices = []
    for book_name in selected_books:
        book_id = np.where(book_pivot.index == book_name)[0][0]
        book_indices.append(book_id)
    
    book_vectors = book_pivot.iloc[book_indices, :].values
    avg_book_vector = np.mean(book_vectors, axis=0).reshape(1, -1)
    
    distance, suggestions = model.kneighbors(avg_book_vector, n_neighbors=20+len(selected_books))
    
    poster_url = fetch_poster(suggestions)
    recommended_books = [book_pivot.index[suggestion] for suggestion in suggestions[0]]
    
    # Исключение выбранных книг из рекомендаций
    filtered_recommended_books = [book for book in recommended_books if book not in selected_books]
    filtered_poster_url = [poster for book, poster in zip(recommended_books, poster_url) if book not in selected_books]

    authors = [books_df[books_df['Название'] == book]['Автор(ы)'].values[0] for book in filtered_recommended_books]  # Получение авторов
    publisher = [books_df[books_df['Название'] == book]['Издатель'].values[0] for book in filtered_recommended_books]  
    # НАДО ПЕРЕДЕЛАТЬ ЧТО БЫ ВЫДАВАЛО {books: {author:..., poster_url:..., publisher:..., date:...}}
    return filtered_recommended_books, filtered_poster_url, authors, publisher

if __name__ == '__main__':
    uvicorn.run("main:app", port=8005, reload=True)
