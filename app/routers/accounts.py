from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.schemas.account import (
    AccountBalanceResponse,
    AccountCreateRequest,
    AccountResponse,
    CompleteAccountRegisterResponse,
    CorporateAccountRegisterRequest,
    IndividualAccountRegisterRequest,
)
from app.services.account_service import AccountService


router = APIRouter(prefix="/accounts", tags=["Accounts"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=AccountResponse, status_code=201)
def create_account(payload: AccountCreateRequest, db: Session = Depends(get_db)):
    account_service = AccountService(db)
    return account_service.create_account(
        account_number=payload.account_number,
        balance=payload.balance,
        individual_customer_id=payload.individual_customer_id,
        corporate_customer_id=payload.corporate_customer_id,
        cpf=payload.cpf,
        cnpj=payload.cnpj,
    )


@router.post(
    "/individual/register",
    response_model=CompleteAccountRegisterResponse,
    status_code=201,
)
def register_individual_account(
    payload: IndividualAccountRegisterRequest,
    db: Session = Depends(get_db),
):
    account_service = AccountService(db)
    return account_service.register_individual_account(payload)


@router.post(
    "/corporate/register",
    response_model=CompleteAccountRegisterResponse,
    status_code=201,
)
def register_corporate_account(
    payload: CorporateAccountRegisterRequest,
    db: Session = Depends(get_db),
):
    account_service = AccountService(db)
    return account_service.register_corporate_account(payload)


@router.get("/number/{account_number}", response_model=AccountResponse)
def get_account_by_number(account_number: str, db: Session = Depends(get_db)):
    account_service = AccountService(db)
    return account_service.get_by_account_number(account_number)


@router.get("/{account_id}/balance", response_model=AccountBalanceResponse)
def get_account_balance(account_id: int, db: Session = Depends(get_db)):
    account_service = AccountService(db)
    return account_service.get_balance(account_id)
