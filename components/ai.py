import numpy as np
from PIL import Image


class AISystemMock:
    def __init__(self, threshold: int = 145) -> None:
        self.threshold = threshold

    def predict(self, image: Image) -> bool:
        """Predict if the image contains a defect or not"""

        image_array = np.array(image)
        defect_present = np.any(image_array >= self.threshold)

        return defect_present
