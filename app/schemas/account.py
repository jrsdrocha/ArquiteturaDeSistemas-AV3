from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, condecimal, constr


MoneyAmount = condecimal(ge=0, max_digits=12, decimal_places=2)
AccountNumber = constr(strip_whitespace=True, min_length=1, max_length=20)
UsernameStr = constr(strip_whitespace=True, min_length=3, max_length=50)
PasswordStr = constr(min_length=6, max_length=255)
CpfStr = constr(strip_whitespace=True, min_length=11, max_length=14)
CnpjStr = constr(strip_whitespace=True, min_length=14, max_length=18)


class AccountCreateRequest(BaseModel):
    account_number: AccountNumber
    balance: MoneyAmount = Decimal("0")
    individual_customer_id: Optional[int] = None
    corporate_customer_id: Optional[int] = None
    cpf: Optional[CpfStr] = None
    cnpj: Optional[CnpjStr] = None


class IndividualAccountRegisterRequest(BaseModel):
    username: UsernameStr
    password: PasswordStr
    full_name: constr(strip_whitespace=True, min_length=1, max_length=100)
    cpf: CpfStr
    account_number: AccountNumber
    balance: MoneyAmount = Decimal("0")


class CorporateAccountRegisterRequest(BaseModel):
    username: UsernameStr
    password: PasswordStr
    company_name: constr(strip_whitespace=True, min_length=1, max_length=150)
    cnpj: CnpjStr
    account_number: AccountNumber
    balance: MoneyAmount = Decimal("0")


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_number: str
    balance: Decimal
    individual_customer_id: Optional[int] = None
    corporate_customer_id: Optional[int] = None


class AccountBalanceResponse(BaseModel):
    account_id: int
    balance: Decimal


class CompleteAccountRegisterResponse(BaseModel):
    user_id: int
    customer_id: int
    account: AccountResponse
