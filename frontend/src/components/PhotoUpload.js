import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { photoAPI } from '../services/api';
import toast from 'react-hot-toast';
import { 
  Upload, 
  Sparkles, 
  AlertCircle,
  CheckCircle,
  Loader
} from 'lucide-react';

const STYLES = [
  { id: 'corporate', name: 'Corporate', description: 'Professional business look' },
  { id: 'creative', name: 'Creative', description: 'Artistic and expressive' },
  { id: 'formal', name: 'Formal', description: 'Elegant and sophisticated' },
  { id: 'casual', name: 'Casual', description: 'Relaxed and approachable' }
];

function PhotoUpload({ onPhotoGenerated, credits }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedStyle, setSelectedStyle] = useState('corporate');
  const [uploading, setUploading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [uploadedUrl, setUploadedUrl] = useState(null);
  const [preview, setPreview] = useState(null);

  const onDrop = (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      setSelectedFile(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => setPreview(e.target.result);
      reader.readAsDataURL(file);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp']
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: false
  });

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    try {
      const response = await photoAPI.upload(selectedFile);
      setUploadedUrl(response.data.url);
      toast.success('Image uploaded successfully!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleGenerate = async () => {
    if (!uploadedUrl) return;

    if (credits < 1) {
      toast.error('Insufficient credits. Please purchase more credits.');
      return;
    }

    setGenerating(true);
    try {
      const response = await photoAPI.generate(uploadedUrl, selectedStyle);
      onPhotoGenerated(response.data);
      
      // Reset form
      setSelectedFile(null);
      setPreview(null);
      setUploadedUrl(null);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Generation failed');
    } finally {
      setGenerating(false);
    }
  };

  const resetUpload = () => {
    setSelectedFile(null);
    setPreview(null);
    setUploadedUrl(null);
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Generate Professional Photos
        </h2>
        <p className="text-gray-600">
          Upload your photo and choose a style to create professional headshots
        </p>
      </div>

      {/* Upload Area */}
      <div className="space-y-4">
        {!preview ? (
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive
                ? 'border-purple-500 bg-purple-50'
                : 'border-gray-300 hover:border-purple-400'
            }`}
          >
            <input {...getInputProps()} />
            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-lg font-medium text-gray-900 mb-2">
              {isDragActive ? 'Drop your image here' : 'Drag & drop your image here'}
            </p>
            <p className="text-gray-500 mb-4">
              or click to browse files
            </p>
            <p className="text-sm text-gray-400">
              Supports JPG, PNG, WEBP • Max 10MB • Min 512x512px
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="relative">
              <img
                src={preview}
                alt="Preview"
                className="w-full max-w-md mx-auto rounded-lg shadow-lg"
              />
              {uploadedUrl && (
                <div className="absolute top-2 right-2 bg-green-500 text-white p-2 rounded-full">
                  <CheckCircle className="w-4 h-4" />
                </div>
              )}
            </div>
            
            <div className="flex justify-center space-x-4">
              {!uploadedUrl ? (
                <button
                  onClick={handleUpload}
                  disabled={uploading}
                  className="btn btn-primary"
                >
                  {uploading ? (
                    <span className="flex items-center">
                      <Loader className="w-4 h-4 mr-2 animate-spin" />
                      Uploading...
                    </span>
                  ) : (
                    'Upload Image'
                  )}
                </button>
              ) : (
                <button
                  onClick={resetUpload}
                  className="btn btn-secondary"
                >
                  Upload Different Image
                </button>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Style Selection */}
      {uploadedUrl && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">Choose Style</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {STYLES.map((style) => (
              <button
                key={style.id}
                onClick={() => setSelectedStyle(style.id)}
                className={`p-4 rounded-lg border-2 transition-all text-left ${
                  selectedStyle === style.id
                    ? 'border-purple-500 bg-purple-50'
                    : 'border-gray-200 hover:border-purple-300'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <div className={`w-4 h-4 rounded-full border-2 ${
                    selectedStyle === style.id
                      ? 'border-purple-500 bg-purple-500'
                      : 'border-gray-300'
                  }`} />
                  <div>
                    <h4 className="font-medium text-gray-900">{style.name}</h4>
                    <p className="text-sm text-gray-500">{style.description}</p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Generate Button */}
      {uploadedUrl && (
        <div className="text-center">
          <button
            onClick={handleGenerate}
            disabled={generating || credits < 1}
            className={`btn btn-primary text-lg px-8 py-3 ${
              credits < 1 ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            {generating ? (
              <span className="flex items-center">
                <Loader className="w-5 h-5 mr-2 animate-spin" />
                Generating...
              </span>
            ) : (
              <span className="flex items-center">
                <Sparkles className="w-5 h-5 mr-2" />
                Generate Photo (1 Credit)
              </span>
            )}
          </button>
          
          {credits < 1 && (
            <p className="text-red-500 text-sm mt-2 flex items-center justify-center">
              <AlertCircle className="w-4 h-4 mr-1" />
              Insufficient credits. Please purchase more credits.
            </p>
          )}
        </div>
      )}
    </div>
  );
}

export default PhotoUpload;
