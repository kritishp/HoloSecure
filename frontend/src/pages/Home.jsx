import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  UserPlus, 
  Camera, 
  ShieldCheck, 
  Activity,
  Clock,
  Users,
  CheckCircle2,
  ChevronRight,
  TrendingUp,
  Cpu,
  Download
} from 'lucide-react';

export default function Home() {
  const navigate = useNavigate();
  const [time, setTime] = useState(new Date());
  const [stats, setStats] = useState({ verified_today: 0, total_enrolled: 0 });

  useEffect(() => {
    fetch('http://localhost:8000/api/stats')
      .then(res => res.json())
      .then(data => setStats(data))
      .catch(err => console.error("Error fetching stats:", err));
  }, []);

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const timeString = time.toLocaleTimeString('en-US', { 
    hour: 'numeric', 
    minute: '2-digit',
    hour12: true 
  });
  const dateString = time.toLocaleDateString('en-US', { 
    weekday: 'long', 
    month: 'long', 
    day: 'numeric' 
  });

  const getGreeting = () => {
    const hour = time.getHours();
    if (hour < 12) return "Good morning";
    if (hour < 17) return "Good afternoon";
    return "Good evening";
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
  };

  return (
    <div className="flex flex-col min-h-screen p-6 max-w-2xl mx-auto">
      
      {/* Header */}
      <motion.header 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        className="flex items-center justify-between mb-8 mt-4"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl glass-panel-solid flex items-center justify-center border-[var(--primary)]/30">
            <ShieldCheck className="w-5 h-5 text-[var(--primary)]" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white">HoloSecure</h1>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[var(--success)] animate-pulse"></span>
              <span className="text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wider">System Online</span>
            </div>
          </div>
        </div>
      </motion.header>

      <motion.div 
        variants={containerVariants}
        initial="hidden"
        animate="show"
        className="space-y-6"
      >
        {/* Greeting Section */}
        <motion.section variants={itemVariants}>
          <h2 className="text-3xl font-semibold tracking-tight text-white mb-1">
            {getGreeting()}, <span className="text-[var(--text-secondary)]">Admin</span>
          </h2>
          <p className="text-[var(--text-secondary)] flex items-center gap-2">
            <Clock className="w-4 h-4" /> {dateString} • {timeString}
          </p>
        </motion.section>

        {/* Core Actions (Hero Cards) */}
        <motion.section variants={itemVariants} className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={() => navigate('/register')}
            className="group relative overflow-hidden glass-panel rounded-[24px] p-6 text-left transition-all duration-300 hover:scale-[1.02]"
          >
            <div className="absolute top-0 right-0 p-6 opacity-0 group-hover:opacity-100 transition-opacity transform translate-x-4 group-hover:translate-x-0 duration-300">
              <ChevronRight className="w-5 h-5 text-[var(--text-secondary)]" />
            </div>
            <div className="w-12 h-12 rounded-2xl glass-panel-solid flex items-center justify-center mb-4 group-hover:border-[var(--primary)]/50 transition-colors">
              <UserPlus className="w-6 h-6 text-[var(--text-primary)]" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-1">Enroll Student</h3>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              Register new facial biometric profiles securely.
            </p>
          </button>

          <button
            onClick={() => navigate('/attendance')}
            className="group relative overflow-hidden glass-panel rounded-[24px] p-6 text-left transition-all duration-300 hover:scale-[1.02] border-[var(--primary)]/30"
          >
            <div className="absolute inset-0 bg-[var(--primary)]/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="absolute top-0 right-0 p-6 opacity-0 group-hover:opacity-100 transition-opacity transform translate-x-4 group-hover:translate-x-0 duration-300">
              <ChevronRight className="w-5 h-5 text-[var(--primary)]" />
            </div>
            <div className="w-12 h-12 rounded-2xl bg-[var(--primary)]/10 flex items-center justify-center mb-4 border border-[var(--primary)]/20 shadow-[0_0_15px_rgba(16,185,129,0.15)] group-hover:shadow-[0_0_25px_rgba(16,185,129,0.25)] transition-all">
              <Camera className="w-6 h-6 text-[var(--primary)]" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-1">Verify Identity</h3>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              Launch AI anti-spoofing attendance scanner.
            </p>
          </button>
        </motion.section>

        {/* Quick Stats Grid */}
        <motion.section variants={itemVariants}>
          <h3 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wider mb-4">Today's Overview</h3>
          <div className="grid grid-cols-2 gap-4">
            
            <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between">
              <div className="flex items-center justify-between mb-3">
                <div className="w-8 h-8 rounded-lg bg-[var(--success)]/10 flex items-center justify-center">
                  <CheckCircle2 className="w-4 h-4 text-[var(--success)]" />
                </div>
                <TrendingUp className="w-4 h-4 text-[var(--success)] opacity-70" />
              </div>
              <div>
                <span className="text-3xl font-bold text-white tracking-tight">{stats.verified_today}</span>
                <span className="text-sm text-[var(--text-secondary)] ml-2">verified</span>
              </div>
            </div>

            <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between">
              <div className="flex items-center justify-between mb-3">
                <div className="w-8 h-8 rounded-lg bg-[var(--secondary)]/10 flex items-center justify-center">
                  <Users className="w-4 h-4 text-[var(--secondary)]" />
                </div>
              </div>
              <div>
                <span className="text-3xl font-bold text-white tracking-tight">{stats.total_enrolled}</span>
                <span className="text-sm text-[var(--text-secondary)] ml-2">enrolled</span>
              </div>
            </div>

          </div>
          
          <button 
            onClick={() => window.open('http://localhost:8000/api/attendance/export', '_blank')}
            className="w-full mt-4 glass-panel p-4 rounded-2xl flex items-center justify-center gap-2 text-[var(--text-secondary)] hover:text-white hover:border-[var(--primary)]/30 transition-colors"
          >
            <Download className="w-4 h-4" />
            <span className="text-sm font-semibold">Export Daily Attendance (CSV)</span>
          </button>
        </motion.section>

        {/* System Health */}
        <motion.section variants={itemVariants} className="pt-2">
          <div className="glass-panel-solid rounded-2xl p-5 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-full bg-[var(--surface-hover)] flex items-center justify-center">
                <Cpu className="w-5 h-5 text-[var(--text-muted)]" />
              </div>
              <div>
                <h4 className="text-sm font-semibold text-white">AI Engine Health</h4>
                <p className="text-xs text-[var(--text-secondary)]">EfficientNet-B0 active</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-[var(--primary)] bg-[var(--primary)]/10 px-2.5 py-1 rounded-full border border-[var(--primary)]/20">
                Optimal
              </span>
            </div>
          </div>
        </motion.section>

      </motion.div>
    </div>
  );
}
