import { VernachainClient, TransactionRequest, CrossShardTransferRequest } from '../src';

async function main() {
    const client = new VernachainClient({
        nodeUrl: 'http://localhost:8545',
        apiKey: 'your-api-key'
    });

    try {
        // Create a cross-shard transfer
        const transferRequest: CrossShardTransferRequest = {
            from_shard: 0,
            to_shard: 1,
            transaction: {
                sender: '0x1234...',
                recipient: '0x5678...',
                amount: 10.0,
                shard_id: 0,
                gas_price: 1.5,
                gas_limit: 21000
            }
        };

        // Initiate the transfer
        const transfer = await client.initiateCrossShardTransfer(transferRequest);
        console.log(`Cross-shard transfer initiated: ${transfer.transfer_id}`);
        console.log(`Status: ${transfer.status}`);

        // Monitor transfer status
        while (!['completed', 'failed'].includes(transfer.status)) {
            await new Promise(resolve => setTimeout(resolve, 5000)); // Wait 5 seconds

            // Get latest blocks from both shards
            const sourceBlock = await client.getLatestBlock(transfer.from_shard);
            const targetBlock = await client.getLatestBlock(transfer.to_shard);

            console.log(`Source shard block: ${sourceBlock.number}`);
            console.log(`Target shard block: ${targetBlock.number}`);

            // Check transaction inclusion
            [sourceBlock, targetBlock].forEach(block => {
                block.transactions.forEach(tx => {
                    if (tx.hash === transfer.transaction.hash) {
                        console.log(`Transaction found in block ${block.number} of shard ${block.shard_id}`);
                        console.log(`Transaction status: ${tx.status}`);
                    }
                });
            });
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

main(); 