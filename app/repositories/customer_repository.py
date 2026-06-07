from typing import Optional

from sqlalchemy.orm import Session

from app.models.corporate_customer import CorporateCustomer
from app.models.individual_customer import IndividualCustomer
from app.models.user import User


_ = User


class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_individual_by_id(
        self,
        customer_id: int,
    ) -> Optional[IndividualCustomer]:
        return (
            self.db.query(IndividualCustomer)
            .filter(IndividualCustomer.id == customer_id)
            .first()
        )

    def get_corporate_by_id(
        self,
        customer_id: int,
    ) -> Optional[CorporateCustomer]:
        return (
            self.db.query(CorporateCustomer)
            .filter(CorporateCustomer.id == customer_id)
            .first()
        )

    def get_individual_by_cpf(self, cpf: str) -> Optional[IndividualCustomer]:
        return (
            self.db.query(IndividualCustomer)
            .filter(IndividualCustomer.cpf == cpf)
            .first()
        )

    def get_corporate_by_cnpj(self, cnpj: str) -> Optional[CorporateCustomer]:
        return (
            self.db.query(CorporateCustomer)
            .filter(CorporateCustomer.cnpj == cnpj)
            .first()
        )

    def create_individual(
        self,
        full_name: str,
        cpf: str,
        user_id: Optional[int] = None,
        birth_date=None,
        monthly_income=None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
    ) -> IndividualCustomer:
        customer = IndividualCustomer(
            user_id=user_id,
            full_name=full_name,
            cpf=cpf,
            birth_date=birth_date,
            monthly_income=monthly_income,
            email=email,
            phone=phone,
            address=address,
        )
        self.db.add(customer)
        return customer

    def create_corporate(
        self,
        company_name: str,
        cnpj: str,
        user_id: Optional[int] = None,
        trade_name: Optional[str] = None,
        annual_revenue=None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
    ) -> CorporateCustomer:
        customer = CorporateCustomer(
            user_id=user_id,
            company_name=company_name,
            trade_name=trade_name,
            cnpj=cnpj,
            annual_revenue=annual_revenue,
            email=email,
            phone=phone,
            address=address,
        )
        self.db.add(customer)
        return customer
