import pickle

# Укажите путь к вашему .pkl файлу
file_path = "artifacts/book_names.pkl"

# Открываем файл в режиме чтения
with open(file_path, "rb") as f:
    # Загружаем содержимое файла с помощью модуля pickle
    data = pickle.load(f)

# Выводим содержимое файла
print(data)
