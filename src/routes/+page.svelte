<script lang="ts">
	import { onMount } from 'svelte';
	import { invoke } from '@tauri-apps/api/core';

	let isCapturing = $state(false);
	let marketData = $state<any[]>([]);
	let status = $state('準備中...');

	async function startCapture() {
		try {
			isCapturing = true;
			status = 'パケット傍受を開始しています...';
			await invoke('start_packet_capture');
			status = '取引所データを監視中...';
		} catch (error) {
			status = `エラー: ${error}`;
			isCapturing = false;
		}
	}

	async function stopCapture() {
		try {
			await invoke('stop_packet_capture');
			isCapturing = false;
			status = '監視を停止しました';
		} catch (error) {
			status = `エラー: ${error}`;
		}
	}

	async function loadMarketData() {
		try {
			const data = await invoke('get_market_data');
			marketData = data as any[];
		} catch (error) {
			console.error('Failed to load market data:', error);
		}
	}

	onMount(() => {
		status = '準備完了';
		// 定期的にデータを更新
		const interval = setInterval(loadMarketData, 5000);
		return () => clearInterval(interval);
	});
</script>

<div class="container">
	<header>
		<h1>⭐ StarResonance Market Analyzer</h1>
		<p class="subtitle">Blue Protocol: Star Resonance 取引所価格分析ツール</p>
	</header>

	<div class="control-panel">
		<div class="status">
			<span class="status-indicator" class:active={isCapturing}></span>
			<span>{status}</span>
		</div>
		
		<div class="buttons">
			{#if !isCapturing}
				<button class="btn btn-primary" onclick={startCapture}>
					📡 監視開始
				</button>
			{:else}
				<button class="btn btn-danger" onclick={stopCapture}>
					⏹️ 監視停止
				</button>
			{/if}
		</div>
	</div>

	<div class="info-panel">
		<div class="info-card">
			<h3>🎯 使い方</h3>
			<ol>
				<li>「監視開始」ボタンをクリック</li>
				<li>ゲームを起動して取引所を開く</li>
				<li>価格データが自動的に記録されます</li>
			</ol>
		</div>

		<div class="info-card">
			<h3>📊 収集データ</h3>
			<ul>
				<li>アイテム名と価格</li>
				<li>出品数と需要</li>
				<li>価格推移の履歴</li>
			</ul>
		</div>

		<div class="info-card">
			<h3>⚠️ 注意事項</h3>
			<ul>
				<li>初回起動時は管理者権限が必要です</li>
				<li>VPNと競合する場合があります</li>
				<li>使用は自己責任でお願いします</li>
			</ul>
		</div>
	</div>

	{#if marketData.length > 0}
		<div class="market-data">
			<h2>📈 取引所データ</h2>
			<div class="data-table">
				<table>
					<thead>
						<tr>
							<th>アイテム名</th>
							<th>現在価格</th>
							<th>出品数</th>
							<th>最終更新</th>
						</tr>
					</thead>
					<tbody>
						{#each marketData as item}
							<tr>
								<td>{item.name}</td>
								<td>{item.price.toLocaleString()} G</td>
								<td>{item.quantity}</td>
								<td>{new Date(item.updated_at).toLocaleString('ja-JP')}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>
	{:else}
		<div class="empty-state">
			<p>🔍 まだデータがありません</p>
			<p class="hint">監視を開始してゲーム内の取引所を開いてください</p>
		</div>
	{/if}
</div>

<style>
	.container {
		width: 100%;
		max-width: 1200px;
		margin: 0 auto;
		padding: 2rem;
	}

	header {
		text-align: center;
		margin-bottom: 2rem;
	}

	h1 {
		font-size: 2.5rem;
		margin: 0;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}

	.subtitle {
		color: #666;
		margin-top: 0.5rem;
	}

	.control-panel {
		background: #f8f9fa;
		border-radius: 12px;
		padding: 1.5rem;
		margin-bottom: 2rem;
		display: flex;
		justify-content: space-between;
		align-items: center;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	.status {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-weight: 500;
	}

	.status-indicator {
		width: 12px;
		height: 12px;
		border-radius: 50%;
		background: #ccc;
		transition: background 0.3s;
	}

	.status-indicator.active {
		background: #00d084;
		animation: pulse 2s infinite;
	}

	@keyframes pulse {
		0%, 100% { opacity: 1; }
		50% { opacity: 0.5; }
	}

	.buttons {
		display: flex;
		gap: 1rem;
	}

	.btn {
		padding: 0.75rem 1.5rem;
		border: none;
		border-radius: 8px;
		font-size: 1rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s;
	}

	.btn-primary {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
	}

	.btn-primary:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
	}

	.btn-danger {
		background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
		color: white;
	}

	.btn-danger:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(245, 87, 108, 0.4);
	}

	.info-panel {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
		gap: 1.5rem;
		margin-bottom: 2rem;
	}

	.info-card {
		background: white;
		border-radius: 12px;
		padding: 1.5rem;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	.info-card h3 {
		margin: 0 0 1rem 0;
		font-size: 1.25rem;
	}

	.info-card ul, .info-card ol {
		margin: 0;
		padding-left: 1.5rem;
	}

	.info-card li {
		margin-bottom: 0.5rem;
		line-height: 1.6;
	}

	.market-data {
		background: white;
		border-radius: 12px;
		padding: 1.5rem;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	.market-data h2 {
		margin: 0 0 1.5rem 0;
	}

	.data-table {
		overflow-x: auto;
	}

	table {
		width: 100%;
		border-collapse: collapse;
	}

	thead {
		background: #f8f9fa;
	}

	th {
		padding: 1rem;
		text-align: left;
		font-weight: 600;
		border-bottom: 2px solid #dee2e6;
	}

	td {
		padding: 1rem;
		border-bottom: 1px solid #dee2e6;
	}

	tbody tr:hover {
		background: #f8f9fa;
	}

	.empty-state {
		text-align: center;
		padding: 4rem 2rem;
		color: #666;
	}

	.empty-state p {
		margin: 0.5rem 0;
	}

	.empty-state .hint {
		font-size: 0.9rem;
		color: #999;
	}
</style>
