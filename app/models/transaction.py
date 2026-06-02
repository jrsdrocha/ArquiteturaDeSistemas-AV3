from sqlalchemy import Column, Integer, ForeignKey, DECIMAL, String

from app.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)

    source_account_id = Column(
        Integer,
        ForeignKey("accounts.id")
    )

    destination_account_id = Column(
        Integer,
        ForeignKey("accounts.id")
    )

    amount = Column(DECIMAL(12, 2))

    transaction_type = Column(
        String(20)
    )