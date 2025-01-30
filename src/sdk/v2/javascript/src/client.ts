import axios, { AxiosInstance } from 'axios';
import WebSocket from 'ws';
import { EventEmitter } from 'events';
import {
  Transaction,
  Block,
  SmartContract,
  Validator,
  CrossShardTransfer,
  BridgeTransfer,
  TransactionRequest,
  ContractDeployRequest,
  CrossShardTransferRequest,
  BridgeTransferRequest,
  TransactionSchema,
  BlockSchema,
  SmartContractSchema,
  ValidatorSchema,
  CrossShardTransferSchema,
  BridgeTransferSchema,
} from './types';
import { Contract } from 'ethers';
import { JsonRpcProvider, Provider, ContractRunner } from 'ethers';

export class VernachainError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'VernachainError';
  }
}

export class ValidationError extends VernachainError {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

export class NetworkError extends VernachainError {
  constructor(message: string) {
    super(message);
    this.name = 'NetworkError';
  }
}

export class AuthenticationError extends VernachainError {
  constructor(message: string) {
    super(message);
    this.name = 'AuthenticationError';
  }
}

export class VernachainClient extends EventEmitter implements ContractRunner {
  private readonly client: AxiosInstance;
  private readonly wsBaseUrl: string;
  private readonly baseUrl: string;
  private readonly apiKey?: string;
  public provider: Provider;

  constructor(config: { nodeUrl: string; apiKey?: string }) {
    super();
    this.provider = new JsonRpcProvider(config.nodeUrl);
    this.client = axios.create({
      baseURL: config.nodeUrl.replace(/\/$/, ''),
      headers: config.apiKey ? { Authorization: `Bearer ${config.apiKey}` } : {},
    });
    this.wsBaseUrl = config.nodeUrl.replace(/^http/, 'ws').replace(/\/$/, '');
    this.baseUrl = config.nodeUrl.replace(/\/$/, '');
    this.apiKey = config.apiKey;

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      response => response,
      error => {
        if (error.response?.status === 401) {
          throw new AuthenticationError('Invalid API key');
        }
        if (error.response?.status >= 400) {
          throw new NetworkError(
            `API request failed: ${error.response?.data?.message || 'Unknown error'}`
          );
        }
        throw new NetworkError(`Network request failed: ${error.message}`);
      }
    );
  }

  private async request<T>(method: string, endpoint: string, body?: any): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Transaction Methods
  async createTransaction(request: TransactionRequest): Promise<Transaction> {
    const response = await this.client.post('/api/v1/transactions', request);
    return TransactionSchema.parse(response.data);
  }

  async getTransaction(txHash: string): Promise<Transaction> {
    const response = await this.client.get(`/api/v1/transactions/${txHash}`);
    return TransactionSchema.parse(response.data);
  }

  // Block Methods
  async getBlock(blockNumber: number, shardId: number = 0): Promise<Block> {
    const response = await this.client.get(
      `/api/v1/blocks/${blockNumber}?shard_id=${shardId}`
    );
    return BlockSchema.parse(response.data);
  }

  async getLatestBlock(shardId: number): Promise<Block> {
    return this.request('GET', `/api/v1/blocks/latest?shard_id=${shardId}`);
  }

  // Smart Contract Methods
  async deployContract(request: ContractDeployRequest): Promise<SmartContract> {
    const response = await this.client.post('/api/v1/contracts', request);
    return SmartContractSchema.parse(response.data);
  }

  async callContract(
    contractAddress: string,
    method: string,
    params: Record<string, unknown>
  ): Promise<unknown> {
    const response = await this.client.post(`/api/v1/contracts/${contractAddress}/call`, {
      method,
      params,
    });
    return response.data;
  }

  // Cross-Shard Operations
  async initiateCrossShardTransfer(request: CrossShardTransferRequest): Promise<CrossShardTransfer> {
    return this.request('POST', '/api/v1/cross-shard/transfer', request);
  }

  // WebSocket Subscriptions
  subscribeToBlocks(shardId: number = 0): void {
    const ws = new WebSocket(`${this.wsBaseUrl}/ws/blocks?shard_id=${shardId}`);

    ws.on('message', (data: string) => {
      try {
        const block = BlockSchema.parse(JSON.parse(data));
        this.emit('block', block);
      } catch (error) {
        this.emit('error', new ValidationError('Invalid block data received'));
      }
    });

    ws.on('error', (error: Error) => {
      this.emit('error', new NetworkError(`WebSocket error: ${error.message}`));
    });
  }

  subscribeToTransactions(shardId: number = 0): void {
    const ws = new WebSocket(`${this.wsBaseUrl}/ws/transactions?shard_id=${shardId}`);

    ws.on('message', (data: string) => {
      try {
        const transaction = TransactionSchema.parse(JSON.parse(data));
        this.emit('transaction', transaction);
      } catch (error) {
        this.emit('error', new ValidationError('Invalid transaction data received'));
      }
    });

    ws.on('error', (error: Error) => {
      this.emit('error', new NetworkError(`WebSocket error: ${error.message}`));
    });
  }

  // Validator Operations
  async getValidatorSet(shardId: number = 0): Promise<Validator[]> {
    const response = await this.client.get(`/api/v1/validators?shard_id=${shardId}`);
    return response.data.validators.map((v: unknown) => ValidatorSchema.parse(v));
  }

  async stake(amount: number, validatorAddress: string): Promise<unknown> {
    const response = await this.client.post('/api/v1/stake', {
      amount,
      validator_address: validatorAddress,
    });
    return response.data;
  }

  // Bridge Operations
  async bridgeTransfer(request: BridgeTransferRequest): Promise<BridgeTransfer> {
    const response = await this.client.post('/api/v1/bridge/transfer', request);
    return BridgeTransferSchema.parse(response.data);
  }

  public async loadContract(address: string, abi: any[]): Promise<Contract> {
    return new Contract(address, abi, this.provider);
  }

  public async waitForTransaction(txHash: string) {
    return await this.provider.waitForTransaction(txHash);
  }

  public async getBridgeTransferStatus(transferId: string) {
    const response = await this.client.get(`/bridge/transfers/${transferId}`);
    return response.data;
  }

  public async getPendingBridgeTransfers(chain: string) {
    const response = await this.client.get(`/bridge/transfers/pending/${chain}`);
    return response.data;
  }

  public async unlockTokens(params: {
    bridge_transfer_id: string;
    proof: Record<string, any>;
    shard_id: number;
    gas_price: number;
    gas_limit: number;
  }) {
    const response = await this.client.post('/bridge/unlock', params);
    return response.data;
  }
}