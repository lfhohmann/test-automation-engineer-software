import unittest

from flask import Flask

from app import app

SAMPLES = 10_000


def base_test(test_case: unittest.TestCase, app: Flask, has_defect: bool, low_lighting: bool) -> None:
    """Base code to be used by all tests"""

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

        # Print test name and its parameters.
        print(f"\n{test_case.__class__.__name__} -> has_defect: {has_defect}, low_lighting: {low_lighting}")

        # Init variable to store the number of tests that passed.
        passed = [1 for r in responses if r.json["has_defect"] == has_defect]

        # Print the number of tests that passed and their accuracy.
        print(f"\tPassed: {len(passed)} out of {SAMPLES} tests.")
        print(f"\tAccuracy: {(len(passed)/SAMPLES)*100:.2f}%")

        # Print a PASS or FAIL message based on whether all tests passed.
        if sum(passed) == SAMPLES:
            print(f"\t\tPASS")
        else:
            print(f"\t\tFAIL")

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


if __name__ == "__main__":
    unittest.main()
