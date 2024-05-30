from uuid import uuid4

from flask import Flask, jsonify, request
from flask_cors import CORS

from components import AISystemMock, CameraMock, Database

# Instantiate the Flask app.
app = Flask(__name__)
CORS(app)

# Initialize the camera, AI system and database.
camera = CameraMock()
ai_system = AISystemMock()
database = Database("test_results.db")


@app.route("/capture_image", methods=["POST"])
def capture_image():
    """POST route to capture the image and predict the result"""

    # Extract requests data.
    data = request.json
    has_defect = data.get("has_defect", False)
    low_lighting = data.get("low_lighting", False)

    # Simulate a captured image.
    image = camera.capture(has_defect, low_lighting)
    image_uuid = uuid4().hex

    # Predict defect.
    defect_present = ai_system.predict_cnn(image)
    database.log_result(image_uuid, defect_present)

    # Return the prediction and it's UUID.
    return jsonify(has_defect=defect_present, prediction_UUID=uuid4().hex)


@app.route("/shutdown", methods=["POST"])
def shutdown():
    """POST route to shutdown the server"""

    # Close the database connection.
    database.close()

    return "Server shutting down..."


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
