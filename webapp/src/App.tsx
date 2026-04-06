import { useState, useEffect } from 'react';
import { motion, AnimatePresence, animate } from 'framer-motion';
import { 
  Home, BarChart3, Settings, 
  Plus
} from 'lucide-react';
import { DashboardWidgets } from './DashboardWidgets';
import { WidgetContent } from './WidgetScreens';

// --- Determine API base URL ---
function getApiBase(): string {
  // If inside Telegram WebApp, try to use the bot's server
  const tg = (window as any).Telegram?.WebApp;
  if (tg) {
    // Same origin for Railway deployment
    const origin = window.location.origin;
    if (origin.includes('github.io')) {
      // GitHub Pages can't reach API - use empty string to show static fallback
      return '';
    }
    return origin;
  }
  // Local development
  return 'http://127.0.0.1:8000';
}

// --- Format money helper ---
function formatMoney(amount: number): string {
  return Math.abs(amount).toLocaleString('ru-RU').replace(/,/g, ' ');
}

// --- Custom Smooth Counter ---
function SmoothCounter({ value }: { value: number }) {
  const [display, setDisplay] = useState(value);
  
  useEffect(() => {
    const control = animate(display, value, {
      duration: 0.5,
      onUpdate: (v) => setDisplay(Math.round(v)),
    });
    return () => control.stop();
  }, [value]);
  
  return <>{formatMoney(display)}</>;
}

// --- Toast Notification ---
function ToastNotification({ message, type, onClose }: { message: string; type: string; onClose: () => void }) {
  useEffect(() => { const t = setTimeout(onClose, 3000); return () => clearTimeout(t); }, [onClose]);
  return (
    <motion.div
      initial={{ opacity: 0, y: -30 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -30 }}
      className={`fixed top-4 left-1/2 -translate-x-1/2 max-w-[340px] w-[90%] z-50 p-4 rounded-2xl text-white font-bold text-center shadow-xl ${type === 'error' ? 'bg-red-500' : 'bg-green-500'}`}
    >{message}</motion.div>
  );
}

// --- Transaction item type ---
interface TransactionItem {
  id: number;
  type: string;
  amount: number;
  description: string;
  category_name: string;
  category_icon: string;
  date: string;
  created_at: string;
}

