# Використовуємо офіційний образ Python як базовий
FROM python:3.12-slim

# Встановлюємо робочий каталог
WORKDIR /app

# Копіюємо всі файли в контейнер
COPY . .

# Встановлюємо залежності
RUN pip install pymongo

# Відкриваємо порт, на якому буде працювати сервер
EXPOSE 3000

# Запускаємо ваш веб-сервер
CMD ["python", "main.py"]
