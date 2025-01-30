import { apiClient } from './client';
import { explorerClient } from './client';

export interface Token {
  id: string;
  name: string;
  symbol: string;
  description: string;
  total_supply: string;
  decimals: number;
  is_mintable: boolean;
  is_burnable: boolean;
  is_pausable: boolean;
  metadata?: Record<string, any>;
  owner_address: string;
  created_at: string;
}

export interface CreateTokenRequest {
  name: string;
  symbol: string;
  description: string;
  initial_supply: string;
  decimals?: number;
  is_mintable?: boolean;
  is_burnable?: boolean;
  is_pausable?: boolean;
  metadata?: Record<string, any>;
}

export interface TokenTransferRequest {
  token_id: string;
  to_address: string;
  amount: string;
}

export interface TokenBurnRequest {
  token_id: string;
  amount: string;
}

export interface TokenMintRequest {
  token_id: string;
  to_address: string;
  amount: string;
}

export interface TokenPermissionRequest {
  token_id: string;
  address: string;
  permission_type: 'mint' | 'burn' | 'transfer' | 'admin';
  grant: boolean;
}

export interface TokenAnalytics {
  total_supply: string;
  holder_count: number;
  transfer_count: number;
  price_history: Array<{
    timestamp: string;
    price: string;
  }>;
  volume_24h: string;
  market_cap: string;
}

export interface TokenInfo {
  address: string;
  name: string;
  symbol: string;
  decimals: number;
  total_supply: string;
  holder_count: number;
  transfer_count: number;
  contract_verified: boolean;
  implementation?: string;
  market_data?: {
    price_usd: number;
    price_change_24h: number;
    market_cap_usd: number;
    volume_24h_usd: number;
    liquidity_usd: number;
  };
  metadata?: {
    website: string;
    email: string;
    blog: string;
    reddit: string;
    slack: string;
    facebook: string;
    twitter: string;
    bitcointalk: string;
    github: string;
    telegram: string;
    whitepaper: string;
    description: string;
  };
}

export interface TokenTransfer {
  transaction_hash: string;
  block_number: number;
  timestamp: number;
  from: string;
  to: string;
  value: string;
  token_id?: string;  // For ERC721/ERC1155
  amount?: string;    // For ERC1155
}

export interface TokenHolder {
  address: string;
  balance: string;
  percentage: number;
  token_count?: number;  // For ERC721/ERC1155
}

export interface TokenContract {
  address: string;
  name: string;
  compiler_version: string;
  optimization: boolean;
  source_code: string;
  abi: string;
  creation_transaction: string;
  implementation?: string;  // For proxy contracts
}

export type TokenType = 'ERC20' | 'ERC721' | 'ERC1155' | 'CUSTOM';

export interface TokenStats {
  unique_holders: number;
  transfers_24h: number;
  active_wallets_24h: number;
  volume_24h: string;
  circulating_supply: string;
  market_cap: string;
  fully_diluted_market_cap: string;
}

// Token API calls
export const createToken = async (request: CreateTokenRequest): Promise<Token> => {
  return apiClient.post('/api/v1/tokens/create', request);
};

export const listTokens = async (): Promise<Token[]> => {
  return apiClient.get('/api/v1/tokens');
};

export const getToken = async (tokenId: string): Promise<Token> => {
  return apiClient.get(`/api/v1/tokens/${tokenId}`);
};

export const transferTokens = async (request: TokenTransferRequest): Promise<void> => {
  return apiClient.post('/api/v1/tokens/transfer', request);
};

export const burnTokens = async (request: TokenBurnRequest): Promise<void> => {
  return apiClient.post('/api/v1/tokens/burn', request);
};

export const mintTokens = async (request: TokenMintRequest): Promise<void> => {
  return apiClient.post('/api/v1/tokens/mint', request);
};

export const manageTokenPermissions = async (
  tokenId: string,
  request: TokenPermissionRequest
): Promise<void> => {
  return apiClient.post(`/api/v1/tokens/${tokenId}/permissions`, request);
};

export const getTokenAnalytics = async (tokenId: string): Promise<TokenAnalytics> => {
  return apiClient.get(`/api/v1/tokens/${tokenId}/analytics`);
};

class TokensAPI {
  async getTokenInfo(address: string): Promise<TokenInfo> {
    return explorerClient.get(`/tokens/${address}`);
  }

  async getTokenTransfers(
    address: string,
    params?: {
      page?: number;
      limit?: number;
      from?: string;
      to?: string;
      start_time?: number;
      end_time?: number;
    }
  ): Promise<{
    transfers: TokenTransfer[];
    pagination: {
      total: number;
      page: number;
      limit: number;
      pages: number;
    };
  }> {
    return explorerClient.get(`/tokens/${address}/transfers`, { params });
  }

  async getTokenHolders(
    address: string,
    params?: {
      page?: number;
      limit?: number;
      min_balance?: string;
    }
  ): Promise<{
    holders: TokenHolder[];
    pagination: {
      total: number;
      page: number;
      limit: number;
      pages: number;
    };
  }> {
    return explorerClient.get(`/tokens/${address}/holders`, { params });
  }

  async getTokenContract(address: string): Promise<TokenContract> {
    return explorerClient.get(`/tokens/${address}/contract`);
  }

  async getTokenType(address: string): Promise<{
    type: TokenType;
    supports: string[];
  }> {
    return explorerClient.get(`/tokens/${address}/type`);
  }

  async getTokenStats(address: string): Promise<TokenStats> {
    return explorerClient.get(`/tokens/${address}/stats`);
  }

  async getTopTokens(
    params?: {
      type?: TokenType;
      sort_by?: 'volume' | 'market_cap' | 'holders' | 'transfers';
      order?: 'asc' | 'desc';
      page?: number;
      limit?: number;
    }
  ): Promise<{
    tokens: TokenInfo[];
    pagination: {
      total: number;
      page: number;
      limit: number;
      pages: number;
    };
  }> {
    return explorerClient.get('/tokens', { params });
  }

  async searchTokens(
    query: string,
    params?: {
      type?: TokenType;
      verified_only?: boolean;
      page?: number;
      limit?: number;
    }
  ): Promise<{
    tokens: TokenInfo[];
    pagination: {
      total: number;
      page: number;
      limit: number;
      pages: number;
    };
  }> {
    return explorerClient.get('/tokens/search', {
      params: { query, ...params }
    });
  }

  async getTokenInventory(
    token_address: string,
    owner_address: string,
    params?: {
      page?: number;
      limit?: number;
    }
  ): Promise<{
    tokens: Array<{
      token_id: string;
      amount?: string;
      metadata?: any;
    }>;
    pagination: {
      total: number;
      page: number;
      limit: number;
      pages: number;
    };
  }> {
    return explorerClient.get(
      `/tokens/${token_address}/inventory/${owner_address}`,
      { params }
    );
  }

  async getTokenMetadata(
    token_address: string,
    token_id: string
  ): Promise<any> {
    return explorerClient.get(
      `/tokens/${token_address}/metadata/${token_id}`
    );
  }

  // Websocket subscription for token updates
  subscribeToTokenUpdates(
    token_address: string,
    callback: (update: {
      type: 'transfer' | 'mint' | 'burn' | 'approval';
      data: any;
    }) => void
  ): () => void {
    const ws = new WebSocket(
      `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${
        window.location.host
      }/ws/tokens/${token_address}`
    );

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      callback(data);
    };

    return () => ws.close();
  }
}

export const tokensAPI = new TokensAPI(); 