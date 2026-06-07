from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.transaction import Transaction
from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository


class TransactionService:
    def __init__(self, db: Session):
        self.db = db
        self.account_repository = AccountRepository(db)
        self.transaction_repository = TransactionRepository(db)

    def transfer_money(
        self,
        source_account_id: int,
        destination_account_id: int,
        amount: Decimal,
    ) -> Transaction:
        if source_account_id == destination_account_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Source and destination accounts must be different",
            )

        source_account = self.account_repository.get_by_id(source_account_id)
        if source_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source account not found",
            )

        destination_account = self.account_repository.get_by_id(destination_account_id)
        if destination_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Destination account not found",
            )

        return self._transfer_between_accounts(
            source_account=source_account,
            destination_account=destination_account,
            amount=amount,
        )

    def transfer_money_by_account_number(
        self,
        source_account_number: str,
        destination_account_number: str,
        amount: Decimal,
    ) -> Transaction:
        if source_account_number == destination_account_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Source and destination accounts must be different",
            )

        source_account = self.account_repository.get_by_account_number(
            source_account_number
        )
        if source_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source account not found",
            )

        destination_account = self.account_repository.get_by_account_number(
            destination_account_number
        )
        if destination_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Destination account not found",
            )

        return self._transfer_between_accounts(
            source_account=source_account,
            destination_account=destination_account,
            amount=amount,
        )

    def _transfer_between_accounts(
        self,
        source_account: Account,
        destination_account: Account,
        amount: Decimal,
    ) -> Transaction:
        amount = Decimal(str(amount))

        if amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transfer amount must be greater than zero",
            )

        source_balance = Decimal(source_account.balance or 0)
        destination_balance = Decimal(destination_account.balance or 0)

        if source_balance < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient funds",
            )

        self.account_repository.update_balance(source_account, source_balance - amount)
        self.account_repository.update_balance(
            destination_account,
            destination_balance + amount,
        )
        transaction = self.transaction_repository.create(
            source_account_id=source_account.id,
            destination_account_id=destination_account.id,
            amount=amount,
        )

        try:
            self.db.commit()
            self.db.refresh(transaction)
            self.db.refresh(source_account)
            self.db.refresh(destination_account)
        except SQLAlchemyError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not complete transfer",
            ) from exc

        return transaction

    def get_transaction(self, transaction_id: int) -> Transaction:
        transaction = self.transaction_repository.get_by_id(transaction_id)
        if transaction is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found",
            )
        return transaction

    def list_account_transactions(self, account_id: int) -> list[Transaction]:
        account = self.account_repository.get_by_id(account_id)
        if account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found",
            )
        return self.transaction_repository.list_by_account(account_id)

    def get_statement_by_account_number(self, account_number: str) -> dict:
        account = self.account_repository.get_by_account_number(account_number)
        if account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found",
            )

        transactions = self.transaction_repository.list_by_account(account.id)
        statement_transactions = []

        for transaction in transactions:
            source_account = self.account_repository.get_by_id(
                transaction.source_account_id
            )
            destination_account = self.account_repository.get_by_id(
                transaction.destination_account_id
            )
            statement_transactions.append(
                {
                    "transaction_id": transaction.id,
                    "direction": (
                        "SENT"
                        if transaction.source_account_id == account.id
                        else "RECEIVED"
                    ),
                    "amount": transaction.amount,
                    "source_account_number": source_account.account_number,
                    "destination_account_number": destination_account.account_number,
                    "transaction_type": transaction.transaction_type,
                }
            )

        return {
            "account_number": account.account_number,
            "balance": account.balance,
            "transactions": statement_transactions,
        }
