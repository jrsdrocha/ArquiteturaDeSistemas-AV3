from typing import Optional

from sqlalchemy.orm import Session

from app.models.transaction import Transaction


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        return (
            self.db.query(Transaction)
            .filter(Transaction.id == transaction_id)
            .first()
        )

    def list_by_account(self, account_id: int) -> list[Transaction]:
        return (
            self.db.query(Transaction)
            .filter(
                (Transaction.source_account_id == account_id)
                | (Transaction.destination_account_id == account_id)
            )
            .order_by(Transaction.id)
            .all()
        )

    def create(
        self,
        source_account_id: int,
        destination_account_id: int,
        amount,
        transaction_type: str = "TRANSFER",
    ) -> Transaction:
        transaction = Transaction(
            source_account_id=source_account_id,
            destination_account_id=destination_account_id,
            amount=amount,
            transaction_type=transaction_type,
        )
        self.db.add(transaction)
        return transaction
