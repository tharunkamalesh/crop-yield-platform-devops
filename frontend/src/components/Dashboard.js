import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import axios from 'axios';
import { Cloud, Thermometer, Droplets, AlertTriangle, CheckCircle, XCircle, Wifi, WifiOff, RefreshCw } from 'lucide-react';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement
);

const Dashboard = () => {
  const { user } = useAuth();
  const { t } = useLanguage();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [offlineStatus, setOfflineStatus] = useState({ online: true, lastSync: null });
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    fetchDashboardData();
    checkOfflineStatus();
    prepareChartData();
  }, [user]);

  const checkOfflineStatus = async () => {
    try {
      const response = await axios.get(`/api/offline/status/${user.id}`);
      setOfflineStatus({
        online: true,
        lastSync: response.data.timestamp,
        cacheStats: response.data.cache_stats
      });
    } catch (error) {
      setOfflineStatus({ online: false, lastSync: null });
    }
  };

  const prepareChartData = () => {
    if (dashboardData?.recent_predictions) {
      const predictions = dashboardData.recent_predictions;
      
      // Yield trend chart
      const yieldChartData = {
        labels: predictions.map(p => new Date(p.created_at).toLocaleDateString()),
        datasets: [{
          label: 'Predicted Yield (tons/ha)',
          data: predictions.map(p => p.predicted_yield),
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.1
        }]
      };

      // Risk level distribution
      const riskCounts = predictions.reduce((acc, p) => {
        acc[p.risk_level] = (acc[p.risk_level] || 0) + 1;
        return acc;
      }, {});

      const riskChartData = {
        labels: Object.keys(riskCounts),
        datasets: [{
          data: Object.values(riskCounts),
          backgroundColor: [
            'rgba(34, 197, 94, 0.8)',
            'rgba(234, 179, 8, 0.8)',
            'rgba(239, 68, 68, 0.8)'
          ],
          borderWidth: 2,
          borderColor: '#fff'
        }]
      };

      setChartData({ yield: yieldChartData, risk: riskChartData });
    }
  };

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get(`/api/dashboard/${user.id}`);
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
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
      case 'Green': return <CheckCircle className="h-5 w-5" />;
      case 'Yellow': return <AlertTriangle className="h-5 w-5" />;
      case 'Red': return <XCircle className="h-5 w-5" />;
      default: return <AlertTriangle className="h-5 w-5" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-green-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pt-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            {t('welcomeBack')}, {user.username}! 🌾
          </h1>
          <p className="text-gray-600 mt-2">
            Monitor your crop predictions and get actionable insights
          </p>
        </div>

        {/* Weather Card */}
        {dashboardData?.weather && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <Cloud className="h-6 w-6 mr-2 text-blue-500" />
              {t('currentWeather')} - {user.region}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="flex items-center space-x-3">
                <Thermometer className="h-8 w-8 text-red-500" />
                <div>
                  <p className="text-sm text-gray-600">Temperature</p>
                  <p className="text-2xl font-bold">{dashboardData.weather.temperature}°C</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <Droplets className="h-8 w-8 text-blue-500" />
                <div>
                  <p className="text-sm text-gray-600">Rainfall</p>
                  <p className="text-2xl font-bold">{dashboardData.weather.rainfall}mm</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <Cloud className="h-8 w-8 text-gray-500" />
                <div>
                  <p className="text-sm text-gray-600">Conditions</p>
                  <p className="text-lg font-semibold capitalize">{dashboardData.weather.weather_desc}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Offline Status */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-800 flex items-center">
              {offlineStatus.online ? (
                <Wifi className="h-6 w-6 mr-2 text-green-500" />
              ) : (
                <WifiOff className="h-6 w-6 mr-2 text-red-500" />
              )}
              {offlineStatus.online ? 'Online Mode' : 'Offline Mode'}
            </h2>
            <button
              onClick={checkOfflineStatus}
              className="flex items-center px-3 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </button>
          </div>
          {offlineStatus.cacheStats && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
              <div className="text-center">
                <p className="text-sm text-gray-600">Cached Predictions</p>
                <p className="text-lg font-semibold text-blue-600">
                  {offlineStatus.cacheStats.unsynced_predictions || 0}
                </p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-600">Weather Data</p>
                <p className="text-lg font-semibold text-green-600">
                  {offlineStatus.cacheStats.valid_weather || 0}
                </p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-600">Pending Sync</p>
                <p className="text-lg font-semibold text-yellow-600">
                  {offlineStatus.cacheStats.pending_sync || 0}
                </p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-600">Last Sync</p>
                <p className="text-sm font-semibold text-gray-600">
                  {offlineStatus.lastSync ? new Date(offlineStatus.lastSync).toLocaleString() : 'Never'}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Total Predictions</h3>
            <p className="text-3xl font-bold text-green-600">
              {dashboardData?.stats?.total_predictions || 0}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Average Yield</h3>
            <p className="text-3xl font-bold text-blue-600">
              {(dashboardData?.stats?.avg_yield || 0).toFixed(1)} t/ha
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Risk Status</h3>
            <div className="flex items-center space-x-2">
              {dashboardData?.recent_predictions?.[0] && (
                <>
                  {getRiskIcon(dashboardData.recent_predictions[0].risk_level)}
                  <span className={`font-semibold ${
                    dashboardData.recent_predictions[0].risk_level === 'Green' ? 'text-green-600' :
                    dashboardData.recent_predictions[0].risk_level === 'Yellow' ? 'text-yellow-600' :
                    'text-red-600'
                  }`}>
                    {t(dashboardData.recent_predictions[0].risk_level === 'Green' ? 'safe' :
                       dashboardData.recent_predictions[0].risk_level === 'Yellow' ? 'warning' : 'risk')}
                  </span>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Charts */}
        {chartData && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Yield Trend</h3>
              <Line 
                data={chartData.yield}
                options={{
                  responsive: true,
                  plugins: {
                    legend: {
                      position: 'top',
                    },
                    title: {
                      display: true,
                      text: 'Predicted Yield Over Time'
                    }
                  },
                  scales: {
                    y: {
                      beginAtZero: true,
                      title: {
                        display: true,
                        text: 'Yield (tons/ha)'
                      }
                    }
                  }
                }}
              />
            </div>
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Risk Distribution</h3>
              <Doughnut 
                data={chartData.risk}
                options={{
                  responsive: true,
                  plugins: {
                    legend: {
                      position: 'bottom',
                    },
                    title: {
                      display: true,
                      text: 'Risk Level Distribution'
                    }
                  }
                }}
              />
            </div>
          </div>
        )}

        {/* Recent Predictions */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-6">
            {t('recentPredictions')}
          </h2>
          
          {dashboardData?.recent_predictions?.length > 0 ? (
            <div className="space-y-4">
              {dashboardData.recent_predictions.map((prediction) => (
                <div key={prediction.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="font-semibold text-lg">{prediction.crop_type}</h3>
                      <p className="text-gray-600 text-sm">
                        {new Date(prediction.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className={`px-3 py-1 rounded-full border flex items-center space-x-1 ${getRiskColor(prediction.risk_level)}`}>
                      {getRiskIcon(prediction.risk_level)}
                      <span className="font-medium">
                        {t(prediction.risk_level === 'Green' ? 'safe' :
                           prediction.risk_level === 'Yellow' ? 'warning' : 'risk')}
                      </span>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">{t('yieldPrediction')}</p>
                      <p className="text-2xl font-bold text-green-600">
                        {prediction.predicted_yield} t/ha
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-500">No predictions yet. Start by entering your farm data!</p>
              <button
                onClick={() => window.location.href = '/data-entry'}
                className="mt-4 bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700 transition-colors"
              >
                Add Farm Data
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
