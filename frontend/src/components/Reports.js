import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import axios from 'axios';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { 
  BarChart3, 
  TrendingUp, 
  Calendar, 
  Download, 
  PieChart, 
  Activity,
  Target,
  AlertTriangle,
  CheckCircle,
  Filter,
  RefreshCw
} from 'lucide-react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import toast from 'react-hot-toast';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const Reports = () => {
  const { user } = useAuth();
  const { t } = useLanguage();
  const [reportsData, setReportsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedCrop, setSelectedCrop] = useState('all');
  const [selectedTimeRange, setSelectedTimeRange] = useState('all');
  const [statsData, setStatsData] = useState(null);

  useEffect(() => {
    fetchReportsData();
  }, [user]);

  useEffect(() => {
    if (reportsData) {
      calculateStats();
    }
  }, [reportsData, selectedCrop, selectedTimeRange]);

  const fetchReportsData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/reports/${user.id}`);
      setReportsData(response.data);
      toast.success('Reports loaded successfully');
    } catch (error) {
      console.error('Error fetching reports:', error);
      toast.error('Failed to load reports data');
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = () => {
    if (!reportsData?.predictions) return;
    
    let filteredData = reportsData.predictions;
    
    // Filter by crop type
    if (selectedCrop !== 'all') {
      filteredData = filteredData.filter(p => p.crop_type === selectedCrop);
    }
    
    // Filter by time range
    if (selectedTimeRange !== 'all') {
      const now = new Date();
      const timeRanges = {
        '7d': 7,
        '30d': 30,
        '90d': 90,
        '1y': 365
      };
      const days = timeRanges[selectedTimeRange];
      const cutoffDate = new Date(now.getTime() - days * 24 * 60 * 60 * 1000);
      filteredData = filteredData.filter(p => new Date(p.created_at) >= cutoffDate);
    }
    
    const totalPredictions = filteredData.length;
    const avgYield = totalPredictions > 0 ? 
      filteredData.reduce((sum, p) => sum + p.predicted_yield, 0) / totalPredictions : 0;
    
    const riskDistribution = filteredData.reduce((acc, p) => {
      acc[p.risk_level] = (acc[p.risk_level] || 0) + 1;
      return acc;
    }, {});
    
    const cropTypes = [...new Set(filteredData.map(p => p.crop_type))];
    
    setStatsData({
      totalPredictions,
      avgYield: avgYield.toFixed(2),
      riskDistribution,
      cropTypes,
      filteredData
    });
  };

  const getFilteredData = () => {
    if (!reportsData?.predictions) return [];
    
    let data = reportsData.predictions;
    
    if (selectedCrop !== 'all') {
      data = data.filter(p => p.crop_type === selectedCrop);
    }
    
    if (selectedTimeRange !== 'all') {
      const now = new Date();
      const timeRanges = {
        '7d': 7,
        '30d': 30,
        '90d': 90,
        '1y': 365
      };
      const days = timeRanges[selectedTimeRange];
      const cutoffDate = new Date(now.getTime() - days * 24 * 60 * 60 * 1000);
      data = data.filter(p => new Date(p.created_at) >= cutoffDate);
    }
    
    return data.slice(0, 20); // Show last 20 entries
  };

  // Chart data preparation
  const yieldTrendData = {
    labels: getFilteredData().map(p => new Date(p.created_at).toLocaleDateString()).slice(-10),
    datasets: [
      {
        label: 'Predicted Yield (t/ha)',
        data: getFilteredData().map(p => p.predicted_yield).slice(-10),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.4,
        fill: true,
        pointBackgroundColor: 'rgb(34, 197, 94)',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 6,
      },
    ],
  };

  const cropYieldData = {
    labels: statsData?.cropTypes || [],
    datasets: [
      {
        label: 'Average Yield by Crop',
        data: statsData?.cropTypes?.map(crop => {
          const cropPredictions = getFilteredData().filter(p => p.crop_type === crop);
          return cropPredictions.length > 0 ? 
            cropPredictions.reduce((sum, p) => sum + p.predicted_yield, 0) / cropPredictions.length : 0;
        }) || [],
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(239, 68, 68, 0.8)',
          'rgba(147, 51, 234, 0.8)',
          'rgba(236, 72, 153, 0.8)',
        ],
        borderColor: [
          'rgba(34, 197, 94, 1)',
          'rgba(59, 130, 246, 1)',
          'rgba(245, 158, 11, 1)',
          'rgba(239, 68, 68, 1)',
          'rgba(147, 51, 234, 1)',
          'rgba(236, 72, 153, 1)',
        ],
        borderWidth: 2,
      },
    ],
  };

  const riskDistributionData = {
    labels: ['Low Risk (Green)', 'Medium Risk (Yellow)', 'High Risk (Red)'],
    datasets: [
      {
        data: [
          statsData?.riskDistribution?.Green || 0,
          statsData?.riskDistribution?.Yellow || 0,
          statsData?.riskDistribution?.Red || 0,
        ],
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(239, 68, 68, 0.8)',
        ],
        borderColor: [
          'rgba(34, 197, 94, 1)',
          'rgba(245, 158, 11, 1)',
          'rgba(239, 68, 68, 1)',
        ],
        borderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          font: {
            size: 12
          }
        }
      },
      title: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0,0,0,0.1)',
        },
        ticks: {
          font: {
            size: 11
          }
        }
      },
      x: {
        grid: {
          color: 'rgba(0,0,0,0.1)',
        },
        ticks: {
          font: {
            size: 11
          }
        }
      }
    }
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          font: {
            size: 12
          },
          padding: 20
        }
      },
    },
  };

  const exportData = () => {
    try {
      const dataToExport = {
        user: user.username,
        exportDate: new Date().toISOString(),
        filters: {
          crop: selectedCrop,
          timeRange: selectedTimeRange
        },
        statistics: statsData,
        predictions: getFilteredData()
      };
      
      const blob = new Blob([JSON.stringify(dataToExport, null, 2)], {
        type: 'application/json'
      });
      
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `crop-reports-${user.username}-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      toast.success('Report exported successfully');
    } catch (error) {
      toast.error('Failed to export report');
    }
  };

  const getRiskIcon = (riskLevel) => {
    switch (riskLevel) {
      case 'Green':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'Yellow':
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
      case 'Red':
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
      default:
        return <Activity className="h-4 w-4 text-gray-600" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center pt-16">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-green-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading reports data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pt-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            <BarChart3 className="h-8 w-8 mr-3 text-green-600" />
            {t('reports')}
          </h1>
          <p className="text-gray-600 mt-2">
            Comprehensive analysis of your crop yield predictions and farming trends
          </p>
        </div>

        {/* Controls */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-4">
              <div className="flex items-center space-x-2">
                <Filter className="h-5 w-5 text-gray-500" />
                <span className="text-sm font-medium text-gray-700">Filters:</span>
              </div>
              
              <select
                value={selectedCrop}
                onChange={(e) => setSelectedCrop(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="all">All Crops</option>
                {statsData?.cropTypes?.map(crop => (
                  <option key={crop} value={crop}>{crop}</option>
                ))}
              </select>
              
              <select
                value={selectedTimeRange}
                onChange={(e) => setSelectedTimeRange(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="all">All Time</option>
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
                <option value="90d">Last 3 Months</option>
                <option value="1y">Last Year</option>
              </select>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={fetchReportsData}
                className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
              >
                <RefreshCw className="h-4 w-4" />
                <span>Refresh</span>
              </button>
              
              <button
                onClick={exportData}
                className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
              >
                <Download className="h-4 w-4" />
                <span>Export</span>
              </button>
            </div>
          </div>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Predictions</p>
                <p className="text-2xl font-bold text-gray-900">{statsData?.totalPredictions || 0}</p>
              </div>
              <Target className="h-10 w-10 text-blue-500" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Average Yield</p>
                <p className="text-2xl font-bold text-green-600">{statsData?.avgYield || '0.00'}</p>
                <p className="text-xs text-gray-500">tons/hectare</p>
              </div>
              <TrendingUp className="h-10 w-10 text-green-500" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">High Risk</p>
                <p className="text-2xl font-bold text-red-600">{statsData?.riskDistribution?.Red || 0}</p>
                <p className="text-xs text-gray-500">predictions</p>
              </div>
              <AlertTriangle className="h-10 w-10 text-red-500" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Safe Predictions</p>
                <p className="text-2xl font-bold text-green-600">{statsData?.riskDistribution?.Green || 0}</p>
                <p className="text-xs text-gray-500">low risk</p>
              </div>
              <CheckCircle className="h-10 w-10 text-green-500" />
            </div>
          </div>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Yield Trend Chart */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-800 flex items-center">
                <TrendingUp className="h-6 w-6 mr-2 text-blue-500" />
                Yield Trends
              </h2>
            </div>
            <div className="h-80">
              {getFilteredData().length > 0 ? (
                <Line data={yieldTrendData} options={chartOptions} />
              ) : (
                <div className="flex items-center justify-center h-full text-gray-500">
                  <div className="text-center">
                    <Activity className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                    <p>No data available for selected filters</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Risk Distribution Chart */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-800 flex items-center">
                <PieChart className="h-6 w-6 mr-2 text-purple-500" />
                Risk Distribution
              </h2>
            </div>
            <div className="h-80">
              {getFilteredData().length > 0 ? (
                <Doughnut data={riskDistributionData} options={doughnutOptions} />
              ) : (
                <div className="flex items-center justify-center h-full text-gray-500">
                  <div className="text-center">
                    <PieChart className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                    <p>No data available for selected filters</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Crop Comparison Chart */}
        {statsData?.cropTypes?.length > 1 && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-800 flex items-center">
                <BarChart3 className="h-6 w-6 mr-2 text-green-500" />
                Crop Yield Comparison
              </h2>
            </div>
            <div className="h-80">
              <Bar data={cropYieldData} options={chartOptions} />
            </div>
          </div>
        )}

        {/* Historical Predictions Table */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-6 flex items-center">
            <Calendar className="h-6 w-6 mr-2 text-green-500" />
            Historical Predictions
            <span className="ml-2 text-sm font-normal text-gray-500">
              ({getFilteredData().length} records)
            </span>
          </h2>

          {getFilteredData().length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Crop Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Predicted Yield
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Risk Level
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Recommendations
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {getFilteredData().map((prediction) => (
                    <tr key={prediction.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div>
                          <div className="font-medium">
                            {new Date(prediction.created_at).toLocaleDateString()}
                          </div>
                          <div className="text-xs text-gray-500">
                            {new Date(prediction.created_at).toLocaleTimeString()}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div className="flex items-center">
                          <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center mr-3">
                            <span className="text-green-600 font-medium text-xs">
                              {prediction.crop_type.charAt(0).toUpperCase()}
                            </span>
                          </div>
                          <span className="font-medium">{prediction.crop_type}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm">
                          <div className="font-bold text-green-600 text-lg">
                            {prediction.predicted_yield}
                          </div>
                          <div className="text-xs text-gray-500">tons/hectare</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center space-x-2">
                          {getRiskIcon(prediction.risk_level)}
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            prediction.risk_level === 'Green' ? 'bg-green-100 text-green-800' :
                            prediction.risk_level === 'Yellow' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {t(prediction.risk_level === 'Green' ? 'safe' :
                               prediction.risk_level === 'Yellow' ? 'warning' : 'risk')}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        <div className="flex items-center space-x-1">
                          <span className="font-medium">{prediction.recommendations.length}</span>
                          <span className="text-gray-500">recommendations</span>
                        </div>
                        {prediction.recommendations.length > 0 && (
                          <div className="mt-1 text-xs text-gray-500 truncate max-w-xs">
                            {prediction.recommendations[0]}
                            {prediction.recommendations.length > 1 && '...'}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button
                          onClick={() => {
                            // Could open a modal with full details
                            toast.info('Detailed view coming soon!');
                          }}
                          className="text-green-600 hover:text-green-900 transition-colors"
                        >
                          View Details
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              {reportsData?.predictions?.length > getFilteredData().length && (
                <div className="mt-4 text-center">
                  <p className="text-sm text-gray-500">
                    Showing {getFilteredData().length} of {reportsData.predictions.length} predictions
                  </p>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="mx-auto w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <BarChart3 className="h-12 w-12 text-gray-400" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Data Available</h3>
              <p className="text-gray-500 mb-6">
                {reportsData?.predictions?.length === 0 
                  ? "You haven't made any predictions yet."
                  : "No data matches your current filter criteria."
                }
              </p>
              <div className="space-x-3">
                {reportsData?.predictions?.length === 0 ? (
                  <button
                    onClick={() => window.location.href = '/data-entry'}
                    className="bg-green-600 text-white px-6 py-3 rounded-md hover:bg-green-700 transition-colors inline-flex items-center space-x-2"
                  >
                    <Target className="h-4 w-4" />
                    <span>Start Making Predictions</span>
                  </button>
                ) : (
                  <button
                    onClick={() => {
                      setSelectedCrop('all');
                      setSelectedTimeRange('all');
                    }}
                    className="bg-gray-600 text-white px-6 py-3 rounded-md hover:bg-gray-700 transition-colors inline-flex items-center space-x-2"
                  >
                    <Filter className="h-4 w-4" />
                    <span>Clear Filters</span>
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Reports;
