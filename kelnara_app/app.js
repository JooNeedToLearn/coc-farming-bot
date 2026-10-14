/**
 * Kelnara Bot CoC — Frontend Application Engine
 * Platform: Android (PWA/Browser) & PC
 */

// Inisialisasi Data Default
const DEFAULT_STATE = {
  account: {
    name: "HAHAHAA BURUH PABRIK",
    th: 13,
    level: 158,
    league: "Champion League III",
    shieldHours: 12,
    shieldMins: 34
  },
  resources: {
    gold: 14250000,
    elixir: 12800000,
    darkElixir: 240500,
    targetGold: 18000000,
    targetElixir: 18000000,
    targetDarkElixir: 300000
  },
  farming: {
    minGold: 350000,
    minElixir: 350000,
    minDe: 3000,
    maxNext: 35,
    autoZoom: true,
    autoHarvest: true,
    autoTrain: true,
    autoSurrender: true
  },
  activePresetId: 1,
  presets: [
    {
      id: 1,
      name: "Barch Perimeter Collector",
      space: "260 / 260 Space",
      thRange: "TH 11 - 13",
      notes: "Sangat efektif untuk desa mati (dead base). Pasukan disebar melingkar 12 titik luar untuk menghabisi kolektor emas dan tambang elixir.",
      units: [
        { name: "🗡️ Barbarian (Lv 9)", count: "120 unit" },
        { name: "🏹 Archer (Lv 9)", count: "140 unit" }
      ]
    },
    {
      id: 2,
      name: "Sneaky Goblin Storage Snatcher",
      space: "260 / 260 Space",
      thRange: "TH 11 - 16",
      notes: "Raja farming tercepat di CoC. Mampu menembus inti base musuh untuk merampok Dark Elixir Storage dan Balai Kota tanpa butuh seluruh pasukan.",
      units: [
        { name: "👺 Sneaky Goblin (Super)", count: "80 unit" },
        { name: "💣 Super Wall Breaker", count: "4 unit" },
        { name: "✨ Jump Spell & Invisibility", count: "4 Spell" }
      ]
    }
  ],
  walls: {
    completed: 185,
    total: 300,
    costPerWall: 4000000
  },
  upgrades: [
    { id: 1, builder: "B1", name: "Scattershot Lv 2", cost: "14,500,000 Gold", finishTime: "01j : 14m", color: "red" },
    { id: 2, builder: "B2", name: "Inferno Tower Lv 7", cost: "12,000,000 Gold", finishTime: "08j : 20m", color: "amber" },
    { id: 3, builder: "B3", name: "Eagle Artillery Lv 4", cost: "17,000,000 Gold", finishTime: "1 Hari 12j", color: "amber" },
    { id: 4, builder: "B4", name: "Royal Champion Lv 18", cost: "185,000 DE", finishTime: "2 Hari 04j", color: "cyan" },
    { id: 5, builder: "B5", name: "Seeking Air Mine Lv 4", cost: "4,000,000 Gold", finishTime: "03j : 45m", color: "amber" }
  ],
  attacks: [
    { time: "5 mnt lalu", gold: 540200, elixir: 510800, de: 4800, stars: "⭐ 1 (54%)", win: true },
    { time: "28 mnt lalu", gold: 620000, elixir: 590400, de: 5200, stars: "⭐ 2 (72%)", win: true },
    { time: "52 mnt lalu", gold: 480000, elixir: 495000, de: 3900, stars: "⭐ 1 (51%)", win: true },
    { time: "1j 15m lalu", gold: 590000, elixir: 580000, de: 4400, stars: "⭐ 2 (68%)", win: true },
    { time: "1j 40m lalu", gold: 610000, elixir: 530000, de: 5100, stars: "⭐ 1 (57%)", win: true },
    { time: "2j 05m lalu", gold: 520000, elixir: 515000, de: 4000, stars: "⭐ 1 (50%)", win: true },
    { time: "2j 30m lalu", gold: 595000, elixir: 560000, de: 4900, stars: "⭐ 2 (75%)", win: true }
  ]
};

// Ambil State dari LocalStorage atau default
let appState = JSON.parse(localStorage.getItem('kelnara_bot_data')) || DEFAULT_STATE;

function saveState() {
  localStorage.setItem('kelnara_bot_data', JSON.stringify(appState));
}

// Inisialisasi Ikon Lucide
document.addEventListener('DOMContentLoaded', () => {
  if (window.lucide) {
    lucide.createIcons();
  }
  initLootChart();
  initSessionTimer();
  updateUI();
});

