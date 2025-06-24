from datetime import datetime, timedelta
from fastapi import FastAPI, Header, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from typing import Annotated
import random
import string
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from .models import (
    GapQuoteRequestDTO,
    GapQuoteResponseDTO,
    GapQuoteResponse,
    GapBindQuoteRequestDTO,
    GapBindResponseDTO,
    VehicleDetails,
    GapPremium,
    ResponseError,
    ErrorCategory
)
from .database import (
    run_migrations,
    get_db,
    Quote,
    VehicleDetail,
    GapPremium as DBGapPremium,
    BindRequest,
    FinanceDetail,
    Applicant,
    ApplicantPostalAddress,
    ApplicantContact,
    BusinessApplicant,
    BusinessContactPerson,
    JointApplicant,
    PolicyStatus
)

app = FastAPI(
    title="Generator Insurance - GAP Quote Service API",
    description="Generator Guaranteed Asset Protection API for creating insurance policy",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    # Migrations should be run manually with: python migrate.py upgrade
    # This ensures the database connection is working
    pass


def generate_quote_ref() -> str:
    """Generate a random quote reference number"""
    return ''.join(random.choices(string.digits, k=8))


def get_vehicle_details_mock(rego_or_vin: str) -> VehicleDetails:
    """Mock function to simulate vehicle lookup"""
    return VehicleDetails(
        registration="MKD546" if len(rego_or_vin) < 10 else None,
        vin="MRHGK5860GP020199" if len(rego_or_vin) < 10 else rego_or_vin,
        make="HONDA",
        model="JAZZ",
        year="2015",
        ccRating="1497",
        fuelType="Petrol",
        odometerReading="89655",
        bodyColour="RED",
        bodyStyle="Hatchback"
    )


def calculate_gap_premium(max_shortfall: str) -> GapPremium:
    """Mock function to calculate GAP premium based on shortfall amount"""
    base_wholesale = 180.55
    base_retail = 361.10
    
    multiplier_map = {
        "GAP_5000": 1.0,
        "GAP_10000": 1.5,
        "GAP_15000": 2.0,
        "GAP_20000": 2.5,
        "GAP_30000": 3.0,
        "GAP_40000": 3.5
    }
    
    multiplier = multiplier_map.get(max_shortfall, 1.0)
    
    return GapPremium(
        wholesaleAmount=base_wholesale * multiplier,
        retailAmount=base_retail * multiplier
    )


@app.post("/quickquote/generator/gap/v2/quote/create", response_model=GapQuoteResponseDTO)
async def create_quote(
    quote_request: GapQuoteRequestDTO,
    x_agent_code: Annotated[str, Header(alias="X-Agent-Code")],
    x_brand_code: Annotated[str, Header(alias="X-Brand-Code")],
    x_user_code: Annotated[str, Header(alias="X-User-Code")],
    db: AsyncSession = Depends(get_db)
):
    """Create a new GAP quote"""
    try:
        # Validate input
        if not quote_request.regoOrVin:
            return GapQuoteResponseDTO(
                errors=[ResponseError(
                    category=ErrorCategory.VALIDATION,
                    code="ER001",
                    message="Registration or VIN is mandatory",
                    field="regoOrVin"
                )]
            )
        
        # Mock vehicle lookup
        vehicle_details = get_vehicle_details_mock(quote_request.regoOrVin)
        
        # Calculate premium
        gap_premium = calculate_gap_premium(quote_request.maxShortfall)
        
        # Generate quote reference
        quote_ref = generate_quote_ref()
        quote_expiry = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        # Save quote to database
        db_quote = Quote(
            quote_ref=quote_ref,
            rego_or_vin=quote_request.regoOrVin,
            max_shortfall=quote_request.maxShortfall.value,
            quote_expiry_date=quote_expiry,
            gst_rate="15",
            policy_status=PolicyStatus.CREATED.value,
            agent_code=x_agent_code,
            brand_code=x_brand_code,
            user_code=x_user_code
        )
        db.add(db_quote)
        await db.flush()
        
        # Save vehicle details
        db_vehicle = VehicleDetail(
            quote_id=db_quote.id,
            registration=vehicle_details.registration,
            vin=vehicle_details.vin,
            make=vehicle_details.make,
            model=vehicle_details.model,
            year=vehicle_details.year,
            cc_rating=vehicle_details.ccRating,
            fuel_type=vehicle_details.fuelType,
            odometer_reading=vehicle_details.odometerReading,
            body_colour=vehicle_details.bodyColour,
            body_style=vehicle_details.bodyStyle
        )
        db.add(db_vehicle)
        
        # Save gap premium
        db_premium = DBGapPremium(
            quote_id=db_quote.id,
            wholesale_amount=gap_premium.wholesaleAmount,
            retail_amount=gap_premium.retailAmount
        )
        db.add(db_premium)
        
        await db.commit()
        
        # Generate quote response
        quote_response = GapQuoteResponse(
            quoteRef=quote_ref,
            quoteExpiryDate=quote_expiry,
            gstRate="15",
            vehicleDetails=vehicle_details,
            gapPremium=gap_premium
        )
        
        return GapQuoteResponseDTO(
            quoteResponse=quote_response,
            errors=[]
        )
        
    except Exception as e:
        await db.rollback()
        return GapQuoteResponseDTO(
            errors=[ResponseError(
                category=ErrorCategory.SYSTEM,
                code="ER999",
                message=f"System error: {str(e)}"
            )]
        )


@app.post("/quickquote/generator/gap/v2/quote/bind", response_model=GapBindResponseDTO)
async def bind_quote(
    bind_request: GapBindQuoteRequestDTO,
    x_agent_code: Annotated[str, Header(alias="X-Agent-Code")],
    x_brand_code: Annotated[str, Header(alias="X-Brand-Code")],
    x_user_code: Annotated[str, Header(alias="X-User-Code")],
    db: AsyncSession = Depends(get_db)
):
    """Bind a GAP quote"""
    try:
        # Validate quote reference exists
        if not bind_request.quoteRef:
            return GapBindResponseDTO(
                errors=[ResponseError(
                    category=ErrorCategory.VALIDATION,
                    code="ER002",
                    message="Quote reference is mandatory",
                    field="quoteRef"
                )]
            )
        
        # Check if quote exists in database
        result = await db.execute(
            select(Quote).where(Quote.quote_ref == bind_request.quoteRef)
        )
        quote = result.scalar_one_or_none()
        
        if not quote:
            return GapBindResponseDTO(
                errors=[ResponseError(
                    category=ErrorCategory.BUSINESS,
                    code="ER404",
                    message="Quote not found or expired",
                    field="quoteRef"
                )]
            )
        
        # Validate mandatory fields
        errors = []
        
        if bind_request.vehicleValue <= 0:
            errors.append(ResponseError(
                category=ErrorCategory.VALIDATION,
                code="ER003",
                message="Vehicle value must be greater than 0",
                field="vehicleValue"
            ))
        
        if not bind_request.agreeToDeclaration:
            errors.append(ResponseError(
                category=ErrorCategory.VALIDATION,
                code="ER004",
                message="Must agree to declaration",
                field="agreeToDeclaration"
            ))
        
        if bind_request.paymentMethod == "FINANCED" and not bind_request.loanContractNumber:
            errors.append(ResponseError(
                category=ErrorCategory.VALIDATION,
                code="ER005",
                message="Loan contract number is mandatory when payment method is FINANCED",
                field="loanContractNumber"
            ))
        
        if errors:
            return GapBindResponseDTO(errors=errors)
        
        # Create bind request record
        db_bind = BindRequest(
            quote_id=quote.id,
            vehicle_value=bind_request.vehicleValue,
            vehicle_insurer=bind_request.vehicleInsurer,
            retail_premium_adjustment=bind_request.retailPremiumAdjustment,
            agree_to_declaration=bind_request.agreeToDeclaration,
            payment_method=bind_request.paymentMethod.value,
            loan_contract_number=bind_request.loanContractNumber,
            applicants_email=bind_request.applicantsEmail,
            vehicle_deposit_provided=bind_request.vehicleDepositProvided,
            continue_purchase=bind_request.continuePurchase,
            agent_code=x_agent_code,
            brand_code=x_brand_code,
            user_code=x_user_code
        )
        db.add(db_bind)
        await db.flush()
        
        # Save finance details
        db_finance = FinanceDetail(
            bind_request_id=db_bind.id,
            company=bind_request.financeDetails.company,
            amount=bind_request.financeDetails.amount,
            balance_payable=bind_request.financeDetails.balancePayable,
            start_date=bind_request.financeDetails.startDate.isoformat(),
            contract_length=bind_request.financeDetails.contractLength
        )
        db.add(db_finance)
        
        # Save applicant
        db_applicant = Applicant(
            bind_request_id=db_bind.id,
            first_name=bind_request.applicant.firstName,
            sur_name=bind_request.applicant.surName,
            date_of_birth=bind_request.applicant.dateOfBirth.isoformat()
        )
        db.add(db_applicant)
        await db.flush()
        
        # Save postal address
        db_address = ApplicantPostalAddress(
            applicant_id=db_applicant.id,
            address_line1=bind_request.applicant.applicantPostalAddress.addressLine1,
            address_line2=bind_request.applicant.applicantPostalAddress.addressLine2,
            suburb=bind_request.applicant.applicantPostalAddress.suburb,
            city=bind_request.applicant.applicantPostalAddress.city,
            postcode=bind_request.applicant.applicantPostalAddress.postcode
        )
        db.add(db_address)
        
        # Save contact
        db_contact = ApplicantContact(
            applicant_id=db_applicant.id,
            phone=bind_request.applicant.applicantContact.phone,
            mobile_num=bind_request.applicant.applicantContact.mobileNum,
            email_address=str(bind_request.applicant.applicantContact.emailAddress) if bind_request.applicant.applicantContact.emailAddress else None
        )
        db.add(db_contact)
        
        # Save business applicant (if present)
        if bind_request.applicant.businessApplicant:
            db_business = BusinessApplicant(
                applicant_id=db_applicant.id,
                business_name=bind_request.applicant.businessApplicant.businessName
            )
            db.add(db_business)
            await db.flush()
            
            # Save business contact persons
            if bind_request.applicant.businessApplicant.businessContactPersons:
                for contact_person in bind_request.applicant.businessApplicant.businessContactPersons:
                    db_contact_person = BusinessContactPerson(
                        business_applicant_id=db_business.id,
                        first_name=contact_person.firstName,
                        surname=contact_person.surname,
                        business_contact_type=contact_person.businessContactType.value
                    )
                    db.add(db_contact_person)
        
        # Save joint applicants
        for joint in bind_request.applicant.jointApplicants:
            db_joint = JointApplicant(
                applicant_id=db_applicant.id,
                first_name=joint.firstName,
                surname=joint.surname,
                date_of_birth=joint.dateOfBirth.isoformat() if joint.dateOfBirth else None
            )
            db.add(db_joint)
        
        # Update quote status to CONVERTED
        await db.execute(
            update(Quote)
            .where(Quote.id == quote.id)
            .values(policy_status=PolicyStatus.CONVERTED.value, updated_at=datetime.utcnow())
        )
        
        await db.commit()
        
        return GapBindResponseDTO(errors=[])
        
    except Exception as e:
        await db.rollback()
        return GapBindResponseDTO(
            errors=[ResponseError(
                category=ErrorCategory.SYSTEM,
                code="ER999",
                message=f"System error: {str(e)}"
            )]
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)