from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from routes import bp  # Import the routes Blueprint
from api.fundus_image import image_bp

app = Flask(__name__)
CORS(app, supports_credentials=True)  # Enable CORS for all routes

# Define a route for the root URL
@app.route("/")
def home():
    return jsonify({"message": "Welcome to Visio-Glance Backend!"})

 
CORS(auth_bp, supports_credentials=True)
CORS(bp, supports_credentials=True)
CORS(image_bp, supports_credentials=True)

# Route to serve static files
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')


# Register Blueprints
app.register_blueprint(bp)  # Image processing routes
app.register_blueprint(image_bp, url_prefix='/api/image')  # Image processing routes

if __name__ == '__main__':
    app.run(debug=True)