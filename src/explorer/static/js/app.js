// Configuration
const config = {
    API_URL: 'http://localhost:8000',
    WS_URL: 'ws://localhost:8000/ws',
    CACHE_DURATION: 5 * 60 * 1000, // 5 minutes
    DEFAULT_PAGE_SIZE: 10
};

// Cache management
const cache = {
    data: new Map(),
    
    set(key, value) {
        this.data.set(key, {
            value,
            timestamp: Date.now()
        });
    },
    
    get(key) {
        const item = this.data.get(key);
        if (!item) return null;
        
        if (Date.now() - item.timestamp > config.CACHE_DURATION) {
            this.data.delete(key);
            return null;
        }
        
        return item.value;
    },
    
    clear() {
        this.data.clear();
    }
};

// WebSocket connection
class WSConnection {
    constructor() {
        this.connect();
        this.subscriptions = new Set();
    }
    
    connect() {
        this.ws = new WebSocket(config.WS_URL);
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.resubscribe();
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket disconnected, reconnecting...');
            setTimeout(() => this.connect(), 5000);
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
    }
    
    subscribe(channel) {
        this.subscriptions.add(channel);
        if (this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'subscribe',
                channel
            }));
        }
    }
    
    resubscribe() {
        this.subscriptions.forEach(channel => this.subscribe(channel));
    }
    
    handleMessage(data) {
        switch (data.type) {
            case 'block':
                updateBlocksUI(data.data);
                break;
            case 'transaction':
                updateTransactionsUI(data.data);
                break;
            case 'validator':
                updateValidatorsUI(data.data);
                break;
        }
    }
}

// API calls with error handling
async function fetchAPI(endpoint, options = {}) {
    const url = `${config.API_URL}${endpoint}`;
    
    try {
        showLoading();
        
        // Check cache first
        const cachedData = cache.get(url);
        if (cachedData) {
            showCacheIndicator();
            return cachedData;
        }
        
        const response = await fetch(url, options);
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Cache the response
        cache.set(url, data);
        
        return data;
    } catch (error) {
        showError(error.message);
        throw error;
    } finally {
        hideLoading();
    }
}

// UI State Management
let state = {
    currentPage: 1,
    sortField: null,
    sortDirection: 'asc',
    filters: {},
    theme: localStorage.getItem('theme') || 'light'
};

// Theme Management
function toggleTheme() {
    state.theme = state.theme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', state.theme);
    localStorage.setItem('theme', state.theme);
}

// Loading State
function showLoading() {
    document.getElementById('loading').style.display = 'block';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

// Error Handling
function showError(message) {
    const toast = document.createElement('div');
    toast.className = 'toast show';
    toast.innerHTML = `
        <div class="toast-header">
            <strong class="me-auto">Error</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
        </div>
        <div class="toast-body">${message}</div>
    `;
    document.querySelector('.toast-container').appendChild(toast);
    
    setTimeout(() => toast.remove(), 5000);
}

// Cache Indicator
function showCacheIndicator() {
    document.getElementById('cacheIndicator').style.display = 'block';
    setTimeout(() => {
        document.getElementById('cacheIndicator').style.display = 'none';
    }, 2000);
}

// Sorting
function updateSort(field) {
    if (state.sortField === field) {
        state.sortDirection = state.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        state.sortField = field;
        state.sortDirection = 'asc';
    }
    
    updateUI();
}

// Filtering
function updateFilters(filters) {
    state.filters = { ...state.filters, ...filters };
    state.currentPage = 1;
    updateUI();
}

// Real-time Updates
function updateBlocksUI(block) {
    const blocksTable = document.querySelector('#blocksTable tbody');
    if (!blocksTable) return;
    
    const row = document.createElement('tr');
    row.innerHTML = `
        <td>${block.index}</td>
        <td>${new Date(block.timestamp * 1000).toLocaleString()}</td>
        <td>${block.validator}</td>
        <td>${block.transactions.length}</td>
        <td>${block.hash}</td>
    `;
    
    blocksTable.insertBefore(row, blocksTable.firstChild);
    
    // Remove last row to maintain page size
    if (blocksTable.children.length > config.DEFAULT_PAGE_SIZE) {
        blocksTable.removeChild(blocksTable.lastChild);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Initialize WebSocket
    const ws = new WSConnection();
    
    // Set initial theme
    document.documentElement.setAttribute('data-theme', state.theme);
    
    // Load initial data
    loadStats();
    showBlocks();
    
    // Add event listeners
    document.querySelector('#themeToggle').addEventListener('click', toggleTheme);
});

// Export functions for use in HTML
window.showBlocks = showBlocks;
window.showTransactions = showTransactions;
window.showValidators = showValidators;
window.showShards = showShards;
window.search = search;
window.updateSort = updateSort;
window.updateFilters = updateFilters; 