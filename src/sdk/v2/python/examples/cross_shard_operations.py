import asyncio
from vernachain_sdk import VernachainClient
from vernachain_sdk.models import TransactionRequest, CrossShardTransferRequest

async def main():
    async with VernachainClient(
        node_url="http://localhost:8545",
        api_key="your-api-key"
    ) as client:
        try:
            # Create a cross-shard transfer
            transfer_request = CrossShardTransferRequest(
                from_shard=0,
                to_shard=1,
                transaction=TransactionRequest(
                    sender="0x1234...",
                    recipient="0x5678...",
                    amount=10.0,
                    shard_id=0,
                    gas_price=1.5,
                    gas_limit=21000
                )
            )
            
            # Initiate the transfer
            transfer = await client.initiate_cross_shard_transfer(transfer_request)
            print(f"Cross-shard transfer initiated: {transfer.transfer_id}")
            print(f"Status: {transfer.status}")
            
            # Monitor transfer status
            while transfer.status not in ["completed", "failed"]:
                # In a real application, you would want to add a delay here
                await asyncio.sleep(5)
                
                # Get the latest block from both shards to check for confirmation
                source_block = await client.get_latest_block(shard_id=transfer.from_shard)
                target_block = await client.get_latest_block(shard_id=transfer.to_shard)
                
                print(f"Source shard block: {source_block.number}")
                print(f"Target shard block: {target_block.number}")
                
                # Check if the transaction is included in any blocks
                for block in [source_block, target_block]:
                    for tx in block.transactions:
                        if tx.hash == transfer.transaction.hash:
                            print(f"Transaction found in block {block.number} of shard {block.shard_id}")
                            print(f"Transaction status: {tx.status}")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 