# pip install ultralytics --break-system-packages
from ultralytics import YOLO

# Загрузка предобученной модели
model = YOLO("yolo26n.pt")  # или например yolo11n.pt
results = model.train(data="dataset.yaml", epochs=10, imgsz=640)