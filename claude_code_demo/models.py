from datetime import date
from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel, EmailStr


class MaxShortfall(str, Enum):
    GAP_5000 = "GAP_5000"
    GAP_10000 = "GAP_10000"
    GAP_15000 = "GAP_15000"
    GAP_20000 = "GAP_20000"
    GAP_30000 = "GAP_30000"
    GAP_40000 = "GAP_40000"


class PaymentMethod(str, Enum):
    FINANCED = "FINANCED"
    CASH_SALES_AGENT = "CASH_SALES_AGENT"


class ErrorCategory(str, Enum):
    VALIDATION = "VALIDATION"
    FUNCTIONAL = "FUNCTIONAL"
    BUSINESS = "BUSINESS"
    SYSTEM = "SYSTEM"


class BusinessContactType(str, Enum):
    PRIMARY = "PRIMARY"
    JOINT = "JOINT"


class Variant(BaseModel):
    code: str
    description: str


class RateChart(BaseModel):
    code: str
    description: str


class VehicleDetails(BaseModel):
    registration: Optional[str] = None
    vin: str
    make: str
    model: str
    year: str
    ccRating: str
    fuelType: str
    odometerReading: str
    bodyColour: str
    bodyStyle: str
    variants: Optional[List[Variant]] = None
    rateCharts: Optional[List[RateChart]] = None


class GapQuoteRequestDTO(BaseModel):
    regoOrVin: str
    maxShortfall: MaxShortfall


class GapPremium(BaseModel):
    wholesaleAmount: float
    retailAmount: float


class ResponseError(BaseModel):
    category: ErrorCategory
    code: str
    message: str
    field: Optional[str] = None


class GapQuoteResponse(BaseModel):
    quoteRef: str
    quoteExpiryDate: Optional[str] = None
    gstRate: Optional[str] = None
    vehicleDetails: VehicleDetails
    gapPremium: Optional[GapPremium] = None


class GapQuoteResponseDTO(BaseModel):
    quoteResponse: Optional[GapQuoteResponse] = None
    errors: List[ResponseError] = []


class ApplicantPostalAddress(BaseModel):
    addressLine1: str
    addressLine2: Optional[str] = None
    suburb: str
    city: str
    postcode: str


class ApplicantContact(BaseModel):
    phone: str
    mobileNum: Optional[str] = None
    emailAddress: Optional[EmailStr] = None


class BusinessContactPerson(BaseModel):
    firstName: str
    surname: str
    businessContactType: BusinessContactType


class BusinessApplicant(BaseModel):
    businessName: str
    businessContactPersons: Optional[List[BusinessContactPerson]] = None


class JointApplicant(BaseModel):
    firstName: str
    surname: str
    dateOfBirth: Optional[date] = None


class Applicant(BaseModel):
    firstName: str
    surName: str
    dateOfBirth: date
    applicantPostalAddress: ApplicantPostalAddress
    applicantContact: ApplicantContact
    businessApplicant: Optional[BusinessApplicant] = None
    jointApplicants: List[JointApplicant] = []
    
    def model_post_init(self, __context):
        # If businessApplicant is provided, this is a business application
        # Individual fields (firstName, surName, dateOfBirth) are always required
        # but when businessApplicant is present, they represent the primary contact person
        pass


class Finance(BaseModel):
    company: str
    amount: int
    balancePayable: int
    startDate: date
    contractLength: int


class GapBindQuoteRequestDTO(BaseModel):
    quoteRef: str
    regoOrVin: Optional[str] = None
    vehicleValue: int
    vehicleInsurer: str
    financeDetails: Finance
    retailPremiumAdjustment: Optional[float] = None
    agreeToDeclaration: bool
    applicant: Applicant
    paymentMethod: PaymentMethod
    loanContractNumber: Optional[str] = None
    applicantsEmail: Optional[str] = None
    vehicleDepositProvided: bool
    continuePurchase: Optional[bool] = None


class GapBindResponseDTO(BaseModel):
    errors: List[ResponseError] = []