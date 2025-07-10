import { motion } from 'framer-motion';
import { Bot, Home } from 'lucide-react';

interface NavbarProps {
  isInChat?: boolean;
  onBackToHome?: () => void;
}

const Navbar = ({ isInChat, onBackToHome }: NavbarProps) => {
  return (
    <motion.nav
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="fixed top-0 left-0 right-0 z-50 flex justify-between items-center px-4 md:px-8 py-4 bg-slate-900/90 backdrop-blur-lg border-b border-white/10"
    >
      <motion.div
        whileHover={{ scale: 1.05 }}
        className="flex items-center space-x-2 text-xl font-bold text-purple-400"
      >
        <Bot className="w-6 h-6" />
        <span>ConverSync</span>
      </motion.div>
      
      {isInChat && (
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onBackToHome}
          className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-purple-500/20 border border-purple-500/50 text-white hover:bg-purple-500/30 transition-colors"
        >
          <Home className="w-4 h-4" />
          <span>Home</span>
        </motion.button>
      )}
    </motion.nav>
  );
};

export default Navbar;