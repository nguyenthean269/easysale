# Warehouse API Documentation

## Tổng quan

API Warehouse cung cấp các endpoint để insert apartment data vào warehouse database với nguyên tắc:
- **Thiếu trường**: Để NULL
- **Thừa trường**: Bỏ qua
- **Flexible validation**: Tự động convert data types

## API Endpoints

### 1. Test Connection
```
GET /warehouse/api/warehouse/apartments/test
```

**Response:**
```json
{
  "success": true,
  "data": {
    "connection_status": "OK",
    "apartments_count": 1234
  },
  "message": "Warehouse database connection successful"
}
```

### 2. Batch Insert
```
POST /warehouse/api/warehouse/apartments/batch-insert
```

**Request Body:**
```json
{
  "apartments": [
    {
      "unit_code": "S1.01-501",
      "unit_floor_number": 5,
      "area_gross": 80.0,
      "num_bedrooms": 2,
      "price": 2500000000.0
    },
    {
      "unit_code": "S1.01-502", 
      "unit_floor_number": 5,
      "area_gross": 75.0,
      "num_bedrooms": 2,
      "price": 2400000000.0
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_items": 2,
    "inserted_count": 2,
    "apartment_ids": [12345, 12346]
  },
  "message": "Successfully inserted 2/2 apartments"
}
```

## Data Validation Rules

### Field Types
- **int**: `property_group`, `unit_type`, `unit_floor_number`, `num_bedrooms`, `num_bathrooms`
- **float**: `area_land`, `area_construction`, `area_net`, `area_gross`, `price`, `price_early`, `price_schedule`, `price_loan`
- **str**: `unit_code`, `unit_axis`, `type_view`, `direction_door`, `direction_balcony`, `notes`, `status`, `unit_allocation`

### Enum Values
- **direction_door/direction_balcony**: `D`, `T`, `N`, `B`, `DB`, `DN`, `TB`, `TN`
- **status**: `CHUA_BAN`, `DA_LOCK`, `DA_COC`, `DA_BAN`
- **unit_allocation**: `QUY_CHEO`, `QUY_DOI`

### Default Values
- **property_group**: 1 (nếu không có)
- **unit_allocation**: `QUY_CHEO` (nếu không có)

### Data Cleaning
- Loại bỏ units: `m2`, `tỷ`, `triệu`
- Convert string numbers: `"75.5"` → `75.5`
- Handle null values: `null`, `""`, `None` → `NULL`

## Usage Examples

### Python Requests
```python
import requests

apartments = [
    {"unit_code": "S1.01-501", "area_gross": 80.0, "price": 2500000000.0},
    {"unit_code": "S1.01-502", "area_gross": 75.0, "price": 2400000000.0}
]

response = requests.post(
    "http://localhost:5000/warehouse/api/warehouse/apartments/batch-insert",
    json={"apartments": apartments}
)

if response.status_code == 200:
    result = response.json()
    if result['success']:
        print(f"Inserted apartment IDs: {result['data']['apartment_ids']}")
```

### JavaScript/Fetch
```javascript
const apartments = [
    { unit_code: "S1.01-501", area_gross: 80.0, price: 2500000000.0 }
];

fetch('http://localhost:5000/warehouse/api/warehouse/apartments/batch-insert', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ apartments })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('Inserted apartment IDs:', data.data.apartment_ids);
    }
});
```

## Error Handling

### Common Errors
- **400**: Invalid JSON data
- **500**: Database connection error
- **500**: SQL execution error

### Error Response Format
```json
{
  "success": false,
  "error": "Error message description"
}
```

## Integration với Zalo Message Processor

Zalo Message Processor giờ sử dụng API warehouse thay vì direct database access:

```python
# Trong ZaloMessageProcessor
def insert_apartment_via_api(self, apartment_data: Dict):
    try:
        import requests

        apartment_record = {
            'property_group': apartment_data.get('property_group', 1),
            'unit_type': self.map_unit_type_to_id(apartment_data.get('unit_type')),
            'unit_code': apartment_data.get('unit_code'),
            # ... other fields
        }

        response = requests.post(
            "http://localhost:5000/warehouse/api/warehouse/apartments/batch-insert",
            json={'apartments': [apartment_record]},
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                apartment_ids = result.get('data', {}).get('apartment_ids', [])
                return apartment_ids[0] if apartment_ids else None
        return False

    except Exception as e:
        logger.error(f"Error calling warehouse API: {e}")
        return False
```

## Testing

### Test Script
```bash
python test_warehouse_api.py
```

### Manual Testing với curl
```bash
# Test connection
curl -X GET http://localhost:5000/warehouse/api/warehouse/apartments/test

# Batch insert
curl -X POST http://localhost:5000/warehouse/api/warehouse/apartments/batch-insert \
  -H "Content-Type: application/json" \
  -d '{"apartments": [{"unit_code": "TEST-002", "area_gross": 75.0}]}'
```

## Benefits

1. **Flexible Data Handling**: Thiếu trường để NULL, thừa trường bỏ qua
2. **Centralized Validation**: Tất cả validation logic ở một chỗ
3. **Better Error Handling**: Detailed error messages và logging
4. **Scalable**: Có thể handle batch operations
5. **Maintainable**: Dễ maintain và update validation rules
6. **Testable**: Dễ test với các test cases khác nhau






