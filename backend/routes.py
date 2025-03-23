from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from api.ml.oct import analyze_image  # Import your analysis function

# Define Blueprint for routes
bp = Blueprint("routes", __name__)

# Configuration
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
#STATIC_FOLDER = os.path.join(os.path.dirname(__file__), "static")
STATIC_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")


# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route("/analyze", methods=["POST"])
def analyze_endpoint():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    file = request.files["image"]
    
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file format"}), 400

    try:
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(temp_path)

        # Perform complete analysis
        analysis_result = analyze_image(temp_path)

        # Convert local paths to server-accessible URLs
        response = {
        "classification": analysis_result["classification"],
        "explanations": {
            # Add full URL with port
            "lime": f"http://localhost:5000/static/xai/{os.path.basename(analysis_result['explanations']['lime_image'])}",
            "shap": f"http://localhost:5000/static/xai/{os.path.basename(analysis_result['explanations']['shap_image'])}"
        }
    }

        return jsonify(response)

    except Exception as e:
        print("Error during processing:", str(e))  # Log error message
        traceback.print_exc()  # Print full error traceback
        return jsonify({"error": str(e)}), 500

    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

@bp.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory(STATIC_FOLDER, filename)