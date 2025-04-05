from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from routes import bp  # Existing blueprint
from api.fundus_image import image_bp  # Image blueprint
from api.ml.chatbot import chat_bp  # New chat blueprint
from api.auth import auth_bp # Authentication blueprint

from api.ml.symptoms import symptoms_bp



app = Flask(__name__)
CORS(app, supports_credentials=True)  # Global CORS

# Define root route
@app.route("/")
def home():
    return jsonify({"message": "Welcome to Visio-Glance Backend!"})

# Apply CORS only to defined blueprints
CORS(bp, supports_credentials=True)
CORS(image_bp, supports_credentials=True)
CORS(chat_bp, supports_credentials=True)

# Static files route
@app.route('/static/<path:filename>')
def static_files(filename):
    try:
        response = send_from_directory('static', filename)
        # Add CORS headers to static files if needed
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except FileNotFoundError:
        return "File not found", 404
    except Exception as e:
        return str(e), 400
    
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Register blueprints
app.register_blueprint(bp)
app.register_blueprint(image_bp, url_prefix='/api/image')
app.register_blueprint(chat_bp, url_prefix='/api/ml')  # Register chat blueprint
app.register_blueprint(auth_bp, url_prefix='/auth')  # Register auth blueprint
app.register_blueprint(symptoms_bp, url_prefix="/api/symptoms")


if __name__ == '__main__':
    app.run(debug=True)