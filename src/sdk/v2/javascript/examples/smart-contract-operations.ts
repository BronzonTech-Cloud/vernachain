import { VernachainClient } from '../src';

async function main() {
    const client = new VernachainClient({
        nodeUrl: 'http://localhost:8545',
        apiKey: 'your-api-key'
    });

    try {
        // Example contract ABI (ERC20 token)
        const contractAbi = [
            {
                "constant": true,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": false,
                "inputs": [
                    {"name": "_to", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "transfer",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            }
        ];

        const contractAddress = '0x1234...'; // Your contract address
        const contract = await client.loadContract(contractAddress, contractAbi);

        // Read operation (no gas needed)
        const balance = await contract.balanceOf('0x5678...');
        console.log(`Token balance: ${balance}`);

        // Write operation (requires gas)
        const transferAmount = '1000000000000000000'; // 1 token with 18 decimals
        const transferResult = await contract.transfer('0x9abc...', transferAmount, {
            from: '0x5678...',
            shard_id: 0,
            gas_price: 1.5,
            gas_limit: 60000
        });

        console.log(`Transfer transaction hash: ${transferResult.transaction_hash}`);
        console.log(`Transaction status: ${transferResult.status}`);

        // Wait for transaction confirmation
        const receipt = await client.waitForTransaction(transferResult.transaction_hash);
        if (receipt) {
            console.log(`Transaction confirmed in block: ${receipt.blockNumber}`);
            console.log(`Gas used: ${receipt.gasUsed}`);

            const events = await contract.getPastEvents('Transfer', {
                fromBlock: receipt.blockNumber,
                toBlock: receipt.blockNumber
            });
        }

    } catch (error) {
        console.error('Error:', error);
    }
}

main(); 