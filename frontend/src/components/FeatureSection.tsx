import { motion } from 'framer-motion';
import { FileText, Mail, MessageSquare } from 'lucide-react';

const FeatureSection = () => {
  const features = [
    {
      icon: FileText,
      title: 'Smart Meeting Minutes',
      description: 'Automatically generate comprehensive meeting minutes with key decisions, action items, and important discussions highlighted for easy reference.',
    },
    {
      icon: Mail,
      title: 'Automated Mail Service',
      description: 'Send personalized follow-up emails to participants with relevant action items, deadlines, and meeting summaries tailored to each attendee.',
    },
    {
      icon: MessageSquare,
      title: 'Follow-Up Questions',
      description: 'Never lose a single detail about the meeting. Have some doubt? Instantly ask ConverSync for clarification.',
    },
  ];

  return (
    <section className="py-20 px-4">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl font-bold text-purple-400 mb-4">FEATURES</h2>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              whileHover={{ y: -10, scale: 1.02 }}
              transition={{ duration: 0.5, delay: index * 0.2 }}
              className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-8 border border-slate-700/50 hover:border-purple-500/50 transition-all"
            >
              <motion.div
                whileHover={{ rotate: 360 }}
                transition={{ duration: 0.5 }}
                className="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center mb-6"
              >
                <feature.icon className="w-8 h-8 text-white" />
              </motion.div>
              
              <h3 className="text-xl font-semibold text-white mb-4">
                {feature.title}
              </h3>
              
              <p className="text-slate-300 leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeatureSection;