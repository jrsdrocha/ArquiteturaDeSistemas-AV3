from sqlalchemy import Column, Integer, String, ForeignKey, DECIMAL
from app.database import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)

    account_number = Column(String(20), unique=True)

    balance = Column(DECIMAL(12, 2), default=0)

    individual_customer_id = Column(
        Integer,
        ForeignKey("individual_customers.id"),
        nullable=True
    )

    corporate_customer_id = Column(
        Integer,
        ForeignKey("corporate_customers.id"),
        nullable=True
    )