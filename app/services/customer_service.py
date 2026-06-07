from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.repositories.customer_repository import CustomerRepository
from app.repositories.user_repository import UserRepository


class CustomerService:
    def __init__(self, db: Session):
        self.db = db
        self.customer_repository = CustomerRepository(db)
        self.user_repository = UserRepository(db)

    def create_individual_customer(self, payload):
        if payload.user_id and self.user_repository.get_by_id(payload.user_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if self.customer_repository.get_individual_by_cpf(payload.cpf):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="CPF already registered",
            )

        customer = self.customer_repository.create_individual(
            full_name=payload.full_name,
            cpf=payload.cpf,
            user_id=payload.user_id,
            birth_date=payload.birth_date,
            monthly_income=payload.monthly_income,
            email=payload.email,
            phone=payload.phone,
            address=payload.address,
        )
        return self._commit_customer(customer, "Could not create individual customer")

    def create_corporate_customer(self, payload):
        if payload.user_id and self.user_repository.get_by_id(payload.user_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if self.customer_repository.get_corporate_by_cnpj(payload.cnpj):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="CNPJ already registered",
            )

        customer = self.customer_repository.create_corporate(
            company_name=payload.company_name,
            cnpj=payload.cnpj,
            user_id=payload.user_id,
            trade_name=payload.trade_name,
            annual_revenue=payload.annual_revenue,
            email=payload.email,
            phone=payload.phone,
            address=payload.address,
        )
        return self._commit_customer(customer, "Could not create corporate customer")

    def _commit_customer(self, customer, error_message: str):
        try:
            self.db.commit()
            self.db.refresh(customer)
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"{error_message}: {exc.orig}",
            ) from exc
        except SQLAlchemyError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"{error_message}: {exc}",
            ) from exc

        return customer
