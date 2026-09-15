import { Routes, Route } from 'react-router-dom';
import Splash from './pages/Splash';
import Home from './pages/Home';
import Registration from './pages/Registration';
import Attendance from './pages/Attendance';

function App() {
  return (
    <div className="min-h-screen bg-[var(--background)] text-[var(--text-primary)] relative overflow-hidden">
      {/* Premium Animated Background Gradients */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-[var(--primary-dark)] rounded-full mix-blend-screen filter blur-[120px] opacity-20 animate-pulse-slow"></div>
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-[var(--secondary)] rounded-full mix-blend-screen filter blur-[120px] opacity-15 animate-pulse-slow" style={{ animationDelay: '3s' }}></div>
      <div className="absolute top-[40%] left-[60%] w-[30%] h-[30%] bg-[var(--accent)] rounded-full mix-blend-screen filter blur-[100px] opacity-5 animate-pulse-slow" style={{ animationDelay: '1s' }}></div>
      
      {/* Subtle Noise Texture (Premium Feel) */}
      <div className="absolute inset-0 opacity-[0.015] pointer-events-none mix-blend-overlay" style={{ backgroundImage: "url('data:image/svg+xml,%3Csvg viewBox=%220 0 200 200%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noiseFilter%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.65%22 numOctaves=%223%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noiseFilter)%22/%3E%3C/svg%3E')" }}></div>

      <div className="relative z-10 min-h-screen">
        <Routes>
          <Route path="/" element={<Splash />} />
          <Route path="/home" element={<Home />} />
          <Route path="/register" element={<Registration />} />
          <Route path="/attendance" element={<Attendance />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;
