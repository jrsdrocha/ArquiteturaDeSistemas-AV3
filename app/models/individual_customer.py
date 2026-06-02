from sqlalchemy import Column, Integer, String, Date, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship

from app.database import Base

class IndividualCustomer(Base):
    __tablename__ = "individual_customers"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    full_name = Column(String(100), nullable=False)
    cpf = Column(String(14), unique=True, nullable=False)
    birth_date = Column(Date)
    monthly_income = Column(DECIMAL(10, 2))

    email = Column(String(100))
    phone = Column(String(20))
    address = Column(String(255))

    user = relationship("User")