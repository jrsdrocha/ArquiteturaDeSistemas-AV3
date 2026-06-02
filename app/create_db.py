from app.database import Base, engine

from app.models.user import User
from app.models.individual_customer import IndividualCustomer
from app.models.corporate_customer import CorporateCustomer
from app.models.account import Account
from app.models.loan import Loan
from app.models.transaction import Transaction

Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")