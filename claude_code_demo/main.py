from datetime import datetime, timedelta
from fastapi import FastAPI, Header, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Annotated
import random
import string

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

app = FastAPI(
    title="Generator Insurance - GAP Quote Service API",
    description="Generator Guaranteed Asset Protection API for creating insurance policy",
    version="1.0.0"
)


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
    x_user_code: Annotated[str, Header(alias="X-User-Code")]
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
        
        # Generate quote
        quote_response = GapQuoteResponse(
            quoteRef=generate_quote_ref(),
            quoteExpiryDate=(datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            gstRate="15",
            vehicleDetails=vehicle_details,
            gapPremium=gap_premium
        )
        
        return GapQuoteResponseDTO(
            quoteResponse=quote_response,
            errors=[]
        )
        
    except Exception as e:
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
    x_user_code: Annotated[str, Header(alias="X-User-Code")]
):
    """Bind a GAP quote"""
    try:
        # Validate quote reference exists (mock validation)
        if not bind_request.quoteRef:
            return GapBindResponseDTO(
                errors=[ResponseError(
                    category=ErrorCategory.VALIDATION,
                    code="ER002",
                    message="Quote reference is mandatory",
                    field="quoteRef"
                )]
            )
        
        # Mock quote validation - check if quote exists
        if len(bind_request.quoteRef) != 8:
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
        
        # Mock successful binding
        return GapBindResponseDTO(errors=[])
        
    except Exception as e:
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