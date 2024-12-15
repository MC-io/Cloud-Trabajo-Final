FROM ultralytics/yolov5:latest-cpu

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN pip install flask

COPY server.py /usr/src/app/server.py
    
EXPOSE 5000

CMD ["python3", "server.py"]