// Real-time WebSocket connection for live market data
// リアルタイム市場データ用WebSocket接続

class RealtimeMarketConnection {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000; // 3 seconds
        this.listeners = new Map();
    }

    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/api/v1/realtime/ws`;

        console.log('Connecting to WebSocket:', wsUrl);

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.notifyListeners('connected', null);
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log('Received WebSocket message:', data);
                
                if (data.type === 'new_listings') {
                    this.handleNewListings(data);
                } else if (data.type === 'connected') {
                    console.log('Server confirmed connection:', data.message);
                }
            } catch (error) {
                console.error('Failed to parse WebSocket message:', error);
            }
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.notifyListeners('error', error);
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.isConnected = false;
            this.notifyListeners('disconnected', null);
            this.attemptReconnect();
        };

        // Keep-alive ping
        this.startPing();
    }

    startPing() {
        this.pingInterval = setInterval(() => {
            if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send('ping');
            }
        }, 30000); // Every 30 seconds
    }

    disconnect() {
        if (this.pingInterval) {
            clearInterval(this.pingInterval);
        }
        if (this.ws) {
            this.ws.close();
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            setTimeout(() => this.connect(), this.reconnectDelay);
        } else {
            console.error('Max reconnection attempts reached');
            this.notifyListeners('max_reconnect_failed', null);
        }
    }

    handleNewListings(data) {
        console.log(`Received ${data.count} new listings`);
        this.notifyListeners('new_listings', data.listings);
        
        // Update UI if callback is registered
        if (this.onNewListingsCallback) {
            this.onNewListingsCallback(data.listings);
        }
    }

    addEventListener(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }

    notifyListeners(event, data) {
        if (this.listeners.has(event)) {
            this.listeners.get(event).forEach(callback => callback(data));
        }
    }

    onNewListings(callback) {
        this.onNewListingsCallback = callback;
    }
}

// Global instance
let realtimeConnection = null;

// Start real-time capture
async function startRealtimeCapture() {
    try {
        const response = await fetch('/api/v1/realtime/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to start capture');
        }

        const result = await response.json();
        console.log('Real-time capture started:', result);

        // Connect WebSocket
        if (!realtimeConnection) {
            realtimeConnection = new RealtimeMarketConnection();
            realtimeConnection.connect();
        }

        return result;
    } catch (error) {
        console.error('Failed to start real-time capture:', error);
        throw error;
    }
}

// Stop real-time capture
async function stopRealtimeCapture() {
    try {
        const response = await fetch('/api/v1/realtime/stop', {
            method: 'POST',
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to stop capture');
        }

        const result = await response.json();
        console.log('Real-time capture stopped:', result);

        // Disconnect WebSocket
        if (realtimeConnection) {
            realtimeConnection.disconnect();
            realtimeConnection = null;
        }

        return result;
    } catch (error) {
        console.error('Failed to stop real-time capture:', error);
        throw error;
    }
}

// Get real-time capture status
async function getRealtimeStatus() {
    try {
        const response = await fetch('/api/v1/realtime/status');
        const status = await response.json();
        return status;
    } catch (error) {
        console.error('Failed to get real-time status:', error);
        return { is_running: false, error: error.message };
    }
}

// Export functions
window.RealtimeMarket = {
    connect: () => {
        if (!realtimeConnection) {
            realtimeConnection = new RealtimeMarketConnection();
        }
        realtimeConnection.connect();
        return realtimeConnection;
    },
    disconnect: () => {
        if (realtimeConnection) {
            realtimeConnection.disconnect();
        }
    },
    startCapture: startRealtimeCapture,
    stopCapture: stopRealtimeCapture,
    getStatus: getRealtimeStatus,
    getInstance: () => realtimeConnection,
};
