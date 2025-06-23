# API Examples

## Example 1 
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
            "propulsion": null,
            "propulsionList": null,
            "year": "2015",
            "ccRating": "1497",
            "fuelType": "Petrol",
            "odometerReading": "89655",
            "originalOdometerReading": "89655",
            "bodyColour": "RED",
            "bodyStyle": "Hatchback",
            "vehicleValue": 0,
            "lastWOFDate": "2024-12-09",
            "variants": [],
            "modifications": null,
            "otherModification": null
        },
        "gapPremium": {
            "wholesaleAmount": 180.550,
            "retailAmount": 361.10
        }
    },
    "errors": []
}
```
