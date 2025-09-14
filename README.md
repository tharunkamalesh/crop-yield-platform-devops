# 🌾 AI Crop Yield Prediction & Advisory Platform

A comprehensive web and mobile application that uses machine learning to predict crop yields and provide farming recommendations. Built with React frontend, Flask backend, and integrated with weather APIs and notification services.

## ✨ Features

### 🎯 Core Functionality
- **AI-Powered Yield Prediction**: Uses Random Forest ML model to predict crop yields (tons/hectare)
- **Real-time Weather Integration**: Connects to OpenWeather API for live weather data
- **Smart Risk Assessment**: Automatically determines risk levels (Green/Yellow/Red) based on predictions
- **Actionable Recommendations**: Provides specific farming advice based on soil and weather conditions

### 📱 Multi-Platform Support
- **Responsive Web App**: Works on desktop, tablet, and mobile browsers
- **Offline Mode**: Cache data locally and sync when online
- **Push Notifications**: Real-time alerts via Firebase Cloud Messaging
- **Multi-language**: English, Hindi, and Tamil support

### 🔔 Notification System
- **SMS Alerts**: Via Twilio for critical alerts
- **WhatsApp Messages**: Automated farming advice
- **Push Notifications**: In-app and mobile notifications
- **Bulk Notifications**: Admin panel for mass communication

### 📊 Analytics & Reporting
- **Interactive Charts**: Yield trends and risk distribution using Chart.js
- **Historical Data**: Track predictions over time
- **Performance Metrics**: Monitor farming success rates
- **Export Reports**: Download data for analysis

## 🏗️ Architecture

### Frontend (React)
- **Components**: Dashboard, Data Entry, Reports, Settings, Login
- **State Management**: React Context for authentication and language
- **Styling**: Tailwind CSS for responsive design
- **Charts**: Chart.js with react-chartjs-2 for data visualization
- **Offline Support**: Service Worker and localStorage for offline functionality

### Backend (Flask)
- **API Endpoints**: RESTful API for all operations
- **ML Integration**: Scikit-learn Random Forest model
- **Database**: SQLite with SQLAlchemy ORM
- **Weather API**: OpenWeather integration
- **Notifications**: Twilio SMS/WhatsApp + Firebase push

### Machine Learning
- **Model**: Random Forest Regressor
- **Features**: Rainfall, temperature, soil pH, nutrients (N/P/K), sowing date
- **Training**: Synthetic dataset with realistic farming parameters
- **Prediction**: Yield in tons per hectare with confidence intervals

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- SQLite3
- OpenWeather API key
- Twilio account (optional)
- Firebase project (optional)

### Backend Setup
```bash
cd backend
pip install -r requirements.txt

# Set environment variables
export OPENWEATHER_API_KEY="your-api-key"
export TWILIO_ACCOUNT_SID="your-twilio-sid"
export TWILIO_AUTH_TOKEN="your-twilio-token"
export FIREBASE_SERVER_KEY="your-firebase-key"

# Run the backend
python app.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Database Setup
The application automatically creates the required database tables on first run.

## 📋 API Endpoints

### Authentication
- `POST /api/register` - User registration
- `POST /api/login` - User login
- `GET /api/dashboard/{user_id}` - Get user dashboard data

### Predictions
- `POST /api/predict` - Generate crop yield prediction
- `GET /api/reports/{user_id}` - Get historical predictions

### Weather
- `GET /api/weather/{region}` - Get current weather for region

### Notifications
- `POST /api/notifications/send` - Send notification to user
- `POST /api/admin/bulk-notify` - Send bulk notifications

### Offline Sync
- `POST /api/offline/sync` - Sync offline data with server
- `GET /api/offline/status/{user_id}` - Get offline cache status

## 🌍 Language Support

### English 
- Primary interface language
- Complete feature coverage
- Technical terminology

### Hindi 
- भारतीय किसानों के लिए
- स्थानीय फसल नाम
- सरल भाषा में सलाह

### Tamil 
- தமிழ் விவசாயிகளுக்காக
- பிராந்திய பயிர் வகைகள்
- புரிந்துகொள்ளக்கூடிய வழிகாட்டுதல்

## 🔧 Configuration

### Environment Variables
```bash
# Required
OPENWEATHER_API_KEY=your-openweather-api-key

