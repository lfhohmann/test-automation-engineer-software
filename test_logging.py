import unittest
from unittest.mock import MagicMock, patch

from app import app, database


class TestLogging(unittest.TestCase):
    """Check if the logging in the database works as expected."""

    # Setup constants.
    MOCK_UUID = "04dfc63c68f443f3b4f3f241f06b9e68"
    MOCK_PREDICT = False

    @patch("app.uuid4")
    @patch("app.ai_system.predict")
    def test_logging_results(self, mock_predict, mock_uuid):

        # Mock both uuid4 and predict functions.
        mock_uuid.return_value = MagicMock(hex=self.MOCK_UUID)
        mock_predict.return_value = MagicMock(item=lambda: self.MOCK_PREDICT)

        # Init test client and post request to capture an image.
        with app.test_client() as client:
            response = client.post("/capture_image", json={"with_defect": False, "low_lighting": False})
            self.assertEqual(response.status_code, 200)  # Assert response code.

            # Attempt to read the database.
            try:
                _, image_id, defect_present = database.read_results()[-1]
            except IndexError:
                self.fail("No results found in the database.")

            # Assert that the image id and defect prediction are correct.
            self.assertEqual(image_id, self.MOCK_UUID)
            self.assertEqual(defect_present, int(self.MOCK_PREDICT))


if __name__ == "__main__":
    unittest.main()
