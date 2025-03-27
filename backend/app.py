from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from routes import bp  # Existing blueprint
from api.fundus_image import image_bp  # Image blueprint
from api.ml.chatbot import chat_bp  # New chat blueprint


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
    return send_from_directory('static', filename)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Register blueprints
app.register_blueprint(bp)
app.register_blueprint(image_bp, url_prefix='/api/image')
app.register_blueprint(chat_bp, url_prefix='/api/ml')  # Register chat blueprint

if __name__ == '__main__':
    app.run(debug=True)