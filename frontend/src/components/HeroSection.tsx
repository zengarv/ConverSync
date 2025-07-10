import { motion } from 'framer-motion';
import { Upload, FileAudio, Play } from 'lucide-react';
import { useState } from 'react';

interface HeroSectionProps {
  onFileUpload: (file: File) => void;
  onDebugTest: () => void;
  uploadProgress: { isUploading: boolean; progress: number; status: string };
}

const HeroSection = ({ onFileUpload, onDebugTest, uploadProgress }: HeroSectionProps) => {
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      setSelectedFile(file);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleUpload = () => {
    if (selectedFile) {
      onFileUpload(selectedFile);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 relative overflow-hidden">
      {/* Animated gradient background */}
      <motion.div
        className="absolute inset-0 bg-gradient-radial from-purple-500/20 via-transparent to-transparent"
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.3, 0.1, 0.3],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="text-center max-w-4xl mx-auto mb-12"
      >
        <motion.h1
          className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-white via-purple-200 to-purple-400 bg-clip-text text-transparent"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          Never Miss a Meeting Detail Again
          <br />
          <span className="text-purple-400">with ConverSync</span>
        </motion.h1>
        
        <motion.p
          className="text-xl text-slate-300 mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          Your Smart Meeting Assistant – Minutes, Mails, and More.
        </motion.p>

        {/* Audio Wave Animation */}
        <motion.div
          className="flex items-center justify-center space-x-1 mb-8 h-12"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
        >
          {[...Array(8)].map((_, i) => (
            <motion.div
              key={i}
              className="w-1 bg-gradient-to-t from-purple-500 to-purple-300 rounded-full flex-shrink-0"
              style={{
                height: '20px',
                transformOrigin: 'center',
              }}
              animate={{
                scaleY: [1, 2, 0.75, 1.75, 1.25, 1.5, 1, 1.75][i % 8],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                delay: i * 0.1,
                ease: 'easeInOut',
                repeatType: 'reverse',
              }}
            />
          ))}
          <span className="ml-4 text-slate-300 font-medium flex-shrink-0">Get started.</span>
        </motion.div>
      </motion.div>

      {/* Upload Section */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="w-full max-w-2xl mx-auto"
      >
        <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-8 border border-slate-700/50">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Drop Zone */}
            <motion.div
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`flex-1 border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all ${
                dragOver
                  ? 'border-purple-400 bg-purple-500/10'
                  : selectedFile
                  ? 'border-green-400 bg-green-500/10'
                  : 'border-purple-500/50 bg-slate-700/30'
              }`}
            >
              <input
                type="file"
                accept="audio/*,video/*"
                onChange={handleFileSelect}
                className="hidden"
                id="file-upload"
              />
              <label htmlFor="file-upload" className="cursor-pointer">
                <div className="flex flex-col items-center space-y-3">
                  <motion.div
                    animate={{ rotate: selectedFile ? 360 : 0 }}
                    transition={{ duration: 0.5 }}
                  >
                    {selectedFile ? (
                      <FileAudio className="w-12 h-12 text-green-400" />
                    ) : (
                      <Upload className="w-12 h-12 text-purple-400" />
                    )}
                  </motion.div>
                  
                  {selectedFile ? (
                    <div>
                      <p className="text-lg font-medium text-green-400">
                        {selectedFile.name}
                      </p>
                      <p className="text-sm text-slate-400">
                        {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                      </p>
                    </div>
                  ) : (
                    <div>
                      <p className="text-lg font-medium text-white">
                        Upload meeting recording
                      </p>
                      <p className="text-sm text-slate-400">
                        Drag and drop or browse files
                      </p>
                    </div>
                  )}
                </div>
              </label>
            </motion.div>

            {/* Action Buttons */}
            <div className="flex flex-col items-center justify-center space-y-3">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleUpload}
                disabled={!selectedFile || uploadProgress.isUploading}
                className={`px-6 py-3 rounded-xl font-semibold transition-all ${
                  uploadProgress.status === 'complete'
                    ? 'bg-green-500 text-white'
                    : uploadProgress.status === 'error'
                    ? 'bg-red-500 text-white'
                    : 'bg-gradient-to-r from-purple-500 to-purple-600 text-white hover:from-purple-600 hover:to-purple-700'
                } ${
                  !selectedFile || uploadProgress.isUploading
                    ? 'opacity-50 cursor-not-allowed'
                    : ''
                }`}
              >
                {uploadProgress.isUploading ? (
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Processing...</span>
                  </div>
                ) : uploadProgress.status === 'complete' ? (
                  'Complete ✓'
                ) : uploadProgress.status === 'error' ? (
                  'Error - Try Again'
                ) : (
                  'Upload'
                )}
              </motion.button>

              {/* <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={onDebugTest}
                className="px-6 py-3 rounded-xl font-semibold bg-gradient-to-r from-orange-500 to-orange-600 text-white hover:from-orange-600 hover:to-orange-700 transition-all flex items-center space-x-2"
              >
                <Play className="w-4 h-4" />
                <span>Demo Mode</span>
              </motion.button> */}
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default HeroSection;