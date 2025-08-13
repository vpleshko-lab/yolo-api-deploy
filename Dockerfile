FROM python:3.12-slim

WORKDIR /yolo-api-docker

RUN apt-get update && apt-get install -y --no-install-recommends \
    # OpenCV (GUI, OpenGL)
    libgl1 \
    libglib2.0-0 \
    # Matplotlib (рендер графіків)
    libfreetype6-dev \
    libpng-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["uvicorn"]
CMD ["app.main:app", "--host", "0.0.0.0", "--port", "8000"]
