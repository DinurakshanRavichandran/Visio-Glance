import os
import numpy as np
import tensorflow as tf
import cv2
from tensorflow.keras.models import load_model



# Load the trained model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "cnn1_model (2).h5")
model = load_model(MODEL_PATH, compile=False)
# Class labels
class_labels = ["CNV", "DME", "DRUSEN", "NORMAL"]

def preprocess_image(image_path):
    """
    Preprocess an image for EfficientNet model.
    - Converts grayscale to RGB
    - Resizes to 224x224
    - Applies EfficientNet preprocessing
    """
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Error: Unable to read image at {image_path}")

    # Convert grayscale to RGB
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

    # Resize to model input size
    image = cv2.resize(image, (224, 224))

    # Apply EfficientNet preprocessing
    image = tf.keras.applications.efficientnet.preprocess_input(image)

    # Expand dimensions to match model input shape
    return np.expand_dims(image, axis=0)

def predict_image(image_path):
    """
    Predicts the class of an image and returns JSON response.
    """
    image = preprocess_image(image_path)
    predictions = model.predict(image)
    predicted_class = np.argmax(predictions, axis=-1)[0]
    confidence = float(np.max(predictions))
    print(f"Confidence: {confidence}, Predicted class: {predicted_class}")

    return {
        "prediction": class_labels[predicted_class],
        "confidence": confidence
    }

predict_image(r"C:\Users\Dinurakshan\Visio-Glance\backend\api\ml\cnv.jpeg")