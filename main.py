from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from typing import Optional
import shutil
import uuid
import os
import matplotlib.pyplot as plt
import cv2
import numpy as np
from ultralytics import YOLO
import os
import requests
import traceback

model = YOLO('yolov8x.pt')

def predict_and_show(img_path: str) -> list:
    """
    Виконує детекцію об'єктів на зображенні за допомогою моделі YOLOv8,
    виводить зображення з bounding boxes і повертає список детекцій у форматі словника.

    Args:
        img_path (str): Шлях до локального зображення або URL.

    Returns:
        list: Список детекцій, кожна — словник з ключами:
              'class_id', 'class_name', 'confidence', 'bbox' (координати).
    """

    def read_image(img_path: str):
        """
        Завантажує зображення з локального шляху або URL.

        Логіка:
        1. Якщо файл існує локально, намагається його відкрити.
        2. Якщо локального файлу немає, завантажує зображення за URL.
        3. Конвертує байти у формат зображення OpenCV.

        Args:
            img_path (str): Шлях до локального файлу або URL.

        Raises:
            ValueError: Якщо файл знайдено, але його не вдалося відкрити.
            ValueError: Якщо не вдалося завантажити зображення за URL.
            ValueError: Якщо дані не є валідним зображенням.

        Returns:
            numpy.ndarray: Зображення у форматі BGR (OpenCV).
        """
        # 1. Перевірка, чи існує файл локально
        if os.path.exists(img_path):
            img = cv2.imread(img_path)
            if img is None:
                raise ValueError(f'File found, but not opened: {img_path}')
            return img
        # 2. Якщо локально файл відсутній - пробуємо завантажити URL
        try:
            resp = requests.get(img_path)
            resp.raise_for_status()
        except Exception as e:
            raise ValueError(f'Cannot download image by url: {img_path}\nReason: {e}')
        # 3. Обробка зображення
        image_array = np.asarray(bytearray(resp.content), dtype=np.uint8)
        img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f'Cannot identify image by url:{img_path}')

        return img

    img = read_image(img_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    h, w = img_rgb.shape[:2]
    font_scale = max(0.5, min(1.5, w / 1800))
    line_thickness_text = max(2, int(round(min(h, w) / 500)))
    line_thickness = max(1, int(round(min(h, w) / 300)))

    results = model(img)
    result = results[0]
    detections = []

    for box in result.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        xyxy = box.xyxy[0].tolist()
        name = str(model.names[cls_id])

        # колір bbox залежно від впевненості
        r = int((1 - conf) * 255)
        g = int(conf * 255)
        color = (r, g, 0)

        x1, y1, x2, y2 = map(int, xyxy)
        cv2.rectangle(img_rgb, (x1, y1), (x2, y2), color=color, thickness=line_thickness)

        label = (f'{name} ({conf:.2f})')
        cv2.putText(img = img_rgb,
                    text = label,
                    org = (x1, max(0, y1 - 10)),
                    fontFace = cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale= font_scale,
                    color = (255, 255, 255),
                    thickness=line_thickness_text)

        detections.append({
            'class_id': cls_id,
            'class_name': name,
            'confidence': round(conf, 3),
            'bbox': [round(x, 2) for x in xyxy]
        })

    plt.figure(figsize=(10,8))
    plt.imshow(img_rgb)
    plt.axis('off')
    plt.title('YOLOv8 Detection')
    plt.show()

    return detections

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
