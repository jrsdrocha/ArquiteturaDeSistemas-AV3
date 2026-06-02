from sqlalchemy import Column, Integer, ForeignKey, DECIMAL, String

from app.database import Base

class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True)

    account_id = Column(
        Integer,
        ForeignKey("accounts.id")
    )

    amount = Column(DECIMAL(12, 2))
    installments = Column(Integer)

    status = Column(
        String(20),
        default="PENDING"
    )