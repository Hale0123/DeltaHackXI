from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import os
import requests

app = Flask(__name__)
CORS(app)

# Nutritionix API Credentials
APP_ID = os.getenv("NUTRITIONIX_APP_ID", "your_app_id_here")
APP_KEY = os.getenv("NUTRITIONIX_APP_KEY", "your_app_key_here")

def get_food_info(food_name):
    """Query the Nutritionix API with the recognized food name."""
    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    headers = {
        "x-app-id": APP_ID,
        "x-app-key": APP_KEY,
        "Content-Type": "application/json"
    }
    payload = {"query": food_name}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # Raise error if the request fails
    return response.json()

@app.route('/analyze', methods=['POST'])
def analyze():
    # Check if an image file was uploaded
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    # Read the uploaded image
    file = request.files['image']
    np_img = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if img is None:
        return jsonify({"error": "Failed to process the image"}), 400

    # Placeholder for OpenCV processing (for now, hardcode "apple")
    # You can add actual object detection or feature extraction here.
    recognized_food = "apple"  # Replace this with your OpenCV logic

    try:
        # Query the Nutritionix API
        food_info = get_food_info(recognized_food)
        return jsonify({
            "message": f"Food recognized: {recognized_food}",
            "info": food_info
        })
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
