import { client } from './client';

export interface NetworkStats {
  total_transactions: number;
  total_blocks: number;
  active_validators: number;
  tps: number;
  market_data: {
    price: number;
    market_cap: number;
    volume_24h: number;
  };
}

export const fetchNetworkStats = async (): Promise<NetworkStats> => {
  return client.get('/api/v1/stats');
};

export interface Block {
  number: number;
  hash: string;
  timestamp: string;
  transactions: string[];
  validator: string;
  size: number;
}

export const fetchBlocks = async (page = 1, limit = 10): Promise<Block[]> => {
  return client.get('/api/v1/blocks', { params: { page, limit } });
};

export interface Transaction {
  hash: string;
  from_address: string;
  to_address: string;
  value: number;
  timestamp: string;
  status: string;
  block_number?: number;
  gas_used?: number;
}

export const fetchTransactions = async (page = 1, limit = 10): Promise<Transaction[]> => {
  return client.get('/api/v1/transactions', { params: { page, limit } });
};

export interface Validator {
  address: string;
  stake: number;
  uptime: number;
  blocks_proposed: number;
  rewards_earned: number;
  status: 'active' | 'jailed' | 'inactive';
}

export const fetchValidators = async (): Promise<Validator[]> => {
  return client.get('/api/v1/validators');
}; 