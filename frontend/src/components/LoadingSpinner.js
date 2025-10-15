import React from 'react';

function LoadingSpinner({ size = 'large', text = 'Loading...' }) {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-6 h-6',
    large: 'w-8 h-8'
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <div className={`spinner ${sizeClasses[size]} mb-4`}></div>
      <p className="text-white/80">{text}</p>
    </div>
  );
}

export default LoadingSpinner;
