from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.schemas.transaction import (
    AccountStatementResponse,
    TransactionResponse,
    TransferByAccountNumberRequest,
    TransferRequest,
)
from app.services.transaction_service import TransactionService


router = APIRouter(prefix="/transactions", tags=["Transactions"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/transfer", response_model=TransactionResponse, status_code=201)
def transfer(payload: TransferRequest, db: Session = Depends(get_db)):
    transaction_service = TransactionService(db)
    return transaction_service.transfer_money(
        source_account_id=payload.source_account_id,
        destination_account_id=payload.destination_account_id,
        amount=payload.amount,
    )


@router.post(
    "/transfer/by-account-number",
    response_model=TransactionResponse,
    status_code=201,
)
def transfer_by_account_number(
    payload: TransferByAccountNumberRequest,
    db: Session = Depends(get_db),
):
    transaction_service = TransactionService(db)
    return transaction_service.transfer_money_by_account_number(
        source_account_number=payload.source_account_number,
        destination_account_number=payload.destination_account_number,
        amount=payload.amount,
    )


@router.get(
    "/statement/{account_number}",
    response_model=AccountStatementResponse,
)
def get_statement_by_account_number(
    account_number: str,
    db: Session = Depends(get_db),
):
    transaction_service = TransactionService(db)
    return transaction_service.get_statement_by_account_number(account_number)


@router.get("/account/{account_id}", response_model=list[TransactionResponse])
def list_account_transactions(account_id: int, db: Session = Depends(get_db)):
    transaction_service = TransactionService(db)
    return transaction_service.list_account_transactions(account_id)


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction_service = TransactionService(db)
    return transaction_service.get_transaction(transaction_id)
