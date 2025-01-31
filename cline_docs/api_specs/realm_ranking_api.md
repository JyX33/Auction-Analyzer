# Realm Ranking API Specification

## Base URL
`/api/v1/rankings`

## Endpoints

### GET `/realms`
- **Purpose**: List available connected realms
- **Parameters**:
  - `region` (string): Filter by region (e.g. "eu", "us")
- **Response**:
```json
{
  "realms": [
    {
      "id": 1234,
      "name": "Argent Dawn",
      "region": "eu",
      "item_count": 1500,
      "last_updated": "2025-01-31T14:30:00Z"
    }
  ]
}
```

### GET `/prices/{realmId}`
- **Purpose**: Get price metrics for a realm
- **Parameters**:
  - `items` (array): Item IDs to analyze
  - `time_range` (string): "7d", "30d", or "all"
- **Response**:
```json
{
  "realm_id": 1234,
  "metrics": {
    "average_price": 254.35,
    "price_trend": 0.12,
    "item_details": [
      {
        "item_id": 12345,
        "current_price": 300.00,
        "historical_low": 250.00,
        "historical_high": 350.00
      }
    ]
  }
}
```

### GET `/comparison`
- **Purpose**: Compare multiple realms
- **Parameters**:
  - `realms` (array): Realm IDs to compare
  - `items` (array): Item IDs to analyze
- **Response**:
```json
{
  "comparison": [
    {
      "realm_id": 1234,
      "total_value": 150000.00,
      "value_per_item": 300.00
    }
  ]
}