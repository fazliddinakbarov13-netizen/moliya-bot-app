import { useState, useEffect } from 'react';
import { motion, AnimatePresence, animate } from 'framer-motion';
import { Moon, Sun, Wallet, TrendingUp, TrendingDown } from 'lucide-react';
import { DashboardWidgets } from './DashboardWidgets';

// --- Custom Smooth Counter ---
function SmoothCounter({ value }: { value: number }) {
  const [displayValue, setDisplayValue] = useState(value);
  
  useEffect(() => {
    const controls = animate(displayValue, value, {
      duration: 0.8,
      ease: "easeOut",
      onUpdate(cur) {
        setDisplayValue(cur);
      }
    });
    return () => controls.stop();
  }, [value]);

  return <span>{Math.round(displayValue).toLocaleString()}</span>;
}

// --- Custom Toast Component ---
function ToastNotification({ message, type, onClose }: any) {
  useEffect(() => {
    const timer = setTimeout(onClose, 3000);
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <motion.div 
      initial={{ opacity: 0, y: -50, scale: 0.8 }}
      animate={{ opacity: 1, y: 20, scale: 1 }}
      exit={{ opacity: 0, y: -20, scale: 0.8 }}
      className={`fixed top-4 left-1/2 -translate-x-1/2 px-6 py-3 rounded-2xl shadow-xl font-bold z-50 flex items-center gap-3 ${
        type === 'error' ? 'bg-red-500 text-white' : 'bg-green-500 text-white'
      }`}
    >
      {message}
    </motion.div>
  );
}

function App() {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    return localStorage.getItem('theme') === 'dark' || 
           window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  const [balance, setBalance] = useState(1200000);
  const [triggerShake, setTriggerShake] = useState(false);
  const [toastMsg, setToastMsg] = useState<{msg: string, type: string} | null>(null);

  // Load Telegram User Info
  const tgUser = (window as any).Telegram?.WebApp?.initDataUnsafe?.user;
  const userName = tgUser?.first_name || "John Doe";
  const userInitial = userName.charAt(0).toUpperCase();

  const toggleTheme = () => setIsDarkMode(prev => !prev);

  useEffect(() => {
    if ((window as any).Telegram?.WebApp) {
      (window as any).Telegram.WebApp.ready();
      (window as any).Telegram.WebApp.expand();
      if (isDarkMode) {
        (window as any).Telegram.WebApp.setHeaderColor('#1e1e2e');
      } else {
        (window as any).Telegram.WebApp.setHeaderColor('#e6eef6');
      }
    }
  }, [isDarkMode]);

  const handleDeposit = () => {
    setBalance(prev => prev + 50000);
    setToastMsg({ msg: "Muaffaqiyatli to'ldirildi! (+50 000)", type: 'success' });
  };

  const handleWithdraw = () => {
    if (balance < 50000) {
      setTriggerShake(true);
      setTimeout(() => setTriggerShake(false), 500); // reset
      setToastMsg({ msg: "Mablag' yetarli emas!", type: 'error' });
      return;
    }
    setBalance(prev => prev - 50000);
  };

  // Framer motion variants for shake error
  const shakeVariants = {
    shake: {
      x: [0, -10, 10, -10, 10, 0],
      transition: { duration: 0.4 }
    },
    normal: { x: 0 }
  };

  return (
    <AnimatePresence>
      <motion.div 
        className="min-h-screen p-6 transition-colors duration-300 relative"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.3 }}
      >
        <AnimatePresence>
          {toastMsg && (
            <ToastNotification 
              message={toastMsg.msg} 
              type={toastMsg.type} 
              onClose={() => setToastMsg(null)} 
            />
          )}
        </AnimatePresence>

        {/* Header & Theme Toggle */}
        <header className="flex justify-between items-center mb-8">
          <div className="flex items-center gap-3">
            {/* Avatar Placeholder */}
            <div className="neo-elem rounded-full w-12 h-12 flex items-center justify-center overflow-hidden">
              <span className="text-xl font-bold">{userInitial}</span>
            </div>
            <div>
              <h1 className="text-xl font-bold">{userName}</h1>
              <p className="text-sm opacity-70">Premium User</p>
            </div>
          </div>

          <motion.button 
            whileTap={{ scale: 0.9, boxShadow: "var(--shadow-inset-neo)" }}
            onClick={toggleTheme}
            className="neo-elem w-12 h-12 flex items-center justify-center rounded-full aria-label='Toggle theme'"
            aria-label="Toggle Dark Mode"
          >
            {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
          </motion.button>
        </header>

        {/* Main Balance Card (Neo Card) */}
        <motion.div 
          className="neo-card p-6 mb-8 flex flex-col items-center justify-center"
          variants={shakeVariants}
          animate={triggerShake ? "shake" : "normal"}
        >
          <p className="text-lg opacity-70 mb-2 font-medium">Umumiy balans</p>
          <div className="text-4xl font-extrabold tracking-tight mb-6">
            <SmoothCounter value={balance} /> UZS
          </div>

          {/* Action Buttons */}
          <div className="w-full flex justify-between gap-4">
            <motion.button 
              className="neo-elem flex-1 flex flex-col items-center justify-center py-4 gap-2 text-green-500"
              whileTap={{ scale: 0.95, boxShadow: "var(--shadow-inset-neo)" }}
              onClick={handleDeposit}
            >
              <TrendingUp size={24} />
              <span className="font-semibold text-sm">Daromad</span>
            </motion.button>
            <motion.button 
              className="neo-elem flex-1 flex flex-col items-center justify-center py-4 gap-2 text-red-500"
              whileTap={{ scale: 0.95, boxShadow: "var(--shadow-inset-neo)" }}
              onClick={handleWithdraw}
            >
              <TrendingDown size={24} />
              <span className="font-semibold text-sm">Xarajat</span>
            </motion.button>
            <motion.button 
              className="neo-elem flex-1 flex flex-col items-center justify-center py-4 gap-2 opacity-80"
              whileTap={{ scale: 0.95, boxShadow: "var(--shadow-inset-neo)" }}
            >
              <Wallet size={24} />
              <span className="font-semibold text-sm">Hisoblar</span>
            </motion.button>
          </div>
        </motion.div>

        {/* Example Input Field for Form */}
        <div className="mb-6">
          <h2 className="text-lg font-bold mb-3">Tezkor o'tkazma</h2>
          <input 
            type="text" 
            placeholder="Summa yoki to'lov maqsadi..."
            className="neo-pressed w-full p-4 text-lg"
            aria-label="Tezkor summa kiriting"
          />
        </div>

        <DashboardWidgets />

      </motion.div>
    </AnimatePresence>
  );
}

export default App;
