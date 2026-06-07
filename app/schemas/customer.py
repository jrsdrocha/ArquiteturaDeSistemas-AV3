from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, condecimal, constr


CpfStr = constr(strip_whitespace=True, min_length=11, max_length=14)
CnpjStr = constr(strip_whitespace=True, min_length=14, max_length=18)


class IndividualCustomerCreateRequest(BaseModel):
    full_name: constr(strip_whitespace=True, min_length=1, max_length=100)
    cpf: CpfStr
    user_id: Optional[int] = None
    birth_date: Optional[date] = None
    monthly_income: Optional[condecimal(ge=0, max_digits=10, decimal_places=2)] = None
    email: Optional[constr(strip_whitespace=True, max_length=100)] = None
    phone: Optional[constr(strip_whitespace=True, max_length=20)] = None
    address: Optional[constr(strip_whitespace=True, max_length=255)] = None


class IndividualCustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    full_name: str
    cpf: str
    birth_date: Optional[date] = None
    monthly_income: Optional[Decimal] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class CorporateCustomerCreateRequest(BaseModel):
    company_name: constr(strip_whitespace=True, min_length=1, max_length=150)
    cnpj: CnpjStr
    user_id: Optional[int] = None
    trade_name: Optional[constr(strip_whitespace=True, max_length=150)] = None
    annual_revenue: Optional[condecimal(ge=0, max_digits=15, decimal_places=2)] = None
    email: Optional[constr(strip_whitespace=True, max_length=100)] = None
    phone: Optional[constr(strip_whitespace=True, max_length=20)] = None
    address: Optional[constr(strip_whitespace=True, max_length=255)] = None


class CorporateCustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    company_name: str
    trade_name: Optional[str] = None
    cnpj: str
    annual_revenue: Optional[Decimal] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
