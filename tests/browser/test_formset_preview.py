from collections.abc import Iterator
from typing import TYPE_CHECKING

import pytest
from django.urls import reverse

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page
    from playwright.sync_api._generated import LocatorAssertions

pytestmark = pytest.mark.browser


@pytest.fixture
def page(preview_server: str) -> Iterator["Page"]:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        errors: list[str] = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        response = page.goto(f"{preview_server}{reverse('formset_preview')}")
        assert response is not None and response.ok
        page.wait_for_function("window.daisyForms !== undefined")
        try:
            yield page
        finally:
            browser.close()
        assert errors == []


def expect(locator: "Locator") -> "LocatorAssertions":
    from playwright.sync_api import expect as playwright_expect

    return playwright_expect(locator)


def total(page: "Page", prefix: str) -> str:
    return page.locator(f'input[name="{prefix}-TOTAL_FORMS"]').input_value()


def test_add_appends_a_numbered_row_and_moves_focus(page: "Page") -> None:
    lines = page.locator("#lines")
    lines.get_by_role("button", name="Add another").click()

    assert total(page, "lines") == "3"
    assert page.evaluate("document.activeElement.id") == "id_lines-2-name"
    expect(lines.get_by_role("status")).to_have_text("Row added.")


def test_add_is_disabled_at_max_num(page: "Page") -> None:
    add = page.locator("#lines").get_by_role("button", name="Add another")
    add.click()

    assert add.is_disabled()


def test_remove_is_disabled_at_min_num(page: "Page") -> None:
    lines = page.locator("#lines")
    lines.get_by_role("button", name="Remove 2").click()

    assert total(page, "lines") == "1"
    assert lines.get_by_role("button", name="Remove 1").is_disabled()


def test_removing_a_new_row_renumbers_later_rows(page: "Page") -> None:
    lines = page.locator("#lines")
    lines.get_by_role("button", name="Add another").click()
    page.fill("#id_lines-2-name", "third")
    lines.get_by_role("button", name="Remove 2").click()

    assert total(page, "lines") == "2"
    assert page.locator("#id_lines-1-name").input_value() == "third"
    assert page.locator('label[for="id_lines-1-name"]').count() == 1
    assert page.evaluate("document.activeElement.getAttribute('aria-label')") == (
        "Remove 2"
    )


def test_removing_a_saved_row_marks_delete_and_can_be_undone(page: "Page") -> None:
    saved = page.locator("#saved")
    delete = page.locator('input[name="saved-0-DELETE"]')

    assert not delete.is_visible()
    saved.get_by_role("button", name="Remove 1").click()

    assert delete.is_checked()
    assert total(page, "saved") == "2"
    assert page.locator("#id_saved-0-name").evaluate(
        "el => el.closest('[inert]') !== null"
    )
    expect(saved.get_by_role("status")).to_have_text("Row removed.")

    saved.get_by_role("button", name="Undo remove 1").click()

    assert not delete.is_checked()
    expect(saved.get_by_role("status")).to_have_text("Row restored.")


def test_deleted_saved_row_is_submitted(page: "Page") -> None:
    page.locator("#saved").get_by_role("button", name="Remove 2").click()
    page.get_by_role("button", name="Submit").click()

    assert page.locator('input[name="saved-1-DELETE"]').is_checked()


def test_table_cells_are_labelled_by_their_headers(page: "Page") -> None:
    name = page.get_by_role("textbox", name="Name").first

    assert name.get_attribute("id") == "id_saved-0-name"


def test_formsets_inserted_by_htmx_are_initialised(page: "Page") -> None:
    page.evaluate(
        """() => {
            const target = document.querySelector("#swap-target");
            target.append(document.querySelector("#swap-source").content.cloneNode(true));
            target.dispatchEvent(new CustomEvent("htmx:load", { bubbles: true }));
        }"""
    )
    swapped = page.locator("#swap-target")
    swapped.get_by_role("button", name="Add another").click()

    assert total(page, "swapped") == "3"


def test_without_javascript_the_delete_checkbox_is_used(preview_server: str) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        try:
            page.goto(f"{preview_server}{reverse('formset_preview')}?nojs=1")
            delete = page.locator('input[name="saved-0-DELETE"]')

            assert delete.is_visible()
            assert page.get_by_role("button", name="Add another").count() == 0
        finally:
            browser.close()
