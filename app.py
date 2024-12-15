import torch

model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

image_path = "input/Normal,_Illinois.jpg"
results = model.predict(image_path)
results.print()