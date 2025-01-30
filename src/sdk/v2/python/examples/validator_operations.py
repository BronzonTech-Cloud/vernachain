import asyncio
from vernachain_sdk import VernachainClient

async def main():
    async with VernachainClient(
        node_url="http://localhost:8545",
        api_key="your-api-key"
    ) as client:
        try:
            # Get validator set for shard 0
            validators = await client.get_validator_set(shard_id=0)
            print(f"Found {len(validators)} validators in shard 0")
            
            # Print validator details
            for validator in validators:
                print(f"\nValidator: {validator.address}")
                print(f"Stake: {validator.stake} VRN")
                print(f"Reputation: {validator.reputation}")
                print(f"Active: {validator.is_active}")
                print(f"Commission Rate: {validator.commission_rate or 0.0}%")
                
                if validator.delegators:
                    print(f"Delegators: {len(validator.delegators)}")
                    total_delegated = sum(d.get('amount', 0) for d in validator.delegators)
                    print(f"Total Delegated: {total_delegated} VRN")
            
            # Find the validator with the highest reputation
            best_validator = max(validators, key=lambda v: v.reputation)
            print(f"\nBest validator by reputation: {best_validator.address}")
            
            # Stake tokens on the best validator
            stake_amount = 100.0  # VRN tokens
            stake_result = await client.stake(
                amount=stake_amount,
                validator_address=best_validator.address
            )
            print(f"\nStaked {stake_amount} VRN on validator {best_validator.address}")
            print(f"Transaction hash: {stake_result.get('transaction_hash')}")
            
            # Monitor validator performance
            print("\nMonitoring validator performance...")
            for _ in range(3):  # Monitor for 3 intervals
                await asyncio.sleep(10)  # Wait 10 seconds between checks
                
                # Get updated validator info
                validators = await client.get_validator_set(shard_id=0)
                updated_validator = next(
                    v for v in validators 
                    if v.address == best_validator.address
                )
                
                print(f"\nValidator {updated_validator.address} status:")
                print(f"Total Blocks Validated: {updated_validator.total_blocks_validated}")
                print(f"Current Reputation: {updated_validator.reputation}")
                print(f"Total Stake: {updated_validator.stake} VRN")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 