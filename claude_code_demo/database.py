from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, relationship
from alembic.config import Config
from alembic import command
import os

Base = declarative_base()

class PolicyStatus(str, Enum):
    CREATED = "CREATED"
    CONVERTED = "CONVERTED"

class Quote(Base):
    __tablename__ = "quotes"
    
    id = Column(Integer, primary_key=True, index=True)
    quote_ref = Column(String(50), unique=True, index=True, nullable=False)
    rego_or_vin = Column(String(100), nullable=False)
    max_shortfall = Column(String(20), nullable=False)
    quote_expiry_date = Column(String(20))
    gst_rate = Column(String(10))
    policy_status = Column(String(20), default=PolicyStatus.CREATED.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Request headers
    agent_code = Column(String(50))
    brand_code = Column(String(50))
    user_code = Column(String(50))
    
    # Relationships
    vehicle_details = relationship("VehicleDetail", back_populates="quote", uselist=False)
    gap_premium = relationship("GapPremium", back_populates="quote", uselist=False)

class VehicleDetail(Base):
    __tablename__ = "vehicle_details"
    
    id = Column(Integer, primary_key=True, index=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=False)
    registration = Column(String(20))
    vin = Column(String(100), nullable=False)
    make = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(String(10), nullable=False)
    cc_rating = Column(String(20), nullable=False)
    fuel_type = Column(String(30), nullable=False)
    odometer_reading = Column(String(20), nullable=False)
    body_colour = Column(String(50), nullable=False)
    body_style = Column(String(50), nullable=False)
    
    # Relationships
    quote = relationship("Quote", back_populates="vehicle_details")

class GapPremium(Base):
    __tablename__ = "gap_premiums"
    
    id = Column(Integer, primary_key=True, index=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=False)
    wholesale_amount = Column(Float, nullable=False)
    retail_amount = Column(Float, nullable=False)
    
    # Relationships
    quote = relationship("Quote", back_populates="gap_premium")

class BindRequest(Base):
    __tablename__ = "bind_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=False)
    vehicle_value = Column(Integer, nullable=False)
    vehicle_insurer = Column(String(100), nullable=False)
    retail_premium_adjustment = Column(Float)
    agree_to_declaration = Column(Boolean, nullable=False)
    payment_method = Column(String(50), nullable=False)
    loan_contract_number = Column(String(100))
    applicants_email = Column(Text)
    vehicle_deposit_provided = Column(Boolean, nullable=False)
    continue_purchase = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Request headers
    agent_code = Column(String(50))
    brand_code = Column(String(50))
    user_code = Column(String(50))
    
    # Relationships
    finance_details = relationship("FinanceDetail", back_populates="bind_request", uselist=False)
    applicant = relationship("Applicant", back_populates="bind_request", uselist=False)

class FinanceDetail(Base):
    __tablename__ = "finance_details"
    
    id = Column(Integer, primary_key=True, index=True)
    bind_request_id = Column(Integer, ForeignKey("bind_requests.id"), nullable=False)
    company = Column(String(100), nullable=False)
    amount = Column(Integer, nullable=False)
    balance_payable = Column(Integer, nullable=False)
    start_date = Column(String(20), nullable=False)
    contract_length = Column(Integer, nullable=False)
    
    # Relationships
    bind_request = relationship("BindRequest", back_populates="finance_details")

class Applicant(Base):
    __tablename__ = "applicants"
    
    id = Column(Integer, primary_key=True, index=True)
    bind_request_id = Column(Integer, ForeignKey("bind_requests.id"), nullable=False)
    first_name = Column(String(100), nullable=False)
    sur_name = Column(String(100), nullable=False)
    date_of_birth = Column(String(20), nullable=False)
    
    # Relationships
    bind_request = relationship("BindRequest", back_populates="applicant")
    postal_address = relationship("ApplicantPostalAddress", back_populates="applicant", uselist=False)
    contact = relationship("ApplicantContact", back_populates="applicant", uselist=False)
    business_applicant = relationship("BusinessApplicant", back_populates="applicant", uselist=False)
    joint_applicants = relationship("JointApplicant", back_populates="applicant")

class ApplicantPostalAddress(Base):
    __tablename__ = "applicant_postal_addresses"
    
    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(Integer, ForeignKey("applicants.id"), nullable=False)
    address_line1 = Column(String(200), nullable=False)
    address_line2 = Column(String(200))
    suburb = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    postcode = Column(String(20), nullable=False)
    
    # Relationships
    applicant = relationship("Applicant", back_populates="postal_address")

class ApplicantContact(Base):
    __tablename__ = "applicant_contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(Integer, ForeignKey("applicants.id"), nullable=False)
    phone = Column(String(50), nullable=False)
    mobile_num = Column(String(50))
    email_address = Column(String(200))
    
    # Relationships
    applicant = relationship("Applicant", back_populates="contact")

class BusinessApplicant(Base):
    __tablename__ = "business_applicants"
    
    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(Integer, ForeignKey("applicants.id"), nullable=False)
    business_name = Column(String(200), nullable=False)
    
    # Relationships
    applicant = relationship("Applicant", back_populates="business_applicant")
    contact_persons = relationship("BusinessContactPerson", back_populates="business_applicant")

class BusinessContactPerson(Base):
    __tablename__ = "business_contact_persons"
    
    id = Column(Integer, primary_key=True, index=True)
    business_applicant_id = Column(Integer, ForeignKey("business_applicants.id"), nullable=False)
    first_name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    business_contact_type = Column(String(20), nullable=False)
    
    # Relationships
    business_applicant = relationship("BusinessApplicant", back_populates="contact_persons")

class JointApplicant(Base):
    __tablename__ = "joint_applicants"
    
    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(Integer, ForeignKey("applicants.id"), nullable=False)
    first_name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    date_of_birth = Column(String(20))
    
    # Relationships
    applicant = relationship("Applicant", back_populates="joint_applicants")

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/gap_quotes")

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

def run_migrations():
    """Run database migrations using Alembic"""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

async def create_tables():
    """Create all tables (deprecated - use run_migrations instead)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    """Dependency to get database session"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()