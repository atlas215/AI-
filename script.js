const IS_GITHUB_PAGES = window.location.hostname.endsWith('github.io') || window.location.hostname.includes('githubusercontent.com');
const API_URL_QUERY_PARAM = 'api_url';
const TUNNEL_URL_QUERY_PARAM = 'tunnel_url';
const API_STORAGE_KEY = 'atlas_api_url';
const isMobileDevice = /Mobi|Android|iPhone|iPad|iPod|Opera Mini|IEMobile/.test(navigator.userAgent);

function getQueryParam(key) {
    const params = new URLSearchParams(window.location.search);
    return params.get(key);
}

function resolveSavedApiUrl() {
    return (
        localStorage.getItem(API_STORAGE_KEY) ||
        sessionStorage.getItem(API_STORAGE_KEY) ||
        getQueryParam(API_URL_QUERY_PARAM) ||
        getQueryParam(TUNNEL_URL_QUERY_PARAM)
    );
}

function detectApiBaseUrl() {
    const savedUrl = resolveSavedApiUrl();
    if (savedUrl) {
        return savedUrl.replace(/\/$/, '');
    }

    if (IS_GITHUB_PAGES) {
        const tunnelUrl = localStorage.getItem('atlas_tunnel_url') || getQueryParam('tunnel_url');
        if (tunnelUrl) {
            return tunnelUrl.replace(/\/$/, '');
        }
        console.warn('GitHub Pages detected. Please set ?api_url=https://your-ngrok-url or save atlas_api_url in localStorage.');
        return window.location.origin;
    }

    return `${window.location.protocol}//${window.location.host}`;
}

const API_BASE_URL = detectApiBaseUrl();
const CURRENT_PROTOCOL = API_BASE_URL.startsWith('https') ? 'https:' : 'http:';
const CURRENT_HOST = new URL(API_BASE_URL).host;
const BASE_HTTP = API_BASE_URL;
const BASE_WS = `${API_BASE_URL.startsWith('https') ? 'wss' : 'ws'}://${CURRENT_HOST}/ws`;

const chatWindow = document.getElementById('chatWindow');
const historyList = document.getElementById('historyList');
const digitalClock = document.getElementById('digitalClock');
const chatInput = document.getElementById('chatInput');
const chatSend = document.getElementById('chatSend');
const openChartButton = document.getElementById('openChart');
const saveChartButton = document.getElementById('saveChart');
const minimizedChart = document.getElementById('minimizedChart');
const customChartCanvas = document.getElementById('customChart');
const chartFullscreenModal = document.getElementById('chartFullscreenModal');
const closeFullscreenBtn = document.getElementById('closeFullscreenBtn');
const customChartFullscreenCanvas = document.getElementById('customChartFullscreen');
const wsStatus = document.getElementById('wsStatus');
const uptimeValue = document.getElementById('uptimeValue');
const memoryCount = document.getElementById('memoryCount');
const nodeHealth = document.getElementById('nodeHealth');
const arbScore = document.getElementById('arbScore');
const fontSelector = document.getElementById('fontSelector');
const toggleRainButton = document.getElementById('toggleRain');
const rainSpeedSlider = document.getElementById('rainSpeed');
const rainCanvas = document.getElementById('matrixRain');
const ctx = rainCanvas.getContext('2d');

let rainColumns = [];
let rainActive = true;
let rainSpeed = Number(rainSpeedSlider.value);
let ws = null;
let reconnectAttempt = 0;
let heartbeatIntervalId = null;
let reconnectTimeoutId = null;
let memoryData = null;
let flashChart = null;
let connectivityChart = null;
let customChart = null;
let activeChart = null;
let initializedHistory = false;
let pageStart = Date.now();

function setWsStatus(text, online) {
    wsStatus.innerHTML = `<span class="connection-pulse"></span>${text}`;
    wsStatus.style.color = online ? '#020b05' : '#ffffff';
    wsStatus.style.backgroundColor = online ? '#34ff7d' : '#ff3d46';
    wsStatus.style.boxShadow = online ? '0 0 18px rgba(52,255,125,0.45)' : '0 0 18px rgba(255,61,70,0.45)';
    wsStatus.classList.toggle('online', online);
}

