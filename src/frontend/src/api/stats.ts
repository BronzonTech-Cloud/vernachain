import { explorerClient } from './client';

export interface NetworkStats {
  total_blocks: number;
  total_transactions: number;
  total_addresses: number;
  total_validators: number;
  total_shards: number;
  average_block_time: number;
  current_tps: number;
  peak_tps: number;
  total_staked: number;
  current_difficulty: number;
  hash_rate: number;
  market_data?: {
    price_usd: number;
    price_change_24h: number;
    market_cap_usd: number;
    volume_24h_usd: number;
  };
}

export interface ChainInfo {
  name: string;
  version: string;
  network: {
    blocks: number;
    transactions: number;
    validators: number;
    shards: number;
    average_block_time: number;
    current_tps: number;
    total_staked: number;
    current_difficulty: number;
  };
  status: string;
  last_updated: string;
}

export interface BlockStats {
  latest_block: number;
  average_block_time: number;
  total_blocks_24h: number;
  difficulty_trend: Array<{
    timestamp: number;
    difficulty: number;
  }>;
}

export interface TransactionStats {
  total_transactions: number;
  transactions_24h: number;
  average_tps_24h: number;
  peak_tps_24h: number;
  pending_transactions: number;
  average_fee_24h: number;
}

export interface ValidatorStats {
  total_validators: number;
  active_validators: number;
  total_staked: number;
  average_uptime: number;
  average_performance: number;
}

export interface AddressStats {
  total_addresses: number;
  active_addresses_24h: number;
  new_addresses_24h: number;
  top_holders: Array<{
    address: string;
    balance: number;
    percentage: number;
  }>;
}

export interface Block {
  number: number;
  hash: string;
  timestamp: string;
  transactions: string[];
  validator: string;
  size: number;
  gas_used: number;
  gas_limit: number;
  parent_hash: string;
  state_root: string;
}

export interface Transaction {
  hash: string;
  from_address: string;
  to_address: string;
  value: string;
  timestamp: string;
  status: 'success' | 'failed' | 'pending';
  block_number?: number;
  gas_used?: number;
  gas_price: string;
  nonce: number;
  input_data?: string;
  error?: string;
}

export interface Validator {
  address: string;
  stake: string;
  uptime: number;
  blocks_proposed: number;
  rewards_earned: string;
  status: 'active' | 'jailed' | 'inactive';
  commission_rate: number;
  delegators: number;
  self_stake: string;
  total_stake: string;
}

export interface AddressInfo {
  address: string;
  balance: string;
  transaction_count: number;
  tokens: Array<{
    token_address: string;
    symbol: string;
    balance: string;
  }>;
  is_contract: boolean;
  contract_info?: {
    name?: string;
    symbol?: string;
    type?: string;
    verified?: boolean;
  };
}

// New analytics interfaces
export interface GasAnalytics {
  average_gas_price: number;
  gas_used_24h: number;
  gas_limit_utilization: number;
  gas_price_history: Array<{
    timestamp: number;
    price: number;
  }>;
}

export interface TokenAnalytics {
  total_tokens: number;
  active_tokens_24h: number;
  token_transfers_24h: number;
  top_tokens: Array<{
    address: string;
    name: string;
    symbol: string;
    volume_24h: number;
    price_change_24h: number;
    market_cap: number;
  }>;
  token_creation_history: Array<{
    timestamp: number;
    count: number;
  }>;
}

export interface ShardAnalytics {
  total_shards: number;
  active_shards: number;
  cross_shard_txs_24h: number;
  shard_sizes: number[];
  shard_tps: number[];
}

export interface NetworkAnalytics {
  node_distribution: Record<string, number>;
  network_latency: number;
  peer_count_average: number;
  bandwidth_usage: {
    inbound: number;
    outbound: number;
    total: number;
  };
}

export interface ValidatorResponse {
  validators: Validator[];
  total_stake: string;
  active_count: number;
}