# Optional (for notifications)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+1234567890
FIREBASE_SERVER_KEY=your-firebase-server-key
FIREBASE_PROJECT_ID=your-firebase-project-id
```

### Model Configuration
- **Training Data**: Located in `backend/app.py`
- **Model File**: `crop_yield_model.pkl` (auto-generated)
- **Parameters**: Configurable in `train_model()` function

## 📱 Offline Functionality

### Local Storage
- **Predictions**: Cached in browser localStorage
- **Weather Data**: Stored with 6-hour expiry
- **User Preferences**: Language and settings saved locally

### Sync Mechanism
- **Automatic**: Syncs when connection is restored
- **Manual**: User-triggered sync button
- **Conflict Resolution**: Server data takes precedence

### Offline Prediction
- **Local Algorithm**: Simple yield calculation when offline
- **Data Validation**: Basic input validation
- **Recommendations**: Standard farming advice

## 🎨 UI Components

### Dashboard
- Weather overview with real-time data
- Recent predictions with risk indicators
- Interactive charts for yield trends
- Offline status and sync information

### Data Entry
- Comprehensive farm data form
- Weather data auto-fetch
- Real-time validation
- Offline mode indicator

### Reports
- Historical prediction data
- Performance analytics
- Export functionality
- Trend analysis

### Settings
- Language preferences
- Notification settings
- Profile management
- Data export options

## 🔒 Security Features

- **Password Hashing**: bcrypt for secure storage
- **Session Management**: Flask sessions with secret key
- **Input Validation**: Server-side data validation
- **API Rate Limiting**: Basic request throttling
- **CORS Support**: Cross-origin resource sharing

## 📊 Performance

### Optimization
- **Lazy Loading**: Components load on demand
- **Image Optimization**: Compressed icons and graphics
- **Code Splitting**: Route-based code splitting
- **Caching**: Aggressive browser caching

### Monitoring
- **Health Checks**: `/api/health` endpoint
- **Error Logging**: Comprehensive error tracking
- **Performance Metrics**: Response time monitoring
- **Database Queries**: Query optimization

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

### API Testing
```bash
# Test prediction endpoint
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "crop_type": "Rice",
    "region": "Punjab",
    "rainfall": 250,
    "temperature": 30,
    "soil_ph": 6.8,
    "nitrogen": 85,
    "phosphorus": 42,
    "potassium": 65,
    "sowing_date_offset": 0
  }'
```

## 🚀 Deployment

### Production Setup
```bash
# Backend
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Frontend
npm run build
serve -s build -l 3000
```

### Docker Support
```bash
# Build and run
docker-compose up --build

# Individual services
docker build -t crop-backend ./backend
docker build -t crop-frontend ./frontend
```

### Environment Variables
Set production environment variables in your deployment platform:
- Database connection strings
- API keys and secrets
- Notification service credentials
- SSL certificates

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code Style
- **Python**: PEP 8 with Black formatter
- **JavaScript**: ESLint with Prettier
- **CSS**: Tailwind CSS classes
- **Documentation**: Clear docstrings and comments

## 🙏 Acknowledgments

- **OpenWeather**: Weather data API
- **Twilio**: SMS and WhatsApp integration
- **Firebase**: Push notification service
- **Chart.js**: Data visualization library
- **Tailwind CSS**: Utility-first CSS framework

## 📞 Support

### Documentation
- [API Reference](docs/API.md)
- [User Guide](docs/UserGuide.md)
- [Developer Guide](docs/DeveloperGuide.md)

### Contact
- **Email**: support@cropyield.ai
- **Issues**: GitHub Issues page
- **Discussions**: GitHub Discussions

### Community
- **Forum**: Community discussions
- **Discord**: Real-time chat support
- **YouTube**: Tutorial videos

---

**Built with ❤️ for farmers worldwide**

*Empowering agriculture through AI and technology*


