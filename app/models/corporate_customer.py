from sqlalchemy import Column, Integer, String, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship

from app.database import Base

class CorporateCustomer(Base):
    __tablename__ = "corporate_customers"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    company_name = Column(String(150), nullable=False)
    trade_name = Column(String(150))
    cnpj = Column(String(18), unique=True, nullable=False)
    annual_revenue = Column(DECIMAL(15, 2))

    email = Column(String(100))
    phone = Column(String(20))
    address = Column(String(255))

    user = relationship("User")