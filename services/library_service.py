"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books, get_patron_borrowed_books
)

def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    
    Args:
        title: Book title (max 200 chars)
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Input validation
    if not title or not title.strip():
        return False, "Title is required."
    
    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."
    
    if not author or not author.strip():
        return False, "Author is required."
    
    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."
    
    if len(isbn) != 13 or not isbn.isdigit():
        return False, "ISBN must be exactly 13 digits."
    
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."
    
    # Check for duplicate ISBN
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."
    
    # Insert new book
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    
    if current_borrowed >= 5:
        return False, "You have reached the maximum borrowing limit of 5 books."
    
    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'

def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Process book return by a patron.
    
    TODO: Implement R4 as per requirements
    """
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    borrowed_books = get_patron_borrowed_books(patron_id)
    
    borrow_record = None
    for record in borrowed_books:
        if record['book_id'] == book_id:
            borrow_record = record
            break
    
    if not borrow_record:
        return False, "No borrowing record found for this patron and book."
    
    return_date = datetime.now()
    success = update_borrow_record_return_date(patron_id, book_id, return_date)
    if not success:
        return False, "Database error occurred while updating return date."
    
    availability_success = update_book_availability(book_id, 1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully returned "{book["title"]}". Return date: {return_date.strftime("%Y-%m-%d")}.'

def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    """
    Calculate late fees for a specific book.
    
    TODO: Implement R5 as per requirements 
    
    
    return { // return the calculated values
        'fee_amount': 0.00,
        'days_overdue': 0,
        'status': 'Late fee calculation not implemented'
    }
    """
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Invalid patron ID. Must be exactly 6 digits.'
        }
    
    book = get_book_by_id(book_id)
    if not book:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Book not found.'
        }
    
    borrowed_books = get_patron_borrowed_books(patron_id)
    
    borrow_record = None
    for record in borrowed_books:
        if record['book_id'] == book_id:
            borrow_record = record
            break
    
    if not borrow_record:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'No active borrowing record found.'
        }
    
    due_date = borrow_record['due_date']
    current_date = datetime.now()
    days_overdue = max(0, (current_date - due_date).days)
    
    fee_amount = 0.00
    if days_overdue > 0:
        if days_overdue <= 7:
            fee_amount = days_overdue * 0.50
        else:
            fee_amount = (7 * 0.50) + ((days_overdue - 7) * 1.00)
        
        fee_amount = min(fee_amount, 15.00)
    
    return {
        'fee_amount': round(fee_amount, 2),
        'days_overdue': days_overdue,
        'status': 'Success' if days_overdue == 0 else f'Overdue by {days_overdue} days'
    }

def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Search for books in the catalog.
    
    TODO: Implement R6 as per requirements
    """
    if not search_term or not search_term.strip():
        return []
    
    valid_types = ['title', 'author', 'isbn']
    if search_type not in valid_types:
        return []
    
    books = get_all_books()
    results = []
    
    search_term_lower = search_term.strip().lower()
    
    for book in books:
        if search_type == 'title':
            if search_term_lower in book['title'].lower():
                results.append(book)
        elif search_type == 'author':
            if search_term_lower in book['author'].lower():
                results.append(book)
        elif search_type == 'isbn':
            if book['isbn'] == search_term.strip():
                results.append(book)
    
    return results

def get_patron_status_report(patron_id: str) -> Dict:
    """
    Get status report for a patron.
    
    TODO: Implement R7 as per requirements
    """
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {
            'error': 'Invalid patron ID. Must be exactly 6 digits.',
            'currently_borrowed_books': [],
            'total_borrowed': 0,
            'total_late_fees': 0.00,
            'borrowing_history': []
        }
    
    borrowed_books = get_patron_borrowed_books(patron_id)
    
    total_late_fees = 0.00
    for record in borrowed_books:
        if record['is_overdue']:
            days_overdue = (datetime.now() - record['due_date']).days
            if days_overdue <= 7:
                late_fee = days_overdue * 0.50
            else:
                late_fee = (7 * 0.50) + ((days_overdue - 7) * 1.00)
            late_fee = min(late_fee, 15.00)
            total_late_fees += late_fee
    
    from database import get_db_connection
    conn = get_db_connection()
    history_records = conn.execute('''
        SELECT br.*, b.title, b.author 
        FROM borrow_records br 
        JOIN books b ON br.book_id = b.id 
        WHERE br.patron_id = ?
        ORDER BY br.borrow_date DESC
    ''', (patron_id,)).fetchall()
    conn.close()
    
    borrowing_history = []
    for record in history_records:
        borrowing_history.append({
            'book_id': record['book_id'],
            'title': record['title'],
            'author': record['author'],
            'borrow_date': record['borrow_date'],
            'due_date': record['due_date'],
            'return_date': record['return_date']
        })
    
    return {
        'currently_borrowed_books': borrowed_books,
        'total_borrowed': len(borrowed_books),
        'total_late_fees': round(total_late_fees, 2),
        'borrowing_history': borrowing_history
    }

from services.payment_service import PaymentGateway

def pay_late_fees(patron_id: str, book_id: int, payment_gateway: PaymentGateway):
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID"
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found"
    r = calculate_late_fee_for_book(patron_id, book_id)
    fee = float(r.get("fee_amount", 0))
    days = int(r.get("days_overdue", 0))
    if r.get("status") in {"Book not found.", "No active borrowing record found."}:
        return False, r.get("status")
    if fee <= 0:
        return True, "No late fees"
    try:
        resp = payment_gateway.process_payment(patron_id, fee)
    except Exception as e:
        return False, f"Payment exception: {e}"
    if not resp or resp.get("status") != "success":
        return False, (resp.get("reason") if isinstance(resp, dict) else "Payment failed")
    return True, {"transaction_id": resp["transaction_id"], "charged": round(fee, 2), "days_overdue": days}

def refund_late_fee_payment(transaction_id: str, amount: float, payment_gateway: PaymentGateway):
    if not transaction_id or not isinstance(transaction_id, str):
        return False, "Invalid transaction"
    try:
        amt = float(amount)
    except Exception:
        return False, "Invalid amount"
    if amt <= 0 or amt > 15.0:
        return False, "Amount must be >0 and ≤15"
    try:
        resp = payment_gateway.refund_payment(transaction_id, amt)
    except Exception as e:
        return False, f"Refund exception: {e}"
    if not resp or resp.get("status") != "refunded":
        return False, (resp.get("reason") if isinstance(resp, dict) else "Refund failed")
    return True, {"refund_id": resp["refund_id"], "refunded": round(amt, 2)}
