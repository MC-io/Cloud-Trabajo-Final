FROM ultralytics/yolov5:latest-cpu

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN pip install flask flask-cors google-cloud-firestore

COPY server2.py /usr/src/app/server2.py
COPY firestore.json /usr/src/app/firestore.json
    
EXPOSE 5000

CMD ["python3", "server2.py"]