import asyncio
from vernachain_sdk import VernachainClient
from vernachain_sdk.models import TransactionRequest, ContractDeployRequest

async def main():
    # Initialize client
    async with VernachainClient(
        node_url="http://localhost:8545",
        api_key="your-api-key"
    ) as client:
        try:
            # Create a transaction
            tx = await client.create_transaction(
                TransactionRequest(
                    sender="0x1234...",
                    recipient="0x5678...",
                    amount=1.0,
                    shard_id=0
                )
            )
            print(f"Transaction created: {tx.hash}")

            # Get latest block
            block = await client.get_latest_block(shard_id=0)
            print(f"Latest block: {block.number}")

            # Deploy a smart contract
            contract = await client.deploy_contract(
                ContractDeployRequest(
                    contract_type="ERC20",
                    params={
                        "name": "MyToken",
                        "symbol": "MTK",
                        "decimals": 18,
                        "total_supply": 1000000
                    },
                    shard_id=0
                )
            )
            print(f"Contract deployed at: {contract.address}")

            # Subscribe to new blocks
            block_queue = await client.subscribe_blocks(shard_id=0)
            
            # Process new blocks for 30 seconds
            try:
                async with asyncio.timeout(30):
                    while True:
                        block = await block_queue.get()
                        print(f"New block received: {block.number}")
                        print(f"Transactions: {len(block.transactions)}")
            except asyncio.TimeoutError:
                print("Block subscription demo completed")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 