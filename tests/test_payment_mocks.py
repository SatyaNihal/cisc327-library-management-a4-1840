from unittest.mock import Mock
from services.library_service import pay_late_fees, refund_late_fee_payment
from services.payment_service import PaymentGateway

FAKE_BOOK = {"id": 1, "title": "T", "author": "A", "isbn": "1234567890123", "available_copies": 1}

def setup_db(mocker, fee=5.0, days=5):
    mocker.patch("services.library_service.get_book_by_id", return_value=FAKE_BOOK)
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": fee, "days_overdue": days, "status": "Success"})

def test_pay_calls_gateway_once(mocker):
    setup_db(mocker, 5.0, 5)
    pg = Mock(spec=PaymentGateway)
    pg.process_payment.return_value = {"status": "success", "transaction_id": "TXN123456500"}
    ok, p = pay_late_fees("123456", 1, pg)
    assert ok and p["transaction_id"] == "TXN123456500"
    pg.process_payment.assert_called_once_with("123456", 5.0)

def test_pay_decline(mocker):
    setup_db(mocker, 7.5, 3)
    pg = Mock(spec=PaymentGateway)
    pg.process_payment.return_value = {"status": "error", "reason": "DECLINED"}
    ok, msg = pay_late_fees("123456", 1, pg)
    assert not ok and "DECLINED" in msg
    pg.process_payment.assert_called_once_with("123456", 7.5)

def test_pay_exception(mocker):
    setup_db(mocker, 2.0, 1)
    pg = Mock(spec=PaymentGateway)
    pg.process_payment.side_effect = RuntimeError("boom")
    ok, msg = pay_late_fees("123456", 1, pg)
    assert not ok and "exception" in msg.lower()
    pg.process_payment.assert_called_once()

def test_pay_invalid_patron_skips_gateway(mocker):
    pg = Mock(spec=PaymentGateway)
    ok, _ = pay_late_fees("12A456", 1, pg)
    assert not ok
    pg.process_payment.assert_not_called()

def test_refund_success():
    pg = Mock(spec=PaymentGateway)
    pg.refund_payment.return_value = {"status": "refunded", "refund_id": "RFtx", "amount": 3.0}
    ok, p = refund_late_fee_payment("tx", 3.0, pg)
    assert ok and p["refund_id"] == "RFtx"
    pg.refund_payment.assert_called_once_with("tx", 3.0)

def test_refund_amount_validation():
    pg = Mock(spec=PaymentGateway)
    ok, _ = refund_late_fee_payment("tx", 0, pg)
    assert not ok
    ok, _ = refund_late_fee_payment("tx", 16.0, pg)
    assert not ok
    pg.refund_payment.assert_not_called()

