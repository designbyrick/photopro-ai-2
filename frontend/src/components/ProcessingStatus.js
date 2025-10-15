import React, { useState, useEffect } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { 
  Loader, 
  CheckCircle, 
  AlertCircle, 
  Clock,
  Sparkles,
  Image as ImageIcon
} from 'lucide-react';

function ProcessingStatus({ photoId, onComplete, onError }) {
  const { messages, isConnected } = useWebSocket();
  const [status, setStatus] = useState('processing');
  const [message, setMessage] = useState('Starting photo generation...');
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    // Filter messages for this specific photo
    const photoMessages = messages.filter(msg => msg.photo_id === photoId);
    
    if (photoMessages.length > 0) {
      const latestMessage = photoMessages[photoMessages.length - 1];
      
      switch (latestMessage.type) {
        case 'photo_status_update':
          setStatus(latestMessage.status);
          setMessage(latestMessage.message);
          
          // Update progress based on message
          if (latestMessage.message.includes('Starting')) {
            setProgress(10);
          } else if (latestMessage.message.includes('Processing')) {
            setProgress(50);
          } else if (latestMessage.message.includes('Generating thumbnail')) {
            setProgress(80);
          }
          break;
          
        case 'photo_completed':
          setStatus('completed');
          setMessage('Photo generation completed!');
          setProgress(100);
          if (onComplete) {
            onComplete({
              id: latestMessage.photo_id,
              processed_url: latestMessage.processed_url,
              thumbnail_url: latestMessage.thumbnail_url
            });
          }
          break;
          
        case 'photo_failed':
          setStatus('failed');
          setMessage(latestMessage.error);
          setProgress(0);
          if (onError) {
            onError(latestMessage.error);
          }
          break;
      }
    }
  }, [messages, photoId, onComplete, onError]);

  const getStatusIcon = () => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-6 h-6 text-green-500" />;
      case 'failed':
        return <AlertCircle className="w-6 h-6 text-red-500" />;
      case 'processing':
        return <Loader className="w-6 h-6 text-blue-500 animate-spin" />;
      default:
        return <Clock className="w-6 h-6 text-gray-400" />;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return 'border-green-200 bg-green-50';
      case 'failed':
        return 'border-red-200 bg-red-50';
      case 'processing':
        return 'border-blue-200 bg-blue-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  if (!isConnected) {
    return (
      <div className="p-4 border border-yellow-200 bg-yellow-50 rounded-lg">
        <div className="flex items-center space-x-2">
          <AlertCircle className="w-5 h-5 text-yellow-600" />
          <span className="text-yellow-800">Connection lost. Attempting to reconnect...</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`p-4 border rounded-lg ${getStatusColor()}`}>
      <div className="flex items-center space-x-3 mb-3">
        {getStatusIcon()}
        <div className="flex-1">
          <h3 className="font-medium text-gray-900">
            {status === 'completed' ? 'Generation Complete!' : 
             status === 'failed' ? 'Generation Failed' : 
             'Processing Photo...'}
          </h3>
          <p className="text-sm text-gray-600">{message}</p>
        </div>
        {status === 'processing' && (
          <Sparkles className="w-5 h-5 text-blue-500 animate-pulse" />
        )}
      </div>
      
      {status === 'processing' && (
        <div className="space-y-2">
          <div className="flex justify-between text-sm text-gray-600">
            <span>Progress</span>
            <span>{progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-500 h-2 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}
      
      {status === 'completed' && (
        <div className="flex items-center space-x-2 text-green-600">
          <CheckCircle className="w-4 h-4" />
          <span className="text-sm font-medium">Your photo is ready!</span>
        </div>
      )}
      
      {status === 'failed' && (
        <div className="flex items-center space-x-2 text-red-600">
          <AlertCircle className="w-4 h-4" />
          <span className="text-sm font-medium">Something went wrong. Please try again.</span>
        </div>
      )}
    </div>
  );
}

export default ProcessingStatus;
