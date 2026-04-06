import { useState } from 'react';
import { 
  PieChart, TrendingUp, TrendingDown, Calendar,
  CreditCard, Banknote,
  ChevronRight, Bell, Globe, Shield, Palette,
  Plus
} from 'lucide-react';

// ═══════════════════════════════════════════════════════
// 1. STATISTIKA
// ═══════════════════════════════════════════════════════
export function StatistikaScreen({ stats }: { stats?: any }) {
  const income = stats?.income || 0;
  const expense = Math.abs(stats?.expense || 0);
  const diff = income - expense;
  
  // Format categories from API
  const categories = stats?.categories || [];
  const topCategories = categories.slice(0, 5).map((c: any) => ({
    name: c.name,
    amount: c.total,
    percent: expense > 0 ? Math.round((c.total / expense) * 100) : 0,
    color: "#" + Math.floor(Math.random()*16777215).toString(16).padStart(6, '0') // random hex color for now
  }));

  const formatM = (num: number) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + "M";
    if (num >= 1000) return (num / 1000).toFixed(1) + "K";
    return num;
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Summary Cards */}
      <div className="flex gap-4">
        <div className="neo-elem flex-1 p-4 rounded-2xl text-center">
          <TrendingUp className="mx-auto mb-2 text-green-500" size={24} />
          <p className="text-xs opacity-60">Daromad</p>
          <p className="font-bold text-green-500">+{formatM(income)}</p>
        </div>
        <div className="neo-elem flex-1 p-4 rounded-2xl text-center">
          <TrendingDown className="mx-auto mb-2 text-red-500" size={24} />
          <p className="text-xs opacity-60">Xarajat</p>
          <p className="font-bold text-red-500">-{formatM(expense)}</p>
        </div>
        <div className="neo-elem flex-1 p-4 rounded-2xl text-center">
          <PieChart className="mx-auto mb-2 text-blue-500" size={24} />
          <p className="text-xs opacity-60">Qoldiq</p>
          <p className="font-bold text-blue-500">{formatM(diff)}</p>
        </div>
      </div>

      {/* Category Breakdown */}
      <div>
        <h3 className="font-bold mb-4 opacity-80">Toifalar bo'yicha xarajat</h3>
        <div className="flex flex-col gap-3">
          {topCategories.length === 0 && <p className="text-sm opacity-50 text-center">Ma'lumot yo'q</p>}
          {topCategories.map((cat: any, i: number) => (
            <div key={i} className="neo-elem rounded-2xl p-4">
              <div className="flex justify-between items-center mb-2">
                <span className="font-bold text-sm">{cat.name}</span>
                <span className="font-bold text-sm">{formatM(cat.amount)}</span>
              </div>
              <div className="w-full h-2 rounded-full bg-[var(--bg-color)] neo-inset overflow-hidden shadow-inner flex mb-1">
                <div 
                  className="h-full rounded-full transition-all duration-700 opacity-80 shadow-md"
                  style={{ width: `${cat.percent}%`, backgroundColor: cat.color }}
                />
              </div>
              <p className="text-xs opacity-50 mt-1 text-right">{cat.percent}%</p>
            </div>
          ))}
        </div>
      </div>

      {/* Monthly Chart */}
      <div>
        <h3 className="font-bold mb-4 opacity-80">6 oylik tendentsiya</h3>
        <div className="neo-inset rounded-3xl p-4 h-36 flex items-end justify-between gap-2">
          {[
            { h: 30, label: "Yan" },
            { h: 45, label: "Fev" },
            { h: 25, label: "Mar" },
            { h: 60, label: "Apr" },
            { h: 40, label: "May" },
            { h: 85, label: "Iyu" },
          ].map((bar, i) => (
            <div key={i} className="flex flex-col items-center flex-1 gap-2">
              <div 
                className={`w-full rounded-t-lg transition-all duration-500 ${i === 5 ? 'bg-green-500' : 'bg-gray-300'}`} 
                style={{ height: `${bar.h}%` }}
              />
              <span className={`text-[10px] font-bold ${i === 5 ? 'text-green-500' : 'opacity-50'}`}>
                {bar.label}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════
// 2. HISOBOT
// ═══════════════════════════════════════════════════════
export function HisobotScreen({ stats, transactions }: { stats?: any, transactions?: any[] }) {
  const [selectedMonth, setSelectedMonth] = useState("Joriy");
  const months = ["Yan", "Fev", "Mar", "Apr", "May", "Joriy"];

  const income = stats?.income || 0;
  const expense = Math.abs(stats?.expense || 0);
  const diff = income - expense;
  const txCount = transactions?.length || 0;

  // Real transactions from DB
  const recentTx = transactions || [];

  const formatM = (num: number) => {
    return Math.abs(num).toLocaleString('ru-RU').replace(/,/g, ' ');
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Month Selector */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {months.map((m) => (
          <button 
            key={m}
            onClick={() => setSelectedMonth(m)}
            className={`px-4 py-2 rounded-full text-sm font-bold transition-all whitespace-nowrap ${
              selectedMonth === m 
                ? 'bg-green-500 text-white shadow-lg' 
                : 'neo-elem opacity-60'
            }`}
          >
            {m}
          </button>
        ))}
      </div>

      {/* Report Summary */}
      <div className="neo-elem rounded-3xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <Calendar className="text-green-500" size={20} />
          <h3 className="font-bold">{selectedMonth} oyi hisoboti</h3>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="neo-inset rounded-2xl p-4 text-center">
            <p className="text-xs opacity-50 mb-1">Umumiy daromad</p>
            <p className="font-bold text-green-500 text-lg">{formatM(income)}</p>
          </div>
          <div className="neo-inset rounded-2xl p-4 text-center">
            <p className="text-xs opacity-50 mb-1">Umumiy xarajat</p>
            <p className="font-bold text-red-500 text-lg">{formatM(expense)}</p>
          </div>
          <div className="neo-inset rounded-2xl p-4 text-center">
            <p className="text-xs opacity-50 mb-1">Qoldiq</p>
            <p className="font-bold text-blue-500 text-lg">{formatM(diff)}</p>
          </div>
          <div className="neo-inset rounded-2xl p-4 text-center">
            <p className="text-xs opacity-50 mb-1">Tranzaksiyalar</p>
            <p className="font-bold text-lg">{txCount} ta</p>
          </div>
        </div>
      </div>

      {/* Top Expenses */}
      <div>
        <h3 className="font-bold mb-3 opacity-80">So'nggi xarajatlar</h3>
        <div className="flex flex-col gap-3">
          {recentTx.length === 0 && <p className="text-sm opacity-50 text-center">Ma'lumot yo'q</p>}
          {recentTx.filter((t: any) => t.type === 'expense').slice(0, 5).map((item: any, i: number) => (
            <div key={i} className="neo-elem rounded-2xl p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{item.category_icon}</span>
                <span className="font-bold text-sm">{item.description || item.category_name}</span>
              </div>
              <span className="font-bold text-red-500 text-sm">-{formatM(item.amount)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════
// 3. MAQSADLAR
// ═══════════════════════════════════════════════════════
export function MaqsadlarScreen() {
  const goals = [
    { name: "Yangi telefon", target: 5000000, saved: 3200000, icon: "📱", deadline: "Avg 2025" },
    { name: "Oylik zaxira", target: 2000000, saved: 1400000, icon: "💰", deadline: "Har oy" },
    { name: "Ta'til sayohati", target: 15000000, saved: 4500000, icon: "✈️", deadline: "Dek 2025" },
  ];

  return (
    <div className="flex flex-col gap-6">
      {/* Add Goal Button */}
      <button className="neo-elem w-full py-4 rounded-2xl flex items-center justify-center gap-3 text-green-500 font-bold">
        <Plus size={20} />
        Yangi maqsad qo'shish
      </button>

      {/* Goals List */}
      <div className="flex flex-col gap-4">
        {goals.map((goal, i) => {
          const percent = Math.round((goal.saved / goal.target) * 100);
          return (
            <div key={i} className="neo-elem rounded-3xl p-5">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">{goal.icon}</span>
                  <div>
                    <h3 className="font-bold">{goal.name}</h3>
                    <p className="text-xs opacity-50">{goal.deadline}</p>
                  </div>
                </div>
                <span className={`text-sm font-bold px-3 py-1 rounded-full ${
                  percent >= 70 ? 'bg-green-500/10 text-green-500' : 'bg-yellow-500/10 text-yellow-600'
                }`}>
                  {percent}%
                </span>
              </div>
              
              {/* Progress Bar */}
              <div className="w-full h-3 rounded-full bg-gray-200 overflow-hidden mb-2">
                <div 
                  className="h-full rounded-full bg-green-500 transition-all duration-700"
                  style={{ width: `${percent}%` }}
                />
              </div>
              <div className="flex justify-between text-xs opacity-60">
                <span>{(goal.saved / 1000000).toFixed(1)}M yig'ildi</span>
                <span>{(goal.target / 1000000).toFixed(1)}M maqsad</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════
// 4. KREDITLAR
// ═══════════════════════════════════════════════════════
export function KreditlarScreen() {
  const credits = [
    { name: "Xonadon ipotekasi", total: 120000000, remaining: 85000000, monthly: 2500000, dueDate: "15-har oy", status: "active" },
    { name: "Avtomobil krediti", total: 35000000, remaining: 12000000, monthly: 1200000, dueDate: "1-har oy", status: "active" },
  ];

  return (
    <div className="flex flex-col gap-6">
      {/* Total Summary */}
      <div className="neo-elem rounded-3xl p-5 text-center">
        <Banknote className="mx-auto mb-2 text-red-400" size={28} />
        <p className="text-xs opacity-50 mb-1">Umumiy qarz qoldig'i</p>
        <p className="text-2xl font-extrabold text-red-500">97 000 000 so'm</p>
        <p className="text-xs opacity-50 mt-2">Oylik to'lov: 3 700 000 so'm</p>
      </div>

      {/* Credit Cards */}
      {credits.map((credit, i) => {
        const paidPercent = Math.round(((credit.total - credit.remaining) / credit.total) * 100);
        return (
          <div key={i} className="neo-elem rounded-3xl p-5">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold">{credit.name}</h3>
              <span className="text-xs px-3 py-1 rounded-full bg-green-500/10 text-green-600 font-bold">Faol</span>
            </div>
            
            <div className="grid grid-cols-2 gap-3 mb-3">
              <div className="neo-inset rounded-xl p-3">
                <p className="text-[10px] opacity-50">Qoldiq</p>
                <p className="font-bold text-red-500 text-sm">{(credit.remaining / 1000000).toFixed(0)}M</p>
              </div>
              <div className="neo-inset rounded-xl p-3">
                <p className="text-[10px] opacity-50">Oylik</p>
                <p className="font-bold text-sm">{(credit.monthly / 1000000).toFixed(1)}M</p>
              </div>
            </div>

            <div className="w-full h-2 rounded-full bg-gray-200 overflow-hidden mb-1">
              <div className="h-full rounded-full bg-green-500" style={{ width: `${paidPercent}%` }} />
            </div>
            <p className="text-[10px] opacity-50 text-right">{paidPercent}% to'langan</p>
          </div>
        );
      })}
    </div>
  );
}

// ═══════════════════════════════════════════════════════
// 5. QARZLARIM
// ═══════════════════════════════════════════════════════
export function QarzlarimScreen() {
  const debts = [
    { person: "Akmal aka", amount: 500000, type: "owed_to_me", date: "2025-05-20", note: "Uy ta'miri uchun" },
    { person: "Sardor", amount: 1200000, type: "i_owe", date: "2025-06-01", note: "Mashina ijarasi" },
    { person: "Dilshod", amount: 300000, type: "owed_to_me", date: "2025-04-15", note: "Tushlik puli" },
  ];

  const totalOwedToMe = debts.filter(d => d.type === "owed_to_me").reduce((s, d) => s + d.amount, 0);
  const totalIOwe = debts.filter(d => d.type === "i_owe").reduce((s, d) => s + d.amount, 0);

  return (
    <div className="flex flex-col gap-6">
      {/* Summary */}
      <div className="flex gap-4">
        <div className="neo-elem flex-1 p-4 rounded-2xl text-center">
          <p className="text-xs opacity-50 mb-1">Menga qarzdor</p>
          <p className="font-bold text-green-500">{(totalOwedToMe / 1000).toFixed(0)}K</p>
        </div>
        <div className="neo-elem flex-1 p-4 rounded-2xl text-center">
          <p className="text-xs opacity-50 mb-1">Men qarzdorman</p>
          <p className="font-bold text-red-500">{(totalIOwe / 1000).toFixed(0)}K</p>
        </div>
      </div>

      {/* Add Debt */}
      <button className="neo-elem w-full py-4 rounded-2xl flex items-center justify-center gap-3 text-green-500 font-bold">
        <Plus size={20} />
        Yangi qarz yozish
      </button>

      {/* Debt List */}
      <div className="flex flex-col gap-3">
        {debts.map((debt, i) => (
          <div key={i} className="neo-elem rounded-2xl p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm ${
                debt.type === "owed_to_me" ? "bg-green-500" : "bg-red-500"
              }`}>
                {debt.person.charAt(0)}
              </div>
              <div>
                <h3 className="font-bold text-sm">{debt.person}</h3>
                <p className="text-[10px] opacity-50">{debt.note}</p>
              </div>
            </div>
            <div className="text-right">
              <p className={`font-bold text-sm ${debt.type === "owed_to_me" ? "text-green-500" : "text-red-500"}`}>
                {debt.type === "owed_to_me" ? "+" : "-"}{(debt.amount / 1000).toFixed(0)}K
              </p>
              <p className="text-[10px] opacity-40">{debt.date}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════
// 6. KARTALAR
// ═══════════════════════════════════════════════════════
export function KartalarScreen() {
  const cards = [
    { bank: "Uzcard", number: "•••• 4523", balance: 8500000, color: "from-green-500 to-emerald-700", type: "Asosiy" },
    { bank: "Humo", number: "•••• 7891", balance: 3200000, color: "from-blue-500 to-indigo-700", type: "Qo'shimcha" },
  ];

  return (
    <div className="flex flex-col gap-6">
      {/* Bank Cards */}
      {cards.map((card, i) => (
        <div key={i} className={`bg-gradient-to-br ${card.color} rounded-3xl p-6 text-white shadow-lg`}>
          <div className="flex justify-between items-start mb-8">
            <div>
              <p className="text-xs opacity-70">{card.type}</p>
              <h3 className="text-lg font-bold">{card.bank}</h3>
            </div>
            <CreditCard size={28} className="opacity-60" />
          </div>
          <p className="text-lg font-mono tracking-widest mb-4">{card.number}</p>
          <div className="flex justify-between items-end">
            <div>
              <p className="text-[10px] opacity-70">Balans</p>
              <p className="text-xl font-extrabold">{card.balance.toLocaleString('ru-RU')}</p>
            </div>
            <p className="text-xs opacity-60">06/28</p>
          </div>
        </div>
      ))}

      {/* Add Card */}
      <button className="neo-elem w-full py-4 rounded-2xl flex items-center justify-center gap-3 opacity-60 font-bold border-2 border-dashed border-gray-300">
        <Plus size={20} />
        Yangi karta qo'shish
      </button>
    </div>
  );
}

// ═══════════════════════════════════════════════════════
// 7. SOZLAMALAR
// ═══════════════════════════════════════════════════════
export function SozlamalarScreen() {
  const [reminders, setReminders] = useState(true);

  interface SettingsItem {
    icon: React.ComponentType<any>;
    label: string;
    value: string;
    action?: boolean;
    toggle?: boolean;
  }

  const settingsGroups: { title: string; items: SettingsItem[] }[] = [
    {
      title: "Umumiy",
      items: [
        { icon: Globe, label: "Til", value: "O'zbek", action: true },
        { icon: Palette, label: "Valyuta", value: "UZS", action: true },
      ]
    },
    {
      title: "Bildirishnomalar",
      items: [
        { icon: Bell, label: "Eslatmalar", value: reminders ? "Yoqilgan" : "O'chirilgan", toggle: true },
      ]
    },
    {
      title: "Xavfsizlik",
      items: [
        { icon: Shield, label: "PIN kod", value: "O'rnatilgan", action: true },
      ]
    },
  ];

  return (
    <div className="flex flex-col gap-6">
      {settingsGroups.map((group, gi) => (
        <div key={gi}>
          <h3 className="font-bold text-sm opacity-50 mb-3 uppercase tracking-wider">{group.title}</h3>
          <div className="flex flex-col gap-2">
            {group.items.map((item, i) => (
              <div key={i} className="neo-elem rounded-2xl p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <item.icon size={20} className="text-green-500" />
                  <span className="font-bold text-sm">{item.label}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs opacity-50">{item.value}</span>
                  {item.toggle ? (
                    <button 
                      onClick={() => setReminders(!reminders)}
                      className={`w-12 h-7 rounded-full transition-all relative ${reminders ? 'bg-green-500' : 'bg-gray-300'}`}
                    >
                      <div className={`w-5 h-5 bg-white rounded-full absolute top-1 transition-all shadow ${reminders ? 'right-1' : 'left-1'}`} />
                    </button>
                  ) : (
                    <ChevronRight size={16} className="opacity-30" />
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}

      {/* App Info */}
      <div className="text-center opacity-40 text-xs mt-4">
        <p>MoliyaBot v2.0</p>
        <p>© 2025 MoliyaBot Team</p>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════
// MAIN WIDGET RENDERER
// ═══════════════════════════════════════════════════════
export function WidgetContent({ widgetName, stats, transactions }: { widgetName: string, stats?: any, transactions?: any[] }) {
  switch (widgetName) {
    case "Statistika": return <StatistikaScreen stats={stats} />;
    case "Hisobot": return <HisobotScreen stats={stats} transactions={transactions} />;
    case "Maqsadlar": return <MaqsadlarScreen />;
    case "Kreditlar": return <KreditlarScreen />;
    case "Qarzlarim": return <QarzlarimScreen />;
    case "Sozlamalar": return <SozlamalarScreen />;
    default: return <p className="text-center opacity-50">Bu bo'lim tugallanmoqda...</p>;
  }
}