function updateDigitalClock() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    digitalClock.textContent = `${hours}:${minutes}:${seconds}`;
}

function resizeCanvas() {
    rainCanvas.width = window.innerWidth;
    rainCanvas.height = window.innerHeight;

    const density = isMobileDevice ? 32 : 18;
    const columns = Math.max(16, Math.floor(rainCanvas.width / density));
    rainColumns = Array.from({ length: columns }, () => Math.random() * rainCanvas.height);

    if (isMobileDevice && rainSpeed > 1.2) {
        rainSpeed = 1.0;
    }
}

function drawRain() {
    if (!rainActive) {
        ctx.clearRect(0, 0, rainCanvas.width, rainCanvas.height);
        return;
    }

    ctx.fillStyle = 'rgba(0, 0, 0, 0.08)';
    ctx.fillRect(0, 0, rainCanvas.width, rainCanvas.height);
    ctx.fillStyle = 'rgba(57, 255, 168, 0.8)';
    ctx.font = '16px Courier New, monospace';

    rainColumns.forEach((y, index) => {
        const x = index * 18;
        const char = String.fromCharCode(0x30a0 + Math.random() * 96);
        ctx.fillText(char, x, y);

        if (y > rainCanvas.height + Math.random() * 1000) {
            rainColumns[index] = 0;
        } else {
            rainColumns[index] = y + 14 * rainSpeed;
        }
    });

    requestAnimationFrame(drawRain);
}

function toggleRain() {
    rainActive = !rainActive;
    toggleRainButton.textContent = rainActive ? 'RAIN: ON' : 'RAIN: OFF';
    if (rainActive) {
        drawRain();
    }
}

function setFontStyle(style) {
    document.body.classList.remove('font-matrix', 'font-futuristic', 'font-techmono');
    document.body.classList.add(`font-${style}`);
}

