import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { Settings as SettingsIcon, Globe, Bell, User, CloudRain, Key } from 'lucide-react';
import toast from 'react-hot-toast';

const Settings = () => {
  const { user } = useAuth();
  const { t, language, changeLanguage } = useLanguage();
  const [apiKey, setApiKey] = useState('');
  const [isUpdatingApi, setIsUpdatingApi] = useState(false);
  const [notifications, setNotifications] = useState({
    sms: true,
    email: true,
    push: false
  });

  const handleLanguageChange = (lang) => {
    changeLanguage(lang);
    toast.success('Language updated successfully!');
  };

  const handleNotificationChange = (type) => {
    setNotifications({
      ...notifications,
      [type]: !notifications[type]
    });
    toast.success('Notification preferences updated!');
  };

  const handleApiKeyUpdate = async () => {
    if (!apiKey.trim()) {
      toast.error('Please enter a valid API key');
      return;
    }

    setIsUpdatingApi(true);
    try {
      const response = await fetch('/api/weather/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ api_key: apiKey }),
      });

      const result = await response.json();
      
      if (response.ok) {
        toast.success('Weather API key updated successfully');
        setApiKey('');
      } else {
        toast.error(result.error || 'Failed to update API key');
      }
    } catch (error) {
      toast.error('Error updating API key');
    } finally {
      setIsUpdatingApi(false);
    }
  };

  const clearWeatherCache = async () => {
    try {
      const response = await fetch('/api/weather/cache/clear', {
        method: 'POST',
      });

      if (response.ok) {
        toast.success('Weather cache cleared successfully');
      } else {
        toast.error('Failed to clear weather cache');
      }
    } catch (error) {
      toast.error('Error clearing weather cache');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 pt-16">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            <SettingsIcon className="h-8 w-8 mr-3 text-green-600" />
            {t('settings')}
          </h1>
          <p className="text-gray-600 mt-2">
            Manage your account preferences and notification settings
          </p>
        </div>

        <div className="space-y-6">
          {/* Profile Settings */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <User className="h-6 w-6 mr-2 text-blue-500" />
              Profile Information
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('username')}
                </label>
                <input
                  type="text"
                  value={user?.username || ''}
                  disabled
                  className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('email')}
                </label>
                <input
                  type="email"
                  value={user?.email || ''}
                  disabled
                  className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('region')}
                </label>
                <input
                  type="text"
                  value={user?.region || ''}
                  disabled
                  className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50"
                />
              </div>
            </div>
          </div>

          {/* Language Settings */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <Globe className="h-6 w-6 mr-2 text-green-500" />
              Language Preferences
            </h2>
            <div className="space-y-3">
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => handleLanguageChange('en')}
                  className={`px-4 py-2 rounded-md border transition-colors ${
                    language === 'en' 
                      ? 'bg-green-500 text-white border-green-500' 
                      : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  English
                </button>
                <button
                  onClick={() => handleLanguageChange('hi')}
                  className={`px-4 py-2 rounded-md border transition-colors ${
                    language === 'hi' 
                      ? 'bg-green-500 text-white border-green-500' 
                      : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  हिंदी (Hindi)
                </button>
                <button
                  onClick={() => handleLanguageChange('ta')}
                  className={`px-4 py-2 rounded-md border transition-colors ${
                    language === 'ta' 
                      ? 'bg-green-500 text-white border-green-500' 
                      : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  தமிழ் (Tamil)
                </button>
              </div>
            </div>
          </div>

          {/* Notification Settings */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <Bell className="h-6 w-6 mr-2 text-yellow-500" />
              Notification Preferences
            </h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900">SMS Notifications</h3>
                  <p className="text-sm text-gray-600">Receive yield alerts via SMS</p>
                </div>
                <button
                  onClick={() => handleNotificationChange('sms')}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    notifications.sms ? 'bg-green-500' : 'bg-gray-300'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      notifications.sms ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900">Email Notifications</h3>
                  <p className="text-sm text-gray-600">Receive detailed reports via email</p>
                </div>
                <button
                  onClick={() => handleNotificationChange('email')}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    notifications.email ? 'bg-green-500' : 'bg-gray-300'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      notifications.email ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900">Push Notifications</h3>
                  <p className="text-sm text-gray-600">Browser notifications for urgent alerts</p>
                </div>
                <button
                  onClick={() => handleNotificationChange('push')}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    notifications.push ? 'bg-green-500' : 'bg-gray-300'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      notifications.push ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
            </div>
          </div>

          {/* Weather API Configuration */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <CloudRain className="h-6 w-6 mr-2 text-blue-500" />
              Weather API Configuration
            </h2>
            <div className="space-y-4">
              <div className="bg-blue-50 rounded-md p-4">
                <p className="text-sm text-blue-800 mb-3">
                  <strong>OpenWeather API:</strong> Configure your API key for real-time weather data. 
                  Get your free API key from{' '}
                  <a href="https://openweathermap.org/api" target="_blank" rel="noopener noreferrer" className="underline">
                    OpenWeatherMap
                  </a>
                </p>
                <div className="flex space-x-3">
                  <input
                    type="password"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder="Enter OpenWeather API Key"
                    className="flex-1 px-3 py-2 border border-blue-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button 
                    onClick={handleApiKeyUpdate}
                    disabled={isUpdatingApi || !apiKey.trim()}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                  >
                    <Key className="h-4 w-4" />
                    <span>{isUpdatingApi ? 'Updating...' : 'Save API Key'}</span>
                  </button>
                </div>
              </div>
              
              <div className="bg-gray-50 rounded-md p-4">
                <p className="text-sm text-gray-600 mb-3">
                  <strong>Cache Management:</strong> Clear weather cache to force fresh data fetch
                </p>
                <button 
                  onClick={clearWeatherCache}
                  className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 transition-colors flex items-center space-x-2"
                >
                  <CloudRain className="h-4 w-4" />
                  <span>Clear Weather Cache</span>
                </button>
              </div>
              
              <div className="bg-yellow-50 rounded-md p-4">
                <p className="text-sm text-yellow-800">
                  <strong>Note:</strong> Without a valid API key, the system will use fallback weather data based on regional patterns. 
                  For accurate real-time weather data, please configure your OpenWeather API key.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;