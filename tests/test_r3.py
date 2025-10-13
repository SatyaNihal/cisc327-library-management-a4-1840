import pytest 

from library_service import borrow_book_by_patron

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