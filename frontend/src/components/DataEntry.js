import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import axios from 'axios';
import toast from 'react-hot-toast';
import { Leaf, Cloud, AlertTriangle, CheckCircle, XCircle, Wifi, WifiOff, Save } from 'lucide-react';

const DataEntry = () => {
  const { user } = useAuth();
  const { t } = useLanguage();
  const [formData, setFormData] = useState({
    crop_type: '',
    region: user?.region || '',
    rainfall: '',
    temperature: '',
    soil_ph: '',
    nitrogen: '',
    phosphorus: '',
    potassium: '',
    sowing_date_offset: ''
  });
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [weatherLoading, setWeatherLoading] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [offlineData, setOfflineData] = useState([]);

  const cropTypes = [
    'Rice', 'Wheat', 'Maize', 'Cotton', 'Sugarcane', 'Soybean', 
    'Groundnut', 'Sunflower', 'Mustard', 'Barley', 'Millets', 'Pulses'
  ];

  // Handle online/offline status
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Load offline data from localStorage
  useEffect(() => {
    const savedData = localStorage.getItem('offlinePredictions');
    if (savedData) {
      setOfflineData(JSON.parse(savedData));
    }
  }, []);

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const fetchWeatherData = async () => {
    if (!formData.region) {
      toast.error('Please enter region first');
      return;
    }

    setWeatherLoading(true);
    try {
      const response = await axios.get(`/api/weather/${formData.region}`);
      const weather = response.data;
      
      setFormData({
        ...formData,
        temperature: weather.temperature.toString(),
        rainfall: weather.rainfall.toString()
      });
      
      toast.success('Weather data fetched successfully!');
    } catch (error) {
      toast.error('Failed to fetch weather data');
    } finally {
      setWeatherLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const predictionData = {
      ...formData,
      rainfall: parseFloat(formData.rainfall),
      temperature: parseFloat(formData.temperature),
      soil_ph: parseFloat(formData.soil_ph),
      nitrogen: parseFloat(formData.nitrogen),
      phosphorus: parseFloat(formData.phosphorus),
      potassium: parseFloat(formData.potassium),
      sowing_date_offset: parseInt(formData.sowing_date_offset)
    };

    if (isOnline) {
      try {
        const response = await axios.post('/api/predict', predictionData);
        setPrediction(response.data);
        toast.success('Prediction generated successfully!');
        
        // Clear form after successful submission
        setFormData({
          crop_type: '',
          region: user?.region || '',
          rainfall: '',
          temperature: '',
          soil_ph: '',
          nitrogen: '',
          phosphorus: '',
          potassium: '',
          sowing_date_offset: ''
        });
      } catch (error) {
        toast.error(error.response?.data?.error || 'Prediction failed');
      }
    } else {
      // Offline mode - store locally
      const offlinePrediction = {
        id: Date.now(),
        ...predictionData,
        timestamp: new Date().toISOString(),
        synced: false
      };
      
      const newOfflineData = [...offlineData, offlinePrediction];
      setOfflineData(newOfflineData);
      localStorage.setItem('offlinePredictions', JSON.stringify(newOfflineData));
      
      // Generate simple offline prediction
      const simplePrediction = generateOfflinePrediction(predictionData);
      setPrediction(simplePrediction);
      toast.success('Prediction saved offline! Will sync when online.');
    }
    
    setLoading(false);
  };

  const generateOfflinePrediction = (data) => {
    // Simple offline prediction algorithm
    let baseYield = 2.0;
    
    // Rainfall impact (optimal: 200-300mm)
    if (180 <= data.rainfall <= 350) {
      baseYield += 0.5;
    } else if (data.rainfall < 180) {
      baseYield -= 0.4;
    } else {
      baseYield += 0.2;
    }
    
    // Temperature impact (optimal: 26-32°C)
    if (26 <= data.temperature <= 32) {
      baseYield += 0.4;
    } else {
      baseYield -= 0.3;
    }
    
    // Soil pH impact (optimal: 6.0-7.5)
    if (6.0 <= data.soil_ph <= 7.5) {
      baseYield += 0.3;
    } else {
      baseYield -= 0.2;
    }
    
    // Nutrient impact
    const nutrientScore = (data.nitrogen + data.phosphorus + data.potassium) / 300;
    baseYield += nutrientScore;
    
    // Sowing date penalty
    const sowingPenalty = Math.abs(data.sowing_date_offset) * 0.05;
    baseYield -= sowingPenalty;
    
    const finalYield = Math.max(0.5, baseYield);
    
    // Generate recommendations
    const recommendations = [];
    if (data.temperature > 32) {
      recommendations.push("High temperature detected. Increase irrigation and use shade nets.");
    }
    if (data.rainfall < 180) {
      recommendations.push("Low rainfall. Consider drip irrigation system.");
    }
    if (data.soil_ph < 6.0) {
      recommendations.push("Acidic soil. Apply lime to increase pH.");
    }
    if (data.soil_ph > 7.5) {
      recommendations.push("Alkaline soil. Add organic matter to reduce pH.");
    }
    
    // Determine risk level
    let riskLevel = 'Green';
    if (finalYield < 2.0 || recommendations.length >= 3) {
      riskLevel = 'Red';
    } else if (finalYield < 2.8 || recommendations.length >= 2) {
      riskLevel = 'Yellow';
    }
    
    return {
      predicted_yield: Math.round(finalYield * 100) / 100,
      unit: 'tons/hectare',
      risk_level: riskLevel,
      recommendations: recommendations,
      input_data: data,
      timestamp: new Date().toISOString(),
      offline: true
    };
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'Green': return 'text-green-600 bg-green-50 border-green-200';
      case 'Yellow': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'Red': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getRiskIcon = (riskLevel) => {
    switch (riskLevel) {
      case 'Green': return <CheckCircle className="h-6 w-6" />;
      case 'Yellow': return <AlertTriangle className="h-6 w-6" />;
      case 'Red': return <XCircle className="h-6 w-6" />;
      default: return <AlertTriangle className="h-6 w-6" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 pt-16">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                <Leaf className="h-8 w-8 mr-3 text-green-600" />
                {t('farmDetails')}
              </h1>
              <p className="text-gray-600 mt-2">
                Enter your farm details to get AI-powered yield predictions and recommendations
              </p>
            </div>
            <div className="flex items-center space-x-2">
              {isOnline ? (
                <div className="flex items-center text-green-600">
                  <Wifi className="h-5 w-5 mr-2" />
                  <span className="text-sm font-medium">Online</span>
                </div>
              ) : (
                <div className="flex items-center text-red-600">
                  <WifiOff className="h-5 w-5 mr-2" />
                  <span className="text-sm font-medium">Offline</span>
                </div>
              )}
            </div>
          </div>
          
          {!isOnline && (
            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
              <p className="text-yellow-800 text-sm">
                <strong>Offline Mode:</strong> Your data will be saved locally and synced when you're back online.
              </p>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Data Entry Form */}
          <div className="bg-white rounded-lg shadow-md p-6">
            {offlineData.length > 0 && (
              <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
                <div className="flex items-center justify-between">
                  <p className="text-blue-800 text-sm">
                    <strong>Offline Data:</strong> {offlineData.length} prediction(s) waiting to sync
                  </p>
                  <button
                    onClick={() => {
                      if (isOnline) {
                        // TODO: Implement sync functionality
                        toast.success('Syncing offline data...');
                      }
                    }}
                    disabled={!isOnline}
                    className="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Save className="h-3 w-3 mr-1 inline" />
                    Sync
                  </button>
                </div>
              </div>
            )}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('cropType')}
                </label>
                <select
                  name="crop_type"
                  value={formData.crop_type}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="">Select crop type</option>
                  {cropTypes.map(crop => (
                    <option key={crop} value={crop}>{crop}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('region')}
                </label>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    name="region"
                    value={formData.region}
                    onChange={handleInputChange}
                    required
                    placeholder="e.g., Punjab, Tamil Nadu"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                  <button
                    type="button"
                    onClick={fetchWeatherData}
                    disabled={weatherLoading}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center"
                  >
                    <Cloud className="h-4 w-4 mr-1" />
                    {weatherLoading ? 'Loading...' : 'Get Weather'}
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {t('rainfall')}
                  </label>
                  <input
                    type="number"
                    name="rainfall"
                    value={formData.rainfall}
                    onChange={handleInputChange}
                    required
                    step="0.1"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {t('temperature')}
                  </label>
                  <input
                    type="number"
                    name="temperature"
                    value={formData.temperature}
                    onChange={handleInputChange}
                    required
                    step="0.1"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('soilPH')}
                </label>
                <input
                  type="number"
                  name="soil_ph"
                  value={formData.soil_ph}
                  onChange={handleInputChange}
                  required
                  step="0.1"
                  min="0"
                  max="14"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {t('nitrogen')}
                  </label>
                  <input
                    type="number"
                    name="nitrogen"
                    value={formData.nitrogen}
                    onChange={handleInputChange}
                    required
                    step="0.1"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {t('phosphorus')}
                  </label>
                  <input
                    type="number"
                    name="phosphorus"
                    value={formData.phosphorus}
                    onChange={handleInputChange}
                    required
                    step="0.1"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {t('potassium')}
                  </label>
                  <input
                    type="number"
                    name="potassium"
                    value={formData.potassium}
                    onChange={handleInputChange}
                    required
                    step="0.1"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('sowingOffset')}
                </label>
                <input
                  type="number"
                  name="sowing_date_offset"
                  value={formData.sowing_date_offset}
                  onChange={handleInputChange}
                  required
                  placeholder="Days from optimal sowing date (+/-)"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-green-600 text-white py-3 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 transition-colors font-semibold"
              >
                {loading ? t('loading') : t('predict')}
              </button>
            </form>
          </div>

          {/* Prediction Results */}
          {prediction && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-6">
                {t('yieldPrediction')}
              </h2>

              {/* Yield Result */}
              <div className="text-center mb-6">
                <div className="text-4xl font-bold text-green-600 mb-2">
                  {prediction.predicted_yield} t/ha
                </div>
                <p className="text-gray-600">Predicted yield for {formData.crop_type}</p>
              </div>

              {/* Risk Level */}
              <div className={`p-4 rounded-lg border mb-6 ${getRiskColor(prediction.risk_level)}`}>
                <div className="flex items-center space-x-2 mb-2">
                  {getRiskIcon(prediction.risk_level)}
                  <span className="font-semibold text-lg">
                    {t(prediction.risk_level === 'Green' ? 'safe' :
                       prediction.risk_level === 'Yellow' ? 'warning' : 'risk')}
                  </span>
                </div>
                <p className="text-sm">
                  {prediction.risk_level === 'Green' && 'Your crop is in good condition with optimal yield expected.'}
                  {prediction.risk_level === 'Yellow' && 'Moderate risk detected. Follow recommendations to improve yield.'}
                  {prediction.risk_level === 'Red' && 'High risk detected. Immediate action required to prevent crop loss.'}
                </p>
              </div>

              {/* Recommendations */}
              {prediction.recommendations && prediction.recommendations.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-800 mb-3">
                    {t('recommendations')}
                  </h3>
                  <div className="space-y-2">
                    {prediction.recommendations.map((rec, index) => (
                      <div key={index} className="flex items-start space-x-2 p-3 bg-blue-50 rounded-md">
                        <AlertTriangle className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                        <p className="text-sm text-blue-800">{rec}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <button
                onClick={() => setPrediction(null)}
                className="w-full mt-6 bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 transition-colors"
              >
                New Prediction
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DataEntry;
