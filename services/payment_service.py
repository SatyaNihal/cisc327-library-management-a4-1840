class PaymentGateway:
    def process_payment(self, patron_id: str, amount: float) -> dict:
        if amount <= 0:
            return {"status": "error", "reason": "invalid amount"}
        return {"status": "success", "transaction_id": f"TXN{patron_id}{int(amount * 100)}"}

    def refund_payment(self, transaction_id: str, amount: float) -> dict:
        if not transaction_id or amount <= 0:
            return {"status": "error", "reason": "invalid refund"}
        return {"status": "refunded", "refund_id": f"RF{transaction_id}", "amount": amount}