export class StatsAPI {
  async getNetworkStats(): Promise<NetworkStats> {
    return explorerClient.get('/stats');
  }

  async getChainInfo(): Promise<ChainInfo> {
    return explorerClient.get('/');
  }

  async getBlockStats(): Promise<BlockStats> {
    return explorerClient.get('/stats/blocks');
  }

  async getTransactionStats(): Promise<TransactionStats> {
    return explorerClient.get('/stats/transactions');
  }

  async getValidatorStats(): Promise<ValidatorStats> {
    return explorerClient.get('/stats/validators');
  }

  async getAddressStats(): Promise<AddressStats> {
    return explorerClient.get('/stats/addresses');
  }

  async getHistoricalStats(
    metric: 'tps' | 'difficulty' | 'hashrate' | 'price',
    timeframe: '24h' | '7d' | '30d' = '24h'
  ): Promise<Array<{ timestamp: number; value: number }>> {
    return explorerClient.get(`/stats/historical/${metric}`, {
      params: { timeframe }
    });
  }

  async getMarketStats(): Promise<{
    price_usd: number;
    price_change_24h: number;
    market_cap_usd: number;
    volume_24h_usd: number;
    circulating_supply: number;
    total_supply: number;
  }> {
    return explorerClient.get('/stats/market');
  }

  async getNetworkHealth(): Promise<{
    status: 'healthy' | 'degraded' | 'unhealthy';
    block_time_health: number;
    validator_health: number;
    transaction_health: number;
    node_health: number;
    last_checked: string;
  }> {
    return explorerClient.get('/stats/health');
  }

  async getResourceUsage(): Promise<{
    memory_usage: number;
    cpu_usage: number;
    disk_usage: number;
    bandwidth_usage: number;
    node_count: number;
    peer_count: number;
  }> {
    return explorerClient.get('/stats/resources');
  }

  async getGasAnalytics(): Promise<GasAnalytics> {
    return explorerClient.get('/analytics/gas');
  }

  async getTokenAnalytics(): Promise<TokenAnalytics> {
    return explorerClient.get('/analytics/tokens');
  }

  async getShardAnalytics(): Promise<ShardAnalytics> {
    return explorerClient.get('/analytics/shards');
  }

  async getNetworkAnalytics(): Promise<NetworkAnalytics> {
    return explorerClient.get('/analytics/network');
  }

  // Enhanced WebSocket subscriptions
  subscribeToUpdates(
    channels: Array<'stats' | 'blocks' | 'transactions' | 'validators'>,
    callback: (update: {
      channel: string;
      type: string;
      data: any;
    }) => void
  ): () => void {
    const connections: WebSocket[] = [];

    channels.forEach(channel => {
      const ws = new WebSocket(
        `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${
          window.location.host
        }/ws/${channel}`
      );

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        callback({
          channel,
          type: data.type || 'update',
          data: data.data || data
        });
      };

      ws.onerror = (error) => {
        console.error(`WebSocket error on channel ${channel}:`, error);
      };

      ws.onclose = () => {
        console.log(`WebSocket connection closed for channel ${channel}`);
      };

      connections.push(ws);
    });

