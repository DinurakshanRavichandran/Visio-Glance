import shap
import lime
from lime import lime_image
import numpy as np
import tensorflow as tf
import cv2
import matplotlib.pyplot as plt
import os
from tensorflow.keras.models import load_model

# Load model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "cnn1_model (2).h5")
model = load_model(MODEL_PATH, compile=False)

# Class labels
class_labels = ["CNV", "DME", "DRUSEN", "NORMAL"]

def explain_with_lime_oct(image_path):
    """
    Generates LIME explanation for an image.
    """
    original_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if original_image is None:
        raise ValueError(f"Error: Unable to read image at {image_path}")

    original_image_rgb = cv2.cvtColor(original_image, cv2.COLOR_GRAY2RGB)
    processed_image = cv2.resize(original_image_rgb, (224, 224))

    explainer = lime_image.LimeImageExplainer()

    def model_predict_wrapper(images):
        images = np.array([tf.keras.applications.efficientnet.preprocess_input(img) for img in images])
        return model.predict(images)

    explanation = explainer.explain_instance(
        processed_image,
        model_predict_wrapper,
        top_labels=1,
        hide_color=0,
        num_samples=1000
    )

    # Get feature importance mask
    _, mask = explanation.get_image_and_mask(
        np.argmax(model.predict(np.expand_dims(processed_image, axis=0))),
        positive_only=True,
        num_features=10,
        hide_rest=False,
    )

    return {
        "lime_explanation": "LIME explanation generated",
        "lime_image_path": image_path  # This can be updated to save & return the heatmap image
    }

def explain_with_shap_oct(image_path):
    """
    Generates SHAP explanation for an image.
    """
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Error: Unable to read image at {image_path}")

    image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    image = cv2.resize(image, (224, 224))
    processed_image = np.expand_dims(tf.keras.applications.efficientnet.preprocess_input(image), axis=0)

    masker = shap.maskers.Image("inpaint_telea", processed_image.shape[1:])
    explainer = shap.Explainer(model, masker, output_names=class_labels)

    shap_values = explainer(processed_image)
    
    return {
        "shap_explanation": "SHAP explanation generated",
        "shap_image_path": image_path  # Similar to LIME, update to save heatmap if needed
    }
#explain_with_lime_oct(r"C:\Users\Dinurakshan\Visio-Glance\backend\api\ml\cnv.jpeg")
#explain_with_shap_oct(r"C:\Users\Dinurakshan\Visio-Glance\backend\api\ml\cnv.jpeg")
def generate_xai_oct(image_path):
    """
    Generates both LIME and SHAP explanations for an OCT image.

    Parameters:
        image_path (str): Path to the input image.

    Returns:
        dict: A dictionary containing both LIME and SHAP explanations.
    """
    # Generate LIME explanation
    lime_result = explain_with_lime_oct(image_path)

    # Generate SHAP explanation
    shap_result = explain_with_shap_oct(image_path)

    # Return combined results
    return {
        "lime_explanation": lime_result,
        "shap_explanation": shap_result
    }