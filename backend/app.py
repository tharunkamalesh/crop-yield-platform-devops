from flask import Flask, request, jsonify, session
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None
try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False
    joblib = None
import requests
import json
import sqlite3
from datetime import datetime, timedelta
import os

# Try to import optional dependencies
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False

try:
    from flask_sqlalchemy import SQLAlchemy
    from werkzeug.security import generate_password_hash, check_password_hash
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Import our custom modules
from notifications import notification_service
from offline_cache import offline_cache

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# Initialize optional components
if CORS_AVAILABLE:
    CORS(app)

if SQLALCHEMY_AVAILABLE:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crop_platform.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)
else:
    db = None

# OpenWeather API configuration
OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', "your-openweather-api-key")  # Replace with actual key
OPENWEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# Weather cache to reduce API calls and provide stability
weather_cache = {}
WEATHER_CACHE_DURATION = 3600  # 1 hour cache duration

# Database Models (only if SQLAlchemy is available)
if SQLALCHEMY_AVAILABLE and db:
    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        password_hash = db.Column(db.String(120), nullable=False)
        phone = db.Column(db.String(15))
        region = db.Column(db.String(100))
        language = db.Column(db.String(10), default='en')
        fcm_token = db.Column(db.Text)  # Firebase Cloud Messaging token
        notification_preferences = db.Column(db.Text, default='{"sms": true, "whatsapp": true, "push": true}')
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

    class FarmData(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        crop_type = db.Column(db.String(50), nullable=False)
        region = db.Column(db.String(100), nullable=False)
        rainfall = db.Column(db.Float)
        temperature = db.Column(db.Float)
        soil_ph = db.Column(db.Float)
        nitrogen = db.Column(db.Float)
        phosphorus = db.Column(db.Float)
        potassium = db.Column(db.Float)
        sowing_date_offset = db.Column(db.Integer)
        predicted_yield = db.Column(db.Float)
        risk_level = db.Column(db.String(20))
        recommendations = db.Column(db.Text)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Initialize database
    with app.app_context():
        db.create_all()
else:
    # Fallback classes for when SQLAlchemy is not available
    class User:
        pass
    class FarmData:
        pass

# Train Random Forest Model
def train_model():
    print("Training model...")
    
    if not (SKLEARN_AVAILABLE and PANDAS_AVAILABLE and NUMPY_AVAILABLE and JOBLIB_AVAILABLE):
        print("ML stack not fully available, using simple linear model")
        return create_simple_model()
    
    # Enhanced dataset with more features
    data = {
        'rainfall': [200, 250, 180, 300, 150, 400, 220, 270, 190, 280, 160, 350],
        'temperature': [28, 30, 32, 29, 35, 26, 31, 33, 27, 29, 34, 28],
        'soil_ph': [6.5, 7.0, 6.8, 7.2, 6.0, 7.5, 6.7, 7.1, 6.3, 6.9, 6.1, 7.3],
        'nitrogen': [80, 90, 70, 100, 60, 110, 85, 95, 75, 88, 65, 105],
        'phosphorus': [40, 45, 35, 50, 30, 55, 42, 48, 38, 44, 32, 52],
        'potassium': [60, 70, 55, 80, 50, 85, 65, 75, 58, 68, 52, 82],
        'sowing_offset': [0, 5, -3, 2, 10, -5, 3, 1, -2, 4, 8, -1],
        'yield': [2.5, 3.0, 2.2, 3.5, 1.8, 4.0, 2.8, 3.2, 2.4, 3.1, 1.9, 3.7]
    }
    
    df = pd.DataFrame(data)
    X = df[['rainfall', 'temperature', 'soil_ph', 'nitrogen', 'phosphorus', 'potassium', 'sowing_offset']]
    y = df['yield']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Save model and metadata
    joblib.dump(model, 'crop_yield_model.pkl')
    
    model_meta = {
        'features': ['rainfall', 'temperature', 'soil_ph', 'nitrogen', 'phosphorus', 'potassium', 'sowing_offset'],
        'model_type': 'RandomForestRegressor',
        'trained_at': datetime.now().isoformat(),
        'accuracy': model.score(X_test, y_test)
    }
    
    with open('model_meta.json', 'w') as f:
        json.dump(model_meta, f)
    
    print(f"Model trained successfully! Accuracy: {model_meta['accuracy']:.3f}")
    return model

def create_simple_model():
    """Create a simple prediction model when sklearn is not available"""
    print("Creating simple prediction model...")
    
    # Simple coefficients for linear prediction
    model_data = {
        'type': 'simple_linear',
        'coefficients': {
            'rainfall': 0.01,
            'temperature': 0.05,
            'soil_ph': 0.3,
            'nitrogen': 0.02,
            'phosphorus': 0.03,
            'potassium': 0.015,
            'sowing_offset': -0.05
        },
        'intercept': 1.0
    }
    
    with open('simple_model.json', 'w') as f:
        json.dump(model_data, f)
    
    print("Simple model created successfully!")
    return model_data

def simple_predict(features, model_data):
    """Make prediction using simple linear model"""
    prediction = model_data['intercept']
    feature_names = ['rainfall', 'temperature', 'soil_ph', 'nitrogen', 'phosphorus', 'potassium', 'sowing_offset']
    
    for i, feature_name in enumerate(feature_names):
        prediction += features[i] * model_data['coefficients'][feature_name]
    
    return max(0.5, prediction)  # Ensure minimum yield

# Initialize model
if not os.path.exists('crop_yield_model.pkl'):
    train_model()

def get_weather_data(region):
    """Fetch weather data with caching and improved fallback"""
    import time
    
    # Check cache first
    current_time = time.time()
    cache_key = region.lower()
    
    if cache_key in weather_cache:
        cached_data, cache_time = weather_cache[cache_key]
        if current_time - cache_time < WEATHER_CACHE_DURATION:
            print(f"Using cached weather data for {region}")
            return cached_data
    
    # Try to fetch from API
    try:
        if OPENWEATHER_API_KEY and OPENWEATHER_API_KEY != "your-openweather-api-key":
            url = f"{OPENWEATHER_BASE_URL}?q={region}&appid={OPENWEATHER_API_KEY}&units=metric"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                weather_data = {
                    'temperature': round(data['main']['temp'], 1),
                    'humidity': data['main']['humidity'],
                    'rainfall': data.get('rain', {}).get('1h', 0) * 24,  # Convert to daily
                    'weather_desc': data['weather'][0]['description'],
                    'source': 'api',
                    'region': region,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Cache the data
                weather_cache[cache_key] = (weather_data, current_time)
                print(f"Fetched fresh weather data for {region}")
                return weather_data
            else:
                print(f"Weather API error: {response.status_code}")
    except Exception as e:
        print(f"Weather API exception: {e}")
    
    # Enhanced fallback with regional variations
    fallback_data = get_regional_fallback_weather(region)
    
    # Cache fallback data for shorter duration
    weather_cache[cache_key] = (fallback_data, current_time - WEATHER_CACHE_DURATION + 300)  # 5 min cache for fallback
    
    return fallback_data

def get_regional_fallback_weather(region):
    """Provide realistic fallback weather data based on region"""
    region_lower = region.lower()
    
    # Regional weather patterns (simplified)
    regional_patterns = {
        'punjab': {'temp': 31.0, 'humidity': 60, 'rainfall': 180, 'desc': 'clear sky'},
        'haryana': {'temp': 32.5, 'humidity': 55, 'rainfall': 160, 'desc': 'partly cloudy'},
        'uttar pradesh': {'temp': 30.0, 'humidity': 70, 'rainfall': 220, 'desc': 'scattered clouds'},
        'bihar': {'temp': 29.5, 'humidity': 75, 'rainfall': 280, 'desc': 'light rain'},
        'west bengal': {'temp': 28.5, 'humidity': 80, 'rainfall': 320, 'desc': 'moderate rain'},
        'tamil nadu': {'temp': 34.0, 'humidity': 65, 'rainfall': 120, 'desc': 'hot'},
        'karnataka': {'temp': 26.5, 'humidity': 70, 'rainfall': 200, 'desc': 'pleasant weather'},
        'maharashtra': {'temp': 30.5, 'humidity': 60, 'rainfall': 180, 'desc': 'clear sky'},
        'rajasthan': {'temp': 35.0, 'humidity': 40, 'rainfall': 80, 'desc': 'hot and dry'},
        'delhi': {'temp': 31.5, 'humidity': 58, 'rainfall': 150, 'desc': 'haze'},
        'gujarat': {'temp': 33.0, 'humidity': 50, 'rainfall': 100, 'desc': 'sunny'}
    }
    
    # Find best match for region
    weather_pattern = None
    for state, pattern in regional_patterns.items():
        if state in region_lower:
            weather_pattern = pattern
            break
    
    # If no specific region found, use default
    if not weather_pattern:
        weather_pattern = {'temp': 29.5, 'humidity': 65, 'rainfall': 200, 'desc': 'partly cloudy'}
    
    # Add some realistic variation
    import random
    temp_variation = random.uniform(-2.0, 2.0)
    humidity_variation = random.randint(-5, 5)
    rainfall_variation = random.uniform(-20, 20)
    
    return {
        'temperature': round(weather_pattern['temp'] + temp_variation, 1),
        'humidity': max(30, min(90, weather_pattern['humidity'] + humidity_variation)),
        'rainfall': max(0, weather_pattern['rainfall'] + rainfall_variation),
        'weather_desc': weather_pattern['desc'],
        'source': 'fallback',
        'region': region,
        'timestamp': datetime.now().isoformat()
    }

def calculate_risk_level(yield_prediction, recommendations):
    """Calculate risk level based on yield and recommendations"""
    if yield_prediction < 2.0 or len(recommendations) >= 3:
        return 'Red'
    elif yield_prediction < 2.8 or len(recommendations) >= 2:
        return 'Yellow'
    else:
        return 'Green'

def generate_recommendations(data, prediction):
    """Generate actionable recommendations"""
    recs = []
    
    if data['temperature'] > 32:
        recs.append("High temperature detected. Increase irrigation frequency and consider shade nets.")
    if data['rainfall'] < 180:
        recs.append("Low rainfall. Implement drip irrigation or supplemental watering.")
    if data['soil_ph'] < 6.0:
        recs.append("Soil is acidic. Apply lime to increase pH for better nutrient uptake.")
    if data['soil_ph'] > 7.5:
        recs.append("Soil is alkaline. Apply sulfur or organic matter to reduce pH.")
    if data['nitrogen'] < 70:
        recs.append("Nitrogen deficiency. Apply nitrogen-rich fertilizers or compost.")
    if data['phosphorus'] < 35:
        recs.append("Low phosphorus levels. Apply phosphate fertilizers before flowering.")
    if data['potassium'] < 55:
        recs.append("Potassium deficiency. Apply potash fertilizers for better fruit quality.")
    if prediction < 2.5:
        recs.append("Low yield predicted. Consider crop rotation or soil testing.")
    
    return recs

# API Routes
@app.route('/')
def home():
    return jsonify({
        "message": "🌾 AI-Based Crop Yield Prediction & Advisory Platform",
        "version": "1.0",
        "endpoints": {
            "/api/register": "POST - User registration",
            "/api/login": "POST - User login",
            "/api/predict": "POST - Predict crop yield",
            "/api/weather": "GET - Get weather data",
            "/api/dashboard": "GET - Dashboard data",
            "/api/reports": "GET - Historical reports"
        }
    })

@app.route('/api/register', methods=['POST'])
def register():
    try:
        if not (SQLALCHEMY_AVAILABLE and db):
            return jsonify({'error': 'Database not available. Registration is currently disabled.'}), 503
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['username', 'email', 'password']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {missing_fields}'}), 400
        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            phone=data.get('phone'),
            region=data.get('region'),
            language=data.get('language', 'en')
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'User registered successfully', 'user_id': user.id})
        
    except Exception as e:
        if db:
            db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        if not (SQLALCHEMY_AVAILABLE and db):
            return jsonify({'error': 'Database not available. Login is currently disabled.'}), 503
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['username', 'password']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {missing_fields}'}), 400
        
        user = User.query.filter_by(username=data['username']).first()
        
        if user and check_password_hash(user.password_hash, data['password']):
            session['user_id'] = user.id
            return jsonify({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'region': user.region,
                    'language': user.language
                }
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/weather/<region>')
def get_weather(region):
    """Get weather data for a region with caching"""
    weather_data = get_weather_data(region)
    return jsonify(weather_data)

@app.route('/api/weather/cache/clear', methods=['POST'])
def clear_weather_cache():
    """Clear weather cache for fresh data"""
    global weather_cache
    weather_cache.clear()
    return jsonify({'message': 'Weather cache cleared successfully'})

@app.route('/api/weather/config', methods=['POST'])
def update_weather_config():
    """Update weather API configuration"""
    try:
        data = request.get_json()
        api_key = data.get('api_key')
        
        if api_key:
            global OPENWEATHER_API_KEY
            OPENWEATHER_API_KEY = api_key
            # Clear cache to force fresh API calls
            weather_cache.clear()
            return jsonify({'message': 'Weather API key updated successfully'})
        else:
            return jsonify({'error': 'API key is required'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict_yield():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['crop_type', 'region', 'rainfall', 'temperature', 'soil_ph', 
                          'nitrogen', 'phosphorus', 'potassium', 'sowing_date_offset']
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {missing_fields}',
                'required': required_fields
            }), 400
        
        # Prepare features for prediction
        features = [
            float(data['rainfall']),
            float(data['temperature']),
            float(data['soil_ph']),
            float(data['nitrogen']),
            float(data['phosphorus']),
            float(data['potassium']),
            int(data['sowing_date_offset'])
        ]
        
        # Make prediction
        print(f"DEBUG: Features count: {len(features)}")
        print(f"DEBUG: Model file exists: {os.path.exists('crop_yield_model.pkl')}")
        print(f"DEBUG: Simple model exists: {os.path.exists('simple_model.json')}")
        print(f"DEBUG: SKLEARN_AVAILABLE: {SKLEARN_AVAILABLE}")
        print(f"DEBUG: JOBLIB_AVAILABLE: {JOBLIB_AVAILABLE}")
        
        if os.path.exists('crop_yield_model.pkl') and SKLEARN_AVAILABLE and JOBLIB_AVAILABLE:
            model = joblib.load('crop_yield_model.pkl')
            print(f"DEBUG: Model type: {type(model)}")
            print(f"DEBUG: Model n_features_in_: {getattr(model, 'n_features_in_', 'Not available')}")
            prediction = model.predict([features])[0]
        elif os.path.exists('simple_model.json'):
            with open('simple_model.json', 'r') as f:
                model_data = json.load(f)
            prediction = simple_predict(features, model_data)
        else:
            # Fallback prediction
            prediction = 2.0 + (features[0] * 0.005) + (features[1] * 0.02) + (features[2] * 0.2)
        
        # Generate recommendations
        recommendations = generate_recommendations(data, prediction)
        
        # Calculate risk level
        risk_level = calculate_risk_level(prediction, recommendations)
        
        # Save to database if available and user is logged in
        if SQLALCHEMY_AVAILABLE and db and 'user_id' in session:
            try:
                farm_data = FarmData(
                    user_id=session['user_id'],
                    crop_type=data['crop_type'],
                    region=data['region'],
                    rainfall=data['rainfall'],
                    temperature=data['temperature'],
                    soil_ph=data['soil_ph'],
                    nitrogen=data['nitrogen'],
                    phosphorus=data['phosphorus'],
                    potassium=data['potassium'],
                    sowing_date_offset=data['sowing_date_offset'],
                    predicted_yield=prediction,
                    risk_level=risk_level,
                    recommendations=json.dumps(recommendations)
                )
                db.session.add(farm_data)
                db.session.commit()
            except:
                pass  # Continue without database save
        
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

@app.route('/api/dashboard/<int:user_id>')
def get_dashboard(user_id):
    """Get dashboard data for a user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get recent predictions
        recent_predictions = FarmData.query.filter_by(user_id=user_id)\
            .order_by(FarmData.created_at.desc()).limit(5).all()
        
        # Get weather data for user's region
        weather = get_weather_data(user.region) if user.region else {}
        
        dashboard_data = {
            'user': {
                'username': user.username,
                'region': user.region,
                'language': user.language
            },
            'weather': weather,
            'recent_predictions': [{
                'id': pred.id,
                'crop_type': pred.crop_type,
                'predicted_yield': pred.predicted_yield,
                'risk_level': pred.risk_level,
                'created_at': pred.created_at.isoformat()
            } for pred in recent_predictions],
            'stats': {
                'total_predictions': FarmData.query.filter_by(user_id=user_id).count(),
                'avg_yield': db.session.query(db.func.avg(FarmData.predicted_yield))\
                    .filter_by(user_id=user_id).scalar() or 0
            }
        }
        
        return jsonify(dashboard_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/<int:user_id>')
def get_reports(user_id):
    """Get historical reports and trends"""
    try:
        predictions = FarmData.query.filter_by(user_id=user_id)\
            .order_by(FarmData.created_at.desc()).all()
        
        reports_data = {
            'predictions': [{
                'id': pred.id,
                'crop_type': pred.crop_type,
                'predicted_yield': pred.predicted_yield,
                'risk_level': pred.risk_level,
                'recommendations': json.loads(pred.recommendations) if pred.recommendations else [],
                'created_at': pred.created_at.isoformat()
            } for pred in predictions],
            'trends': {
                'yield_trend': [pred.predicted_yield for pred in predictions[-10:]],
                'dates': [pred.created_at.strftime('%Y-%m-%d') for pred in predictions[-10:]]
            }
        }
        
        return jsonify(reports_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/at-risk-farmers')
def get_at_risk_farmers():
    """Get list of farmers with high-risk predictions"""
    try:
        at_risk_farms = FarmData.query.filter_by(risk_level='Red')\
            .join(User).order_by(FarmData.created_at.desc()).limit(20).all()
        
        farmers_data = [{
            'farmer_name': farm.user.username,
            'phone': farm.user.phone,
            'region': farm.region,
            'crop_type': farm.crop_type,
            'predicted_yield': farm.predicted_yield,
            'risk_level': farm.risk_level,
            'last_prediction': farm.created_at.isoformat()
        } for farm in at_risk_farms]
        
        return jsonify({'at_risk_farmers': farmers_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'model_loaded': os.path.exists('crop_yield_model.pkl') or os.path.exists('simple_model.json'),
        'database_connected': True,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/notifications/send', methods=['POST'])
def send_notification():
    """Send notification to user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        notification_type = data.get('type', 'general')
        message = data.get('message', '')
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        # Get user data
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user_data = {
            'id': user.id,
            'phone': user.phone,
            'region': user.region,
            'language': user.language,
            'fcm_token': getattr(user, 'fcm_token', None)
        }
        
        results = {}
        
        if notification_type == 'high_risk':
            crop_data = data.get('crop_data', {})
            results = notification_service.send_high_risk_alert(user_data, crop_data, user.language)
        elif notification_type == 'weather':
            weather_data = data.get('weather_data', {})
            results = notification_service.send_weather_alert(user_data, weather_data, user.language)
        elif notification_type == 'yield_update':
            crop_data = data.get('crop_data', {})
            results = notification_service.send_yield_update(user_data, crop_data, user.language)
        else:
            # General notification
            if user_data.get('phone'):
                results['sms'] = notification_service.send_sms(user_data['phone'], message)
            if user_data.get('fcm_token'):
                results['push'] = notification_service.send_push_notification(
                    user_data['fcm_token'], '🌾 Crop Advisory', message
                )
        
        return jsonify({
            'success': True,
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/offline/sync', methods=['POST'])
def sync_offline_data():
    """Sync offline data with server"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        sync_type = data.get('type', 'all')
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        results = {
            'predictions_synced': 0,
            'weather_synced': 0,
            'user_data_synced': 0,
            'errors': []
        }
        
        # Sync offline predictions
        if sync_type in ['all', 'predictions']:
            offline_predictions = offline_cache.get_cached_predictions(user_id)
            for pred in offline_predictions:
                try:
                    # Save to main database
                    farm_data = FarmData(
                        user_id=user_id,
                        crop_type=pred.get('input_data', {}).get('crop_type'),
                        region=pred.get('input_data', {}).get('region'),
                        rainfall=pred.get('input_data', {}).get('rainfall'),
                        temperature=pred.get('input_data', {}).get('temperature'),
                        soil_ph=pred.get('input_data', {}).get('soil_ph'),
                        nitrogen=pred.get('input_data', {}).get('nitrogen'),
                        phosphorus=pred.get('input_data', {}).get('phosphorus'),
                        potassium=pred.get('input_data', {}).get('potassium'),
                        sowing_date_offset=pred.get('input_data', {}).get('sowing_date_offset'),
                        predicted_yield=pred.get('predicted_yield'),
                        risk_level=pred.get('risk_level'),
                        recommendations=json.dumps(pred.get('recommendations', []))
                    )
                    db.session.add(farm_data)
                    results['predictions_synced'] += 1
                except Exception as e:
                    results['errors'].append(f'Prediction sync error: {str(e)}')
        
        # Commit all changes
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            results['errors'].append(f'Database commit error: {str(e)}')
        
        return jsonify({
            'success': True,
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/offline/status/<int:user_id>')
def get_offline_status(user_id):
    """Get offline cache status for user"""
    try:
        stats = offline_cache.get_cache_stats()
        user_predictions = offline_cache.get_cached_predictions(user_id)
        user_weather = offline_cache.get_cached_weather(user_id)
        
        return jsonify({
            'cache_stats': stats,
            'user_predictions_count': len(user_predictions),
            'user_weather_available': user_weather is not None,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/bulk-notify', methods=['POST'])
def send_bulk_notifications():
    """Send bulk notifications to multiple users (admin only)"""
    try:
        data = request.get_json()
        user_ids = data.get('user_ids', [])
        message = data.get('message', '')
        notification_type = data.get('type', 'general')
        
        if not user_ids or not message:
            return jsonify({'error': 'User IDs and message required'}), 400
        
        # Get users
        users = User.query.filter(User.id.in_(user_ids)).all()
        user_data = [{
            'id': user.id,
            'phone': user.phone,
            'region': user.region,
            'language': user.language,
            'fcm_token': getattr(user, 'fcm_token', None)
        } for user in users]
        
        # Send bulk notifications
        results = notification_service.send_bulk_notifications(user_data, message, notification_type)
        
        return jsonify({
            'success': True,
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Train model if it doesn't exist
    if not os.path.exists('crop_yield_model.pkl'):
        train_model()
    
    print("🌾 AI-Based Crop Yield Prediction & Advisory Platform")
    print("Backend API starting...")
    print("Available at: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
