from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import os
import requests

app = Flask(__name__)
CORS(app)

# Nutritionix API Credentials
APP_ID = os.getenv("NUTRITIONIX_APP_ID", "your_app_id_here")
APP_KEY = os.getenv("NUTRITIONIX_APP_KEY", "your_app_key_here")

# Load TensorFlow Hub EfficientNet model
model = hub.load("https://tfhub.dev/google/efficientnet/b0/classification/1")

# Load Food101 class labels
with open("food101_labels.txt") as f:
    labels = [line.strip() for line in f]

def get_food_info(food_name):
    """Query the Nutritionix API with the recognized food name."""
    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    headers = {
        "x-app-id": APP_ID,
        "x-app-key": APP_KEY,
        "Content-Type": "application/json"
    }
    payload = {"query": food_name}

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Nutritionix API Response: {response.status_code}, {response.text}")  # Debug log
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Nutritionix API Error for food '{food_name}': {e}")
        raise

# Load TensorFlow Hub model as a Keras layer
model_layer = hub.KerasLayer("https://tfhub.dev/google/efficientnet/b0/classification/1")

def recognize_food_with_tensorflow(image_path):
    """Recognize food using TensorFlow EfficientNet."""
    # Load and preprocess the image
    img = cv2.imread(image_path)
    img = cv2.resize(img, (224, 224))  # Resize to 224x224
    img = np.expand_dims(img, axis=0).astype(np.float32) / 255.0  # Normalize and add batch dimension

    # Run the model
    predictions = model_layer(img)  # Use the KerasLayer
    predicted_label_idx = np.argmax(predictions)
    predicted_label = labels[predicted_label_idx]
    confidence = np.max(predictions)

    return predicted_label, confidence
def recognize_food(img):
    """Improved color-based recognition logic using OpenCV."""
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    img_area = img.shape[0] * img.shape[1]  # Total area of the image

    # Detect red (apples)
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 50, 50])
    upper_red2 = np.array([180, 255, 255])
    mask_red = cv2.inRange(hsv_img, lower_red1, upper_red1) | cv2.inRange(hsv_img, lower_red2, upper_red2)
    red_area = cv2.countNonZero(mask_red)

    # Detect yellow (bananas)
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([30, 255, 255])
    mask_yellow = cv2.inRange(hsv_img, lower_yellow, upper_yellow)
    yellow_area = cv2.countNonZero(mask_yellow)

    # Detect orange (oranges)
    lower_orange = np.array([10, 150, 150])
    upper_orange = np.array([25, 255, 255])
    mask_orange = cv2.inRange(hsv_img, lower_orange, upper_orange)
    orange_area = cv2.countNonZero(mask_orange)

    # Detect blue (blueberries)
    lower_blue = np.array([100, 150, 50])
    upper_blue = np.array([140, 255, 255])
    mask_blue = cv2.inRange(hsv_img, lower_blue, upper_blue)
    blue_area = cv2.countNonZero(mask_blue)

    # Debugging logs
    print(f"Red Area: {red_area}, Yellow Area: {yellow_area}, Orange Area: {orange_area}, Blue Area: {blue_area}")

    # Threshold for significant area detection
    detection_threshold = img_area * 0.05

    # Classify based on the largest detected area
    if red_area > detection_threshold:
        return "apple"
    elif yellow_area > detection_threshold:
        return "banana"
    elif orange_area > detection_threshold:
        return "orange"
    elif blue_area > detection_threshold:
        return "blueberry"
    else:
        return "unknown"  # Fallback for unrecognized food






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

    # Recognize food based on color
    recognized_food = recognize_food(img)
    print(f"Recognized food: {recognized_food}")

    # Hardcoded response for detected food
    try:
        if recognized_food == "unknown":
            return jsonify({"message": "Food not recognized.", "info": None})

        # Query Nutritionix API (optional, can hardcode nutritional data if needed)
        food_info = get_food_info(recognized_food)
        return jsonify({
            "message": f"Food recognized: {recognized_food}",
            "info": food_info
        })
    except requests.exceptions.RequestException as e:
        print(f"Nutritionix API Error: {e}")
        return jsonify({"error": f"Failed to fetch information for {recognized_food}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
