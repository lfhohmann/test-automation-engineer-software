import json

import pytest
from playwright.async_api import async_playwright

from components import Database


@pytest.mark.asyncio
async def test_capture_request():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Go to the frontend page.
        await page.goto("http://localhost:3000")

        # Expected POST data.
        expected_post_data = {"with_defect": True, "low_lighting": True}

        # Intercept network requests.
        async def handle_request(route, request):
            assert request.method == "POST", f"Expected POST request, got {request.method}"
            assert request.url == "http://127.0.0.1:8000/capture_image", f"Wrong url, got {request.url}"

            if request.method == "POST" and request.url == "http://127.0.0.1:8000/capture_image":
                post_data = json.loads(request.post_data)
                assert post_data == expected_post_data, f"Post data does not match: {post_data}"

                print("\nCAPTURE POST request made to the backend with expected data.")

            await route.continue_()

        await page.route("**/*", handle_request)

        # Use expect_response as a context manager.
        async with page.expect_response("http://127.0.0.1:8000/capture_image") as response:

            # Click the button using its inner text.
            await page.locator("text=Capture").click()

            # Extract response data.
            response = await response.value
            response = await response.text()
            response = json.loads(response)

        # Wait for a while to ensure the request is made.
        await page.wait_for_timeout(5000)

        # Close browser
        await browser.close()

        # Check if the image capture and prediction were logged in the DB.
        database = Database("test_results.db")
        entries = database.read_results()

        # Try to get the last entry from the DB.
        try:
            db_id, image_id, defect_present = entries[-1]
        except IndexError:
            assert False, "No results found in the database."

        # Check if the image ID matches the response from the backend.
        assert image_id == response["image_id"]


@pytest.mark.asyncio
async def test_shutdown_request():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Go to the frontend page.
        await page.goto("http://localhost:3000")

        # Intercept network requests.
        async def handle_request(route, request):
            assert request.method == "POST", f"Expected POST request, got {request.method}"
            assert request.url == "http://127.0.0.1:8000/shutdown", f"Wrong url, got {request.url}"

            if request.method == "POST" and request.url == "http://127.0.0.1:8000/shutdown":
                print("\nSHUTDOWN POST request made to the backend.")

            await route.continue_()

        await page.route("**/*", handle_request)

        # Click the button using its inner text.
        await page.locator(f"text=Shutdown").click()

        # Wait for a while to ensure the request is made.
        await page.wait_for_timeout(5000)

        # Close browser.
        await browser.close()


# Running the test using pytest
if __name__ == "__main__":
    pytest.main(["-s", "playwright_integration_test.py"])
