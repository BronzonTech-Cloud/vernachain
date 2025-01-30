import { VernachainClient } from '../src';

async function main() {
    const client = new VernachainClient({
        nodeUrl: 'http://localhost:8545',
        apiKey: 'your-api-key'
    });

    try {
        // Lock tokens in source chain
        const lockRequest = {
            token_address: '0x1234...', // ERC20 token address
            amount: Number('1000000000000000000'), // Convert to number
            target_chain: 'ethereum',
            recipient: '0x5678...', // recipient address on target chain
            shard_id: 0,
            gas_price: 1.5,
            gas_limit: 100000
        };

        const lockResult = await client.bridgeTransfer(lockRequest);
        console.log(`Tokens locked. Transfer ID: ${lockResult.transfer_id}`);
        console.log(`Status: ${lockResult.status}`);

        // Monitor bridge transfer status
        let bridgeStatus = await client.getBridgeTransferStatus(lockResult.transfer_id);
        while (!['completed', 'failed'].includes(bridgeStatus.status)) {
            console.log(`Bridge transfer status: ${bridgeStatus.status}`);
            console.log(`Confirmations: ${bridgeStatus.confirmations}/${bridgeStatus.required_confirmations}`);
            
            await new Promise(resolve => setTimeout(resolve, 10000)); // Wait 10 seconds
            bridgeStatus = await client.getBridgeTransferStatus(lockResult.transfer_id);
        }

        console.log(`Final bridge transfer status: ${bridgeStatus.status}`);
        if (bridgeStatus.status === 'completed') {
            console.log(`Target chain transaction hash: ${bridgeStatus.target_transaction_hash}`);
        }

        // Example of unlocking tokens (receiving from another chain)
        const pendingTransfers = await client.getPendingBridgeTransfers('ethereum');
        for (const transfer of pendingTransfers) {
            if (transfer.status === 'pending_unlock') {
                const unlockResult = await client.unlockTokens({
                    bridge_transfer_id: transfer.bridge_transfer_id,
                    proof: transfer.proof,
                    shard_id: 0,
                    gas_price: 1.5,
                    gas_limit: 150000
                });
                console.log(`Tokens unlocked. Transaction hash: ${unlockResult.transaction_hash}`);
            }
        }

    } catch (error) {
        console.error('Error:', error);
    }
}

main(); 