"""Example usage of the Vernachain Python SDK."""

from vernachain import VernachainSDK

def main():
    # Initialize the SDK
    sdk = VernachainSDK(
        api_url="https://api.vernachain.com",
        api_key="your-api-key-here"
    )

    # Use context manager for automatic cleanup
    with sdk:
        # Get network stats
        stats = sdk.get_network_stats()
        print("Network Stats:", stats)

        # Get active validators
        validators = sdk.get_validators()
        print("Active Validators:", validators)

        # Get balance of an address
        address = "0x1234567890abcdef1234567890abcdef12345678"
        balance = sdk.get_balance(address)
        print(f"Balance of {address}: {balance} VERNA")

        # Send a transaction
        tx_hash = sdk.send_transaction(
            to_address="0xrecipient_address",
            value=1.5,  # amount
            private_key="your-private-key",
            gas_limit=21000  # optional
        )
        print("Transaction sent:", tx_hash)

        # Get transaction details
        tx = sdk.get_transaction(tx_hash)
        print("Transaction details:", tx)

        # Deploy a smart contract
        contract_address = sdk.deploy_contract(
            bytecode="0x608060405234801561001057600080fd5b50610150806100206000396000f3",
            abi={"contract": "abi"},  # Replace with actual ABI
            private_key="your-private-key",
            gas_limit=500000  # optional
        )
        print("Contract deployed at:", contract_address)

        # Call a contract function
        result = sdk.call_contract(
            contract_address=contract_address,
            function_name="balanceOf",
            args=[address],
            abi={"contract": "abi"}  # Replace with actual ABI
        )
        print("Contract call result:", result)

        # Initiate a cross-chain transfer
        bridge_tx = sdk.bridge_transfer(
            from_chain="vernachain",
            to_chain="ethereum",
            token="VERNA",
            amount=0.5,
            to_address="0xeth_recipient_address",
            private_key="your-private-key"
        )
        print("Bridge transfer initiated:", bridge_tx)

        # Get bridge transaction status
        bridge_status = sdk.get_bridge_transaction(bridge_tx)
        print("Bridge transaction status:", bridge_status)

if __name__ == "__main__":
    main() 