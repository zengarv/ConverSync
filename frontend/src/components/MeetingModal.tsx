import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect } from 'react';
import { X, FileText, Mail, Loader2 } from 'lucide-react';
import { MeetingDetails } from '../types';
import { apiService } from '../services/api';

interface MeetingModalProps {
  isOpen: boolean;
  onClose: () => void;
  type: 'pdf' | 'email';
  sessionId: string;
}

const MeetingModal = ({ isOpen, onClose, type, sessionId }: MeetingModalProps) => {
  const [formData, setFormData] = useState<MeetingDetails>({
    title: '',
    date: new Date().toISOString().split('T')[0],
    companyName: '',
    recipients: [],
    customMessage: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  // Reset states when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      setIsSubmitting(false);
      setIsSuccess(false);
    }
  }, [isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      if (type === 'pdf') {
        const response = await apiService.generateMinutes(sessionId, formData);
        if (response.success && response.download_url) {
          // Construct the download URL
          const downloadUrl = import.meta.env.PROD 
            ? response.download_url 
            : `http://localhost:5000${response.download_url}`;
          
          // Extract filename from download_url or pdf_file
          let filename = 'meeting_minutes.pdf';
          if (response.pdf_file) {
            filename = response.pdf_file.split('/').pop() || filename;
          } else if (response.download_url) {
            filename = response.download_url.split('/').pop() || filename;
          }
          
          // Create a temporary link and trigger download
          const link = document.createElement('a');
          link.href = downloadUrl;
          link.download = filename;
          link.style.display = 'none';
          document.body.appendChild(link);
          link.click();
          
          // Clean up
          setTimeout(() => {
            document.body.removeChild(link);
          }, 100);
          
          console.log('PDF download initiated successfully');
          
          // Show success state briefly
          setIsSuccess(true);
          setTimeout(() => {
            onClose();
          }, 1000); // Close modal after 1 second to show success state
        } else {
          throw new Error(response.error || 'Failed to generate PDF');
        }
      } else {
        // Ensure recipients are provided for email
        if (!formData.recipients || formData.recipients.length === 0) {
          throw new Error('Please provide at least one recipient email address');
        }
        
        console.log('📧 Sending email with data:', {
          sessionId,
          title: formData.title,
          date: formData.date,
          companyName: formData.companyName,
          recipients: formData.recipients,
          customMessage: formData.customMessage
        });
        
        const response = await apiService.sendEmail(sessionId, formData);
        console.log('📧 Email response:', response);
        
        if (response.success) {
          setIsSuccess(true);
          setTimeout(() => {
            onClose();
          }, 1000);
        } else {
          throw new Error(response.error || 'Failed to send email');
        }
      }
      
      // Don't close immediately for success cases, we handle it above
      if (!isSuccess) {
        onClose();
      }
    } catch (error) {
      console.error('Operation failed:', error);
      
      let errorMessage = `Failed to ${type === 'pdf' ? 'generate PDF' : 'send email'}: `;
      
      if (error instanceof Error) {
        if (error.message.includes('Browser extension interference')) {
          errorMessage += 'Browser extension detected. Please disable extensions and try again.';
        } else if (error.message.includes('Email configuration incomplete')) {
          errorMessage += 'Email is not configured. Please set up email settings in the server configuration.';
        } else if (error.message.includes('Network connection failed')) {
          errorMessage += 'Cannot connect to server. Please check if the server is running.';
        } else {
          errorMessage += error.message;
        }
      } else {
        errorMessage += 'Unknown error occurred.';
      }
      
      alert(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (field: keyof MeetingDetails, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: field === 'recipients' ? value.split(',').map(email => email.trim()) : value,
    }));
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={onClose}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            onClick={(e) => e.stopPropagation()}
            className="bg-slate-800 rounded-2xl p-6 w-full max-w-md border border-slate-700/50 backdrop-blur-lg"
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-2">
                {type === 'pdf' ? (
                  <FileText className="w-6 h-6 text-purple-400" />
                ) : (
                  <Mail className="w-6 h-6 text-purple-400" />
                )}
                <h2 className="text-xl font-semibold text-white">
                  {type === 'pdf' ? 'Generate PDF' : 'Send Email'}
                </h2>
              </div>
              
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={onClose}
                className="p-2 rounded-full hover:bg-slate-700/50 transition-colors"
              >
                <X className="w-5 h-5 text-slate-400" />
              </motion.button>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Meeting Title
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                  className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600/50 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                  placeholder="Enter meeting title"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Meeting Date
                </label>
                <input
                  type="date"
                  value={formData.date}
                  onChange={(e) => handleInputChange('date', e.target.value)}
                  className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600/50 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Company Name
                </label>
                <input
                  type="text"
                  value={formData.companyName}
                  onChange={(e) => handleInputChange('companyName', e.target.value)}
                  className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600/50 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                  placeholder="Enter company name"
                  required
                />
              </div>

              {type === 'email' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Recipients (comma-separated)
                    </label>
                    <textarea
                      value={formData.recipients?.join(', ')}
                      onChange={(e) => handleInputChange('recipients', e.target.value)}
                      className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600/50 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all resize-none"
                      placeholder="john@example.com, jane@example.com"
                      rows={3}
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Custom Message (optional)
                    </label>
                    <textarea
                      value={formData.customMessage}
                      onChange={(e) => handleInputChange('customMessage', e.target.value)}
                      className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600/50 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all resize-none"
                      placeholder="Add a custom message..."
                      rows={3}
                    />
                  </div>
                </>
              )}

              {/* Actions */}
              <div className="flex space-x-3 pt-4">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  type="button"
                  onClick={onClose}
                  className="flex-1 px-4 py-2 border border-slate-600/50 rounded-lg text-slate-300 hover:bg-slate-700/50 transition-colors"
                >
                  Cancel
                </motion.button>
                
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  type="submit"
                  disabled={isSubmitting || isSuccess}
                  className={`flex-1 px-4 py-2 text-white rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 ${
                    isSuccess 
                      ? 'bg-gradient-to-r from-green-500 to-green-600' 
                      : 'bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700'
                  }`}
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Processing...</span>
                    </>
                  ) : isSuccess ? (
                    <span>✓ {type === 'pdf' ? 'PDF Generated!' : 'Email Sent!'}</span>
                  ) : (
                    <span>{type === 'pdf' ? 'Generate PDF' : 'Send Email'}</span>
                  )}
                </motion.button>
              </div>
            </form>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default MeetingModal;