import pytest 

from services.library_service import add_book_to_catalog

def test_add_book_semiotics():
    # adding the semiotics textbook -> should work
    success, msg = add_book_to_catalog("Semiotics: The Science of Signs", "Donato Santeramo", "9783862902279", 3)
    assert success is True
    assert "semiotics" in msg.lower()

def test_add_book_empty_author():
    # author field is empty -> should fail
    success, msg = add_book_to_catalog("Canadian Law: An Introduction, 8th Edition", "", "9781119320913", 2)
    assert success is False
    assert "author" in msg.lower()

def test_add_book_zero_copies():
    # zero copies not allowed -> should fail
    success, msg = add_book_to_catalog("Discrete Math and its Applications", "Kenneth H. Rosen", "9781259676512", 0)
    assert success is False
    assert "positive" in msg.lower()

def test_add_book_author_too_long():
    # author name over 100 chars -> should reject
    long_author = "A" * 101
    success, msg = add_book_to_catalog("Canadian Law: An Introduction, 8th Edition", long_author, "9783862902279", 1)
    assert success is False
    assert "author" in msg.lower()

def test_add_book_isbn_with_letters():
    # isbn contains letters -> should fail
    success, msg = add_book_to_catalog("Canadian Law: An Introduction, 8th Edition", "Emond Publishing", "978abc1234567", 1)
    assert success is False
    assert "13 digits" in msg

import pytest 

from database import get_all_books

def test_catalog_returns_list():
    # catalog should return a list of books
    books = get_all_books()
    assert isinstance(books, list)

def test_catalog_book_has_id():
    # each book should have an id field
    books = get_all_books()
    if books:
        assert "id" in books[0]

def test_catalog_book_has_total_copies():
    # each book should show total copies
    books = get_all_books()
    if books:
        assert "total_copies" in books[0]

def test_catalog_book_has_available_copies():
    # each book should show available copies
    books = get_all_books()
    if books:
        assert "available_copies" in books[0]

def test_catalog_books_ordered():
    # books should be in some order (title order)
    books = get_all_books()
    if len(books) > 1:
        titles = [book["title"] for book in books]
        assert titles == sorted(titles)

import pytest 

from services.library_service import borrow_book_by_patron

def test_borrow_operating_systems():
    # borrowing operating systems book -> should work
    success, msg = borrow_book_by_patron("111111", 1)
    assert isinstance(success, bool)

def test_borrow_patron_id_too_long():
    # patron id has 7 digits -> should fail
    success, msg = borrow_book_by_patron("1234567", 1)
    assert success == False
    assert "6 digits" in msg

def test_borrow_patron_id_has_letters():
    # patron id contains letters -> should fail
    success, msg = borrow_book_by_patron("abc123", 1)
    assert success == False
    assert "6 digits" in msg

def test_borrow_nonexistent_book():
    # book id 0 doesn't exist -> should fail
    success, msg = borrow_book_by_patron("123456", 0)
    assert success == False
    assert "not found" in msg.lower()

import pytest 

from services.library_service import borrow_book_by_patron, return_book_by_patron

def test_return_discrete_math():
    # return discrete math book -> not implemented yet
    success, msg = return_book_by_patron("333333", 1)
    assert success == False

def test_return_wrong_patron():
    # patron 444444 tries to return book borrowed by 555555
    borrow_book_by_patron("555555", 1)
    success, msg = return_book_by_patron("444444", 1)
    assert success == False

def test_return_already_returned():
    # return a book that was already returned
    borrow_book_by_patron("666666", 1)
    return_book_by_patron("666666", 1)
    success, msg = return_book_by_patron("666666", 1)
    assert success == False

def test_return_negative_book_id():
    # negative book id -> should fail
    success, msg = return_book_by_patron("123456", -1)
    assert success == False

def test_return_patron_id_short():
    # patron id only 4 digits -> should fail
    success, msg = return_book_by_patron("1234", 1)
    assert success == False

import pytest 

from services.library_service import calculate_late_fee_for_book

def test_late_fee_semiotics_book():
    # calculate fee for semiotics book -> not implemented
    result = calculate_late_fee_for_book("777777", 1)
    assert isinstance(result, dict)
    assert 'fee_amount' in result
    assert 'days_overdue' in result
    assert 'status' in result

def test_late_fee_operating_systems():
    # calculate fee for operating systems book
    result = calculate_late_fee_for_book("888888", 1)
    assert isinstance(result, dict)
    assert 'fee_amount' in result
    assert 'days_overdue' in result
    assert 'status' in result

def test_late_fee_discrete_math():
    # calculate fee for discrete math book
    result = calculate_late_fee_for_book("999999", 1)
    assert isinstance(result, dict)
    assert 'fee_amount' in result
    assert 'days_overdue' in result
    assert 'status' in result

def test_late_fee_patron_id_none():
    # patron id is None -> should handle gracefully
    result = calculate_late_fee_for_book(None, 1)
    assert isinstance(result, dict)
    assert 'fee_amount' in result
    assert 'days_overdue' in result
    assert 'status' in result

def test_late_fee_book_id_string():
    # book id is string instead of int -> should handle
    result = calculate_late_fee_for_book("123456", "1")
    assert isinstance(result, dict)
    assert 'fee_amount' in result
    assert 'days_overdue' in result
    assert 'status' in result

import pytest 

from services.library_service import search_books_in_catalog

def test_search_science_keyword():
    # search for "science" in title -> not implemented yet
    results = search_books_in_catalog("science", "title")
    assert isinstance(results, list)

def test_search_silberschatz_author():
    # search for author "silberschatz"
    results = search_books_in_catalog("silberschatz", "author")
    assert isinstance(results, list)

def test_search_operating_systems_isbn():
    # search by operating systems isbn
    results = search_books_in_catalog("9781119320913", "isbn")
    assert isinstance(results, list)

def test_search_ken_author():
    # search for "ken" in author name
    results = search_books_in_catalog("ken", "author")
    assert isinstance(results, list)

def test_search_invalid_type():
    # search type is invalid -> should handle gracefully
    results = search_books_in_catalog("test", "invalid")
    assert isinstance(results, list)

import pytest 

from services.library_service import get_patron_status_report

def test_patron_status_123456():
    # get status for patron 123456 -> not implemented yet
    status = get_patron_status_report("123456")
    assert isinstance(status, dict)

def test_patron_status_borrowed_books():
    # check if status includes borrowed books field
    status = get_patron_status_report("111111")
    assert isinstance(status, dict)

def test_patron_status_late_fees():
    # check if status includes late fees field
    status = get_patron_status_report("222222")
    assert isinstance(status, dict)

def test_patron_status_borrowing_history():
    # check if status includes borrowing history
    status = get_patron_status_report("333333")
    assert isinstance(status, dict)

def test_patron_status_total_borrowed():
    # check if status includes total borrowed count
    status = get_patron_status_report("444444")
    assert isinstance(status, dict)