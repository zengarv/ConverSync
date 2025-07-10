import { motion } from 'framer-motion';
import { Bot, User } from 'lucide-react';
import { Message } from '../types';

interface ChatMessageProps {
  message: Message;
}

const ChatMessage = ({ message }: ChatMessageProps) => {
  const isBot = message.sender === 'bot';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
      className={`flex gap-3 ${isBot ? '' : 'flex-row-reverse'}`}
    >
      {/* Avatar */}
      <motion.div
        whileHover={{ scale: 1.1 }}
        className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
          isBot
            ? 'bg-gradient-to-br from-purple-500 to-purple-600'
            : 'bg-gradient-to-br from-blue-500 to-blue-600'
        }`}
      >
        {isBot ? (
          <Bot className="w-5 h-5 text-white" />
        ) : (
          <User className="w-5 h-5 text-white" />
        )}
      </motion.div>

      {/* Message Content */}
      <motion.div
        whileHover={{ scale: 1.01 }}
        className={`max-w-[70%] px-4 py-3 rounded-2xl backdrop-blur-lg border ${
          isBot
            ? 'bg-slate-800/50 border-slate-700/50 text-white'
            : 'bg-purple-500/20 border-purple-500/30 text-white'
        }`}
        style={{
          borderRadius: isBot ? '20px 20px 20px 5px' : '20px 20px 5px 20px',
        }}
      >
        <p className="text-sm leading-relaxed whitespace-pre-wrap">
          {message.text}
        </p>
        
        <div className="flex justify-end mt-2">
          <span className="text-xs text-slate-400">
            {message.timestamp.toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default ChatMessage;