function addMessageBubble(sender, message, type) {
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${type}`;
    bubble.innerHTML = `<span class="meta">${sender}</span><span class="content"></span>`;
    chatWindow.appendChild(bubble);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    return bubble.querySelector('.content');
}

function addUserMessage(message) {
    const content = addMessageBubble('SIR BURTON', message, 'user');
    content.textContent = message;
}

function typewriterMessage(message) {
    const content = addMessageBubble('ATLAS', '', 'atlas');
    let idx = 0;
    const interval = Math.max(20, 45 - Math.round(rainSpeed * 10));
    const timer = setInterval(() => {
        content.textContent += message[idx] || '';
        idx += 1;
        chatWindow.scrollTop = chatWindow.scrollHeight;

        if (idx > message.length - 1) {
            clearInterval(timer);
        }
    }, interval);
}

function fetchHealth() {
    fetch(`${BASE_HTTP}/health`)
        .then((response) => response.json())
        .then(() => {
            const uptimeSeconds = Math.floor((Date.now() - pageStart) / 1000);
            uptimeValue.textContent = `${Math.floor(uptimeSeconds / 60)}m ${uptimeSeconds % 60}s`;
            setWsStatus('WS: Connected', true);
        })
        .catch(() => {
            setWsStatus('WS: Disconnected', false);
        });
}

function fetchMemory() {
    fetch(`${BASE_HTTP}/memory`)
        .then((response) => response.json())
        .then((memory) => {
            memoryData = memory;
            updateMetrics(memory);
            populateHistory(memory);
            updateCharts(memory);
        })
        .catch(() => {
            // ignore transient failures
        });
}

function updateMetrics(memory) {
    const totalMessages = Array.isArray(memory.messages) ? memory.messages.length : 0;
    memoryCount.textContent = `${totalMessages}`;
    nodeHealth.textContent = `${Math.min(99, 76 + totalMessages)}%`;
    arbScore.textContent = `${Math.max(68, 88 - Math.floor(totalMessages / 2))}%`;
}

function populateHistory(memory) {
    if (!memory || !Array.isArray(memory.messages)) {
        return;
    }
    chatWindow.innerHTML = '';
    historyList.innerHTML = '';

    const latest = memory.messages.slice(-10);
    latest.forEach((item) => {
        if (item.user && item.user.toLowerCase().includes('sir')) {
            const bubble = addMessageBubble(item.user, item.message, 'user');
            bubble.textContent = item.message;
        } else {
            const bubble = addMessageBubble('ATLAS', item.message, 'atlas');
            bubble.textContent = item.message;
        }
    });

    memory.messages.slice().reverse().forEach((item) => {
        addHistoryEntry(item);
    });
}

function addHistoryEntry(item) {
    const entry = document.createElement('div');
    entry.className = `history-entry ${item.user && item.user.toLowerCase().includes('sir') ? 'user' : 'atlas'}`;
    entry.innerHTML = `<span class="history-user">${item.user || 'UNKNOWN'}</span><span class="history-time">${new Date(item.timestamp).toLocaleTimeString()}</span><div class="history-text">${item.message}</div>`;
    historyList.appendChild(entry);
}

function getReconnectDelay(attempt) {
    return Math.min(16000, 2000 * Math.pow(2, attempt));
}

function clearHeartbeat() {
    if (heartbeatIntervalId) {
        clearInterval(heartbeatIntervalId);
        heartbeatIntervalId = null;
    }
}

function startHeartbeat() {
    clearHeartbeat();
    heartbeatIntervalId = setInterval(() => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'heartbeat', timestamp: new Date().toISOString() }));
        }
    }, 10000);
}

function resetReconnect() {
    reconnectAttempt = 0;
    if (reconnectTimeoutId) {
        clearTimeout(reconnectTimeoutId);
        reconnectTimeoutId = null;
    }
}

function scheduleReconnect() {
    clearHeartbeat();
    if (reconnectTimeoutId) {
        return;
    }
    reconnectAttempt = Math.min(reconnectAttempt + 1, 3);
    const delay = getReconnectDelay(reconnectAttempt);
    setWsStatus(`WS: Reconnecting in ${delay / 1000}s`, false);
    reconnectTimeoutId = setTimeout(() => {
        reconnectTimeoutId = null;
        createWebSocket();
    }, delay);
}

function createWebSocket() {
    if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
        return;
    }

    ws = new WebSocket(BASE_WS);
    setWsStatus('WS: Connecting...', false);

    ws.addEventListener('open', () => {
        setWsStatus('Live Pulse', true);
        resetReconnect();
        fetchHealth();
        fetchMemory();
        startHeartbeat();
    });

    ws.addEventListener('message', (event) => {
        try {
            const payload = JSON.parse(event.data);
            if (payload.type === 'heartbeat' || payload.type === 'heartbeat_ack') {
                setWsStatus('Live Pulse', true);
                return;
            }

            if (payload.status === 'received' && payload.data) {
                typewriterMessage(`Memory saved. Message received at ${new Date(payload.data.timestamp).toLocaleTimeString()}`);
                fetchMemory();
            }
        } catch (error) {
            typewriterMessage('Atlas received an update. Verifying system memory.');
        }
    });

    ws.addEventListener('close', () => {
        ws = null;
        scheduleReconnect();
    });

    ws.addEventListener('error', () => {
        setWsStatus('WS: Error', false);
        if (ws) {
            ws.close();
        }
    });
}

function sendChat() {
    const message = chatInput.value.trim();
    if (!message) {
        return;
    }
    addUserMessage(message);
    chatInput.value = '';
    const payload = {
        user: 'SIR BURTON',
        message,
        timestamp: new Date().toISOString(),
    };

    // Auto-show chart on fullscreen when message is sent
    setTimeout(() => {
        openNewChart();
        setTimeout(showChartFullscreen, 500);
    }, 1500);

    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(payload));
    } else {
        fetch(`${BASE_HTTP}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        })
            .then((response) => response.json())
            .then((data) => {
                typewriterMessage(`Atlas logged your message at ${new Date(data.timestamp).toLocaleTimeString()}`);
                fetchMemory();
            })
            .catch(() => {
                typewriterMessage('Atlas is offline. Your message will retry when connection returns.');
            });
    }
}

