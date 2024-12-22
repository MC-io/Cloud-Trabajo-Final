from flask import Flask, request, jsonify
import torch
from pathlib import Path
# Initialize Flask app
app = Flask(__name__)

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5s.pt')

# Define inference route
@app.route('/predict', methods=['POST'])
def predict():

    # Get the uploaded file
    detections_dict = dict()

    for name, frame in request.files.items():
        input_path = f"./input/{frame.filename}"
        output_path = "./output"

        # Save the file locally
        Path("input").mkdir(exist_ok=True)
        Path("output").mkdir(exist_ok=True)
        frame.save(input_path)

        # Perform inference
        results = model(input_path)

        # Extract detection results
        detections = results.pandas().xyxy[0]  # Get bounding boxes as a pandas DataFrame
        output_data = []

        for _, row in detections.iterrows():
            output_data.append({
                "label": row["name"],  # Object label
                "index": int(row["class"]),  # Class index
                "confidence": float(row["confidence"]),  # Confidence score
                "bbox": {
                    "x_min": float(row["xmin"]),
                    "y_min": float(row["ymin"]),
                    "x_max": float(row["xmax"]),
                    "y_max": float(row["ymax"]),
                }
            })
        detections_dict[name] = output_data

    # Send response
    return jsonify({
        "message": "Inference complete",
        "detections": detections_dict
    }), 200


# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)