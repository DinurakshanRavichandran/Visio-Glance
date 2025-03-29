from flask import Blueprint, request, jsonify, send_file
import numpy as np
import joblib
import tensorflow as tf
import matplotlib.pyplot as plt
import cv2
import os
import traceback
from PIL import Image
from pathlib import Path
from datetime import datetime
from lime import lime_image
from skimage.segmentation import mark_boundaries
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications.resnet50 import preprocess_input, ResNet50

# Blueprint for image processing
image_bp = Blueprint('image', __name__)

# Load model and ResNet50 feature extractor
model_path = 'Sakuna_Eye_Disease_Detection_Model.h5'
model = joblib.load(model_path)
resnet_model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

class_names = ['Diabetic retinopathy', 'Normal', 'Glaucoma', 'Cataract']

# Set up paths (works in Codespaces)
BASE_DIR = Path(__file__).parent.parent
STATIC_DIR = BASE_DIR / 'static'
XAI_DIR = STATIC_DIR / 'xai'
UPLOAD_DIR = BASE_DIR / 'uploads'

for directory in [STATIC_DIR, XAI_DIR, UPLOAD_DIR]:
    directory.mkdir(exist_ok=True)

def predict_disease(image_path):
    """Predict eye disease from fundus image"""
    img = load_img(image_path, target_size=(224, 224))
    img_array = img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    features = resnet_model.predict(img_array, verbose=0)
    features = features.flatten()
    prediction = model.predict(features.reshape(1, -1))
    return class_names[int(prediction[0])]

def show_lime_explanation(image_path):
    try:
        # Load image
        img = load_img(image_path, target_size=(224, 224))
        img_array = img_to_array(img)
        
        # Corrected prediction function
        def predict_fn(images):
            processed = preprocess_input(images.copy())
            features = resnet_model.predict(processed, verbose=0)
            
            # Reshape features and get predictions
            predictions = model.predict(features.reshape(features.shape[0], -1))
            
            # Ensure 2D output (samples × classes)
            if predictions.ndim == 1:
                predictions = predictions.reshape(-1, 1)
            return predictions

        explainer = lime_image.LimeImageExplainer()
        explanation = explainer.explain_instance(
            img_array.astype('double'),
            predict_fn,
            top_labels=1,
            hide_color=0,
            num_samples=100
        )

        temp, mask = explanation.get_image_and_mask(
            explanation.top_labels[0],
            positive_only=True,
            num_features=3,
            hide_rest=True
        )
        
        output_path = XAI_DIR / f"lime_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.figure(figsize=(6,6))
        plt.imshow(mark_boundaries(temp, mask))
        plt.axis('off')
        plt.savefig(output_path, bbox_inches='tight', dpi=100)
        plt.close()
        
        return f"xai/{output_path.name}"

    except Exception as e:
        print(f"LIME Error: {str(e)}")
        traceback.print_exc()
        return None

def show_grad_cam_explanation(image_path):
    try:
        img = load_img(image_path, target_size=(224, 224))
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array.copy())

        last_conv_layer = resnet_model.get_layer('conv5_block3_out')
        
        grad_model = tf.keras.models.Model(
            inputs=resnet_model.input,
            outputs=[last_conv_layer.output, resnet_model.output]
        )

        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(img_array)
            
            if len(predictions.shape) == 2:
                loss = predictions[:, tf.argmax(predictions[0])]
            else:  # Handle other output types
                loss = tf.reduce_mean(predictions, axis=[1, 2])

        grads = tape.gradient(loss, conv_outputs)
        if grads is None:
            raise ValueError("Gradients could not be computed")
            
        grads = grads[0] 
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

        heatmap = tf.reduce_sum(conv_outputs[0] * pooled_grads, axis=-1)
        heatmap = np.maximum(heatmap, 0)
        max_val = np.max(heatmap)
        if max_val > 0:
            heatmap /= max_val

        img = load_img(image_path)
        img = img_to_array(img)
        
        heatmap = np.uint8(255 * heatmap)
        
        jet = plt.cm.get_cmap("jet")
        
        jet_colors = jet(np.arange(256))[:, :3]
        jet_heatmap = jet_colors[heatmap]
        
        jet_heatmap = tf.keras.preprocessing.image.array_to_img(jet_heatmap)
        jet_heatmap = jet_heatmap.resize((img.shape[1], img.shape[0]))
        jet_heatmap = tf.keras.preprocessing.image.img_to_array(jet_heatmap)
        
        superimposed_img = jet_heatmap * 0.4 + img * 0.6
        superimposed_img = tf.keras.preprocessing.image.array_to_img(superimposed_img)

        output_path = XAI_DIR / f"gradcam_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        superimposed_img.save(output_path)
        
        return f"xai/{output_path.name}"

    except Exception as e:
        print(f"Grad-CAM Error: {str(e)}")
        traceback.print_exc()
        return None

@image_bp.route('/predict', methods=['POST'])
def predict():
    """Endpoint for disease prediction"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    temp_path = UPLOAD_DIR / 'temp_upload.png'
    file.save(temp_path)
    try:
        disease = predict_disease(temp_path)
        return jsonify({'predicted_disease': disease})
    finally:
        if temp_path.exists():
            temp_path.unlink()

@image_bp.route('/lime', methods=['POST'])
def lime():
    """Endpoint for LIME explanation"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    file = request.files['file']
    temp_path = UPLOAD_DIR / 'temp_lime.png'
    file.save(temp_path)
    
    try:
        relative_path = show_lime_explanation(temp_path)
        if not relative_path:
            return jsonify({'error': 'Failed to generate explanation'}), 500
            
        return jsonify({'lime_url': f"/static/{relative_path}"})
    finally:
        if temp_path.exists():
            temp_path.unlink()

@image_bp.route('/gradcam', methods=['POST'])
def gradcam():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        # Save with unique name
        temp_path = UPLOAD_DIR / f"gradcam_temp_{datetime.now().strftime('%f')}.png"
        file.save(temp_path)

        # Process with timeout
        try:
            relative_path = show_grad_cam_explanation(temp_path)
            if not relative_path:
                return jsonify({'error': 'Grad-CAM processing failed'}), 500
                
            return jsonify({'gradcam_url': f"/static/{relative_path}"})
        finally:
            if temp_path.exists():
                temp_path.unlink()

    except Exception as e:
        print(f"Endpoint Error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
        