from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import torch
from pathlib import Path

from google.cloud import firestore

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins="*")
model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5s.pt')

@app.route('/predict', methods=['POST'])
def predict():
    db = firestore.Client.from_service_account_json('firestore.json',  database='god-eyes-firestore')

    data = request.get_json()
    obj = data
    detections_dict = dict()

    
    url = obj['url']
    timestamp = obj['timestamp']
    name = obj['name']

    response = requests.get(url)

    if response.status_code == 200:
        with open(f"{name}-{timestamp}.jpg", "wb") as file:
            file.write(response.content)

    results = model(f"{name}-{timestamp}.jpg")

    detections = results.pandas().xyxy[0]  # Get bounding boxes as a pandas DataFrame

    metadata = []
    metadata_labels = set()

    for _, row in detections.iterrows():
        mtd = {
            "label": row["name"],
            "confidence": float(row["confidence"]),
            "bbox": {
                "x_min": float(row['xmin']),
                "y_min": float(row['ymin']),
                "x_max": float(row['xmax']),
                "y_max": float(row['ymax'])
            }
        }
        metadata.append(mtd)
        metadata_labels.add(row["name"])
    metadata_labels = list(metadata_labels)

    data = {
        "name": name,
        "url": url,
        "timestamp": timestamp,
        "metadata": metadata,
        "metadata_labels": metadata_labels
    }
    db.collection("detections").add(data)

    # Aqui que sube a la base de datos
    ####################################
    ####################################

    
    return jsonify(data), 200



@app.route('/history/<search_term>', methods=['GET'])
def history(search_term):
    # AQUI VA CONSULTA A LA BASE DE DATOS EN FIRESTORE 
    #############################################
    #############################################
    db = firestore.Client.from_service_account_json("firestore.json", database='god-eyes-firestore')

    # Reference a Firestore collection
    query = (
        db.collection("detections")
        .where("metadata_labels", "array_contains", search_term)  # Filter by label
        .order_by("timestamp")  # Order by timestamp (earlier to later)
    )

    # Execute the query and convert results to dictionaries
    results = query.stream()
    filtered_objects = [doc.to_dict() for doc in results]

    return jsonify(filtered_objects), 200 

    


# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)