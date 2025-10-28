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

### 2. Single Insert
```
POST /warehouse/api/warehouse/apartments/single-insert
```

**Request Body:**
```json
{
  "property_group": 1,
  "unit_type": 10,
  "unit_code": "S1.01-501",
  "unit_axis": "A",
  "unit_floor_number": 5,
  "area_land": 100.5,
  "area_construction": 85.0,
  "area_net": 75.0,
  "area_gross": 80.0,
  "num_bedrooms": 2,
  "num_bathrooms": 2,
  "type_view": "CITY_VIEW",
  "direction_door": "DN",
  "direction_balcony": "DB",
  "price": 2500000000.0,
  "price_early": 2400000000.0,
  "price_schedule": 2450000000.0,
  "price_loan": 2300000000.0,
  "notes": "Căn hộ đẹp, view thành phố",
  "status": "CHUA_BAN",
  "unit_allocation": "QUY_CHEO"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "apartment_id": 12345,
    "apartment_data": { ... }
  },
  "message": "Successfully inserted apartment: S1.01-501"
}
```

### 3. Batch Insert
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
    "error_count": 0,
    "errors": []
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

# Single insert
apartment_data = {
    "unit_code": "S1.01-501",
    "unit_floor_number": 5,
    "area_gross": 80.0,
    "num_bedrooms": 2,
    "price": 2500000000.0
}

response = requests.post(
    "http://localhost:5000/warehouse/api/warehouse/apartments/single-insert",
    json=apartment_data
)

if response.status_code == 200:
    result = response.json()
    if result['success']:
        print(f"Inserted apartment ID: {result['data']['apartment_id']}")
```

### Batch Insert
```python
apartments = [
    {"unit_code": "S1.01-501", "area_gross": 80.0, "price": 2500000000.0},
    {"unit_code": "S1.01-502", "area_gross": 75.0, "price": 2400000000.0}
]

response = requests.post(
    "http://localhost:5000/warehouse/api/warehouse/apartments/batch-insert",
    json={"apartments": apartments}
)
```

### JavaScript/Fetch
```javascript
const apartmentData = {
    unit_code: "S1.01-501",
    unit_floor_number: 5,
    area_gross: 80.0,
    num_bedrooms: 2,
    price: 2500000000.0
};

fetch('http://localhost:5000/warehouse/api/warehouse/apartments/single-insert', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(apartmentData)
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('Inserted apartment ID:', data.data.apartment_id);
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
def insert_apartment_via_api(self, apartment_data: Dict) -> bool:
    try:
        import requests
        
        # Prepare data
        apartment_record = {
            'property_group': apartment_data.get('property_group', 1),
            'unit_type': self.map_unit_type_to_id(apartment_data.get('unit_type')),
            'unit_code': apartment_data.get('unit_code'),
            # ... other fields
        }
        
        # Call API
        response = requests.post(
            "http://localhost:5000/warehouse/api/warehouse/apartments/single-insert",
            json=apartment_record,
            timeout=30
        )
        
        return response.status_code == 200 and response.json().get('success')
        
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

# Single insert
curl -X POST http://localhost:5000/warehouse/api/warehouse/apartments/single-insert \
  -H "Content-Type: application/json" \
  -d '{"unit_code": "TEST-001", "area_gross": 80.0, "price": 2500000000.0}'

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
