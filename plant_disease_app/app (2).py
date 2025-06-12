
  
  from flask import Flask, request, jsonify
from inference_sdk import InferenceHTTPClient
import os
app = Flask(__name__)
# Initialize Roboflow client
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="fV5LNBhyGxlZQNNZec6W"
)
MODEL_ID = "my-first-project-mdags/1"  # replace with your correct model ID
@app.route("/", methods=["GET"])
def home():
    return "Plant Disease Detection API is running!"
@app.route("/predict", methods=["POST"])
def predict():
    print("Request method:", request.method)
    print("Request files:", request.files)
    
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    image = request.files.get("image") or request.files.get("file")
    if not image:
        return jsonify({"error": "No image uploaded"}), 400

    try:
        result = CLIENT.infer(image_path, model_id=MODEL_ID)
        os.remove(image_path)  # clean up after inference
        predictions = result.get("predictions", [])
        if not predictions:
            return jsonify({"result": "No disease detected"})
        best = sorted(predictions, key=lambda x: x['confidence'], reverse=True)[0]
        label = best['class']
        confidence = best['confidence']
        return jsonify({
            "predicted_class": label,
            "confidence": round(confidence, 2)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