    return () => connections.forEach(ws => ws.close());
  }

  // Analytics data caching
  private analyticsCache: Map<string, {
    data: any;
    timestamp: number;
    ttl: number;
  }> = new Map();

  private async getCachedAnalytics<T>(
    key: string,
    fetcher: () => Promise<T>,
    ttl: number = 300000 // 5 minutes default
  ): Promise<T> {
    const cached = this.analyticsCache.get(key);
    const now = Date.now();

    if (cached && now - cached.timestamp < cached.ttl) {
      return cached.data as T;
    }

    const data = await fetcher();
    this.analyticsCache.set(key, {
      data,
      timestamp: now,
      ttl
    });

    return data;
  }

  async getGasAnalyticsCached(): Promise<GasAnalytics> {
    return this.getCachedAnalytics(
      'gas',
      () => this.getGasAnalytics(),
      60000 // 1 minute TTL
    );
  }

  async getTokenAnalyticsCached(): Promise<TokenAnalytics> {
    return this.getCachedAnalytics(
      'tokens',
      () => this.getTokenAnalytics(),
      300000 // 5 minutes TTL
    );
  }

  async getShardAnalyticsCached(): Promise<ShardAnalytics> {
    return this.getCachedAnalytics(
      'shards',
      () => this.getShardAnalytics(),
      60000 // 1 minute TTL
    );
  }

  async getNetworkAnalyticsCached(): Promise<NetworkAnalytics> {
    return this.getCachedAnalytics(
      'network',
      () => this.getNetworkAnalytics(),
      30000 // 30 seconds TTL
    );
  }

  // Batch analytics fetching
  async getAllAnalytics(): Promise<{
    gas: GasAnalytics;
    tokens: TokenAnalytics;
    shards: ShardAnalytics;
    network: NetworkAnalytics;
  }> {
    const [gas, tokens, shards, network] = await Promise.all([
      this.getGasAnalyticsCached(),
      this.getTokenAnalyticsCached(),
      this.getShardAnalyticsCached(),
      this.getNetworkAnalyticsCached()
    ]);

    return {
      gas,
      tokens,
      shards,
      network
    };
  }

  // Websocket subscription for real-time stats
  subscribeToStats(
    callback: (stats: Partial<NetworkStats>) => void
  ): () => void {
    const ws = new WebSocket(
      `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${
        window.location.host
      }/ws/stats`
    );

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      callback(data);
    };

    // Return unsubscribe function
    return () => ws.close();
  }

  // Cache management
  async clearStatsCache(): Promise<void> {
    return explorerClient.post('/stats/cache/clear');
  }

  async warmupStatsCache(): Promise<void> {
    return explorerClient.post('/stats/cache/warmup');
  }

  async getAllValidators(): Promise<ValidatorResponse> {
    const response = await explorerClient.get<ValidatorResponse>('/api/v1/validators');
    return response.data;
  }
}

export const statsAPI = new StatsAPI();

// Network stats
export const fetchNetworkStats = async (): Promise<NetworkStats> => {
  return explorerClient.get('/api/v1/stats');
};

// Blocks
export const fetchBlocks = async (page = 1, limit = 10): Promise<{
  blocks: Block[];
  total: number;
}> => {
  return explorerClient.get('/api/v1/blocks', { params: { page, limit } });
};

export const fetchBlock = async (blockNumber: number): Promise<Block> => {
  return explorerClient.get(`/api/v1/block/${blockNumber}`);
};

// Transactions
export const fetchTransactions = async (page = 1, limit = 10): Promise<{
  transactions: Transaction[];
  total: number;
}> => {
  return explorerClient.get('/api/v1/transactions', { params: { page, limit } });
};

export const fetchTransaction = async (hash: string): Promise<Transaction> => {
  return explorerClient.get(`/api/v1/transaction/${hash}`);
};

export const fetchAddressTransactions = async (
  address: string,
  page = 1,
  limit = 10
): Promise<{
  transactions: Transaction[];
  total: number;
}> => {
  return explorerClient.get(`/api/v1/address/${address}/transactions`, {
    params: { page, limit },
  });
};

// Validators
export const fetchValidators = async (): Promise<{
  validators: Validator[];
  total_stake: string;
  active_count: number;
}> => {
  return explorerClient.get('/api/v1/validators');
};

export const fetchValidator = async (address: string): Promise<Validator> => {
  return explorerClient.get(`/api/v1/validator/${address}`);
};

// Address info
export const fetchAddressInfo = async (address: string): Promise<AddressInfo> => {
  return explorerClient.get(`/api/v1/address/${address}`);
}; 