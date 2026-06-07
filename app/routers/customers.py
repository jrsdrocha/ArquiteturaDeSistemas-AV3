from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.schemas.customer import (
    CorporateCustomerCreateRequest,
    CorporateCustomerResponse,
    IndividualCustomerCreateRequest,
    IndividualCustomerResponse,
)
from app.services.customer_service import CustomerService


router = APIRouter(prefix="/customers", tags=["Customers"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/individual",
    response_model=IndividualCustomerResponse,
    status_code=201,
)
def create_individual_customer(
    payload: IndividualCustomerCreateRequest,
    db: Session = Depends(get_db),
):
    customer_service = CustomerService(db)
    return customer_service.create_individual_customer(payload)


@router.post(
    "/corporate",
    response_model=CorporateCustomerResponse,
    status_code=201,
)
def create_corporate_customer(
    payload: CorporateCustomerCreateRequest,
    db: Session = Depends(get_db),
):
    customer_service = CustomerService(db)
    return customer_service.create_corporate_customer(payload)
