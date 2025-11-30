import os
import re
import uuid
import threading
import time
import sys

import pytest
from playwright.sync_api import sync_playwright, Page, expect

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app


BASE_URL = os.getenv("APP_BASE_URL", "http://127.0.0.1:5000")
ADD_BOOK_URL = f"{BASE_URL}/add_book"
CATALOG_URL = f"{BASE_URL}/catalog"

BORROW_SUCCESS_PATTERN = re.compile(r"success", re.IGNORECASE)


def run_server():
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)


@pytest.fixture(scope="session", autouse=True)
def start_flask_app():
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    time.sleep(2)


@pytest.fixture
def browser_page():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        yield page
        browser.close()


def make_unique_book_data():
    suffix = uuid.uuid4().hex[:6]
    isbn_suffix_int = uuid.uuid4().int % 10**10
    isbn_13_digits = "978" + f"{isbn_suffix_int:010d}"

    return {
        "title": f"Test Book {suffix}",
        "author": f"Test Author {suffix}",
        "isbn": isbn_13_digits,
        "total_copies": "3",
    }


def add_book_through_ui(page: Page, book: dict):
    page.goto(ADD_BOOK_URL)
    page.locator('input[name="title"]').fill(book["title"])
    page.locator('input[name="author"]').fill(book["author"])
    page.locator('input[name="isbn"]').fill(book["isbn"])
    page.locator('input[name="total_copies"]').fill(book["total_copies"])

    with page.expect_navigation(url=re.compile(r".*/catalog$")):
        page.locator('button[type="submit"]').click()


def assert_book_visible_in_catalog(page: Page, book: dict):
    page.goto(CATALOG_URL)
    expect(page).to_have_url(re.compile(r".*/catalog$"))

    title_locator = page.get_by_text(book["title"])
    expect(title_locator).to_be_visible()


def borrow_book_from_catalog(page: Page, book: dict, patron_id: str):
    page.goto(CATALOG_URL)
    expect(page).to_have_url(re.compile(r".*/catalog$"))

    title_locator = page.get_by_text(book["title"])
    expect(title_locator).to_be_visible()
    row = title_locator.locator("xpath=ancestor::tr[1]")
    row = row.first

    row.locator('input[name="patron_id"]').fill(patron_id)

    with page.expect_navigation(url=re.compile(r".*/catalog$")):
        row.get_by_text(re.compile(r"Borrow", re.IGNORECASE)).click()


def assert_borrow_confirmation_visible(page: Page):
    confirmation = page.get_by_text(BORROW_SUCCESS_PATTERN)
    expect(confirmation).to_be_visible()


@pytest.mark.e2e
def test_add_new_book_appears_in_catalog(browser_page: Page):
    book = make_unique_book_data()
    add_book_through_ui(browser_page, book)
    assert_book_visible_in_catalog(browser_page, book)


@pytest.mark.e2e
def test_borrow_book_flow_shows_confirmation_message(browser_page: Page):
    book = make_unique_book_data()
    patron_id = "123456"

    add_book_through_ui(browser_page, book)
    assert_book_visible_in_catalog(browser_page, book)
    borrow_book_from_catalog(browser_page, book, patron_id)
    assert_borrow_confirmation_visible(browser_page)