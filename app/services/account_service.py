from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.account import Account
from app.repositories.account_repository import AccountRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.user_repository import UserRepository
from app.schemas.account import AccountBalanceResponse
from app.services.auth_service import AuthService


class AccountService:
    def __init__(self, db: Session):
        self.db = db
        self.account_repository = AccountRepository(db)
        self.customer_repository = CustomerRepository(db)
        self.user_repository = UserRepository(db)
        self.auth_service = AuthService(db)

    def create_account(
        self,
        account_number: str,
        balance,
        individual_customer_id: int | None = None,
        corporate_customer_id: int | None = None,
        cpf: str | None = None,
        cnpj: str | None = None,
    ) -> dict:
        owner_fields = [
            individual_customer_id,
            corporate_customer_id,
            cpf,
            cnpj,
        ]
        if sum(value is not None for value in owner_fields) > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account can be linked to only one customer",
            )

        if self.account_repository.get_by_account_number(account_number):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Account number already exists",
            )

        if cpf:
            individual_customer = self.customer_repository.get_individual_by_cpf(cpf)
            if individual_customer is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Individual customer not found for this CPF",
                )
            individual_customer_id = individual_customer.id

        if cnpj:
            corporate_customer = self.customer_repository.get_corporate_by_cnpj(cnpj)
            if corporate_customer is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Corporate customer not found for this CNPJ",
                )
            corporate_customer_id = corporate_customer.id

        if individual_customer_id:
            individual_customer = self.customer_repository.get_individual_by_id(
                individual_customer_id
            )
            if individual_customer is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Individual customer not found",
                )

        if corporate_customer_id:
            corporate_customer = self.customer_repository.get_corporate_by_id(
                corporate_customer_id
            )
            if corporate_customer is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Corporate customer not found",
                )

        account = self.account_repository.create(
            account_number=account_number,
            balance=balance,
            individual_customer_id=individual_customer_id,
            corporate_customer_id=corporate_customer_id,
        )

        try:
            self.db.commit()
            self.db.refresh(account)
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Could not create account: {exc.orig}",
            ) from exc
        except SQLAlchemyError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not create account: {exc}",
            ) from exc

        return {
            "id": account.id,
            "account_number": account.account_number,
            "balance": account.balance,
            "individual_customer_id": account.individual_customer_id,
            "corporate_customer_id": account.corporate_customer_id,
        }

    def register_individual_account(self, payload) -> dict:
        self._validate_complete_register(
            username=payload.username,
            account_number=payload.account_number,
        )

        if self.customer_repository.get_individual_by_cpf(payload.cpf):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="CPF already registered",
            )

        user = self.user_repository.create_pending(
            username=payload.username,
            password=self.auth_service.get_password_hash(payload.password),
        )

        try:
            self.db.flush()
            customer = self.customer_repository.create_individual(
                user_id=user.id,
                full_name=payload.full_name,
                cpf=payload.cpf,
            )
            self.db.flush()
            account = self.account_repository.create(
                account_number=payload.account_number,
                balance=payload.balance,
                individual_customer_id=customer.id,
            )
            self.db.commit()
            self.db.refresh(account)
            self.db.refresh(customer)
            self.db.refresh(user)
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Could not complete register: {exc.orig}",
            ) from exc
        except SQLAlchemyError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not complete register: {exc}",
            ) from exc

        return self._complete_register_response(user.id, customer.id, account)

    def register_corporate_account(self, payload) -> dict:
        self._validate_complete_register(
            username=payload.username,
            account_number=payload.account_number,
        )

        if self.customer_repository.get_corporate_by_cnpj(payload.cnpj):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="CNPJ already registered",
            )

        user = self.user_repository.create_pending(
            username=payload.username,
            password=self.auth_service.get_password_hash(payload.password),
        )

        try:
            self.db.flush()
            customer = self.customer_repository.create_corporate(
                user_id=user.id,
                company_name=payload.company_name,
                cnpj=payload.cnpj,
            )
            self.db.flush()
            account = self.account_repository.create(
                account_number=payload.account_number,
                balance=payload.balance,
                corporate_customer_id=customer.id,
            )
            self.db.commit()
            self.db.refresh(account)
            self.db.refresh(customer)
            self.db.refresh(user)
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Could not complete register: {exc.orig}",
            ) from exc
        except SQLAlchemyError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not complete register: {exc}",
            ) from exc

        return self._complete_register_response(user.id, customer.id, account)

    def _validate_complete_register(
        self,
        username: str,
        account_number: str,
    ) -> None:
        if self.user_repository.get_by_username(username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already registered",
            )

        if self.account_repository.get_by_account_number(account_number):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Account number already exists",
            )

    @staticmethod
    def _complete_register_response(
        user_id: int,
        customer_id: int,
        account: Account,
    ) -> dict:
        return {
            "user_id": user_id,
            "customer_id": customer_id,
            "account": {
                "id": account.id,
                "account_number": account.account_number,
                "balance": account.balance,
                "individual_customer_id": account.individual_customer_id,
                "corporate_customer_id": account.corporate_customer_id,
            },
        }

    def get_balance(self, account_id: int) -> AccountBalanceResponse:
        account = self.account_repository.get_by_id(account_id)
        if account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found",
            )

        return AccountBalanceResponse(
            account_id=account.id,
            balance=account.balance,
        )

    def get_by_account_number(self, account_number: str) -> dict:
        account = self.account_repository.get_by_account_number(account_number)
        if account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found",
            )

        return {
            "id": account.id,
            "account_number": account.account_number,
            "balance": account.balance,
            "individual_customer_id": account.individual_customer_id,
            "corporate_customer_id": account.corporate_customer_id,
        }
