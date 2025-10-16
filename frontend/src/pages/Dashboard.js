import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { photoAPI, creditAPI } from '../services/api';
import toast from 'react-hot-toast';
import PhotoUpload from '../components/PhotoUpload';
import PhotoGallery from '../components/PhotoGallery';
import CreditDisplay from '../components/CreditDisplay';
import UserProfile from '../components/UserProfile';
import { 
  Camera, 
  Image as ImageIcon, 
  History, 
  User, 
  LogOut,
  Sparkles
} from 'lucide-react';

function Dashboard() {
  const { user, logout, updateUser } = useAuth();
  const [activeTab, setActiveTab] = useState('upload');
  const [photos, setPhotos] = useState([]);
  const [loading] = useState(false);
  const [credits, setCredits] = useState(user?.credits || 0);

  const loadCredits = useCallback(async () => {
    try {
      const response = await creditAPI.getCredits();
      setCredits(response.data.credits);
      updateUser({ credits: response.data.credits });
    } catch (error) {
      console.error('Failed to load credits:', error);
    }
  }, [updateUser]);

  const loadPhotoHistory = async () => {
    try {
      const response = await photoAPI.getHistory();
      setPhotos(response.data);
    } catch (error) {
      console.error('Failed to load photo history:', error);
    }
  };

  useEffect(() => {
    loadPhotoHistory();
    loadCredits();
  }, [loadCredits]);

  const handlePhotoGenerated = (newPhoto) => {
    setPhotos(prev => [newPhoto, ...prev]);
    loadCredits(); // Refresh credits after generation
    toast.success('Photo generated successfully!');
  };

  const handleLogout = () => {
    logout();
    toast.success('Logged out successfully');
  };

  const tabs = [
    { id: 'upload', label: 'Generate Photo', icon: Camera },
    { id: 'gallery', label: 'My Photos', icon: ImageIcon },
    { id: 'history', label: 'History', icon: History },
    { id: 'profile', label: 'Profile', icon: User },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 via-blue-600 to-indigo-800">
      {/* Header */}
      <header className="bg-white/10 backdrop-blur-md border-b border-white/20">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-8 h-8 text-white" />
                <h1 className="text-2xl font-bold text-white">PhotoPro AI</h1>
              </div>
              <CreditDisplay credits={credits} />
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-white/80">
                Welcome, {user?.full_name || user?.username}!
              </span>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 text-white/80 hover:text-white transition-colors"
              >
                <LogOut className="w-4 h-4" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="container mx-auto px-4 py-6">
        <div className="flex flex-wrap gap-2 mb-6">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
                  activeTab === tab.id
                    ? 'bg-white text-purple-600 shadow-lg'
                    : 'bg-white/20 text-white/80 hover:bg-white/30'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Tab Content */}
        <div className="card">
          {activeTab === 'upload' && (
            <PhotoUpload 
              onPhotoGenerated={handlePhotoGenerated}
              credits={credits}
            />
          )}
          
          {activeTab === 'gallery' && (
            <PhotoGallery 
              photos={photos.filter(photo => photo.status === 'completed')}
              loading={loading}
            />
          )}
          
          {activeTab === 'history' && (
            <PhotoGallery 
              photos={photos}
              loading={loading}
              showAll={true}
            />
          )}
          
          {activeTab === 'profile' && (
            <UserProfile 
              user={user}
              onCreditsUpdate={loadCredits}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
