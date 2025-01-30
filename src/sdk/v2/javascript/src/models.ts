import { z } from 'zod';

export const TransactionRequestSchema = z.object({
    sender: z.string(),
    recipient: z.string(),
    amount: z.number(),
    shard_id: z.number(),
    gas_price: z.number().optional(),
    gas_limit: z.number().optional(),
    data: z.record(z.string(), z.any()).optional()
});

export const CrossShardTransferRequestSchema = z.object({
    from_shard: z.number(),
    to_shard: z.number(),
    transaction: TransactionRequestSchema
});

export type TransactionRequest = z.infer<typeof TransactionRequestSchema>;
export type CrossShardTransferRequest = z.infer<typeof CrossShardTransferRequestSchema>;