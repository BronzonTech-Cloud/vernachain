import asyncio
from vernachain_sdk import VernachainClient
from vernachain_sdk.models import ContractDeployRequest

async def main():
    async with VernachainClient(
        node_url="http://localhost:8545",
        api_key="your-api-key"
    ) as client:
        try:
            # Deploy an ERC20 token contract
            deploy_request = ContractDeployRequest(
                contract_type="ERC20",
                params={
                    "name": "Vernachain Token",
                    "symbol": "VRN",
                    "decimals": 18,
                    "initial_supply": 1_000_000
                },
                shard_id=0,
                gas_limit=5_000_000
            )
            
            contract = await client.deploy_contract(deploy_request)
            print(f"Contract deployed at: {contract.address}")
            print(f"Contract type: {contract.contract_type}")
            print(f"Created by: {contract.creator}")
            
            # Interact with the contract
            # 1. Get total supply
            total_supply = await client.call_contract(
                contract_address=contract.address,
                method="totalSupply",
                params={}
            )
            print(f"\nTotal supply: {total_supply['value']} VRN")
            
            # 2. Transfer tokens
            transfer_result = await client.call_contract(
                contract_address=contract.address,
                method="transfer",
                params={
                    "to": "0x9876...",
                    "amount": 1000
                }
            )
            print(f"\nTransfer transaction hash: {transfer_result['transaction_hash']}")
            
            # 3. Get balance of an address
            balance = await client.call_contract(
                contract_address=contract.address,
                method="balanceOf",
                params={
                    "account": "0x9876..."
                }
            )
            print(f"Balance of recipient: {balance['value']} VRN")
            
            # 4. Approve spending
            approve_result = await client.call_contract(
                contract_address=contract.address,
                method="approve",
                params={
                    "spender": "0x5432...",
                    "amount": 500
                }
            )
            print(f"\nApproval transaction hash: {approve_result['transaction_hash']}")
            
            # 5. Check allowance
            allowance = await client.call_contract(
                contract_address=contract.address,
                method="allowance",
                params={
                    "owner": "0x1234...",
                    "spender": "0x5432..."
                }
            )
            print(f"Spender allowance: {allowance['value']} VRN")
            
            # 6. Get contract events
            # Note: In a real application, you would use WebSocket subscriptions
            # to listen for events in real-time
            print("\nRecent transfer events:")
            events = await client.call_contract(
                contract_address=contract.address,
                method="getPastEvents",
                params={
                    "event": "Transfer",
                    "fromBlock": "latest",
                    "toBlock": "latest"
                }
            )
            
            for event in events.get('events', []):
                print(f"From: {event['from']}")
                print(f"To: {event['to']}")
                print(f"Amount: {event['value']} VRN")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 