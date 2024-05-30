import time
import unittest

from flask import Flask

from app import app
from components import AISystemMock, CameraMock

SAMPLES = 1000


def base_test(test_case: unittest.TestCase, app: Flask, has_defect: bool, low_lighting: bool) -> None:
    """Base code to be used by all tests"""

    # Start timer.
    start = time.perf_counter()

    # Init test client and perform multiple requests to capture an image.
    with app.test_client() as client:

        # Init variable to keep track of the responses.
        responses = []

        for _ in range(SAMPLES):
            response = client.post(
                "/capture_image",
                json={
                    "has_defect": has_defect,
                    "low_lighting": low_lighting,
                },
            )
            responses.append(response)

    # Stop timer and compute number of samples per second.
    end = time.perf_counter()
    elapsed_time = end - start
    samples_per_second = SAMPLES / elapsed_time

    # Print test name and its parameters.
    print(f"\n{test_case.__class__.__name__} -> has_defect: {has_defect}, low_lighting: {low_lighting}")

    # Init variable to store the number of tests that passed.
    passed = [1 for r in responses if r.json["has_defect"] == has_defect]

    # Print the number of tests that passed and their accuracy.
    print(f"\tTest took: {elapsed_time:.2f}s, performing {samples_per_second:.2f} samples per second")
    print(f"\tPassed: {len(passed)} out of {SAMPLES} tests.")
    print(f"\tAccuracy: {(len(passed)/SAMPLES)*100:.2f}%")

    # Print a PASS or FAIL message based on whether all tests passed.
    if sum(passed) == SAMPLES:
        print(f"\t\tPASS")
    else:
        print(f"\t\tFAIL")

    print(flush=True)

    # Assert that the response code and prediction.
    for response in responses:
        test_case.assertEqual(response.status_code, 200)
        test_case.assertEqual(response.json["has_defect"], has_defect)


class TestDefectDetection(unittest.TestCase):
    def test_no_defect_normal_lighting(self):
        base_test(self, app, has_defect=False, low_lighting=False)

    def test_no_defect_low_lighting(self):
        base_test(self, app, has_defect=False, low_lighting=True)

    def test_has_defect_normal_lighting(self):
        base_test(self, app, has_defect=True, low_lighting=False)

    def test_has_defect_low_lighting(self):
        base_test(self, app, has_defect=True, low_lighting=True)


class TestInferenceSpeed(unittest.TestCase):
    def test_regular_predict(self):

        # Instantiate AI system and camera objects.
        ai_system = AISystemMock()
        camera = CameraMock()

        # Start timer.
        start = time.perf_counter()

        # Perform multiple predictions.
        for _ in range(SAMPLES):
            ai_system.predict(camera.capture(has_defect=True, low_lighting=True))

        # Stop timer and compute number of samples per second.
        end = time.perf_counter()
        elapsed_time = end - start
        samples_per_second = SAMPLES / elapsed_time

        # Print test name and its results.
        print(f"\n{self.__class__.__name__}.{self.test_regular_predict.__name__}()")
        print(f"\tTest took: {elapsed_time:.2f}s, performing {samples_per_second:.2f} samples per second")
        print(flush=True)

    def test_cnn_predict(self):

        # Instantiate AI system and camera objects.
        ai_system = AISystemMock()
        camera = CameraMock()

        # Start timer.
        start = time.perf_counter()

        # Perform multiple predictions.
        for _ in range(SAMPLES):
            ai_system.predict_cnn(camera.capture(has_defect=True, low_lighting=True))

        # Stop timer and compute number of samples per second.
        end = time.perf_counter()
        elapsed_time = end - start
        samples_per_second = SAMPLES / elapsed_time

        # Print test name and its results.
        print(f"\n{self.__class__.__name__}.{self.test_cnn_predict.__name__}()")
        print(f"\tTest took: {elapsed_time:.2f}s, performing {samples_per_second:.2f} samples per second")
        print(flush=True)


if __name__ == "__main__":
    unittest.main()
