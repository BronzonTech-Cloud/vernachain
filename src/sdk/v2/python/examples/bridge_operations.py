import asyncio
from vernachain_sdk import VernachainClient
from vernachain_sdk.models import BridgeTransferRequest

async def main():
    async with VernachainClient(
        node_url="http://localhost:8545",
        api_key="your-api-key"
    ) as client:
        try:
            # Create a bridge transfer to Ethereum
            transfer_request = BridgeTransferRequest(
                target_chain="ethereum",
                amount=5.0,
                recipient="0xETH_ADDRESS...",
                gas_limit=100000
            )
            
            # Initiate the bridge transfer
            transfer = await client.bridge_transfer(transfer_request)
            print(f"Bridge transfer initiated: {transfer.transfer_id}")
            print(f"From: {transfer.sender} (Vernachain)")
            print(f"To: {transfer.recipient} (Ethereum)")
            print(f"Amount: {transfer.amount}")
            print(f"Status: {transfer.status}")
            
            # Monitor the transfer status
            while transfer.status not in ["completed", "failed"]:
                await asyncio.sleep(10)  # Check every 10 seconds
                
                # In a real application, you would want to:
                # 1. Get the transfer status from both chains
                # 2. Verify the proof of transfer
                # 3. Handle any required confirmations
                print("\nChecking transfer status...")
                print(f"Current status: {transfer.status}")
                
                if transfer.completed_at:
                    print(f"Completed at: {transfer.completed_at}")
                    if transfer.proof:
                        print("Transfer verified with proof")
                        print(f"Transaction hash on target chain: {transfer.proof.get('target_tx_hash')}")
                
            print("\nFinal transfer status:")
            print(f"Status: {transfer.status}")
            if transfer.status == "completed":
                print("Transfer successfully completed!")
                print(f"Time taken: {transfer.completed_at - transfer.initiated_at}")
            else:
                print("Transfer failed. Please check the error details.")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 