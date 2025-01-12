from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Access the variables
APP_ID = os.getenv("NUTRITIONIX_APP_ID")
APP_KEY = os.getenv("NUTRITIONIX_APP_KEY")

app = Flask(__name__)
CORS(app)

# Function to preprocess image
def preprocess_image(image_file):
    # Read the image file into a numpy array
    np_img = np.frombuffer(image_file.read(), np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    # Resize or preprocess the image as needed
    resized_img = cv2.resize(img, (224, 224))  # Resize for ML model or API
    return resized_img

# Function to call external API for food information
def get_food_info(recognized_food):
    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    headers = {
        "x-app-id": APP_ID,  # Use environment variable
        "x-app-key": APP_KEY,  # Use environment variable
        "Content-Type": "application/json",
    }
    payload = {"query": recognized_food}
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files['image']

    # Preprocess the image using OpenCV
    processed_image = preprocess_image(image_file)

    # Placeholder for OpenCV-based recognition logic
    # For now, we'll use a dummy recognized food name
    recognized_food = "apple"  # Replace with actual recognition logic later

    # Get food information from the external API
    try:
        food_info = get_food_info(recognized_food)
        return jsonify({"message": "Image processed!", "food": recognized_food, "info": food_info})
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve food info: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
