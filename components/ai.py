import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model


class AISystemMock:
    def __init__(self, threshold=145):
        self.threshold = threshold
        self.cnn_model = load_model("components/cnn_model.keras")

    def predict(self, image):
        """Predict if the image contains a defect using a simple threshold"""

        # Convert image to numpy array and check if any pixel is above
        # threshold.
        image_array = np.array(image)
        defect_present = np.any(image_array >= self.threshold)

        return defect_present

    def predict_cnn(self, image: Image) -> bool:
        """Predict if the image contains a defect using a cnn"""

        # Reshape image and scale it to the range [0, 1].
        image_data = np.array(image).reshape((1, 100, 100, 1)) / 255.0

        # Predict if the image contains a defect or not.
        results = self.cnn_model.predict(image_data, verbose=0)
        result = np.argmax(results[0])

        # Return the result as bool.
        return bool(result)
