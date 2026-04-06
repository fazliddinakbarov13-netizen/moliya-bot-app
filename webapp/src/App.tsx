import { useState, useEffect } from 'react';
import { motion, AnimatePresence, animate } from 'framer-motion';
import { 
  Home, BarChart3, Settings, 
  Plus,
  ShoppingCart, Briefcase, Coffee
} from 'lucide-react';
import { DashboardWidgets } from './DashboardWidgets';
import { WidgetContent } from './WidgetScreens';

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

  return <span>{Math.round(displayValue).toLocaleString('ru-RU')}</span>;
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
  const [balance, setBalance] = useState(12450000);
  const [triggerShake, setTriggerShake] = useState(false);
  const [toastMsg, setToastMsg] = useState<{msg: string, type: string} | null>(null);
  
  // Modal states
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [activeWidget, setActiveWidget] = useState<string | null>(null);

  // Load Telegram User Info
  const tgUser = (window as any).Telegram?.WebApp?.initDataUnsafe?.user;
  const tgUserId = tgUser?.id || null;
  const userName = tgUser?.first_name || "Jasur";
  const userInitial = userName.charAt(0).toUpperCase();

  useEffect(() => {
    if (tgUserId) {
      fetch(`http://127.0.0.1:8000/api/user?tg_id=${tgUserId}`)
        .then(r => r.json())
        .then(data => {
          if (data.status === 'ok') {
            setBalance(data.balance);
          }
        })
        .catch(err => console.error("API error:", err));
    }
    
    if ((window as any).Telegram?.WebApp) {
      (window as any).Telegram.WebApp.ready();
      (window as any).Telegram.WebApp.expand();
      (window as any).Telegram.WebApp.setHeaderColor('#e6eef6');
    }
  }, [tgUserId]);

  const handleTransaction = async (isExpense: boolean) => {
    if (!inputValue || isNaN(Number(inputValue)) || Number(inputValue) <= 0) return;
    const amount = Number(inputValue);
    
    if (!tgUserId) {
      if (isExpense && balance < amount) {
        setToastMsg({ msg: "Mablag' yetarli emas!", type: 'error' });
        setTriggerShake(true);
        setTimeout(() => setTriggerShake(false), 500);
        return;
      }
      setBalance(prev => isExpense ? prev - amount : prev + amount);
      setToastMsg({ msg: "Muaffaqiyatli! (" + (isExpense ? "-" : "+") + amount + ")", type: 'success' });
      setInputValue('');
      setIsAddModalOpen(false);
      return;
    }

    try {
      const res = await fetch('http://127.0.0.1:8000/api/transaction', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tg_id: tgUserId, amount: amount, is_expense: isExpense })
      });
      const data = await res.json();
      
      if (!res.ok || data.error) {
        setToastMsg({ msg: data.error || "Xatolik yuz berdi", type: "error" });
        setTriggerShake(true);
        setTimeout(() => setTriggerShake(false), 500);
      } else if (data.success) {
        setBalance(data.new_balance);
        setToastMsg({ msg: "Haqiqiy Tranzaksiya tushdi!", type: "success" });
        setInputValue('');
        setIsAddModalOpen(false);
      } else {
        setToastMsg({ msg: "Mablag' yetarli emas!", type: "error" });
        setTriggerShake(true);
        setTimeout(() => setTriggerShake(false), 500);
      }
    } catch (err) {
      console.error(err);
      setToastMsg({ msg: "Server uzoqda! Lokal saqlandi (" + (isExpense ? "-" : "+") + amount + ")", type: "error" });
      setBalance(prev => isExpense ? prev - amount : prev + amount);
      setInputValue('');
      setIsAddModalOpen(false);
    }
  };

  const shakeVariants = {
    shake: { x: [0, -10, 10, -10, 10, 0], transition: { duration: 0.4 } },
    normal: { x: 0 }
  };

  return (
    <div className="min-h-[100dvh] pb-24 transition-colors duration-300 relative bg-[var(--bg-color)] font-sans max-w-md mx-auto shadow-2xl overflow-hidden border-x border-[var(--bg-color)] dark:border-gray-800">
      <AnimatePresence>
        {toastMsg && (
          <ToastNotification message={toastMsg.msg} type={toastMsg.type} onClose={() => setToastMsg(null)} />
        )}
      </AnimatePresence>

      <div className="p-6">
        {/* Header */}
        <header className="flex justify-between items-center mb-6">
          <div>
            <p className="text-sm opacity-60 mb-1">Xayrli kun,</p>
            <h1 className="text-2xl font-bold">{userName} 👋</h1>
          </div>
          <div className="neo-elem rounded-full w-12 h-12 flex items-center justify-center text-xl font-bold bg-[#14b8a6] text-white">
            {userInitial}
          </div>
        </header>

        {/* Main Balance Card */}
        <motion.div 
          className="neo-elem p-6 mb-6 rounded-3xl flex flex-col items-center justify-center text-center"
          variants={shakeVariants}
          animate={triggerShake ? "shake" : "normal"}
        >
          <p className="text-sm opacity-60 font-medium mb-2">Umumiy balans</p>
          <div className="text-3xl font-extrabold tracking-tight mb-2 text-[var(--text-color)]">
            <SmoothCounter value={balance} /> so'm
          </div>
          <p className="text-sm text-green-500 font-semibold bg-green-500/10 px-3 py-1 rounded-full">
            ↑ +3.2% bu oy
          </p>
        </motion.div>

        {/* Income / Expense Summary */}
        <div className="flex gap-4 mb-6">
          <div className="neo-elem flex-1 p-4 rounded-2xl">
            <p className="text-xs opacity-60 mb-1 font-medium">Daromad</p>
            <p className="text-green-500 font-bold text-lg">+4 200 000</p>
          </div>
          <div className="neo-elem flex-1 p-4 rounded-2xl">
            <p className="text-xs opacity-60 mb-1 font-medium">Xarajat</p>
            <p className="text-red-500 font-bold text-lg">-1 750 000</p>
          </div>
        </div>

        {/* Qo'shish tugmasi */}
        <div className="flex mb-6">
          <button 
            onClick={() => setIsAddModalOpen(true)}
            className="neo-elem w-full py-4 rounded-2xl flex items-center justify-center gap-3 hover:shadow-lg transition-all"
          >
            <Plus className="text-indigo-500" size={22} />
            <span className="font-bold opacity-80">Tranzaksiya qo'shish</span>
          </button>
        </div>

        {/* Menyu va Vidjetlar */}
        <DashboardWidgets onWidgetClick={(_, name) => setActiveWidget(name)} />

        {/* Monthly Chart Placeholder */}
        <div className="mb-8">
          <h2 className="text-lg font-bold mb-4 opacity-90">Oylik xarajatlar</h2>
          <div className="neo-inset rounded-3xl p-4 h-32 flex items-end justify-between gap-2">
            {[30, 45, 25, 60, 40, 85].map((h, i) => (
              <div key={i} className="flex flex-col items-center flex-1 gap-2">
                <div 
                  className={`w-full rounded-t-lg transition-all duration-500 ${i === 5 ? 'bg-green-500' : 'bg-gray-300 dark:bg-gray-600'}`} 
                  style={{ height: `${h}%` }}
                ></div>
                <span className={`text-[10px] font-bold ${i === 5 ? 'text-green-500' : 'opacity-50'}`}>
                  {['Yan', 'Fev', 'Mar', 'Apr', 'May', 'Iyu'][i]}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Transactions */}
        <div>
          <h2 className="text-lg font-bold mb-4 opacity-90">So'nggi tranzaksiyalar</h2>
          <div className="flex flex-col gap-4">
            <div className="neo-elem rounded-2xl p-4 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 neo-inset rounded-full flex items-center justify-center text-green-600 bg-green-500/10">
                  <ShoppingCart size={20} />
                </div>
                <div>
                  <h3 className="font-bold">Korzinka</h3>
                  <p className="text-xs opacity-50">Bugun, 14:32</p>
                </div>
              </div>
              <span className="font-bold text-red-500">-85 000</span>
            </div>
            <div className="neo-elem rounded-2xl p-4 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 neo-inset rounded-full flex items-center justify-center text-blue-600 bg-blue-500/10">
                  <Briefcase size={20} />
                </div>
                <div>
                  <h3 className="font-bold">Maosh</h3>
                  <p className="text-xs opacity-50">Kecha, 09:00</p>
                </div>
              </div>
              <span className="font-bold text-green-500">+4 200 000</span>
            </div>
            <div className="neo-elem rounded-2xl p-4 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 neo-inset rounded-full flex items-center justify-center text-orange-600 bg-orange-500/10">
                  <Coffee size={20} />
                </div>
                <div>
                  <h3 className="font-bold">Starbucks</h3>
                  <p className="text-xs opacity-50">3 kun oldin</p>
                </div>
              </div>
              <span className="font-bold text-red-500">-35 000</span>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Navigation */}
      <div className="fixed bottom-6 left-1/2 -translate-x-1/2 w-[90%] max-w-[400px] neo-elem rounded-full p-2 flex justify-between items-center z-30">
        <button onClick={() => setActiveWidget(null)} className="flex-1 py-3 flex justify-center text-green-500 neo-pressed rounded-full"><Home size={22} /></button>
        <button onClick={() => setActiveWidget("Statistika")} className="flex-1 py-3 flex justify-center opacity-50 hover:opacity-100 active:scale-90 transition-all"><BarChart3 size={22} /></button>
        <button onClick={() => setActiveWidget("Sozlamalar")} className="flex-1 py-3 flex justify-center opacity-50 hover:opacity-100 active:scale-90 transition-all"><Settings size={22} /></button>
      </div>

      {/* Add Transaction Modal */}
      <AnimatePresence>
        {isAddModalOpen && (
          <motion.div 
            initial={{ opacity: 0, y: 300 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 300 }}
            className="fixed inset-x-0 bottom-0 mx-auto max-w-md z-50 p-6 flex flex-col bg-[var(--bg-color)] rounded-t-3xl shadow-2xl"
            style={{ boxShadow: "0 -10px 40px rgba(0,0,0,0.15)" }}
          >
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold">Tranzaksiya qo'shish</h2>
              <button 
                onClick={() => setIsAddModalOpen(false)}
                className="neo-elem w-10 h-10 flex items-center justify-center rounded-full font-bold opacity-70"
              >✕</button>
            </div>
            
            <input 
              type="number" 
              placeholder="0 UZS"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              className="neo-pressed w-full font-bold p-4 text-2xl text-center mb-6 bg-transparent rounded-2xl"
              autoFocus
            />
            
            <div className="flex gap-4">
              <button 
                onClick={() => handleTransaction(false)}
                className="flex-1 neo-elem py-4 rounded-2xl text-green-500 font-bold text-lg active:scale-95 transition-transform"
              >+ Daromad</button>
              <button 
                onClick={() => handleTransaction(true)}
                className="flex-1 neo-elem py-4 rounded-2xl text-red-500 font-bold text-lg active:scale-95 transition-transform"
              >- Xarajat</button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Widget Detailed Modal */}
      <AnimatePresence>
        {activeWidget && (
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="fixed inset-0 mx-auto max-w-md z-50 flex flex-col bg-[var(--bg-color)] shadow-2xl overflow-hidden"
          >
            <div className="flex justify-between items-center p-6 pb-4">
              <h2 className="text-2xl font-bold">{activeWidget}</h2>
              <button 
                onClick={() => setActiveWidget(null)}
                className="neo-elem w-10 h-10 flex items-center justify-center rounded-full font-bold opacity-70"
              >✕</button>
            </div>
            <div className="flex-1 overflow-y-auto p-6 pt-2">
              <WidgetContent widgetName={activeWidget} />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

    </div>
  );
}

export default App;