// Tab Switcher
function switchTab(tabId) {
  const panes = document.querySelectorAll('.tab-pane');
  panes.forEach(p => p.classList.add('hidden'));

  const target = document.getElementById(`tab-${tabId}`);
  if (target) {
    target.classList.remove('hidden');
  }

  // Update PC Nav Active State
  const pcBtns = document.querySelectorAll('.nav-btn');
  pcBtns.forEach(btn => {
    if (btn.dataset.tab === tabId) {
      btn.className = 'nav-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl text-sm font-semibold transition bg-amber-500/10 text-amber-400 border border-amber-500/30';
    } else {
      btn.className = 'nav-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl text-sm font-semibold transition text-slate-400 hover:text-slate-200 hover:bg-slate-800/50';
    }
  });

  // Update Mobile Nav Active State
  const mobBtns = document.querySelectorAll('.mobile-nav-btn');
  mobBtns.forEach(btn => {
    if (btn.dataset.tab === tabId) {
      btn.classList.add('text-amber-400');
      btn.classList.remove('text-slate-400');
    } else {
      btn.classList.remove('text-amber-400');
      btn.classList.add('text-slate-400');
    }
  });

  if (window.lucide) lucide.createIcons();
}

// Update Elemen Tampilan UI
function updateUI() {
  document.getElementById('dashAccountName').innerText = appState.account.name;
  document.getElementById('sideAccountName').innerText = appState.account.name;

  document.getElementById('dashGoldVal').innerText = appState.resources.gold.toLocaleString('id-ID');
  document.getElementById('dashElixirVal').innerText = appState.resources.elixir.toLocaleString('id-ID');
  document.getElementById('dashDeVal').innerText = appState.resources.darkElixir.toLocaleString('id-ID');

  document.getElementById('inpTargetGold').value = appState.resources.targetGold / 1000000;
  document.getElementById('inpTargetElixir').value = appState.resources.targetElixir / 1000000;
  document.getElementById('inpTargetDe').value = appState.resources.targetDarkElixir / 1000;

  document.getElementById('inpMinGold').value = appState.farming.minGold;
  document.getElementById('inpMinElixir').value = appState.farming.minElixir;
  document.getElementById('inpMinDe').value = appState.farming.minDe;
  document.getElementById('inpMaxNext').value = appState.farming.maxNext;

  document.getElementById('chkAutoZoom').checked = appState.farming.autoZoom;
  document.getElementById('chkAutoHarvest').checked = appState.farming.autoHarvest;
  document.getElementById('chkAutoTrain').checked = appState.farming.autoTrain;
  document.getElementById('chkAutoSurrender').checked = appState.farming.autoSurrender;
}

// Simpan Pengaturan Farming
function saveFarmingSettings() {
  appState.resources.targetGold = (parseFloat(document.getElementById('inpTargetGold').value) || 18) * 1000000;
  appState.resources.targetElixir = (parseFloat(document.getElementById('inpTargetElixir').value) || 18) * 1000000;
  appState.resources.targetDarkElixir = (parseFloat(document.getElementById('inpTargetDe').value) || 300) * 1000;

  appState.farming.minGold = parseInt(document.getElementById('inpMinGold').value) || 350000;
  appState.farming.minElixir = parseInt(document.getElementById('inpMinElixir').value) || 350000;
  appState.farming.minDe = parseInt(document.getElementById('inpMinDe').value) || 3000;
  appState.farming.maxNext = parseInt(document.getElementById('inpMaxNext').value) || 35;

  appState.farming.autoZoom = document.getElementById('chkAutoZoom').checked;
  appState.farming.autoHarvest = document.getElementById('chkAutoHarvest').checked;
  appState.farming.autoTrain = document.getElementById('chkAutoTrain').checked;
  appState.farming.autoSurrender = document.getElementById('chkAutoSurrender').checked;

  saveState();
  updateUI();
  showToast("✅ Konfigurasi Farming Kelnara Berhasil Disimpan!");
}

// Session Timer Stopwatch
let sessionSeconds = 2535; // 42m 15s
let sessionRunning = true;
let sessionInterval = null;

function initSessionTimer() {
  sessionInterval = setInterval(() => {
    if (sessionRunning) {
      sessionSeconds++;
      updateSessionDisplay();
    }
  }, 1000);
}

function updateSessionDisplay() {
  const hrs = String(Math.floor(sessionSeconds / 3600)).padStart(2, '0');
  const mins = String(Math.floor((sessionSeconds % 3600) / 60)).padStart(2, '0');
  const secs = String(sessionSeconds % 60).padStart(2, '0');
  const el = document.getElementById('sessionTimerDisplay');
  if (el) el.innerText = `${hrs}:${mins}:${secs}`;
}

