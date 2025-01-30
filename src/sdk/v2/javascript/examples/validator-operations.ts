import { VernachainClient } from '../src';

async function main() {
    const client = new VernachainClient({
        nodeUrl: 'http://localhost:8545',
        apiKey: 'your-api-key'
    });

    try {
        // Get validator set for shard 0
        const validators = await client.getValidatorSet(0);
        console.log(`Found ${validators.length} validators in shard 0`);

        // Print validator details
        validators.forEach(validator => {
            console.log(`\nValidator: ${validator.address}`);
            console.log(`Stake: ${validator.stake} VRN`);
            console.log(`Reputation: ${validator.reputation}`);
            console.log(`Active: ${validator.is_active}`);
            console.log(`Commission Rate: ${validator.commission_rate ?? 0.0}%`);
            console.log(`Total Blocks Validated: ${validator.total_blocks_validated}`);

            if (validator.delegators) {
                console.log(`Delegators: ${validator.delegators.length}`);
                const totalDelegated = validator.delegators.reduce(
                    (sum: number, d: { amount?: number }) => sum + (d.amount ?? 0),
                    0
                );
                console.log(`Total Delegated: ${totalDelegated} VRN`);
            }
        });

        // Find the validator with highest reputation
        const bestValidator = validators.reduce(
            (best, current) => current.reputation > best.reputation ? current : best,
            validators[0]
        );
        console.log(`\nBest validator by reputation: ${bestValidator.address}`);

        // Stake tokens on the best validator
        const stakeAmount = 100.0; // VRN tokens
        interface StakeResult { transactionHash: string }
        const stakeResult = await client.stake(stakeAmount, bestValidator.address) as StakeResult;
        console.log(`\nStaked ${stakeAmount} VRN on validator ${bestValidator.address}`);
        console.log(`Transaction hash: ${stakeResult.transactionHash}`);

        // Monitor validator performance
        console.log('\nMonitoring validator performance...');
        for (let i = 0; i < 3; i++) {
            await new Promise(resolve => setTimeout(resolve, 10000)); // Wait 10 seconds

            const updatedValidators = await client.getValidatorSet(0);
            const updatedValidator = updatedValidators.find(
                v => v.address === bestValidator.address
            );

            if (updatedValidator) {
                console.log(`\nValidator ${updatedValidator.address} status:`);
                console.log(`Total Blocks Validated: ${updatedValidator.total_blocks_validated}`);
                console.log(`Current Reputation: ${updatedValidator.reputation}`);
                console.log(`Total Stake: ${updatedValidator.stake} VRN`);
            }
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

main();
