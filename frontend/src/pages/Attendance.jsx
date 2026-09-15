import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import Webcam from 'react-webcam';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ArrowLeft, 
  ShieldCheck, 
  CheckCircle2, 
  AlertTriangle,
  Fingerprint,
  RefreshCcw,
  Check,
  UserCheck,
  Download
} from 'lucide-react';

export default function Attendance() {
  const navigate = useNavigate();
  const webcamRef = useRef(null);
  const wsRef = useRef(null);
  const timerRef = useRef(null);
  const transitioningRef = useRef(false);
  
  const [tasks, setTasks] = useState([]);
  const [currentTaskIndex, setCurrentTaskIndex] = useState(0);
  const [status, setStatus] = useState('LOADING'); // LOADING, VERIFYING, SUCCESS, ERROR
  const [wsData, setWsData] = useState({ 
    detected: false, 
    recognition_confidence: 0,
    liveness_confidence: 0,
    student: null
  });
  const [errorMsg, setErrorMsg] = useState('');
  const [markMessage, setMarkMessage] = useState('');
  const [timeLeft, setTimeLeft] = useState(20);
  
  const currentTaskIndexRef = useRef(currentTaskIndex);
  const tasksRef = useRef(tasks);
  const studentRef = useRef(null);
  
  useEffect(() => {
    currentTaskIndexRef.current = currentTaskIndex;
  }, [currentTaskIndex]);
  
  useEffect(() => {
    tasksRef.current = tasks;
  }, [tasks]);

  // Fetch tasks
  useEffect(() => {
    fetch('http://localhost:8000/api/tasks')
      .then(res => res.json())
      .then(data => {
        setTasks(data.tasks);
        setStatus('VERIFYING');
      })
      .catch(err => {
        setErrorMsg('Failed to load tasks from server.');
        setStatus('ERROR');
      });
  }, []);

  // Timer Countdown Logic
  useEffect(() => {
    if (status !== 'VERIFYING') return;

    setTimeLeft(20);

    const countdown = setInterval(() => {
      if (transitioningRef.current) return;
      
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(countdown);
          setErrorMsg('Verification timeout. Please try again.');
          setStatus('ERROR');
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(countdown);
  }, [currentTaskIndex, status]);

  // WebSocket Connection
  useEffect(() => {
    const markAttendance = async (student) => {
      try {
        console.log('Marking attendance for:', student);
        const response = await fetch('http://localhost:8000/api/attendance/mark', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ student_id: student.student_id })
        });
        const result = await response.json();
        setMarkMessage(result.message || '');
        if (!result.success) {
          console.error('Failed to mark attendance:', result);
        } else {
          console.log('Successfully marked attendance');
        }
      } catch (e) {
        console.error('Network error while marking attendance:', e);
      }
    };

    if (status !== 'VERIFYING') return;

    wsRef.current = new WebSocket('ws://localhost:8000/ws/attendance');
    
    wsRef.current.onopen = () => {
      console.log('WebSocket Connected');
      startFrameLoop();
    };
    
    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.student) {
        studentRef.current = data.student;
      }
      
      setWsData(prev => ({
        ...data,
        student: data.student || prev.student
      }));
      
      const currentExpectedTask = tasksRef.current[currentTaskIndexRef.current];
      if (data.task_passed && data.evaluated_task === currentExpectedTask && !transitioningRef.current) {
        transitioningRef.current = true;
        
        // Wait 1s so user can see it passed
        setTimeout(() => {
          if (currentTaskIndexRef.current < tasksRef.current.length - 1) {
            setCurrentTaskIndex(prev => prev + 1);
            transitioningRef.current = false;
          } else {
            // All tasks completed
            setStatus('SUCCESS');
            const finalStudent = data.student || studentRef.current;
            if (finalStudent) {
              markAttendance(finalStudent);
            }
          }
        }, 1000);
      }
    };

    wsRef.current.onerror = (error) => {
      console.error('WebSocket Error:', error);
      setErrorMsg('Lost connection to verification server.');
      setStatus('ERROR');
    };

    return () => {
      if (wsRef.current) wsRef.current.close();
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [status]); // Removed currentTaskIndex and tasks to prevent reconnects

  const startFrameLoop = useCallback(() => {
    if (timerRef.current) clearInterval(timerRef.current);
    
    timerRef.current = setInterval(() => {
      if (webcamRef.current && wsRef.current && wsRef.current.readyState === WebSocket.OPEN && !transitioningRef.current) {
        const imageSrc = webcamRef.current.getScreenshot();
        if (imageSrc) {
          const currentTask = tasksRef.current[currentTaskIndexRef.current];
          wsRef.current.send(JSON.stringify({
            frame: imageSrc,
            current_task: currentTask
          }));
        }
      }
    }, 100);
  }, []);

  const currentTask = tasks[currentTaskIndex];
  
  const getTaskDisplayName = (task) => {
    if (!task) return '';
    return task.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
  };

  const CircularProgress = ({ score, color, label }) => {
    const radius = 24;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (score * circumference);
    return (
      <div className="flex flex-col items-center gap-1">
        <div className="relative w-14 h-14 flex items-center justify-center">
          <svg className="transform -rotate-90 w-14 h-14">
            <circle cx="28" cy="28" r="24" stroke="currentColor" strokeWidth="4" fill="transparent" className="text-[var(--border)]" />
            <circle cx="28" cy="28" r="24" stroke="currentColor" strokeWidth="4" fill="transparent" className={color}
              strokeDasharray={circumference} strokeDashoffset={strokeDashoffset} strokeLinecap="round" style={{ transition: 'stroke-dashoffset 0.3s ease' }} />
          </svg>
          <span className="absolute text-[10px] font-bold text-white">{Math.round(score * 100)}%</span>
        </div>
        <span className="text-[9px] uppercase tracking-wider text-[var(--text-secondary)] font-semibold">{label}</span>
      </div>
    );
  };

  return (
    <div className="flex flex-col min-h-screen p-6 max-w-xl mx-auto">
      
      {/* Header */}
      <div className="flex items-center gap-4 mt-8 mb-6 relative z-10">
        <button onClick={() => navigate('/home')} className="w-10 h-10 rounded-full glass-panel flex items-center justify-center hover:bg-white/10 transition-colors">
          <ArrowLeft className="w-5 h-5 text-white" />
        </button>
        <h1 className="text-2xl font-bold text-white tracking-tight">Identity Verification</h1>
      </div>

      <AnimatePresence mode="wait">
        
        {status === 'LOADING' && (
          <motion.div 
            key="loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex-1 flex flex-col items-center justify-center"
          >
            <div className="w-16 h-16 rounded-full glass-panel flex items-center justify-center mb-4">
              <RefreshCcw className="w-6 h-6 text-[var(--primary)] animate-spin-slow" />
            </div>
            <p className="text-[var(--text-secondary)] font-medium">Initializing AI Engine...</p>
          </motion.div>
        )}

        {status === 'VERIFYING' && currentTask && (
          <motion.div 
            key="verifying"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
            className="flex-1 flex flex-col relative"
          >
            {/* Premium Camera Viewport */}
            <div className="relative w-full aspect-[3/4] rounded-[32px] overflow-hidden glass-panel-solid mb-6 p-2 shadow-2xl">
              <div className="relative w-full h-full rounded-[24px] overflow-hidden bg-black">
                <Webcam
                  ref={webcamRef}
                  audio={false}
                  screenshotFormat="image/jpeg"
                  screenshotQuality={0.8}
                  forceScreenshotSourceSize={true}
                  videoConstraints={{ facingMode: "user", width: 1280, height: 720 }}
                  className="w-full h-full object-cover"
                />
                
                {/* HUD Elements */}
                <div className="absolute top-4 left-4 right-4 flex justify-between items-start">
                  <div className={`px-3 py-1.5 rounded-full flex items-center gap-2 border ${wsData.detected ? 'bg-[var(--success)]/20 border-[var(--success)]/40 text-[var(--success)]' : 'bg-[var(--error)]/20 border-[var(--error)]/40 text-[var(--error)]'} backdrop-blur-md`}>
                    <div className={`w-2 h-2 rounded-full ${wsData.detected ? 'bg-[var(--success)] animate-pulse' : 'bg-[var(--error)]'}`}></div>
                    <span className="text-[10px] font-bold uppercase tracking-wider">{wsData.detected ? 'Face Detected' : 'No Face'}</span>
                  </div>
                  
                  {wsData.detected && (
                    <div className="flex gap-3 bg-[var(--background)]/60 backdrop-blur-md p-2 rounded-2xl border border-[var(--border)]">
                      <CircularProgress score={wsData.recognition_confidence} color="text-[var(--secondary)]" label="Match" />
                      <div className="w-[1px] h-10 bg-[var(--border)] self-center"></div>
                      <CircularProgress score={wsData.liveness_confidence} color="text-[var(--primary)]" label="Live" />
                    </div>
                  )}
                </div>

                {/* Corner Guides */}
                <div className="absolute top-8 left-8 w-12 h-12 border-t-[3px] border-l-[3px] border-[var(--primary)] rounded-tl-2xl opacity-70"></div>
                <div className="absolute top-8 right-8 w-12 h-12 border-t-[3px] border-r-[3px] border-[var(--primary)] rounded-tr-2xl opacity-70"></div>
                <div className="absolute bottom-8 left-8 w-12 h-12 border-b-[3px] border-l-[3px] border-[var(--primary)] rounded-bl-2xl opacity-70"></div>
                <div className="absolute bottom-8 right-8 w-12 h-12 border-b-[3px] border-r-[3px] border-[var(--primary)] rounded-br-2xl opacity-70"></div>
                
                {/* Scan Beam */}
                <div className="absolute inset-0 z-10 animate-scan-beam opacity-30"></div>
              </div>
            </div>
            
            {/* Interactive Verification Task Card */}
            <AnimatePresence mode="wait">
              <motion.div
                key={currentTaskIndex}
                initial={{ y: 20, opacity: 0, scale: 0.95 }}
                animate={{ y: 0, opacity: 1, scale: 1 }}
                exit={{ y: -20, opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
                className={`glass-panel p-6 rounded-[24px] text-center border-2 transition-colors duration-500 ${transitioningRef.current ? 'border-[var(--success)] bg-[var(--success)]/10' : 'border-[var(--border)]'}`}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Fingerprint className="w-5 h-5 text-[var(--primary)]" />
                    <span className="text-xs uppercase tracking-widest text-[var(--text-secondary)] font-bold">Challenge {currentTaskIndex + 1} of {tasks.length}</span>
                  </div>
                  {!transitioningRef.current && (
                    <div className={`text-sm font-bold ${timeLeft <= 5 ? 'text-[var(--error)] animate-pulse' : 'text-[var(--text-secondary)]'}`}>
                      {timeLeft}s
                    </div>
                  )}
                  {transitioningRef.current && (
                    <div className="bg-[var(--success)] rounded-full p-1">
                      <Check className="w-4 h-4 text-white" />
                    </div>
                  )}
                </div>
                
                <h2 className="text-3xl font-bold text-white tracking-tight mb-6">
                  {getTaskDisplayName(currentTask)}
                </h2>
                
                {/* Segmented Progress */}
                <div className="flex justify-center gap-2">
                  {tasks.map((_, idx) => (
                    <div 
                      key={idx} 
                      className={`h-1.5 flex-1 rounded-full transition-all duration-500 ${
                        idx < currentTaskIndex || (idx === currentTaskIndex && transitioningRef.current)
                        ? 'bg-[var(--success)] shadow-[0_0_10px_var(--success-glow)]' 
                        : idx === currentTaskIndex 
                        ? 'bg-[var(--primary)] shadow-[0_0_10px_var(--primary-glow)]' 
                        : 'bg-[var(--surface-hover)]'
                      }`}
                    ></div>
                  ))}
                </div>
              </motion.div>
            </AnimatePresence>
          </motion.div>
        )}

        {status === 'SUCCESS' && (
          <motion.div 
            key="success"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            className="flex-1 flex flex-col items-center justify-center text-center py-10"
          >
            <div className="relative mb-8">
              <div className="w-32 h-32 rounded-full glass-panel flex items-center justify-center shadow-[0_0_50px_var(--success-glow)]">
                <CheckCircle2 className="w-16 h-16 text-[var(--success)]" />
              </div>
              <div className="absolute inset-0 rounded-full border-2 border-[var(--success)] animate-pulse-ring"></div>
            </div>
            
            <h2 className="text-3xl font-bold text-white mb-2 tracking-tight">
              {markMessage === 'Already marked present today' ? 'Already Marked' : 'Identity Verified'}
            </h2>
            <p className="text-[var(--text-secondary)] mb-8">
              {markMessage === 'Already marked present today' 
                ? `${wsData.student?.name || 'User'} has already been marked present for today.` 
                : 'Biometric attendance securely logged.'}
            </p>
            
            <div className="glass-panel w-full p-6 rounded-[24px] mb-10 flex items-center gap-4">
              <div className="w-14 h-14 rounded-2xl bg-[var(--surface-solid)] flex items-center justify-center">
                <UserCheck className="w-6 h-6 text-[var(--text-primary)]" />
              </div>
              <div className="text-left flex-1">
                <h3 className="text-lg font-bold text-white">{wsData.student?.name || 'Verified User'}</h3>
                <p className="text-sm text-[var(--text-secondary)]">{wsData.student?.student_id || 'ID Confirmed'}</p>
              </div>
              <div className="px-3 py-1 bg-[var(--success)]/20 text-[var(--success)] rounded-full text-xs font-bold border border-[var(--success)]/30">
                MATCHED
              </div>
            </div>
            
            <div className="w-full space-y-4">
              <button 
                onClick={() => { setStatus('LOADING'); setCurrentTaskIndex(0); window.location.reload(); }}
                className="w-full premium-btn-primary p-4 rounded-2xl font-bold text-base"
              >
                Scan Next Student
              </button>
              <button 
                onClick={() => navigate('/')}
                className="w-full bg-[var(--surface-hover)] text-white hover:bg-[var(--surface-solid)] transition-colors p-4 rounded-2xl font-bold text-base"
              >
                Return to Dashboard
              </button>
              <button 
                onClick={() => window.open('http://localhost:8000/api/attendance/export', '_blank')}
                className="w-full premium-btn p-4 rounded-2xl font-semibold text-base text-white flex items-center justify-center gap-2"
              >
                Export to CSV <Download className="w-5 h-5" />
              </button>
            </div>
          </motion.div>
        )}

        {status === 'ERROR' && (
          <motion.div 
            key="error"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex-1 flex flex-col items-center justify-center text-center"
          >
            <div className="w-32 h-32 rounded-full bg-[var(--error)]/10 border border-[var(--error)]/20 flex items-center justify-center shadow-[0_0_50px_var(--error-glow)] mb-8">
              <AlertTriangle className="w-16 h-16 text-[var(--error)]" />
            </div>
            
            <h2 className="text-3xl font-bold text-white mb-3 tracking-tight">Access Denied</h2>
            <p className="text-[var(--text-secondary)] mb-10 max-w-[80%] mx-auto leading-relaxed">
              {errorMsg || 'Failed to verify identity. Please ensure you are clearly visible and follow instructions.'}
            </p>
            
            <div className="w-full space-y-4">
              <button 
                onClick={() => { setStatus('LOADING'); setCurrentTaskIndex(0); window.location.reload(); }}
                className="w-full premium-btn p-4 rounded-2xl font-bold text-base text-[var(--error)] border-[var(--error)]/30"
              >
                Retry Scan
              </button>
              <button 
                onClick={() => navigate('/home')}
                className="w-full premium-btn p-4 rounded-2xl font-semibold text-base text-white"
              >
                Return to Dashboard
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
