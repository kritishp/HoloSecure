import { useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import Webcam from 'react-webcam';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ArrowLeft, 
  Camera, 
  CheckCircle2, 
  ChevronRight, 
  Scan, 
  ShieldCheck, 
  User,
  GraduationCap
} from 'lucide-react';

const POSES = [
  "Look Straight",
  "Look Left",
  "Look Right",
  "Look Up",
  "Look Down",
  "Smile",
  "Neutral Face"
];

export default function Registration() {
  const navigate = useNavigate();
  const webcamRef = useRef(null);
  const isCapturingRef = useRef(false);
  
  const [currentStep, setCurrentStep] = useState(1);
  const [apiError, setApiError] = useState('');
  
  const [formData, setFormData] = useState({
    name: '',
    student_id: '',
    roll_number: '',
    department: '',
    semester: '',
    section: ''
  });

  const [poseIndex, setPoseIndex] = useState(0);
  const [capturedImages, setCapturedImages] = useState([]);
  const [isCapturing, setIsCapturing] = useState(false);

  const isStep1Valid = formData.name.trim() !== '' && formData.student_id.trim() !== '';
  const isStep2Valid = formData.roll_number.trim() !== '' && formData.department.trim() !== '' && formData.semester.trim() !== '' && formData.section.trim() !== '';

  const nextStep = () => {
    if (currentStep === 1 && isStep1Valid) setCurrentStep(2);
    else if (currentStep === 2 && isStep2Valid) setCurrentStep(3);
  };

  const prevStep = () => {
    if (currentStep > 1 && currentStep < 4) setCurrentStep(currentStep - 1);
    else if (currentStep === 1) navigate('/home');
  };

  const capturePose = useCallback(() => {
    if (!webcamRef.current || isCapturingRef.current || capturedImages.length >= POSES.length) return;
    
    isCapturingRef.current = true;
    setIsCapturing(true);
    
    setTimeout(() => {
      const imageSrc = webcamRef.current.getScreenshot();
      if (imageSrc) {
        const newLength = capturedImages.length + 1;
        setCapturedImages(prev => [...prev, imageSrc]);
        
        if (newLength === POSES.length) {
          submitRegistration([...capturedImages, imageSrc]);
        } else {
          setPoseIndex(prevIdx => prevIdx + 1);
        }
      }
      isCapturingRef.current = false;
      setIsCapturing(false);
    }, 1200); 
  }, [capturedImages.length, formData]);

  const submitRegistration = async (images) => {
    try {
      const response = await fetch('http://localhost:8000/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...formData, images })
      });
      
      const result = await response.json();
      if (result.success) {
        setCurrentStep(4);
      } else {
        setApiError(result.message || 'Registration failed');
        setCurrentStep(2); // Go back to form
      }
    } catch (e) {
      setApiError('Failed to connect to server');
      setCurrentStep(2);
    }
  };

  // Animation variants
  const slideVariants = {
    enter: (direction) => ({
      x: direction > 0 ? 50 : -50,
      opacity: 0
    }),
    center: {
      zIndex: 1,
      x: 0,
      opacity: 1
    },
    exit: (direction) => ({
      zIndex: 0,
      x: direction < 0 ? 50 : -50,
      opacity: 0
    })
  };

  return (
    <div className="flex flex-col min-h-screen p-6 max-w-xl mx-auto">
      
      {/* Header */}
      <div className="flex items-center gap-4 mt-8 mb-8 relative z-10">
        <button 
          onClick={prevStep}
          className="w-10 h-10 rounded-full glass-panel flex items-center justify-center hover:bg-white/10 transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-white" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Enrollment</h1>
          <p className="text-xs text-[var(--text-secondary)] uppercase tracking-wider font-semibold">
            {currentStep === 1 && "Step 1: Personal Details"}
            {currentStep === 2 && "Step 2: Academic Profile"}
            {currentStep === 3 && "Step 3: Biometric Scan"}
            {currentStep === 4 && "Step 4: Completion"}
          </p>
        </div>
      </div>

      {/* Progress Indicator */}
      {currentStep < 4 && (
        <div className="flex gap-2 mb-8">
          {[1, 2, 3].map((step) => (
            <div 
              key={step} 
              className={`h-1.5 flex-1 rounded-full transition-all duration-500 ${
                step < currentStep ? 'bg-[var(--primary)]' : 
                step === currentStep ? 'bg-[var(--primary)] shadow-[0_0_10px_var(--primary-glow)]' : 
                'bg-[var(--surface-hover)]'
              }`}
            />
          ))}
        </div>
      )}

      {apiError && currentStep !== 4 && (
        <motion.div 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 p-4 rounded-xl bg-[var(--error)]/10 border border-[var(--error)]/30 flex items-center gap-3"
        >
          <ShieldCheck className="w-5 h-5 text-[var(--error)]" />
          <p className="text-sm text-[var(--error)]">{apiError}</p>
        </motion.div>
      )}

      <div className="flex-1 relative flex flex-col">
        <AnimatePresence mode="wait" custom={1}>
          
          {/* STEP 1: Personal Info */}
          {currentStep === 1 && (
            <motion.div
              key="step1"
              custom={1}
              variants={slideVariants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
              className="flex flex-col flex-1"
            >
              <div className="glass-panel p-6 rounded-[24px] space-y-5 flex-1">
                <div className="flex items-center gap-3 mb-6 pb-4 border-b border-[var(--border)]">
                  <div className="w-10 h-10 rounded-xl bg-[var(--primary)]/10 flex items-center justify-center">
                    <User className="w-5 h-5 text-[var(--primary)]" />
                  </div>
                  <h2 className="text-lg font-semibold text-white">Personal Information</h2>
                </div>

                <div>
                  <label className="block text-xs uppercase tracking-wider text-[var(--text-secondary)] font-semibold mb-2 ml-1">Full Name</label>
                  <input 
                    type="text" 
                    placeholder="Enter legal name"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    className="w-full premium-input rounded-xl p-4 text-white text-base"
                  />
                </div>
                
                <div>
                  <label className="block text-xs uppercase tracking-wider text-[var(--text-secondary)] font-semibold mb-2 ml-1">Student ID</label>
                  <input 
                    type="text" 
                    placeholder="e.g. STU-2026-001"
                    value={formData.student_id}
                    onChange={(e) => setFormData({...formData, student_id: e.target.value})}
                    className="w-full premium-input rounded-xl p-4 text-white text-base"
                  />
                </div>
              </div>

              <button
                disabled={!isStep1Valid}
                onClick={nextStep}
                className={`mt-6 p-4 rounded-2xl font-bold text-base flex items-center justify-center gap-2 transition-all ${
                  isStep1Valid 
                  ? 'premium-btn-primary' 
                  : 'bg-[var(--surface-solid)] text-[var(--text-muted)] cursor-not-allowed border border-[var(--border)]'
                }`}
              >
                Continue to Academics <ChevronRight className="w-5 h-5" />
              </button>
            </motion.div>
          )}

          {/* STEP 2: Academic Info */}
          {currentStep === 2 && (
            <motion.div
              key="step2"
              custom={1}
              variants={slideVariants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
              className="flex flex-col flex-1"
            >
              <div className="glass-panel p-6 rounded-[24px] space-y-5 flex-1">
                <div className="flex items-center gap-3 mb-6 pb-4 border-b border-[var(--border)]">
                  <div className="w-10 h-10 rounded-xl bg-[var(--secondary)]/10 flex items-center justify-center">
                    <GraduationCap className="w-5 h-5 text-[var(--secondary)]" />
                  </div>
                  <h2 className="text-lg font-semibold text-white">Academic Details</h2>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs uppercase tracking-wider text-[var(--text-secondary)] font-semibold mb-2 ml-1">Roll No.</label>
                    <input 
                      type="text" 
                      value={formData.roll_number}
                      onChange={(e) => setFormData({...formData, roll_number: e.target.value})}
                      className="w-full premium-input rounded-xl p-4 text-white text-base"
                    />
                  </div>
                  <div>
                    <label className="block text-xs uppercase tracking-wider text-[var(--text-secondary)] font-semibold mb-2 ml-1">Semester</label>
                    <input 
                      type="text" 
                      value={formData.semester}
                      onChange={(e) => setFormData({...formData, semester: e.target.value})}
                      className="w-full premium-input rounded-xl p-4 text-white text-base"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs uppercase tracking-wider text-[var(--text-secondary)] font-semibold mb-2 ml-1">Department</label>
                  <input 
                    type="text" 
                    value={formData.department}
                    onChange={(e) => setFormData({...formData, department: e.target.value})}
                    className="w-full premium-input rounded-xl p-4 text-white text-base"
                  />
                </div>

                <div>
                  <label className="block text-xs uppercase tracking-wider text-[var(--text-secondary)] font-semibold mb-2 ml-1">Section</label>
                  <input 
                    type="text" 
                    value={formData.section}
                    onChange={(e) => setFormData({...formData, section: e.target.value})}
                    className="w-full premium-input rounded-xl p-4 text-white text-base"
                  />
                </div>
              </div>

              <button
                disabled={!isStep2Valid}
                onClick={nextStep}
                className={`mt-6 p-4 rounded-2xl font-bold text-base flex items-center justify-center gap-2 transition-all ${
                  isStep2Valid 
                  ? 'premium-btn-primary' 
                  : 'bg-[var(--surface-solid)] text-[var(--text-muted)] cursor-not-allowed border border-[var(--border)]'
                }`}
              >
                Proceed to Biometrics <Scan className="w-5 h-5 ml-1" />
              </button>
            </motion.div>
          )}

          {/* STEP 3: Camera Capture */}
          {currentStep === 3 && (
            <motion.div
              key="step3"
              custom={1}
              variants={slideVariants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
              className="flex flex-col flex-1 items-center justify-center"
            >
              <div className="w-full max-w-sm glass-panel p-2 rounded-[32px] mb-8 relative">
                <div className="relative w-full aspect-[3/4] rounded-[24px] overflow-hidden bg-black">
                  <Webcam
                    ref={webcamRef}
                    audio={false}
                    screenshotFormat="image/jpeg"
                    screenshotQuality={0.8}
                    forceScreenshotSourceSize={true}
                    videoConstraints={{ facingMode: "user", width: 1280, height: 720 }}
                    className="w-full h-full object-cover"
                  />
                  
                  {/* Corner Guides */}
                  <div className="absolute top-8 left-8 w-12 h-12 border-t-4 border-l-4 border-[var(--primary)] rounded-tl-xl opacity-70"></div>
                  <div className="absolute top-8 right-8 w-12 h-12 border-t-4 border-r-4 border-[var(--primary)] rounded-tr-xl opacity-70"></div>
                  <div className="absolute bottom-8 left-8 w-12 h-12 border-b-4 border-l-4 border-[var(--primary)] rounded-bl-xl opacity-70"></div>
                  <div className="absolute bottom-8 right-8 w-12 h-12 border-b-4 border-r-4 border-[var(--primary)] rounded-br-xl opacity-70"></div>

                  {/* Scanning Effect during capture */}
                  {isCapturing && (
                    <div className="absolute inset-0 animate-scan-beam"></div>
                  )}
                </div>
              </div>

              <motion.div
                key={poseIndex}
                initial={{ y: 10, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                className="text-center mb-8"
              >
                <div className="inline-flex items-center gap-2 bg-[var(--primary)]/10 text-[var(--primary)] px-3 py-1 rounded-full text-xs font-semibold mb-3 border border-[var(--primary)]/20">
                  <Scan className="w-3 h-3" />
                  Capture {poseIndex + 1} of {POSES.length}
                </div>
                <h2 className="text-2xl font-bold text-white tracking-tight">{POSES[poseIndex]}</h2>
              </motion.div>

              <button 
                onClick={capturePose}
                disabled={isCapturing || capturedImages.length >= POSES.length}
                className={`w-20 h-20 rounded-full flex items-center justify-center transition-all ${
                  isCapturing 
                  ? 'bg-[var(--surface-solid)] border-2 border-[var(--primary)] opacity-50 cursor-not-allowed'
                  : 'bg-white border-4 border-[var(--primary)]/30 hover:scale-95 shadow-[0_0_30px_var(--primary-glow)]'
                }`}
              >
                {isCapturing ? (
                  <div className="w-8 h-8 border-3 border-[var(--primary)] border-t-transparent rounded-full animate-spin"></div>
                ) : (
                  <Camera className="w-8 h-8 text-[var(--background)]" />
                )}
              </button>
            </motion.div>
          )}

          {/* STEP 4: Success */}
          {currentStep === 4 && (
            <motion.div
              key="step4"
              custom={1}
              variants={slideVariants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
              className="flex flex-col flex-1 items-center justify-center text-center py-10"
            >
              <div className="relative mb-8">
                <div className="w-32 h-32 rounded-full glass-panel flex items-center justify-center shadow-[0_0_50px_var(--success-glow)]">
                  <CheckCircle2 className="w-16 h-16 text-[var(--success)]" />
                </div>
                <div className="absolute inset-0 rounded-full border-2 border-[var(--success)] animate-pulse-ring"></div>
              </div>
              
              <h2 className="text-3xl font-bold text-white mb-3 tracking-tight">Enrollment Secure</h2>
              <p className="text-[var(--text-secondary)] mb-10 max-w-[250px] leading-relaxed">
                <span className="text-white font-medium">{formData.name}</span>'s biometric profile has been successfully encrypted and stored.
              </p>
              
              <div className="w-full space-y-4">
                <button 
                  onClick={() => { 
                    setCurrentStep(1); 
                    setPoseIndex(0); 
                    setCapturedImages([]); 
                    setFormData({name: '', student_id: '', roll_number: '', department: '', semester: '', section: ''}); 
                  }}
                  className="w-full premium-btn p-4 rounded-2xl font-semibold text-base text-white"
                >
                  Enroll Another Student
                </button>
                <button 
                  onClick={() => navigate('/attendance')}
                  className="w-full premium-btn-primary p-4 rounded-2xl font-bold text-base flex items-center justify-center gap-2"
                >
                  Verify Identity <ShieldCheck className="w-5 h-5" />
                </button>
              </div>
            </motion.div>
          )}

        </AnimatePresence>
      </div>
    </div>
  );
}
