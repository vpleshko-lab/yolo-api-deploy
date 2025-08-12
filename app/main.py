from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from typing import Optional
import shutil
import uuid
import os
import traceback

from app.predict import predict_and_show

app = FastAPI()

@app.post('/predict')
async def predict(file: Optional[UploadFile] = File(None), url: Optional[str] = Form(None)):
    """
    Обробляє POST-запит для детекції об'єктів на зображенні.
    Можна надіслати файл зображення або URL.

    Args:
        file (UploadFile, optional): Завантажений файл зображення.
        url (str, optional): URL зображення.

    Returns:
        JSON: Результати детекції у форматі JSON.
    """
    temp_file = None

    try:
        if file:
            # saving temp file
            temp_file = f'temp_{uuid.uuid4().hex}.jpg'
            with open(temp_file, 'wb') as buffer:
                shutil.copyfileobj(file.file, buffer)
            image_path = temp_file

        elif url:
            image_path = url

        else:
            return JSONResponse(status_code=400, content={'error': 'No file or URL provided'})

        result = predict_and_show(image_path)
        return result

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={'error': str(e)})

    finally:
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)
