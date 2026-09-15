import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ShieldCheck } from 'lucide-react';

export default function Splash() {
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => {
      navigate('/home');
    }, 3000);
    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <motion.div 
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
        className="relative mb-8"
      >
        <div className="absolute inset-0 bg-[var(--primary)] blur-[80px] opacity-20 rounded-full animate-pulse-ring"></div>
        <div className="w-24 h-24 rounded-[32px] glass-panel-solid flex items-center justify-center relative z-10 border border-[var(--primary)]/30 shadow-[0_0_40px_rgba(16,185,129,0.2)]">
          <ShieldCheck className="w-12 h-12 text-[var(--primary)]" strokeWidth={1.5} />
          {/* Scanning beam across icon */}
          <div className="absolute inset-0 overflow-hidden rounded-[32px]">
            <div className="absolute inset-0 animate-scan-beam"></div>
          </div>
        </div>
      </motion.div>
      
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.3, duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        className="text-center"
      >
        <h1 className="text-4xl font-bold tracking-tight text-white mb-3">HoloSecure</h1>
        <div className="flex items-center justify-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-[var(--primary)] animate-pulse"></div>
          <p className="text-[var(--text-secondary)] text-sm uppercase tracking-[0.2em] font-medium">Enterprise Security</p>
        </div>
      </motion.div>
    </div>
  );
}
