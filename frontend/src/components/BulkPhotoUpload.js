import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { photoAPI } from '../services/api';
import toast from 'react-hot-toast';
import { 
  Upload, 
  Image as ImageIcon, 
  Sparkles, 
  AlertCircle,
  CheckCircle,
  Loader,
  X,
  Plus,
  Zap
} from 'lucide-react';

const STYLES = [
  { id: 'corporate', name: 'Corporate', description: 'Professional business look' },
  { id: 'creative', name: 'Creative', description: 'Artistic and expressive' },
  { id: 'formal', name: 'Formal', description: 'Elegant and sophisticated' },
  { id: 'casual', name: 'Casual', description: 'Relaxed and approachable' }
];

function BulkPhotoUpload({ onPhotosGenerated, credits }) {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [selectedStyles, setSelectedStyles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [uploadedUrls, setUploadedUrls] = useState([]);
  const [generationQueue, setGenerationQueue] = useState([]);

  const onDrop = (acceptedFiles) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      preview: URL.createObjectURL(file),
      uploaded: false,
      generated: false
    }));
    
    setSelectedFiles(prev => [...prev, ...newFiles]);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp']
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: true
  });

  const removeFile = (fileId) => {
    setSelectedFiles(prev => {
      const file = prev.find(f => f.id === fileId);
      if (file) {
        URL.revokeObjectURL(file.preview);
      }
      return prev.filter(f => f.id !== fileId);
    });
  };

  const toggleStyle = (styleId) => {
    setSelectedStyles(prev => 
      prev.includes(styleId) 
        ? prev.filter(s => s !== styleId)
        : [...prev, styleId]
    );
  };

  const uploadAllFiles = async () => {
    if (selectedFiles.length === 0) return;

    setUploading(true);
    const uploadPromises = selectedFiles.map(async (fileObj) => {
      try {
        const response = await photoAPI.upload(fileObj.file);
        return {
          ...fileObj,
          uploaded: true,
          url: response.data.url
        };
      } catch (error) {
        toast.error(`Failed to upload ${fileObj.file.name}`);
        return fileObj;
      }
    });

    const results = await Promise.all(uploadPromises);
    setSelectedFiles(results);
    setUploadedUrls(results.filter(r => r.uploaded).map(r => r.url));
    setUploading(false);
    
    toast.success(`${results.filter(r => r.uploaded).length} files uploaded successfully!`);
  };

  const generateAllPhotos = async () => {
    if (uploadedUrls.length === 0 || selectedStyles.length === 0) {
      toast.error('Please upload files and select at least one style');
      return;
    }

    const totalGenerations = uploadedUrls.length * selectedStyles.length;
    if (credits < totalGenerations) {
      toast.error(`Insufficient credits. Need ${totalGenerations}, have ${credits}`);
      return;
    }

    setGenerating(true);
    const generationPromises = [];

    for (const url of uploadedUrls) {
      for (const style of selectedStyles) {
        const promise = photoAPI.generate(url, style)
          .then(response => ({
            success: true,
            data: response.data,
            url,
            style
          }))
          .catch(error => ({
            success: false,
            error: error.response?.data?.detail || 'Generation failed',
            url,
            style
          }));
        
        generationPromises.push(promise);
      }
    }

    const results = await Promise.all(generationPromises);
    const successful = results.filter(r => r.success);
    const failed = results.filter(r => !r.success);

    if (successful.length > 0) {
      onPhotosGenerated(successful.map(r => r.data));
      toast.success(`Generated ${successful.length} photos successfully!`);
    }

    if (failed.length > 0) {
      toast.error(`${failed.length} generations failed`);
    }

    setGenerating(false);
    
    // Reset form
    setSelectedFiles([]);
    setSelectedStyles([]);
    setUploadedUrls([]);
  };

  const resetForm = () => {
    selectedFiles.forEach(file => URL.revokeObjectURL(file.preview));
    setSelectedFiles([]);
    setSelectedStyles([]);
    setUploadedUrls([]);
  };

  const totalCost = uploadedUrls.length * selectedStyles.length;

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Bulk Photo Generation
        </h2>
        <p className="text-gray-600">
          Upload multiple photos and generate them in different styles at once
        </p>
      </div>

      {/* File Upload */}
      <div className="space-y-4">
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
            {isDragActive ? 'Drop your images here' : 'Drag & drop multiple images here'}
          </p>
          <p className="text-gray-500 mb-4">
            or click to browse files
          </p>
          <p className="text-sm text-gray-400">
            Supports JPG, PNG, WEBP • Max 10MB each • Min 512x512px
          </p>
        </div>

        {/* Selected Files */}
        {selectedFiles.length > 0 && (
          <div className="space-y-2">
            <h3 className="font-medium text-gray-900">Selected Files ({selectedFiles.length})</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {selectedFiles.map((fileObj) => (
                <div key={fileObj.id} className="relative">
                  <img
                    src={fileObj.preview}
                    alt="Preview"
                    className="w-full h-24 object-cover rounded-lg"
                  />
                  <button
                    onClick={() => removeFile(fileObj.id)}
                    className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                  >
                    <X className="w-3 h-3" />
                  </button>
                  {fileObj.uploaded && (
                    <div className="absolute inset-0 bg-green-500 bg-opacity-20 rounded-lg flex items-center justify-center">
                      <CheckCircle className="w-6 h-6 text-green-500" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Style Selection */}
      {selectedFiles.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">Choose Styles</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {STYLES.map((style) => (
              <button
                key={style.id}
                onClick={() => toggleStyle(style.id)}
                className={`p-4 rounded-lg border-2 transition-all text-left ${
                  selectedStyles.includes(style.id)
                    ? 'border-purple-500 bg-purple-50'
                    : 'border-gray-200 hover:border-purple-300'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <div className={`w-4 h-4 rounded-full border-2 ${
                    selectedStyles.includes(style.id)
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

      {/* Cost Summary */}
      {uploadedUrls.length > 0 && selectedStyles.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium text-blue-900">Generation Summary</h4>
              <p className="text-sm text-blue-700">
                {uploadedUrls.length} photos × {selectedStyles.length} styles = {totalCost} credits
              </p>
            </div>
            <div className="text-right">
              <p className="text-lg font-bold text-blue-900">{totalCost} Credits</p>
              <p className="text-sm text-blue-700">
                You have {credits} credits
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-4 justify-center">
        {selectedFiles.length > 0 && uploadedUrls.length === 0 && (
          <button
            onClick={uploadAllFiles}
            disabled={uploading}
            className="btn btn-primary"
          >
            {uploading ? (
              <span className="flex items-center">
                <Loader className="w-4 h-4 mr-2 animate-spin" />
                Uploading...
              </span>
            ) : (
              <span className="flex items-center">
                <Upload className="w-4 h-4 mr-2" />
                Upload All Files
              </span>
            )}
          </button>
        )}

        {uploadedUrls.length > 0 && selectedStyles.length > 0 && (
          <button
            onClick={generateAllPhotos}
            disabled={generating || credits < totalCost}
            className="btn btn-primary"
          >
            {generating ? (
              <span className="flex items-center">
                <Loader className="w-4 h-4 mr-2 animate-spin" />
                Generating...
              </span>
            ) : (
              <span className="flex items-center">
                <Zap className="w-4 h-4 mr-2" />
                Generate All ({totalCost} credits)
              </span>
            )}
          </button>
        )}

        {selectedFiles.length > 0 && (
          <button
            onClick={resetForm}
            className="btn btn-secondary"
          >
            <X className="w-4 h-4 mr-2" />
            Clear All
          </button>
        )}
      </div>

      {credits < totalCost && totalCost > 0 && (
        <div className="text-center">
          <p className="text-red-500 text-sm flex items-center justify-center">
            <AlertCircle className="w-4 h-4 mr-1" />
            Insufficient credits. Please purchase more credits.
          </p>
        </div>
      )}
    </div>
  );
}

export default BulkPhotoUpload;
