from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.corporate_customer import CorporateCustomer
from app.models.individual_customer import IndividualCustomer
from app.models.user import User


_ = CorporateCustomer, IndividualCustomer, User


class AccountRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, account_id: int) -> Optional[Account]:
        return self.db.query(Account).filter(Account.id == account_id).first()

    def get_by_account_number(self, account_number: str) -> Optional[Account]:
        return (
            self.db.query(Account)
            .filter(Account.account_number == account_number)
            .first()
        )

    def create(
        self,
        account_number: str,
        balance: Decimal = Decimal("0"),
        individual_customer_id: Optional[int] = None,
        corporate_customer_id: Optional[int] = None,
    ) -> Account:
        account = Account(
            account_number=account_number,
            balance=balance,
            individual_customer_id=individual_customer_id,
            corporate_customer_id=corporate_customer_id,
        )
        self.db.add(account)
        return account

    def update_balance(self, account: Account, balance: Decimal) -> Account:
        account.balance = balance
        self.db.add(account)
        return account
