from unittest.mock import Mock
from services.library_service import pay_late_fees
from services.payment_service import PaymentGateway

FAKE_BOOK = {"id": 1, "title": "T", "author": "A", "isbn": "1234567890123", "available_copies": 1}

def test_pay_late_fees_stub_success(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value=FAKE_BOOK)
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 4.0, "days_overdue": 3, "status": "Success"})
    pg = Mock(spec=PaymentGateway)
    pg.process_payment.return_value = {"status": "success", "transaction_id": "TXN123456400"}
    ok, p = pay_late_fees("123456", 1, pg)
    assert ok and p["transaction_id"] == "TXN123456400" and p["charged"] == 4.0 and p["days_overdue"] == 3

def test_pay_late_fees_stub_zero_fee(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value=FAKE_BOOK)
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 0.0, "days_overdue": 0, "status": "Success"})
    pg = Mock(spec=PaymentGateway)
    ok, msg = pay_late_fees("123456", 1, pg)
    assert ok and msg == "No late fees"
    pg.process_payment.assert_not_called()
