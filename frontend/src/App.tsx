import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Navbar from './components/Navbar';
import HeroSection from './components/HeroSection';
import FeatureSection from './components/FeatureSection';
import ChatInterface from './components/ChatInterface';
import FloatingElements from './components/FloatingElements';
import { SessionData, UploadProgress } from './types';
import { apiService } from './services/api';

function App() {
  const [currentSession, setCurrentSession] = useState<SessionData | null>(null);
  const [uploadProgress, setUploadProgress] = useState<UploadProgress>({
    isUploading: false,
    progress: 0,
    status: 'idle',
  });

  const handleFileUpload = async (file: File) => {
    setUploadProgress({
      isUploading: true,
      progress: 0,
      status: 'uploading',
    });

    try {
      // Update progress while uploading
      setUploadProgress(prev => ({
        ...prev,
        progress: 30,
      }));

      // Determine if it's video or audio and transcribe
      let result;
      if (file.type.startsWith('video/')) {
        setUploadProgress(prev => ({
          ...prev,
          status: 'processing',
          progress: 50,
        }));
        result = await apiService.transcribeOnly(file);
      } else if (file.type.startsWith('audio/')) {
        setUploadProgress(prev => ({
          ...prev,
          status: 'processing',
          progress: 50,
        }));
        result = await apiService.transcribeOnly(file);
      } else {
        throw new Error('Unsupported file type');
      }

      if (!result.success) {
        throw new Error(result.error || 'Failed to process file');
      }

      // Start chat session with transcript
      setUploadProgress(prev => ({
        ...prev,
        progress: 80,
      }));

      const chatResult = await apiService.startChatSession(result.transcript || '');
      
      if (!chatResult.success) {
        throw new Error(chatResult.error || 'Failed to start chat session');
      }

      // Create session
      const sessionData: SessionData = {
        id: chatResult.session_id || `session-${Date.now()}`,
        transcript: result.transcript || '',
        isActive: true,
      };

      setCurrentSession(sessionData);
      setUploadProgress({
        isUploading: false,
        progress: 100,
        status: 'complete',
      });

    } catch (error) {
      console.error('Upload failed:', error);
      setUploadProgress({
        isUploading: false,
        progress: 0,
        status: 'error',
      });
    }
  };

  const handleDebugTest = async () => {
    setUploadProgress({
      isUploading: true,
      progress: 0,
      status: 'processing',
    });

    try {
      // Create a test session with sample transcript
      const sampleTranscript = `This is a sample meeting transcript for testing purposes. 
      
Participants: John Smith, Sarah Johnson, Mike Davis

Meeting started at 10:00 AM.

John: Welcome everyone to today's team meeting. Let's start by reviewing our quarterly goals.

Sarah: Thanks John. I wanted to update everyone on the marketing campaign we launched last week. We've seen a 25% increase in engagement.

Mike: That's great news Sarah. From the development side, we've completed 80% of the features for the next release.

John: Excellent progress. Let's discuss the action items for next week.

Action Items:
1. Sarah to prepare detailed marketing report by Friday
2. Mike to complete remaining features by Wednesday
3. Schedule follow-up meeting for next Monday

Meeting ended at 10:45 AM.`;

      setUploadProgress(prev => ({
        ...prev,
        progress: 50,
      }));

      const chatResult = await apiService.startChatSession(sampleTranscript);
      
      if (!chatResult.success) {
        throw new Error(chatResult.error || 'Failed to start test session');
      }

      const sessionData: SessionData = {
        id: chatResult.session_id || `debug-session-${Date.now()}`,
        transcript: sampleTranscript,
        isActive: true,
      };

      setCurrentSession(sessionData);
      setUploadProgress({
        isUploading: false,
        progress: 100,
        status: 'complete',
      });

    } catch (error) {
      console.error('Debug test failed:', error);
      setUploadProgress({
        isUploading: false,
        progress: 0,
        status: 'error',
      });
    }
  };

  const handleBackToHome = () => {
    setCurrentSession(null);
    setUploadProgress({
      isUploading: false,
      progress: 0,
      status: 'idle',
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white relative overflow-hidden">
      <FloatingElements />
      
      <AnimatePresence mode="wait">
        {currentSession ? (
          <motion.div
            key="chat"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            <ChatInterface
              sessionId={currentSession.id}
              onBackToHome={handleBackToHome}
            />
          </motion.div>
        ) : (
          <motion.div
            key="home"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Navbar />
            
            <main className="pt-20">
              <HeroSection
                onFileUpload={handleFileUpload}
                onDebugTest={handleDebugTest}
                uploadProgress={uploadProgress}
              />
              
              <FeatureSection />
            </main>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;