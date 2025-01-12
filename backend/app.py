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
    # Ensure an image file is provided
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    # Get the uploaded file (but don't process it yet)
    image_file = request.files['image']
    app.logger.info(f"File received: {image_file.filename}")  # Use logger for better logging
    print("File received:", image_file.filename, flush=True)  # Also print for debugging

    # Simulate a successful response with "apple" data
    hardcoded_response = {
        "message": "Image processed successfully!",
        "food": "apple",
        "info": {
            "foods": [
                {
                    "food_name": "apple",
                    "serving_qty": 1,
                    "serving_unit": "medium (3\" dia)",
                    "serving_weight_grams": 182,
                    "nf_calories": 95,
                    "nf_total_fat": 0.3,
                    "nf_protein": 0.5,
                    "nf_total_carbohydrate": 25,
                    "full_nutrients": []
                }
            ]
        }
    }

    try:
        # Send back the hardcoded response for now
        return jsonify(hardcoded_response), 200
    except Exception as e:
        # Return error message if something fails
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)  # Enable debug mode