function toggleSessionTimer() {
  sessionRunning = !sessionRunning;
  const btn = document.getElementById('btnSessionToggle');
  const txt = document.getElementById('txtSessionToggle');
  if (sessionRunning) {
    btn.className = "px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-black text-xs shadow flex items-center space-x-1.5 transition";
    txt.innerText = "Jeda Sesi";
  } else {
    btn.className = "px-5 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-600 text-slate-950 font-black text-xs shadow flex items-center space-x-1.5 transition";
    txt.innerText = "Lanjutkan Sesi";
  }
}

function resetSessionTimer() {
  sessionSeconds = 0;
  updateSessionDisplay();
  showToast("⏱️ Timer sesi telah direset ke 00:00:00");
}

function saveSessionSettings() {
  showToast("☕ Jadwal istirahat anti-burnout telah aktif!");
}

// Chart.js Loot Progress
let lootChartInstance = null;
function initLootChart() {
  const ctx = document.getElementById('lootChart');
  if (!ctx) return;

  const labels = ['#1', '#2', '#3', '#4', '#5', '#6', '#7'];
  const goldData = [595, 520, 610, 590, 480, 620, 540];
  const elixirData = [560, 515, 530, 580, 495, 590, 510];

  lootChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Gold (K)',
          data: goldData,
          backgroundColor: '#f59e0b',
          borderRadius: 6
        },
        {
          label: 'Elixir (K)',
          data: elixirData,
          backgroundColor: '#d946ef',
          borderRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: '#94a3b8', font: { size: 11, weight: 'bold' } }
        }
      },
      scales: {
        y: {
          ticks: { color: '#64748b' },
          grid: { color: 'rgba(51, 65, 85, 0.4)' }
        },
        x: {
          ticks: { color: '#94a3b8' },
          grid: { display: false }
        }
      }
    }
  });
}

// Preset Actions
function setActivePreset(id) {
  appState.activePresetId = id;
  saveState();
  showToast("⚔️ Preset aktif berhasil diubah!");
  setTimeout(() => location.reload(), 600);
}

function setReminder(buildingName) {
  if ("Notification" in window) {
    Notification.requestPermission().then(permission => {
      if (permission === "granted") {
        showToast(`🔔 Pengingat diatur untuk ${buildingName}!`);
      } else {
        showToast(`🔔 Pengingat diatur untuk ${buildingName} (Via Suara & Layar)!`);
      }
    });
  } else {
    showToast(`🔔 Pengingat diatur untuk ${buildingName}!`);
  }
}

// Floating Bot Modal Actions
function openFloatingModal() {
  document.getElementById('modalFloating').classList.remove('hidden');
}

function closeFloatingModal() {
  document.getElementById('modalFloating').classList.add('hidden');
}

function startQuickFarmAction() {
  openFloatingModal();
}

function copyBotScriptPath() {
  navigator.clipboard.writeText("android/kelnara_bot.js").then(() => {
    showToast("📋 Lokasi skrip berhasil disalin!");
  });
}

// JSON Export & Import
function exportDataJson() {
  const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(appState, null, 2));
  const dlAnchor = document.createElement('a');
  dlAnchor.setAttribute("href", dataStr);
  dlAnchor.setAttribute("download", `kelnara_bot_coc_backup_${new Date().toISOString().slice(0, 10)}.json`);
  document.body.appendChild(dlAnchor);
  dlAnchor.click();
  dlAnchor.remove();
  showToast("💾 Cadangan data Kelnara berhasil diunduh!");
}

function importDataJson(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function(e) {
    try {
      const imported = JSON.parse(e.target.result);
      appState = imported;
      saveState();
      updateUI();
      showToast("✅ Konfigurasi Kelnara berhasil dipulihkan!");
    } catch (err) {
      alert("Format JSON tidak valid!");
    }
  };
  reader.readAsText(file);
}

// Toast Notifier
function showToast(message) {
  const toast = document.createElement('div');
  toast.className = 'fixed top-16 left-1/2 transform -translate-x-1/2 z-50 bg-[#0f172a] text-white border border-emerald-500/50 px-4 py-2.5 rounded-xl shadow-2xl text-xs font-bold flex items-center space-x-2 transition-all duration-300 pointer-events-none';
  toast.innerHTML = `<span>${message}</span>`;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 2500);
}
