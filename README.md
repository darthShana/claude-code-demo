# GAP Quote Service API

Generator Guaranteed Asset Protection API for creating insurance policies with PostgreSQL backend.

## Features

- RESTful API for GAP insurance quotes
- PostgreSQL database with normalized schema
- Database migrations with Alembic
- Policy status tracking (CREATED → CONVERTED)
- Async/await support with SQLAlchemy 2.0

## Setup

1. Install dependencies:
```bash
poetry install
```

2. Set database URL:
```bash
export DATABASE_URL="postgresql+asyncpg://username:password@localhost/gap_quotes"
```

3. Run initial migration:
```bash
python migrate.py upgrade
```

4. Start the application:
```bash
python run.py
```

## Database Migrations

The application uses Alembic for database schema versioning. When you modify the database models:

### Create a new migration:
```bash
python migrate.py create "description of changes"
```

### Apply migrations:
```bash
python migrate.py upgrade
```

### Rollback migrations:
```bash
python migrate.py downgrade <revision>
```

### View migration status:
```bash
python migrate.py current
python migrate.py history
```

## API Endpoints

### Create Quote
```bash
POST /quickquote/generator/gap/v2/quote/create
```

### Bind Quote
```bash
POST /quickquote/generator/gap/v2/quote/bind
```

### Health Check
```bash
GET /health
```

## Database Schema

The application uses a normalized relational schema:

- `quotes` - Main quote table with policy status
- `vehicle_details` - Vehicle information
- `gap_premiums` - Premium calculations
- `bind_requests` - Bind request details
- `finance_details` - Finance information
- `applicants` - Applicant personal details
- `applicant_postal_addresses` - Addresses
- `applicant_contacts` - Contact information
- `business_applicants` - Business details
- `business_contact_persons` - Business contacts
- `joint_applicants` - Joint applicant details

## Development

The application automatically runs migrations on startup. For development, you can also run migrations manually using the `migrate.py` script.

## API Examples

### Example 1 - Create Quote
Request:
```json
{
  "regoOrVin": "MKD546",
  "maxShortfall": "GAP_5000"
}
```
Response:
```json
{
    "quoteResponse": {
        "quoteRef": "20160159",
        "quoteExpiryDate": "2025-07-11",
        "gstRate": "15",
        "vehicleDetails": {
            "registration": "MKD546",
            "vin": "MRHGK5860GP020199",
            "make": "HONDA",
            "model": "JAZZ",
            "year": "2015",
            "ccRating": "1497",
            "fuelType": "Petrol",
            "odometerReading": "89655",
            "bodyColour": "RED",
            "bodyStyle": "Hatchback"
        },
        "gapPremium": {
            "wholesaleAmount": 180.550,
            "retailAmount": 361.10
        }
    },
    "errors": []
}
```
### Example 2 = Bond Quote
Request:
```json
{
    "quoteRef": "10047692",
    "vehicleValue": "25000",
    "vehicleInsurer": "AA", "vehicleDepositProvided": "false",
    "financeDetails": {
        "company": "AA Finance",
        "amount": "20001",
        "balancePayable": "400",
        "startDate": "2021-05-19",
        "contractLength": "60"
    },
    "agreeToDeclaration": "true",
    "applicant": {
        "firstName": "Mary",
        "surName": "Smith",
        "dateOfBirth": "1990-12-30",
        "applicantPostalAddress": {
            "addressLine1": "105 Leonard Road",
            "suburb": "Penrose",
            "city": "Auckland",
            "postcode": "1061"
        },
        "applicantContact": {
            "phone": "092863319",
            "mobileNum": "021222999",
            "emailAddress": "here@there.com"
        }
    },
    "paymentMethod": "FINANCED",
    "loanContractNumber": "LP234243",
    "applicantsEmail": "abc@gmail.com"
}
```