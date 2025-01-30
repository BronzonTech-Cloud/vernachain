import { z } from 'zod';

// Base schemas
export const TransactionSchema = z.object({
  hash: z.string(),
  sender: z.string(),
  recipient: z.string(),
  amount: z.number(),
  timestamp: z.date(),
  shard_id: z.number(),
  status: z.string(),
  signature: z.string().optional(),
  nonce: z.number().optional(),
  gas_price: z.number().optional(),
  gas_limit: z.number().optional(),
  data: z.record(z.unknown()).optional(),
});

export const BlockSchema = z.object({
  number: z.number(),
  hash: z.string(),
  previous_hash: z.string(),
  timestamp: z.date(),
  transactions: z.array(TransactionSchema),
  validator: z.string(),
  shard_id: z.number(),
  merkle_root: z.string(),
  state_root: z.string(),
  signature: z.string().optional(),
  size: z.number().optional(),
  gas_used: z.number().optional(),
  gas_limit: z.number().optional(),
});

export const SmartContractSchema = z.object({
  address: z.string(),
  contract_type: z.string(),
  creator: z.string(),
  creation_timestamp: z.date(),
  shard_id: z.number(),
  abi: z.record(z.unknown()),
  bytecode: z.string(),
  state: z.record(z.unknown()).optional(),
  version: z.string().optional(),
});

export const ValidatorSchema = z.object({
  address: z.string(),
  stake: z.number(),
  reputation: z.number(),
  total_blocks_validated: z.number(),
  is_active: z.boolean(),
  last_active: z.date(),
  shard_id: z.number(),
  commission_rate: z.number().optional(),
  delegators: z.array(z.record(z.unknown())).optional(),
});

export const CrossShardTransferSchema = z.object({
  transfer_id: z.string(),
  from_shard: z.number(),
  to_shard: z.number(),
  transaction: TransactionSchema,
  status: z.string(),
  initiated_at: z.date(),
  completed_at: z.date().optional(),
  proof: z.record(z.unknown()).optional(),
});

export const BridgeTransferSchema = z.object({
  transfer_id: z.string(),
  source_chain: z.string(),
  target_chain: z.string(),
  amount: z.number(),
  sender: z.string(),
  recipient: z.string(),
  status: z.string(),
  initiated_at: z.date(),
  completed_at: z.date().optional(),
  proof: z.record(z.unknown()).optional(),
});

// Request schemas
export const TransactionRequestSchema = z.object({
  sender: z.string(),
  recipient: z.string(),
  amount: z.number(),
  shard_id: z.number().default(0),
  gas_price: z.number().optional(),
  gas_limit: z.number().optional(),
  data: z.record(z.unknown()).optional(),
});

export const ContractDeployRequestSchema = z.object({
  contract_type: z.string(),
  params: z.record(z.unknown()),
  shard_id: z.number().default(0),
  gas_limit: z.number().optional(),
});

export const CrossShardTransferRequestSchema = z.object({
  from_shard: z.number(),
  to_shard: z.number(),
  transaction: TransactionRequestSchema,
});

export const BridgeTransferRequestSchema = z.object({
  target_chain: z.string(),
  amount: z.number(),
  recipient: z.string(),
  gas_limit: z.number().optional(),
});

// Type exports
export type Transaction = z.infer<typeof TransactionSchema>;
export type Block = z.infer<typeof BlockSchema>;
export type SmartContract = z.infer<typeof SmartContractSchema>;
export type Validator = z.infer<typeof ValidatorSchema>;
export type CrossShardTransfer = z.infer<typeof CrossShardTransferSchema>;
export type BridgeTransfer = z.infer<typeof BridgeTransferSchema>;
export type TransactionRequest = z.infer<typeof TransactionRequestSchema>;
export type ContractDeployRequest = z.infer<typeof ContractDeployRequestSchema>;
export type CrossShardTransferRequest = z.infer<typeof CrossShardTransferRequestSchema>;
export type BridgeTransferRequest = z.infer<typeof BridgeTransferRequestSchema>; 