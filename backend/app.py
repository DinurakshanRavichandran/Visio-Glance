from flask import Flask, jsonify
from flask_cors import CORS
from api.auth import auth_bp
from routes import bp  # Import the routes Blueprint
from api.Fundus_image import image_bp

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Define a route for the root URL
@app.route("/")
def home():
    return jsonify({"message": "Welcome to Visio-Glance Backend!"})

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')  # Authentication routes
app.register_blueprint(bp)  # Image processing routes
app.register_blueprint(image_bp, url_prefix='/api/image')  # Image processing routes

if __name__ == '__main__':
    app.run(debug=True)