from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

# Simple prediction function
def predict_crop_yield(rainfall, temperature, soil_ph, nitrogen, phosphorus, potassium, sowing_offset):
    """Calculate crop yield based on input parameters"""
    base_yield = 2.0
    
    # Rainfall impact (optimal: 200-300mm)
    if 180 <= rainfall <= 350:
        rainfall_bonus = 0.5
    elif rainfall < 180:
        rainfall_bonus = -0.4
    else:
        rainfall_bonus = 0.2
    
    # Temperature impact (optimal: 26-32°C)
    if 26 <= temperature <= 32:
        temp_bonus = 0.4
    else:
        temp_bonus = -0.3
    
    # Soil pH impact (optimal: 6.0-7.5)
    if 6.0 <= soil_ph <= 7.5:
        ph_bonus = 0.3
    else:
        ph_bonus = -0.2
    
    # Nutrient impact
    nutrient_score = (nitrogen + phosphorus + potassium) / 300
    
    # Sowing date penalty
    sowing_penalty = abs(sowing_offset) * 0.05
    
    yield_prediction = base_yield + rainfall_bonus + temp_bonus + ph_bonus + nutrient_score - sowing_penalty
    return max(0.5, yield_prediction)

def generate_recommendations(data, prediction):
    """Generate farming recommendations"""
    recommendations = []
    
    if data['temperature'] > 32:
        recommendations.append("High temperature detected. Increase irrigation and use shade nets.")
    if data['rainfall'] < 180:
        recommendations.append("Low rainfall. Consider drip irrigation system.")
    if data['soil_ph'] < 6.0:
        recommendations.append("Acidic soil. Apply lime to increase pH.")
    if data['soil_ph'] > 7.5:
        recommendations.append("Alkaline soil. Add organic matter to reduce pH.")
    if data['nitrogen'] < 70:
        recommendations.append("Low nitrogen. Apply nitrogen-rich fertilizers.")
    if data['phosphorus'] < 35:
        recommendations.append("Low phosphorus. Use phosphate fertilizers.")
    if data['potassium'] < 55:
        recommendations.append("Low potassium. Apply potash fertilizers.")
    if prediction < 2.5:
        recommendations.append("Low yield predicted. Consider soil testing and crop rotation.")
    
    return recommendations

def get_risk_level(prediction, recommendations):
    """Determine risk level based on yield and recommendations"""
    if prediction < 2.0 or len(recommendations) >= 3:
        return 'Red'
    elif prediction < 2.8 or len(recommendations) >= 2:
        return 'Yellow'
    else:
        return 'Green'

# HTML template for the web interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🌾 Crop Yield Prediction Platform</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2d5016; text-align: center; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        button { background: #4CAF50; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background: #45a049; }
        .result { margin-top: 20px; padding: 20px; border-radius: 8px; }
        .green { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
        .yellow { background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; }
        .red { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
        .recommendations { margin-top: 15px; }
        .rec-item { background: #e9ecef; padding: 8px; margin: 5px 0; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌾 AI-Based Crop Yield Prediction Platform</h1>
        
        <form id="predictionForm">
            <div class="form-group">
                <label>Crop Type:</label>
                <select name="crop_type" required>
                    <option value="">Select Crop</option>
                    <option value="Rice">Rice</option>
                    <option value="Wheat">Wheat</option>
                    <option value="Maize">Maize</option>
                    <option value="Cotton">Cotton</option>
                    <option value="Sugarcane">Sugarcane</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>Region:</label>
                <input type="text" name="region" placeholder="e.g., Punjab, Tamil Nadu" required>
            </div>
            
            <div class="form-group">
                <label>Rainfall (mm):</label>
                <input type="number" name="rainfall" step="0.1" placeholder="200" required>
            </div>
            
            <div class="form-group">
                <label>Temperature (°C):</label>
                <input type="number" name="temperature" step="0.1" placeholder="30" required>
            </div>
            
            <div class="form-group">
                <label>Soil pH:</label>
                <input type="number" name="soil_ph" step="0.1" min="0" max="14" placeholder="6.8" required>
            </div>
            
            <div class="form-group">
                <label>Nitrogen (kg/ha):</label>
                <input type="number" name="nitrogen" step="0.1" placeholder="85" required>
            </div>
            
            <div class="form-group">
                <label>Phosphorus (kg/ha):</label>
                <input type="number" name="phosphorus" step="0.1" placeholder="42" required>
            </div>
            
            <div class="form-group">
                <label>Potassium (kg/ha):</label>
                <input type="number" name="potassium" step="0.1" placeholder="65" required>
            </div>
            
            <div class="form-group">
                <label>Sowing Date Offset (days):</label>
                <input type="number" name="sowing_date_offset" placeholder="0" required>
            </div>
            
            <button type="submit">🔮 Predict Crop Yield</button>
        </form>
        
        <div id="result"></div>
    </div>

    <script>
        document.getElementById('predictionForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            
            // Convert numeric fields
            ['rainfall', 'temperature', 'soil_ph', 'nitrogen', 'phosphorus', 'potassium', 'sowing_date_offset'].forEach(field => {
                data[field] = parseFloat(data[field]);
            });
            
            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.error) {
                    document.getElementById('result').innerHTML = `<div class="result red">Error: ${result.error}</div>`;
                    return;
                }
                
                const riskClass = result.risk_level.toLowerCase();
                const riskText = result.risk_level === 'Green' ? 'Safe' : result.risk_level === 'Yellow' ? 'Warning' : 'High Risk';
                
                let html = `
                    <div class="result ${riskClass}">
                        <h3>🎯 Prediction Results</h3>
                        <p><strong>Predicted Yield:</strong> ${result.predicted_yield} tons/hectare</p>
                        <p><strong>Risk Level:</strong> ${riskText}</p>
                        <p><strong>Crop:</strong> ${result.input_data.crop_type}</p>
                        <p><strong>Region:</strong> ${result.input_data.region}</p>
                `;
                
                if (result.recommendations.length > 0) {
                    html += '<div class="recommendations"><h4>📋 Recommendations:</h4>';
                    result.recommendations.forEach(rec => {
                        html += `<div class="rec-item">• ${rec}</div>`;
                    });
                    html += '</div>';
                }
                
                html += '</div>';
                document.getElementById('result').innerHTML = html;
                
            } catch (error) {
                document.getElementById('result').innerHTML = `<div class="result red">Error: ${error.message}</div>`;
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    """Main web interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/predict', methods=['POST'])
def predict():
    """API endpoint for crop yield prediction"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['crop_type', 'region', 'rainfall', 'temperature', 'soil_ph', 
                          'nitrogen', 'phosphorus', 'potassium', 'sowing_date_offset']
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing fields: {missing_fields}'}), 400
        
        # Make prediction
        prediction = predict_crop_yield(
            data['rainfall'], data['temperature'], data['soil_ph'],
            data['nitrogen'], data['phosphorus'], data['potassium'],
            data['sowing_date_offset']
        )
        
        # Generate recommendations
        recommendations = generate_recommendations(data, prediction)
        
        # Get risk level
        risk_level = get_risk_level(prediction, recommendations)
        
        return jsonify({
            'predicted_yield': round(prediction, 2),
            'unit': 'tons/hectare',
            'risk_level': risk_level,
            'recommendations': recommendations,
            'input_data': data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Crop Yield Prediction API is running',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("Starting Crop Yield Prediction Platform...")
    print("Web Interface: http://localhost:5000")
    print("API Health Check: http://localhost:5000/health")
    print("API Endpoint: POST http://localhost:5000/predict")
    print("\nPlatform is ready to use!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
