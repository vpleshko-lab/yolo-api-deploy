FROM python:3.10
WORKDIR /yolo-api-deploy
COPY requirements.txt .
RUN apt-get update && apt-get install -y libgl1-mesa-glx && rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt
COPY . .
ENTRYPOINT ["uvicorn"]
CMD ["app.main:app", "--host", "0.0.0.0", "--port", "8000"]
