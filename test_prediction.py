import requests
import json

# Test data with 7 features
test_data = {
    "crop_type": "wheat",
    "region": "Delhi", 
    "rainfall": 200,
    "temperature": 28,
    "soil_ph": 6.5,
    "nitrogen": 80,
    "phosphorus": 40,
    "potassium": 60,
    "sowing_date_offset": 0
}

try:
    response = requests.post(
        'http://localhost:5000/api/predict',
        json=test_data,
        timeout=10
    )
    print("Status Code:", response.status_code)
    print("Response:", response.json())
    print("Features sent:", len([test_data['rainfall'], test_data['temperature'], test_data['soil_ph'], test_data['nitrogen'], test_data['phosphorus'], test_data['potassium'], test_data['sowing_date_offset']]))
except Exception as e:
    print("Error:", str(e))