function App() {
  const [balance, setBalance] = useState(0);
  const [monthlyIncome, setMonthlyIncome] = useState(0);
  const [monthlyExpense, setMonthlyExpense] = useState(0);
  const [transactions, setTransactions] = useState<TransactionItem[]>([]);
  const [triggerShake, setTriggerShake] = useState(false);
  const [toastMsg, setToastMsg] = useState<{msg: string, type: string} | null>(null);
  const [dataLoaded, setDataLoaded] = useState(false);
  
  // Modal states
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [activeWidget, setActiveWidget] = useState<string | null>(null);

  // Load Telegram User Info — fallback to URL param for testing
  const tgUser = (window as any).Telegram?.WebApp?.initDataUnsafe?.user;
  const urlParams = new URLSearchParams(window.location.search);
  const tgUserId = tgUser?.id || urlParams.get('tg_id') || null;
  const userName = tgUser?.first_name || "Foydalanuvchi";
  const userInitial = userName.charAt(0).toUpperCase();

  const API_BASE = getApiBase();

  // Fetch all data from backend
  const fetchAllData = async () => {
    if (!tgUserId || !API_BASE) return;
    try {
      const [userRes, txRes, statsRes] = await Promise.all([
        fetch(`${API_BASE}/api/user?tg_id=${tgUserId}`).then(r => r.json()),
        fetch(`${API_BASE}/api/transactions?tg_id=${tgUserId}`).then(r => r.json()),
        fetch(`${API_BASE}/api/stats?tg_id=${tgUserId}`).then(r => r.json()),
      ]);

      if (userRes.status === 'ok') setBalance(userRes.balance);
      if (txRes.transactions) setTransactions(txRes.transactions);
      if (statsRes) {
        setMonthlyIncome(statsRes.income || 0);
        setMonthlyExpense(statsRes.expense || 0);
      }
      setDataLoaded(true);
    } catch (err) {
      console.error("API sync error:", err);
    }
  };

  useEffect(() => {
    fetchAllData();
    
    if ((window as any).Telegram?.WebApp) {
      (window as any).Telegram.WebApp.ready();
      (window as any).Telegram.WebApp.expand();
      (window as any).Telegram.WebApp.setHeaderColor('#e6eef6');
    }

    // Auto-refresh every 5 seconds to sync with bot
    const interval = setInterval(fetchAllData, 5000);
    return () => clearInterval(interval);
  }, [tgUserId]);

  const handleTransaction = async (isExpense: boolean) => {
    if (!inputValue || isNaN(Number(inputValue)) || Number(inputValue) <= 0) return;
    const amount = Number(inputValue);
    
    if (!tgUserId || !API_BASE) {
      if (isExpense && balance < amount) {
        setToastMsg({ msg: "Mablag' yetarli emas!", type: 'error' });
        setTriggerShake(true);
        setTimeout(() => setTriggerShake(false), 500);
        return;
      }
      setBalance(prev => isExpense ? prev - amount : prev + amount);
      setToastMsg({ msg: "Saqlandi! (" + (isExpense ? "-" : "+") + formatMoney(amount) + ")", type: 'success' });
      setInputValue('');
      setIsAddModalOpen(false);
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/api/transaction`, {
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
        setToastMsg({ msg: "✅ Tranzaksiya saqlandi!", type: "success" });
        setInputValue('');
        setIsAddModalOpen(false);
        // Re-fetch all data to sync
        await fetchAllData();
      } else {
        setToastMsg({ msg: "Mablag' yetarli emas!", type: "error" });
        setTriggerShake(true);
        setTimeout(() => setTriggerShake(false), 500);
      }
    } catch (err) {
      console.error(err);
      setToastMsg({ msg: "Server bilan aloqa yo'q!", type: "error" });
    }
  };

  // Calculate percentage change
  const netChange = monthlyIncome - monthlyExpense;
  const changePercent = monthlyIncome > 0 ? ((netChange / monthlyIncome) * 100).toFixed(1) : "0";

  // Format relative date
  const formatDate = (dateStr: string): string => {
    const txDate = new Date(dateStr);
    const today = new Date();
    const diff = Math.floor((today.getTime() - txDate.getTime()) / (1000 * 60 * 60 * 24));
    if (diff === 0) return "Bugun";
    if (diff === 1) return "Kecha";
    if (diff < 7) return `${diff} kun oldin`;
    return txDate.toLocaleDateString('uz-UZ');
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
          {dataLoaded && (
            <p className={`text-sm font-semibold px-3 py-1 rounded-full ${
              netChange >= 0 ? 'text-green-500 bg-green-500/10' : 'text-red-500 bg-red-500/10'
            }`}>
              {netChange >= 0 ? '↑' : '↓'} {netChange >= 0 ? '+' : ''}{changePercent}% bu oy
            </p>
          )}
        </motion.div>

        {/* Income / Expense Summary — REAL DATA */}
        <div className="flex gap-4 mb-6">
          <div className="neo-elem flex-1 p-4 rounded-2xl">
            <p className="text-xs opacity-60 mb-1 font-medium">Daromad</p>
            <p className="text-green-500 font-bold text-lg">+{formatMoney(monthlyIncome)}</p>
          </div>
          <div className="neo-elem flex-1 p-4 rounded-2xl">
            <p className="text-xs opacity-60 mb-1 font-medium">Xarajat</p>
            <p className="text-red-500 font-bold text-lg">-{formatMoney(monthlyExpense)}</p>
          </div>
        </div>

        {/* Qo'shish tugmasi */}
        <div className="flex mb-6">
          <button 
            onClick={() => setIsAddModalOpen(true)}
            className="neo-elem w-full py-4 rounded-2xl flex items-center justify-center gap-3 hover:shadow-lg transition-all"
          >
            <Plus className="text-green-500" size={22} />
            <span className="font-bold opacity-80">Tranzaksiya qo'shish</span>
          </button>
        </div>

        {/* Menyu va Vidjetlar */}
        <DashboardWidgets onWidgetClick={(_, name) => setActiveWidget(name)} />

        {/* Recent Transactions — REAL DATA FROM DATABASE */}
        <div className="mt-6">
          <h2 className="text-lg font-bold mb-4 opacity-90">So'nggi tranzaksiyalar</h2>
          <div className="flex flex-col gap-3">
            {transactions.length === 0 && dataLoaded && (
              <div className="neo-inset rounded-2xl p-6 text-center opacity-50">
                <p>Hali tranzaksiya yo'q</p>
                <p className="text-xs mt-1">Botga "taksiga 15000 ketdi" deb yozing!</p>
              </div>
            )}
            {transactions.length === 0 && !dataLoaded && !API_BASE && (
              <div className="neo-inset rounded-2xl p-6 text-center opacity-50">
                <p>Bot bilan sinxronlash uchun</p>
                <p className="text-xs mt-1">Telegram orqali oching</p>
              </div>
            )}
            {transactions.map((tx) => (
              <div key={tx.id} className="neo-elem rounded-2xl p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-11 h-11 neo-inset rounded-full flex items-center justify-center text-lg ${
                    tx.type === 'income' ? 'bg-green-500/10' : 'bg-red-500/5'
                  }`}>
                    {tx.category_icon}
                  </div>
                  <div>
                    <h3 className="font-bold text-sm">{tx.description || tx.category_name}</h3>
                    <p className="text-xs opacity-50">{formatDate(tx.date)}</p>
                  </div>
                </div>
                <span className={`font-bold text-sm ${tx.type === 'income' ? 'text-green-500' : 'text-red-500'}`}>
                  {tx.type === 'income' ? '+' : '-'}{formatMoney(tx.amount)}
                </span>
              </div>
            ))}
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
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 bg-black/30 flex items-end justify-center"
            onClick={() => setIsAddModalOpen(false)}
          >
            <motion.div 
              initial={{ y: 300 }} animate={{ y: 0 }} exit={{ y: 300 }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
              className="bg-[var(--bg-color)] w-full max-w-md rounded-t-3xl p-8 shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="w-10 h-1 bg-gray-300 rounded-full mx-auto mb-6" />
              <h2 className="text-xl font-bold mb-6 text-center">Tranzaksiya qo'shish</h2>

              <div className="neo-inset rounded-2xl p-4 mb-6">
                <input 
                  type="number"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="Summani kiriting..."
                  className="w-full bg-transparent text-center text-2xl font-bold outline-none"
                  autoFocus
                />
              </div>

              <div className="flex gap-4">
                <button 
                  onClick={() => handleTransaction(true)}
                  className="flex-1 bg-red-500 text-white py-4 rounded-2xl font-bold text-lg shadow-lg hover:bg-red-600 active:scale-95 transition-all"
                >
                  − Xarajat
                </button>
                <button 
                  onClick={() => handleTransaction(false)}
                  className="flex-1 bg-green-500 text-white py-4 rounded-2xl font-bold text-lg shadow-lg hover:bg-green-600 active:scale-95 transition-all"
                >
                  + Daromad
                </button>
              </div>
            </motion.div>
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
