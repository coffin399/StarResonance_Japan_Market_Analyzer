// API Base URL
const API_BASE = '/api/v1';

// 数値をカンマ区切りでフォーマット
function formatNumber(num) {
    if (num === null || num === undefined) return '-';
    return num.toLocaleString('ja-JP');
}

// 日付をフォーマット
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('ja-JP');
}

// 市場概要を取得
async function loadMarketOverview() {
    try {
        const response = await fetch(`${API_BASE}/statistics/market-overview`);
        const data = await response.json();
        
        document.getElementById('active-listings').textContent = formatNumber(data.active_listings);
        document.getElementById('unique-items').textContent = formatNumber(data.unique_items);
        document.getElementById('total-value').textContent = formatNumber(data.total_value);
        document.getElementById('new-listings').textContent = formatNumber(data.new_listings_24h);
    } catch (error) {
        console.error('Failed to load market overview:', error);
    }
}

// トレンドアイテムを取得
async function loadTrendingItems() {
    try {
        const response = await fetch(`${API_BASE}/listings/trending?hours=24&limit=10`);
        const data = await response.json();
        
        const tbody = document.getElementById('trending-body');
        
        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="loading">データがありません</td></tr>';
            return;
        }
        
        tbody.innerHTML = data.map(item => `
            <tr>
                <td>${item.item_name}</td>
                <td>${formatNumber(item.listing_count)}</td>
                <td>${formatNumber(item.min_price)}</td>
                <td>${formatNumber(item.max_price)}</td>
                <td>${formatNumber(Math.round(item.avg_price))}</td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Failed to load trending items:', error);
        document.getElementById('trending-body').innerHTML = 
            '<tr><td colspan="5" class="loading">読み込みエラー</td></tr>';
    }
}

// 最新の出品情報を取得
async function loadLatestListings() {
    try {
        const response = await fetch(`${API_BASE}/listings/latest/all?limit=50`);
        const data = await response.json();
        
        const tbody = document.getElementById('listings-body');
        
        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="loading">データがありません</td></tr>';
            return;
        }
        
        tbody.innerHTML = data.map(listing => `
            <tr>
                <td>${listing.item_name}</td>
                <td>${formatNumber(listing.quantity)}</td>
                <td>${formatNumber(listing.price)}</td>
                <td>${formatNumber(Math.round(listing.unit_price))}</td>
                <td>${listing.seller || '-'}</td>
                <td>${formatDate(listing.captured_at)}</td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Failed to load latest listings:', error);
        document.getElementById('listings-body').innerHTML = 
            '<tr><td colspan="6" class="loading">読み込みエラー</td></tr>';
    }
}

// アイテムを検索
async function searchItems() {
    const searchTerm = document.getElementById('search-input').value.trim();
    
    if (!searchTerm) {
        loadLatestListings();
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/items?search=${encodeURIComponent(searchTerm)}&limit=50`);
        const items = await response.json();
        
        if (items.length === 0) {
            document.getElementById('listings-body').innerHTML = 
                '<tr><td colspan="6" class="loading">検索結果がありません</td></tr>';
            return;
        }
        
        // 各アイテムの最新出品を取得
        const tbody = document.getElementById('listings-body');
        tbody.innerHTML = '<tr><td colspan="6" class="loading">読み込み中...</td></tr>';
        
        const allListings = [];
        for (const item of items) {
            const listingResponse = await fetch(`${API_BASE}/listings?item_id=${item.id}&status=active&limit=5`);
            const listings = await listingResponse.json();
            allListings.push(...listings.map(l => ({ ...l, item_name: item.name })));
        }
        
        if (allListings.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="loading">アクティブな出品がありません</td></tr>';
            return;
        }
        
        tbody.innerHTML = allListings.map(listing => `
            <tr>
                <td>${listing.item_name}</td>
                <td>${formatNumber(listing.quantity)}</td>
                <td>${formatNumber(listing.price)}</td>
                <td>${formatNumber(Math.round(listing.unit_price || (listing.price / listing.quantity)))}</td>
                <td>${listing.seller_name || '-'}</td>
                <td>${formatDate(listing.captured_at)}</td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Failed to search items:', error);
        document.getElementById('listings-body').innerHTML = 
            '<tr><td colspan="6" class="loading">検索エラー</td></tr>';
    }
}

// Enterキーで検索
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                searchItems();
            }
        });
    }
});

// 損益を計算
async function calculateProfit() {
    const buyPrice = parseInt(document.getElementById('buy-price').value);
    const sellPrice = parseInt(document.getElementById('sell-price').value);
    const quantity = parseInt(document.getElementById('quantity').value);
    const feeRate = parseFloat(document.getElementById('fee-rate').value) / 100;
    const hasMonthlyCard = document.getElementById('monthly-card').checked;
    
    if (!buyPrice || !sellPrice || !quantity) {
        alert('すべての項目を入力してください');
        return;
    }
    
    if (buyPrice <= 0 || sellPrice <= 0 || quantity <= 0) {
        alert('正の値を入力してください');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/calculate-profit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                buy_price: buyPrice,
                sell_price: sellPrice,
                quantity: quantity,
                fee_rate: feeRate,
                has_monthly_card: hasMonthlyCard,
            }),
        });
        
        const result = await response.json();
        
        // 結果を表示
        const resultDiv = document.getElementById('calculator-result');
        const isProfit = result.profit > 0;
        
        resultDiv.innerHTML = `
            <div class="result-highlight">
                <div class="result-label">純利益</div>
                <div class="big-number ${isProfit ? 'positive' : 'negative'}">
                    ${isProfit ? '+' : ''}${formatNumber(result.profit)}
                </div>
                <div style="margin-top: 0.5rem; color: var(--text-muted);">
                    利益率: ${result.profit_rate.toFixed(2)}% | ROI: ${(result.roi * 100).toFixed(2)}%
                </div>
            </div>
            
            <div class="result-item">
                <span class="result-label">購入総額</span>
                <span class="result-value">${formatNumber(result.total_buy_cost)}</span>
            </div>
            <div class="result-item">
                <span class="result-label">販売総額</span>
                <span class="result-value">${formatNumber(result.total_sell_revenue)}</span>
            </div>
            <div class="result-item">
                <span class="result-label">手数料 (${(result.fee_rate * 100).toFixed(1)}%)</span>
                <span class="result-value">${formatNumber(result.fee)}</span>
            </div>
            <div class="result-item">
                <span class="result-label">純収入</span>
                <span class="result-value">${formatNumber(result.net_revenue)}</span>
            </div>
        `;
    } catch (error) {
        console.error('Failed to calculate profit:', error);
        alert('計算に失敗しました');
    }
}

// ページ読み込み時にデータを取得
document.addEventListener('DOMContentLoaded', () => {
    loadMarketOverview();
    loadTrendingItems();
    loadLatestListings();
    
    // 30秒ごとに更新
    setInterval(() => {
        loadMarketOverview();
        loadTrendingItems();
    }, 30000);
});
