import React, { createContext, useContext, useState, useEffect } from 'react';

const LanguageContext = createContext();

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

const translations = {
  en: {
    // Navigation
    dashboard: 'Dashboard',
    dataEntry: 'Data Entry',
    reports: 'Reports',
    settings: 'Settings',
    logout: 'Logout',
    
    // Login/Register
    login: 'Login',
    register: 'Register',
    username: 'Username',
    email: 'Email',
    password: 'Password',
    phone: 'Phone Number',
    region: 'Region',
    
    // Dashboard
    welcomeBack: 'Welcome Back',
    currentWeather: 'Current Weather',
    recentPredictions: 'Recent Predictions',
    yieldPrediction: 'Yield Prediction',
    riskLevel: 'Risk Level',
    recommendations: 'Recommendations',
    
    // Data Entry
    farmDetails: 'Farm Details',
    cropType: 'Crop Type',
    rainfall: 'Rainfall (mm)',
    temperature: 'Temperature (°C)',
    soilPH: 'Soil pH',
    nitrogen: 'Nitrogen (kg/ha)',
    phosphorus: 'Phosphorus (kg/ha)',
    potassium: 'Potassium (kg/ha)',
    sowingOffset: 'Sowing Date Offset (days)',
    predict: 'Predict Yield',
    
    // Risk Levels
    safe: 'Safe',
    warning: 'Warning',
    risk: 'High Risk',
    
    // Common
    submit: 'Submit',
    cancel: 'Cancel',
    loading: 'Loading...',
    error: 'Error',
    success: 'Success'
  },
  hi: {
    // Navigation
    dashboard: 'डैशबोर्ड',
    dataEntry: 'डेटा एंट्री',
    reports: 'रिपोर्ट्स',
    settings: 'सेटिंग्स',
    logout: 'लॉगआउट',
    
    // Login/Register
    login: 'लॉगिन',
    register: 'रजिस्टर',
    username: 'उपयोगकर्ता नाम',
    email: 'ईमेल',
    password: 'पासवर्ड',
    phone: 'फोन नंबर',
    region: 'क्षेत्र',
    
    // Dashboard
    welcomeBack: 'वापसी पर स्वागत',
    currentWeather: 'वर्तमान मौसम',
    recentPredictions: 'हाल की भविष्यवाणियां',
    yieldPrediction: 'उत्पादन भविष्यवाणी',
    riskLevel: 'जोखिम स्तर',
    recommendations: 'सिफारिशें',
    
    // Data Entry
    farmDetails: 'खेत का विवरण',
    cropType: 'फसल का प्रकार',
    rainfall: 'वर्षा (मिमी)',
    temperature: 'तापमान (°C)',
    soilPH: 'मिट्टी pH',
    nitrogen: 'नाइट्रोजन (किग्रा/हेक्टेयर)',
    phosphorus: 'फास्फोरस (किग्रा/हेक्टेयर)',
    potassium: 'पोटेशियम (किग्रा/हेक्टेयर)',
    sowingOffset: 'बुवाई दिनांक ऑफसेट (दिन)',
    predict: 'उत्पादन की भविष्यवाणी करें',
    
    // Risk Levels
    safe: 'सुरक्षित',
    warning: 'चेतावनी',
    risk: 'उच्च जोखिम',
    
    // Common
    submit: 'जमा करें',
    cancel: 'रद्द करें',
    loading: 'लोड हो रहा है...',
    error: 'त्रुटि',
    success: 'सफलता'
  },
  ta: {
    // Navigation
    dashboard: 'டாஷ்போர்டு',
    dataEntry: 'தரவு உள்ளீடு',
    reports: 'அறிக்கைகள்',
    settings: 'அமைப்புகள்',
    logout: 'வெளியேறு',
    
    // Login/Register
    login: 'உள்நுழைவு',
    register: 'பதிவு',
    username: 'பயனர் பெயர்',
    email: 'மின்னஞ்சல்',
    password: 'கடவுச்சொல்',
    phone: 'தொலைபேசி எண்',
    region: 'பகுதி',
    
    // Dashboard
    welcomeBack: 'மீண்டும் வரவேற்கிறோம்',
    currentWeather: 'தற்போதைய வானிலை',
    recentPredictions: 'சமீபத்திய கணிப்புகள்',
    yieldPrediction: 'விளைச்சல் கணிப்பு',
    riskLevel: 'ஆபத்து நிலை',
    recommendations: 'பரிந்துரைகள்',
    
    // Data Entry
    farmDetails: 'பண்ணை விவரங்கள்',
    cropType: 'பயிர் வகை',
    rainfall: 'மழைப்பொழிவு (மிமீ)',
    temperature: 'வெப்பநிலை (°C)',
    soilPH: 'மண் pH',
    nitrogen: 'நைட்ரஜன் (கிலோ/ஹெக்டேர்)',
    phosphorus: 'பாஸ்பரஸ் (கிலோ/ஹெக்டேர்)',
    potassium: 'பொட்டாசியம் (கிலோ/ஹெக்டேர்)',
    sowingOffset: 'விதைப்பு தேதி ஆஃப்செட் (நாட்கள்)',
    predict: 'விளைச்சலை கணிக்கவும்',
    
    // Risk Levels
    safe: 'பாதுகாப்பான',
    warning: 'எச்சரிக்கை',
    risk: 'அதிக ஆபத்து',
    
    // Common
    submit: 'சமர்ப்பிக்கவும்',
    cancel: 'ரத்து செய்',
    loading: 'ஏற்றுகிறது...',
    error: 'பிழை',
    success: 'வெற்றி'
  }
};

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState('en');

  const t = (key) => {
    return translations[language][key] || key;
  };

  const changeLanguage = (lang) => {
    setLanguage(lang);
    localStorage.setItem('language', lang);
  };

  useEffect(() => {
    const savedLang = localStorage.getItem('language');
    if (savedLang && translations[savedLang]) {
      setLanguage(savedLang);
    }
  }, []);

  return (
    <LanguageContext.Provider value={{ language, changeLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};
