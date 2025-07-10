import { motion, AnimatePresence } from 'framer-motion';
import { useState, useRef, useEffect } from 'react';
import { Send, Volume2, VolumeX, FileText, Mail, Home } from 'lucide-react';
import { Message } from '../types';
import ChatMessage from './ChatMessage';
import MeetingModal from './MeetingModal';
import { apiService } from '../services/api';

interface ChatInterfaceProps {
  sessionId: string;
  onBackToHome: () => void;
}

const ChatInterface = ({ sessionId, onBackToHome }: ChatInterfaceProps) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hi! I've analyzed your meeting recording. You can ask me questions about the meeting content, generate a PDF summary, send minutes to participants, or just have a general conversation - I'm here to help with anything!",
      sender: 'bot',
      timestamp: new Date(),
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [ttsEnabled, setTtsEnabled] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState<'pdf' | 'email'>('pdf');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    const messageText = inputText;
    setInputText('');
    setIsTyping(true);

    try {
      const response = await apiService.sendChatMessage(sessionId, messageText);
      
      if (response.success && response.response) {
        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: response.response,
          sender: 'bot',
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, botMessage]);

        // If TTS is enabled, play the response
        if (ttsEnabled) {
          try {
            const ttsResponse = await apiService.generateTTS(sessionId, response.response);
            
            if (ttsResponse.success && ttsResponse.audio_url) {
              // The backend returns the full path like "/audio/temp/filename.wav"
              const audioUrl = import.meta.env.PROD 
                ? ttsResponse.audio_url 
                : `http://localhost:5000${ttsResponse.audio_url}`;
                
              const audio = new Audio(audioUrl);
              audio.play().catch(console.error);
            } else {
              console.error('TTS failed:', ttsResponse.error || 'No audio URL returned');
            }
          } catch (ttsError) {
            console.error('TTS failed:', ttsError);
          }
        }
      } else {
        throw new Error(response.error || 'Failed to get response');
      }
    } catch (error) {
      console.error('Chat message failed:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "I'm sorry, I'm having trouble responding right now. Please try again.",
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleTextareaResize = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-900 overflow-hidden z-50">
      {/* Navbar */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex justify-between items-center px-4 md:px-8 py-4 bg-slate-800/90 backdrop-blur-lg border-b border-slate-700/50"
      >
        <div className="flex items-center space-x-2 text-xl font-bold text-purple-400">
          <span>ConverSync</span>
        </div>
        
        <div className="flex items-center space-x-3">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => {
              setModalType('pdf');
              setShowModal(true);
            }}
            className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-purple-500/20 border border-purple-500/50 text-white hover:bg-purple-500/30 transition-colors"
          >
            <FileText className="w-4 h-4" />
            <span className="hidden sm:inline">Generate PDF</span>
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => {
              setModalType('email');
              setShowModal(true);
            }}
            className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-purple-500/20 border border-purple-500/50 text-white hover:bg-purple-500/30 transition-colors"
          >
            <Mail className="w-4 h-4" />
            <span className="hidden sm:inline">Send Email</span>
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onBackToHome}
            className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-slate-500/20 border border-slate-500/50 text-white hover:bg-slate-500/30 transition-colors"
          >
            <Home className="w-4 h-4" />
            <span className="hidden sm:inline">Home</span>
          </motion.button>
        </div>
      </motion.div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4" style={{ height: 'calc(100vh - 200px)' }}>
        <AnimatePresence>
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
        </AnimatePresence>
        
        {/* Typing Indicator */}
        <AnimatePresence>
          {isTyping && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="flex items-center space-x-3 ml-12"
            >
              <div className="text-slate-400 text-sm">ConverSync is thinking...</div>
              <div className="flex space-x-1">
                {[...Array(3)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="w-2 h-2 bg-purple-500 rounded-full"
                    animate={{ scale: [1, 1.5, 1] }}
                    transition={{
                      duration: 0.6,
                      repeat: Infinity,
                      delay: i * 0.2,
                    }}
                  />
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="p-4 bg-slate-800/90 backdrop-blur-lg border-t border-slate-700/50"
      >
        <div className="max-w-4xl mx-auto">
          <div className="relative">
            <textarea
              ref={textareaRef}
              value={inputText}
              onChange={(e) => {
                setInputText(e.target.value);
                handleTextareaResize();
              }}
              onKeyDown={handleKeyDown}
              placeholder="Ask me anything..."
              className="w-full px-4 py-3 pr-20 bg-slate-700/50 border border-slate-600/50 rounded-2xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all resize-none"
              style={{ minHeight: '50px', maxHeight: '120px' }}
            />
            
            <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center space-x-2">
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={() => setTtsEnabled(!ttsEnabled)}
                className={`p-2 rounded-full transition-colors ${
                  ttsEnabled 
                    ? 'bg-green-500 text-white' 
                    : 'bg-slate-600 text-slate-300 hover:bg-slate-500'
                }`}
              >
                {ttsEnabled ? (
                  <Volume2 className="w-4 h-4" />
                ) : (
                  <VolumeX className="w-4 h-4" />
                )}
              </motion.button>
              
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={handleSendMessage}
                disabled={!inputText.trim()}
                className="p-2 rounded-full bg-purple-500 text-white hover:bg-purple-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send className="w-4 h-4" />
              </motion.button>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Modal */}
      <MeetingModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        type={modalType}
        sessionId={sessionId}
      />
    </div>
  );
};

export default ChatInterface;