# 1. Вибираємо базовий образ з Python 3.10
FROM python:3.12-slim

# 2. Встановлюємо робочу директорію
WORKDIR /yolo-api-docker

RUN apt-get update && apt-get install -y --no-install-recommends \
    # OpenCV (GUI, OpenGL)
    libgl1 \
    libglib2.0-0 \
    # Matplotlib (рендер графіків)
    libfreetype6-dev \
    libpng-dev \
 && rm -rf /var/lib/apt/lists/*

# 4. Копіюємо requirements.txt
COPY requirements.txt .

# 5. Оновлюємо pip і встановлюємо пакети
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. Копіюємо весь проєкт
COPY . .

# 7. Встановлюємо команду запуску FastAPI через Uvicorn
ENTRYPOINT ["uvicorn"]
CMD ["app.main:app", "--host", "0.0.0.0", "--port", "8000"]
