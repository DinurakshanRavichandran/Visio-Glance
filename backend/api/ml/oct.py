import os
import numpy as np
import tensorflow as tf
import cv2
from tensorflow.keras.models import load_model
import shap
import lime
from lime import lime_image
import matplotlib
matplotlib.use('Agg')  # Force non-GUI backend
import tkinter as tk  # Initialize Tkinter

import matplotlib.pyplot as plt
from PIL import Image

# Get absolute paths for reliable file handling
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # Should be backend/api/ml/
BACKEND_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))  # Go up 2 levels to backend/
STATIC_DIR = os.path.join(BACKEND_DIR, "static", "xai")  # backend/static/xai
os.makedirs(STATIC_DIR, exist_ok=True)

# Load model
MODEL_PATH = os.path.join(SCRIPT_DIR, "cnn1_model (2).h5")
model = load_model(MODEL_PATH, compile=False)
class_labels = ["CNV", "DME", "DRUSEN", "NORMAL"]

def preprocess_image(image_path):
    """Preprocess an image for EfficientNet model."""
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Error: Unable to read image at {image_path}")

    # Convert and resize
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    image = cv2.resize(image, (224, 224))
    
    # Apply preprocessing
    processed = tf.keras.applications.efficientnet.preprocess_input(image)
    return np.expand_dims(processed, axis=0)

def predict_oct(image_path):
    """Predicts the class of an image."""
    image = preprocess_image(image_path)
    predictions = model.predict(image)
    return {
        "prediction": class_labels[np.argmax(predictions[0])],
        "confidence": float(np.max(predictions))
    }

def explain_with_lime_oct(image_path):
    """
    Generates LIME explanation for an image and saves the heatmap.
    """
    # Load image in grayscale and convert to 3-channel RGB for visualization
    original_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if original_image is None:
        raise ValueError(f"Error: Unable to read image at {image_path}")
    original_image_rgb = cv2.cvtColor(original_image, cv2.COLOR_GRAY2RGB)
    
    # Resize image for display purposes
    original_image_resized = cv2.resize(original_image_rgb, (224, 224))
    
    # Preprocess image for the model (assumes you have defined preprocess_image elsewhere)
    processed_image = preprocess_image(image_path)[0]

    explainer = lime_image.LimeImageExplainer()

    def model_predict_wrapper(images):
        processed_images = np.array([
            tf.keras.applications.efficientnet.preprocess_input(img) for img in images
        ])
        return model.predict(processed_images)

    # Generate LIME explanation using the processed image
    explanation = explainer.explain_instance(
        processed_image,
        model_predict_wrapper,
        top_labels=1,
        hide_color=0,
        num_samples=1000
    )

    # Get predicted label from the model using the processed image
    predictions = model.predict(np.expand_dims(processed_image, axis=0))
    label = np.argmax(predictions, axis=-1)[0]

    # Get explanation mask for the predicted label
    temp, mask = explanation.get_image_and_mask(
        label,
        positive_only=True,
        num_features=10,
        hide_rest=False,
    )

    # Create a visualization by overlaying the heatmap on the original image
    base_name = os.path.splitext(os.path.basename(image_path))[0]  # Remove extension
    lime_filename = f"lime_{base_name}.png"
    lime_path = os.path.join(STATIC_DIR, lime_filename)
    
    plt.figure(figsize=(8, 8))
    # Show the original image (displayed in grayscale)
    plt.imshow(original_image_resized, cmap="gray")
    # Overlay the explanation mask using a jet colormap with transparency
    plt.imshow(mask, cmap='jet', alpha=0.5)
    plt.title(f"LIME Explanation for Label {label}")
    plt.axis('off')
    plt.savefig(lime_path, bbox_inches='tight', pad_inches=0)
    plt.close()

    return {
        "lime_image": f"static/xai/{lime_filename}",
        "explanation": "LIME explanation generated"
    }


def explain_with_shap_oct(image_path):
    """Generates and saves SHAP explanation."""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Can't read image: {image_path}")
    
    # Process image
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    img = cv2.resize(img, (224, 224))
    img_array = np.expand_dims(tf.keras.applications.efficientnet.preprocess_input(img), axis=0)

    # SHAP explanation
    masker = shap.maskers.Image("inpaint_telea", img_array.shape[1:])
    explainer = shap.Explainer(model, masker)
    shap_values = explainer(img_array)
    
    # Save and return paths
    base_name = os.path.splitext(os.path.basename(image_path))[0]  # Remove original extension
    shap_filename = f"shap_{base_name}.png"
    shap_path = os.path.join(STATIC_DIR, shap_filename)
    plt.figure(figsize=(10, 6))
    shap.image_plot(shap_values, show=False)
    plt.savefig(shap_path, bbox_inches='tight', dpi=100)
    plt.close()
    
    return {"shap_image": f"static/xai/{shap_filename}"}

def analyze_image(image_path):
    """Full analysis pipeline with verification."""
    classification = predict_oct(image_path)
    explanations = {
        "lime_image": explain_with_lime_oct(image_path)["lime_image"],
        "shap_image": explain_with_shap_oct(image_path)["shap_image"]
    }
    
    # Verify files using absolute paths
    for key in explanations:
        rel_path = explanations[key]
        abs_path = os.path.join(BACKEND_DIR, rel_path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"File missing: {abs_path}")
        Image.open(abs_path).show()
    
    return {
        "classification": classification,
        "explanations": explanations
    }

# Example test
if __name__ == "__main__":
    test_img = os.path.join(SCRIPT_DIR, "cnv.jpeg")
    if not os.path.exists(test_img):
        # Create random test image
        cv2.imwrite(test_img, 
                   np.random.randint(0, 255, (224, 224), dtype=np.uint8),
                   [cv2.IMWRITE_JPEG_QUALITY, 90])
    
    result = analyze_image(test_img)
    print("Analysis Result:")
    print(f"Classification: {result['classification']}")
    print(f"LIME Explanation: {result['explanations']['lime_image']}")
    print(f"SHAP Explanation: {result['explanations']['shap_image']}")