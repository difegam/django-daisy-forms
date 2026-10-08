import re
from collections.abc import Iterator
from threading import Thread
from wsgiref.simple_server import make_server

import pytest
from django.core.wsgi import get_wsgi_application
from django.urls import reverse


@pytest.fixture
def preview_server() -> Iterator[str]:
    server = make_server("127.0.0.1", 0, get_wsgi_application())
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


@pytest.mark.browser
def test_form_preview_layouts_addons_and_errors(preview_server: str) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 390, "height": 844})
        try:
            response = page.goto(f"{preview_server}{reverse('form_preview')}")
            assert response is not None and response.ok

            email_label = page.locator('label[for="id_email"]')
            email = page.locator("#id_email")
            label_box = email_label.bounding_box()
            input_box = email.bounding_box()
            assert label_box is not None and input_box is not None
            assert label_box["y"] < input_box["y"]

            inline_choices = page.locator("#id_plan")
            assert (
                inline_choices.evaluate(
                    "element => getComputedStyle(element).flexDirection"
                )
                == "row"
            )
            assert (
                inline_choices.evaluate("element => getComputedStyle(element).flexWrap")
                == "wrap"
            )
            checkbox_choices = page.locator("#id_features")
            assert (
                checkbox_choices.evaluate(
                    "element => getComputedStyle(element).flexDirection"
                )
                == "row"
            )

            price = page.locator("#id_price")
            addon_group = price.locator("xpath=..")
            addon_group_class = addon_group.get_attribute("class")
            assert addon_group_class is not None
            assert "join" in addon_group_class.split()
            assert addon_group.locator("span").all_text_contents() == ["$", "USD"]
            price_class = price.get_attribute("class")
            assert price_class is not None
            assert "join-item" in price_class.split()

            page.set_viewport_size({"width": 1280, "height": 900})
            label_box = email_label.bounding_box()
            input_box = email.bounding_box()
            assert label_box is not None and input_box is not None
            horizontal_group = email_label.locator("xpath=..")
            assert (
                horizontal_group.evaluate(
                    "element => getComputedStyle(element).display"
                )
                == "flex"
            )
            assert (
                horizontal_group.evaluate(
                    "element => getComputedStyle(element).flexDirection"
                )
                == "row"
            )
            assert input_box["x"] > label_box["x"]

            page.locator("form").evaluate("form => form.noValidate = true")
            page.get_by_role("button", name="Validate fields").click()
            email = page.locator("#id_email")
            assert email.get_attribute("aria-invalid") == "true"
            describedby = email.get_attribute("aria-describedby")
            assert describedby is not None
            assert re.search(r"id_email_error", describedby)
            assert page.locator("#id_email_error").is_visible()
        finally:
            browser.close()
