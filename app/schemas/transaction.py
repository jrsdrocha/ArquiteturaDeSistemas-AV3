from decimal import Decimal

from pydantic import BaseModel, ConfigDict, condecimal, constr


MoneyAmount = condecimal(gt=0, max_digits=12, decimal_places=2)
AccountNumber = constr(strip_whitespace=True, min_length=1, max_length=20)


class TransferRequest(BaseModel):
    source_account_id: int
    destination_account_id: int
    amount: MoneyAmount


class TransferByAccountNumberRequest(BaseModel):
    source_account_number: AccountNumber
    destination_account_number: AccountNumber
    amount: MoneyAmount


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_account_id: int
    destination_account_id: int
    amount: Decimal
    transaction_type: str


class StatementTransactionResponse(BaseModel):
    transaction_id: int
    direction: str
    amount: Decimal
    source_account_number: str
    destination_account_number: str
    transaction_type: str


class AccountStatementResponse(BaseModel):
    account_number: str
    balance: Decimal
    transactions: list[StatementTransactionResponse]
