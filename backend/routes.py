import os
from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from api.ml.oct import predict_oct
from api.ml.fundus import predict_fundus
from api.ml.octxa import generate_xai_oct
from api.ml.fundusxai import generate_xai_fundus

# Define Blueprint for routes
bp = Blueprint("routes", __name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
XAI_FOLDER = os.path.join(os.path.dirname(__file__), "static", "xai")

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(XAI_FOLDER, exist_ok=True)

# Helper function to check file extension
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to classify an uploaded image
@bp.route("/classify", methods=["POST"])
def classify_image():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    file = request.files["image"]

    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file format"}), 400

    # Save the uploaded image
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    # Determine model type (OCT or Fundus)
    model_type = request.form.get("model_type", "oct")  # Default to OCT
    if model_type not in ["oct", "fundus"]:
        return jsonify({"error": "Invalid model type"}), 400

    try:
        # Predict using the corresponding model
        if model_type == "oct":
            prediction_result = predict_oct(file_path)
            xai_result = generate_xai_oct(file_path)
        else:
            prediction_result = predict_fundus(file_path)
            xai_result = generate_xai_fundus(file_path)

        # Save XAI images to the XAI_FOLDER
        shap_image_path = os.path.join(XAI_FOLDER, f"shap_{filename}")
        lime_image_path = os.path.join(XAI_FOLDER, f"lime_{filename}")

        # Assuming xai_result contains SHAP and LIME images
        xai_result["shap_image"].save(shap_image_path)
        xai_result["lime_image"].save(lime_image_path)

        # Construct response
        response = {
            "prediction": prediction_result["prediction"],
            "confidence": prediction_result["confidence"],
            "shap_image_url": f"/static/xai/shap_{filename}",
            "lime_image_url": f"/static/xai/lime_{filename}"
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Clean up the uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)

# Route to serve XAI images (ONLY ONCE)
@bp.route("/static/xai/<filename>")
def get_xai_image(filename):
    return send_from_directory(XAI_FOLDER, filename)