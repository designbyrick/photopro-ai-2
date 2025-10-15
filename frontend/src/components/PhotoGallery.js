import React, { useState } from 'react';
import { 
  Download, 
  Eye, 
  Calendar, 
  Sparkles,
  AlertCircle,
  CheckCircle,
  Clock,
  Image as ImageIcon
} from 'lucide-react';

function PhotoGallery({ photos, loading, showAll = false }) {
  const [selectedPhoto, setSelectedPhoto] = useState(null);
  const [viewMode, setViewMode] = useState('grid');

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'processing':
        return <Clock className="w-4 h-4 text-yellow-500 animate-spin" />;
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'completed':
        return 'Completed';
      case 'processing':
        return 'Processing...';
      case 'failed':
        return 'Failed';
      default:
        return 'Unknown';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const downloadImage = (url, filename) => {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename || 'photopro-image.jpg';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="spinner w-8 h-8 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading photos...</p>
        </div>
      </div>
    );
  }

  if (photos.length === 0) {
    return (
      <div className="text-center py-12">
        <ImageIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          {showAll ? 'No photos yet' : 'No completed photos'}
        </h3>
        <p className="text-gray-500">
          {showAll 
            ? 'Start by uploading and generating your first photo!'
            : 'Generate some photos to see them here.'
          }
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            {showAll ? 'All Photos' : 'My Photos'}
          </h2>
          <p className="text-gray-600">
            {photos.length} {photos.length === 1 ? 'photo' : 'photos'}
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setViewMode('grid')}
            className={`p-2 rounded-lg ${
              viewMode === 'grid' 
                ? 'bg-purple-100 text-purple-600' 
                : 'text-gray-400 hover:text-gray-600'
            }`}
          >
            <div className="w-4 h-4 grid grid-cols-2 gap-0.5">
              <div className="bg-current rounded-sm"></div>
              <div className="bg-current rounded-sm"></div>
              <div className="bg-current rounded-sm"></div>
              <div className="bg-current rounded-sm"></div>
            </div>
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-2 rounded-lg ${
              viewMode === 'list' 
                ? 'bg-purple-100 text-purple-600' 
                : 'text-gray-400 hover:text-gray-600'
            }`}
          >
            <div className="w-4 h-4 flex flex-col space-y-0.5">
              <div className="bg-current h-0.5 rounded"></div>
              <div className="bg-current h-0.5 rounded"></div>
              <div className="bg-current h-0.5 rounded"></div>
            </div>
          </button>
        </div>
      </div>

      {/* Photos Grid/List */}
      <div className={
        viewMode === 'grid' 
          ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
          : 'space-y-4'
      }>
        {photos.map((photo) => (
          <div
            key={photo.id}
            className={`bg-white rounded-lg shadow-md overflow-hidden transition-all hover:shadow-lg ${
              viewMode === 'list' ? 'flex' : ''
            }`}
          >
            {/* Image */}
            <div className={`${viewMode === 'list' ? 'w-32 h-32 flex-shrink-0' : 'aspect-square'}`}>
              {photo.thumbnail_url ? (
                <img
                  src={photo.thumbnail_url}
                  alt={`${photo.style} style photo`}
                  className="w-full h-full object-cover cursor-pointer"
                  onClick={() => setSelectedPhoto(photo)}
                />
              ) : (
                <div className="w-full h-full bg-gray-100 flex items-center justify-center">
                  <ImageIcon className="w-8 h-8 text-gray-400" />
                </div>
              )}
            </div>

            {/* Content */}
            <div className={`p-4 ${viewMode === 'list' ? 'flex-1' : ''}`}>
              <div className="flex items-center justify-between mb-2">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                  {photo.style}
                </span>
                <div className="flex items-center space-x-1">
                  {getStatusIcon(photo.status)}
                  <span className="text-xs text-gray-500">
                    {getStatusText(photo.status)}
                  </span>
                </div>
              </div>

              <div className="flex items-center text-sm text-gray-500 mb-3">
                <Calendar className="w-4 h-4 mr-1" />
                {formatDate(photo.created_at)}
              </div>

              {photo.status === 'completed' && (
                <div className="flex space-x-2">
                  <button
                    onClick={() => setSelectedPhoto(photo)}
                    className="flex items-center space-x-1 text-sm text-purple-600 hover:text-purple-700"
                  >
                    <Eye className="w-4 h-4" />
                    <span>View</span>
                  </button>
                  <button
                    onClick={() => downloadImage(photo.processed_url, `photopro-${photo.style}-${photo.id}.jpg`)}
                    className="flex items-center space-x-1 text-sm text-gray-600 hover:text-gray-700"
                  >
                    <Download className="w-4 h-4" />
                    <span>Download</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Photo Modal */}
      {selectedPhoto && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl max-h-full overflow-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">
                  {selectedPhoto.style} Style Photo
                </h3>
                <button
                  onClick={() => setSelectedPhoto(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              
              {selectedPhoto.processed_url ? (
                <div className="space-y-4">
                  <img
                    src={selectedPhoto.processed_url}
                    alt="Generated photo"
                    className="w-full max-w-2xl mx-auto rounded-lg shadow-lg"
                  />
                  
                  <div className="flex justify-center space-x-4">
                    <button
                      onClick={() => downloadImage(selectedPhoto.processed_url, `photopro-${selectedPhoto.style}-${selectedPhoto.id}.jpg`)}
                      className="btn btn-primary"
                    >
                      <Download className="w-4 h-4 mr-2" />
                      Download
                    </button>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12">
                  <AlertCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">Photo not available</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default PhotoGallery;
