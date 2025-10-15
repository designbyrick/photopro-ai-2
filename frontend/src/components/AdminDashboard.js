import React, { useState, useEffect } from 'react';
import { 
  Users, 
  Image as ImageIcon, 
  Coins, 
  TrendingUp,
  Activity,
  BarChart3,
  UserCheck,
  UserX,
  Plus,
  Eye,
  Download
} from 'lucide-react';

function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [photos, setPhotos] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    try {
      setLoading(true);
      
      // Load stats
      const statsResponse = await fetch('/admin/stats', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const statsData = await statsResponse.json();
      setStats(statsData);
      
      // Load users
      const usersResponse = await fetch('/admin/users', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const usersData = await usersResponse.json();
      setUsers(usersData);
      
      // Load photos
      const photosResponse = await fetch('/admin/photos', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const photosData = await photosResponse.json();
      setPhotos(photosData);
      
      // Load analytics
      const analyticsResponse = await fetch('/admin/analytics/daily?days=30', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const analyticsData = await analyticsResponse.json();
      setAnalytics(analyticsData);
      
    } catch (error) {
      console.error('Failed to load admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleUserActive = async (userId, currentStatus) => {
    try {
      const response = await fetch(`/admin/users/${userId}/toggle-active`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      
      if (response.ok) {
        loadAdminData(); // Reload data
      }
    } catch (error) {
      console.error('Failed to toggle user status:', error);
    }
  };

  const addCreditsToUser = async (userId, amount) => {
    try {
      const response = await fetch(`/admin/users/${userId}/add-credits`, {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          amount, 
          description: 'Admin credit adjustment' 
        })
      });
      
      if (response.ok) {
        loadAdminData(); // Reload data
      }
    } catch (error) {
      console.error('Failed to add credits:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="spinner w-8 h-8 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading admin dashboard...</p>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'users', label: 'Users', icon: Users },
    { id: 'photos', label: 'Photos', icon: ImageIcon },
    { id: 'analytics', label: 'Analytics', icon: TrendingUp }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
              <p className="text-gray-600">PhotoPro AI Management</p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={loadAdminData}
                className="btn btn-secondary"
              >
                Refresh Data
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex space-x-1 mb-6">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
                  activeTab === tab.id
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Tab Content */}
        <div className="bg-white rounded-lg shadow">
          {activeTab === 'overview' && stats && (
            <div className="p-6">
              <h2 className="text-xl font-semibold mb-6">System Overview</h2>
              
              {/* Stats Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <div className="bg-blue-50 rounded-lg p-4">
                  <div className="flex items-center">
                    <Users className="w-8 h-8 text-blue-600" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-blue-600">Total Users</p>
                      <p className="text-2xl font-bold text-blue-900">{stats.users.total}</p>
                    </div>
                  </div>
                </div>
                
                <div className="bg-green-50 rounded-lg p-4">
                  <div className="flex items-center">
                    <ImageIcon className="w-8 h-8 text-green-600" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-green-600">Photos Generated</p>
                      <p className="text-2xl font-bold text-green-900">{stats.photos.completed}</p>
                    </div>
                  </div>
                </div>
                
                <div className="bg-yellow-50 rounded-lg p-4">
                  <div className="flex items-center">
                    <Coins className="w-8 h-8 text-yellow-600" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-yellow-600">Credits Used</p>
                      <p className="text-2xl font-bold text-yellow-900">{stats.credits.total_used}</p>
                    </div>
                  </div>
                </div>
                
                <div className="bg-purple-50 rounded-lg p-4">
                  <div className="flex items-center">
                    <Activity className="w-8 h-8 text-purple-600" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-purple-600">Success Rate</p>
                      <p className="text-2xl font-bold text-purple-900">{stats.photos.success_rate}%</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Style Popularity */}
              <div className="mb-8">
                <h3 className="text-lg font-semibold mb-4">Style Popularity</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {stats.styles.map((style) => (
                    <div key={style.style} className="bg-gray-50 rounded-lg p-4">
                      <h4 className="font-medium text-gray-900 capitalize">{style.style}</h4>
                      <p className="text-2xl font-bold text-gray-700">{style.count}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'users' && (
            <div className="p-6">
              <h2 className="text-xl font-semibold mb-6">User Management</h2>
              
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        User
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Plan
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Credits
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {users.map((user) => (
                      <tr key={user.id}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900">{user.full_name}</div>
                            <div className="text-sm text-gray-500">{user.email}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                            {user.plan}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {user.credits}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            user.is_active 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {user.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                          <button
                            onClick={() => toggleUserActive(user.id, user.is_active)}
                            className={`${
                              user.is_active 
                                ? 'text-red-600 hover:text-red-900' 
                                : 'text-green-600 hover:text-green-900'
                            }`}
                          >
                            {user.is_active ? <UserX className="w-4 h-4" /> : <UserCheck className="w-4 h-4" />}
                          </button>
                          <button
                            onClick={() => addCreditsToUser(user.id, 10)}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            <Plus className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'photos' && (
            <div className="p-6">
              <h2 className="text-xl font-semibold mb-6">Photo Management</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {photos.map((photo) => (
                  <div key={photo.id} className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-purple-100 text-purple-800">
                        {photo.style}
                      </span>
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        photo.status === 'completed' 
                          ? 'bg-green-100 text-green-800'
                          : photo.status === 'processing'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {photo.status}
                      </span>
                    </div>
                    
                    {photo.thumbnail_url && (
                      <img
                        src={photo.thumbnail_url}
                        alt="Photo thumbnail"
                        className="w-full h-32 object-cover rounded mb-2"
                      />
                    )}
                    
                    <div className="text-sm text-gray-600">
                      <p>User ID: {photo.user_id}</p>
                      <p>Credits Used: {photo.credits_used}</p>
                      <p>Created: {new Date(photo.created_at).toLocaleDateString()}</p>
                    </div>
                    
                    <div className="flex space-x-2 mt-3">
                      <button className="flex items-center space-x-1 text-sm text-blue-600 hover:text-blue-800">
                        <Eye className="w-4 h-4" />
                        <span>View</span>
                      </button>
                      {photo.processed_url && (
                        <button className="flex items-center space-x-1 text-sm text-green-600 hover:text-green-800">
                          <Download className="w-4 h-4" />
                          <span>Download</span>
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'analytics' && analytics && (
            <div className="p-6">
              <h2 className="text-xl font-semibold mb-6">Analytics</h2>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="text-lg font-medium mb-4">Daily User Registrations</h3>
                  <div className="space-y-2">
                    {analytics.daily_users.slice(-7).map((day, index) => (
                      <div key={index} className="flex justify-between">
                        <span className="text-sm text-gray-600">{day.date}</span>
                        <span className="font-medium">{day.count} users</span>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="text-lg font-medium mb-4">Daily Photo Generations</h3>
                  <div className="space-y-2">
                    {analytics.daily_photos.slice(-7).map((day, index) => (
                      <div key={index} className="flex justify-between">
                        <span className="text-sm text-gray-600">{day.date}</span>
                        <span className="font-medium">{day.count} photos</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default AdminDashboard;
