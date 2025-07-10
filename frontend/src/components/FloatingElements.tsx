import { motion } from 'framer-motion';

const FloatingElements = () => {
  const bubbles = [
    { 
      size: 120, 
      delay: 0, 
      position: { top: '15%', left: '8%' },
      duration: 8,
      opacity: [0.3, 0.6, 0.3]
    },
    { 
      size: 180, 
      delay: 2, 
      position: { top: '45%', right: '12%' },
      duration: 10,
      opacity: [0.4, 0.7, 0.4]
    },
    { 
      size: 90, 
      delay: 4, 
      position: { bottom: '25%', left: '15%' },
      duration: 7,
      opacity: [0.25, 0.5, 0.25]
    },
    { 
      size: 150, 
      delay: 1, 
      position: { top: '70%', right: '25%' },
      duration: 9,
      opacity: [0.35, 0.65, 0.35]
    },
    { 
      size: 100, 
      delay: 3, 
      position: { top: '30%', left: '70%' },
      duration: 6,
      opacity: [0.2, 0.45, 0.2]
    },
    { 
      size: 200, 
      delay: 5, 
      position: { bottom: '10%', right: '5%' },
      duration: 12,
      opacity: [0.15, 0.4, 0.15]
    },
    { 
      size: 80, 
      delay: 2.5, 
      position: { top: '5%', left: '45%' },
      duration: 5,
      opacity: [0.3, 0.6, 0.3]
    },
    { 
      size: 140, 
      delay: 6, 
      position: { bottom: '50%', left: '5%' },
      duration: 11,
      opacity: [0.25, 0.55, 0.25]
    }
  ];

  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden">
      {bubbles.map((bubble, index) => (
        <motion.div
          key={index}
          className="absolute rounded-full"
          style={{
            width: bubble.size,
            height: bubble.size,
            background: 'radial-gradient(circle, rgba(124, 58, 237, 0.8) 0%, rgba(168, 85, 247, 0.6) 30%, rgba(124, 58, 237, 0.4) 60%, rgba(168, 85, 247, 0.2) 80%, transparent 100%)',
            boxShadow: '0 0 40px rgba(124, 58, 237, 0.3), inset 0 0 20px rgba(168, 85, 247, 0.2)',
            ...bubble.position,
          }}
          animate={{
            y: [-30, 30, -30],
            x: [-15, 15, -15],
            scale: [1, 1.15, 1],
            opacity: bubble.opacity,
          }}
          transition={{
            duration: bubble.duration,
            repeat: Infinity,
            delay: bubble.delay,
            ease: 'easeInOut',
          }}
        />
      ))}
      
      {/* Additional medium-sized glowing orbs */}
      {Array.from({ length: 6 }).map((_, index) => (
        <motion.div
          key={`orb-${index}`}
          className="absolute rounded-full"
          style={{
            width: 40 + Math.random() * 30,
            height: 40 + Math.random() * 30,
            top: `${Math.random() * 100}%`,
            left: `${Math.random() * 100}%`,
            background: 'radial-gradient(circle, rgba(168, 85, 247, 0.6) 0%, rgba(124, 58, 237, 0.3) 50%, transparent 100%)',
            boxShadow: '0 0 20px rgba(168, 85, 247, 0.4)',
          }}
          animate={{
            y: [-25, 25, -25],
            x: [-12, 12, -12],
            opacity: [0.3, 0.7, 0.3],
            scale: [0.8, 1.2, 0.8],
          }}
          transition={{
            duration: 6 + Math.random() * 4,
            repeat: Infinity,
            delay: Math.random() * 6,
            ease: 'easeInOut',
          }}
        />
      ))}
      
      {/* Smaller floating particles with more visibility */}
      {Array.from({ length: 15 }).map((_, index) => (
        <motion.div
          key={`particle-${index}`}
          className="absolute rounded-full"
          style={{
            width: 8 + Math.random() * 12,
            height: 8 + Math.random() * 12,
            top: `${Math.random() * 100}%`,
            left: `${Math.random() * 100}%`,
            background: 'radial-gradient(circle, rgba(168, 85, 247, 0.8) 0%, rgba(124, 58, 237, 0.4) 70%, transparent 100%)',
            boxShadow: '0 0 10px rgba(168, 85, 247, 0.5)',
          }}
          animate={{
            y: [-20, 20, -20],
            x: [-10, 10, -10],
            opacity: [0.2, 0.8, 0.2],
            scale: [0.5, 1.3, 0.5],
          }}
          transition={{
            duration: 4 + Math.random() * 4,
            repeat: Infinity,
            delay: Math.random() * 8,
            ease: 'easeInOut',
          }}
        />
      ))}
    </div>
  );
};

export default FloatingElements;