function updateCharts(memory) {
    const base = Array.from({ length: 6 }, (_, index) => {
        return Math.round(65 + index * 4 + (memory.messages?.length || 0) * 0.4 + (Math.random() - 0.5) * 8);
    });

    const connectivity = [
        Math.round(Math.min(100, 82 + (memory.messages?.length || 0) * 0.3 + Math.random() * 6)),
        Math.round(Math.max(0, 12 + Math.random() * 8)),
        Math.round(Math.max(0, 4 + Math.random() * 4)),
    ];

    flashChart.data.datasets[0].data = base;
    connectivityChart.data.datasets[0].data = connectivity;
    flashChart.update();
    connectivityChart.update();
}

function createCharts() {
    const flashCtx = document.getElementById('arbitrageChart').getContext('2d');
    flashChart = new Chart(flashCtx, {
        type: 'line',
        data: {
            labels: ['T-5', 'T-4', 'T-3', 'T-2', 'T-1', 'NOW'],
            datasets: [
                {
                    label: 'Flash Loan Arbitrage',
                    data: [72, 78, 82, 88, 91, 94],
                    borderColor: '#36ffdb',
                    backgroundColor: 'rgba(54, 255, 219, 0.16)',
                    tension: 0.35,
                    pointRadius: 4,
                    pointBackgroundColor: '#39f4ff',
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: { mode: 'index', intersect: false }
            },
            scales: {
                x: { grid: { color: 'rgba(62, 255, 184, 0.08)' }, ticks: { color: '#8dffdf' } },
                y: { beginAtZero: true, max: 110, grid: { color: 'rgba(62, 255, 184, 0.08)' }, ticks: { color: '#8dffdf' } }
            }
        }
    });

    const connectivityCtx = document.getElementById('connectivityChart').getContext('2d');
    connectivityChart = new Chart(connectivityCtx, {
        type: 'doughnut',
        data: {
            labels: ['Online', 'Latency', 'Offline'],
            datasets: [
                {
                    data: [88, 8, 4],
                    backgroundColor: ['#39f4ff', '#78ffca', '#2c8d9e'],
                    borderWidth: 0,
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#b5fff1' }
                }
            }
        }
    });
}

function openNewChart() {
    if (!memoryData || !Array.isArray(memoryData.messages)) {
        typewriterMessage('Loading chat memory before generating the new chart...');
        fetchMemory();
        return;
    }

    const counts = memoryData.messages.reduce((acc, msg) => {
        const user = msg.user || 'UNKNOWN';
        acc[user] = (acc[user] || 0) + 1;
        return acc;
    }, {});

    const labels = Object.keys(counts);
    const data = labels.map((label) => counts[label]);
    const bgColors = labels.map((label, index) => {
        const palette = ['#39f4ff', '#7ef4c5', '#ff7f92', '#ffcd38', '#7d5fff', '#ff6bc5'];
        return palette[index % palette.length];
    });

    if (customChart) {
        customChart.destroy();
    }

    customChart = new Chart(customChartCanvas.getContext('2d'), {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Message Count',
                data,
                backgroundColor: bgColors,
                borderColor: '#ffffff55',
                borderWidth: 1,
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                title: {
                    display: true,
                    text: 'ATLAS Chat History Breakdown',
                    color: '#b5fff1',
                    font: { size: 16 }
                }
            },
            scales: {
                x: { ticks: { color: '#b5fff1' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                y: { beginAtZero: true, ticks: { color: '#b5fff1' }, grid: { color: 'rgba(255,255,255,0.05)' } }
            }
        }
    });

    minimizedChart.classList.remove('hidden');
    activeChart = customChart;
}

function saveCurrentChart() {
    const chartToSave = activeChart || customChart || flashChart;
    if (!chartToSave) {
        typewriterMessage('No chart is available to save yet. Open a chart first.');
        return;
    }

    const imageUrl = chartToSave.toBase64Image();
    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = `atlas_chart_${Date.now()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    typewriterMessage('Chart saved locally. Sir Burton can review it anytime.');
}

function showChartFullscreen() {
    if (!customChart) {
        openNewChart();
    }
    
    setTimeout(() => {
        // Recreate chart for fullscreen canvas
        if (customChart) {
            customChart.destroy();
        }

        const counts = memoryData.messages.reduce((acc, msg) => {
            const user = msg.user || 'UNKNOWN';
            acc[user] = (acc[user] || 0) + 1;
            return acc;
        }, {});

        const labels = Object.keys(counts);
        const data = labels.map((label) => counts[label]);
        const bgColors = labels.map((label, index) => {
            const palette = ['#39f4ff', '#7ef4c5', '#ff7f92', '#ffcd38', '#7d5fff', '#ff6bc5'];
            return palette[index % palette.length];
        });

        customChart = new Chart(customChartFullscreenCanvas.getContext('2d'), {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Message Count',
                    data,
                    backgroundColor: bgColors,
                    borderColor: '#ffffff55',
                    borderWidth: 2,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: true },
                    title: {
                        display: true,
                        text: 'ATLAS Chat History Breakdown [FULLSCREEN MODE]',
                        color: '#b5fff1',
                        font: { size: 24 }
                    }
                },
                scales: {
                    x: { ticks: { color: '#b5fff1', font: { size: 14 } }, grid: { color: 'rgba(255,255,255,0.05)' } },
                    y: { beginAtZero: true, ticks: { color: '#b5fff1', font: { size: 14 } }, grid: { color: 'rgba(255,255,255,0.05)' } }
                }
            }
        });

        minimizedChart.classList.add('hidden');
        chartFullscreenModal.classList.remove('hidden');
        activeChart = customChart;
    }, 100);
}

function closeChartFullscreen() {
    chartFullscreenModal.classList.add('hidden');
    minimizedChart.classList.remove('hidden');
    if (customChart) {
        customChart.destroy();
        customChart = new Chart(customChartCanvas.getContext('2d'), {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Message Count',
                    data: [],
                    backgroundColor: [],
                    borderColor: '#ffffff55',
                    borderWidth: 1,
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                    title: {
                        display: true,
                        text: 'ATLAS Chat History Breakdown',
                        color: '#b5fff1',
                        font: { size: 16 }
                    }
                },
                scales: {
                    x: { ticks: { color: '#b5fff1' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                    y: { beginAtZero: true, ticks: { color: '#b5fff1' }, grid: { color: 'rgba(255,255,255,0.05)' } }
                }
            }
        });
    }
}

let deferredInstallPrompt = null;
window.addEventListener('beforeinstallprompt', (event) => {
    event.preventDefault();
    deferredInstallPrompt = event;
    console.info('ATLAS install prompt ready.');
});

async function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        try {
            await navigator.serviceWorker.register('/service-worker.js');
            console.info('ATLAS service worker registered');
        } catch (error) {
            console.warn('Service worker registration failed:', error);
        }
    }
}

function getPwaInstallPrompt() {
    if (deferredInstallPrompt) {
        deferredInstallPrompt.prompt();
        deferredInstallPrompt.userChoice.then((choiceResult) => {
            console.info('User choice:', choiceResult.outcome);
            deferredInstallPrompt = null;
        });
    }
}

chatSend.addEventListener('click', sendChat);
chatInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
        event.preventDefault();
        sendChat();
    }
});

fontSelector.addEventListener('change', (event) => {
    setFontStyle(event.target.value);
});

openChartButton.addEventListener('click', openNewChart);
saveChartButton.addEventListener('click', saveCurrentChart);

minimizedChart.addEventListener('click', showChartFullscreen);
closeFullscreenBtn.addEventListener('click', closeChartFullscreen);

toggleRainButton.addEventListener('click', toggleRain);
rainSpeedSlider.addEventListener('input', (event) => {
    rainSpeed = Number(event.target.value);
});

window.addEventListener('resize', resizeCanvas);

setFontStyle('matrix');
resizeCanvas();
createCharts();
registerServiceWorker();
createWebSocket();
fetchMemory();
fetchHealth();
updateDigitalClock();
setInterval(updateDigitalClock, 1000);
requestAnimationFrame(drawRain);
setInterval(fetchMemory, 18000);
