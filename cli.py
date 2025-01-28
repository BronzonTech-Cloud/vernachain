#!/usr/bin/env python3

import argparse
import json
import sys
import time
from src.networking.node import Node
from src.networking.bootstrap_node import BootstrapNode
from src.blockchain.transaction import Transaction


class VernaChainCLI:
    def __init__(self):
        """Initialize the CLI."""
        self.node = None
        self.bootstrap_node = None

    def start_bootstrap(self, args):
        """Start a bootstrap node."""
        self.bootstrap_node = BootstrapNode(args.host, args.port)
        try:
            print(f"Starting bootstrap node on {args.host}:{args.port}")
            self.bootstrap_node.start()
        except KeyboardInterrupt:
            self.bootstrap_node.stop()
            print("\nBootstrap node stopped.")

    def start(self, args):
        """Start a blockchain node."""
        self.node = Node(
            host=args.host,
            port=args.port,
            bootstrap_host=args.bootstrap_host,
            bootstrap_port=args.bootstrap_port,
            num_shards=args.num_shards
        )
        try:
            self.node.start()
            print("Node started successfully. Press Ctrl+C to stop.")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.node.stop()
            print("\nNode stopped.")

    def deploy_contract(self, args):
        """Deploy a smart contract."""
        if not self.node:
            print("Node not started. Please start the node first.")
            return
            
        try:
            with open(args.file, 'r') as f:
                code = f.read()
                
            constructor_args = json.loads(args.args) if args.args else None
            address = self.node.blockchain.deploy_contract(
                code,
                constructor_args,
                args.sender,
                float(args.value)
            )
            
            if address:
                print(f"Contract deployed successfully")
                print(f"Contract address: {address}")
                print("\nContract ABI:")
                contract_state = self.node.blockchain.get_contract_state(address)
                print(json.dumps(contract_state["abi"], indent=2))
            else:
                print("Failed to deploy contract")
                
        except Exception as e:
            print(f"Error deploying contract: {e}")

    def call_contract(self, args):
        """Call a smart contract function."""
        if not self.node:
            print("Node not started. Please start the node first.")
            return
            
        try:
            function_args = json.loads(args.args) if args.args else None
            result = self.node.blockchain.call_contract(
                args.address,
                args.function,
                function_args,
                args.sender,
                float(args.value)
            )
            
            print(f"Function call successful")
            print(f"Result: {result}")
            
            # Show updated contract state
            print("\nUpdated contract state:")
            contract_state = self.node.blockchain.get_contract_state(args.address)
            print(json.dumps(contract_state, indent=2))
            
        except Exception as e:
            print(f"Error calling contract: {e}")

    def get_contract(self, args):
        """Get information about a smart contract."""
        if not self.node:
            print("Node not started. Please start the node first.")
            return
            
        contract_state = self.node.blockchain.get_contract_state(args.address)
        if contract_state:
            print(json.dumps(contract_state, indent=2))
        else:
            print(f"No contract found at address {args.address}")

    def connect(self, args):
        """Connect to a peer node."""
        if not self.node:
            print("Node not started. Please start the node first.")
            return
            
        if self.node.connect_to_peer(args.host, args.port):
            print(f"Successfully connected to peer {args.host}:{args.port}")
        else:
            print("Failed to connect to peer")

    def stake(self, args):
        """Stake tokens to become a validator."""
        if not self.node:
            print("Node not started. Please start the node first.")
            return
            
        if self.node.blockchain.stake_tokens(args.address, args.amount):
            # Assign validator to a shard
            if self.node.blockchain.assign_validator_to_shard(args.address):
                print(f"Successfully staked {args.amount} tokens for {args.address}")
                print(json.dumps(self.node.blockchain.get_validator_info(args.address), indent=2))
            else:
                print("Failed to assign validator to a shard")
        else:
            print("Failed to stake tokens. Make sure you have enough balance.")

    def unstake(self, args):
        """Remove stake and validator status."""
        if not self.node:
            print("Node not started. Please start the node first.")
            return
            
        if self.node.blockchain.unstake_tokens(args.address):
            print(f"Successfully unstaked tokens for {args.address}")
        else:
            print("Failed to unstake tokens. Address might not be a validator.")

    def create_block(self, args):
        """Create a new block as a validator."""
        if not self.node:
            print("Node not started. Please start the node first.")
            return
            
        block = self.node.blockchain.create_block(args.address)
        if block:
            self.node.broadcast_block(block)
            print(f"Successfully created block {block.index}")
            print(json.dumps(block.to_dict(), indent=2))
        else:
            print("Failed to create block. Make sure you are an active validator and it's your turn.")

    def transaction(self, args):
        """Create a new transaction."""
        if not self.node:
            print("Node not started. Please start the node first.")
            return
            
        transaction = Transaction(args.sender, args.receiver, float(args.amount))
        if self.node.blockchain.add_transaction(transaction):
            self.node.broadcast_transaction(transaction)
            print("Transaction added to pool")
            print(json.dumps(transaction.to_dict(), indent=2))
            
            # Show shard information
            sender_shard = self.node.blockchain.master_chain.get_shard_for_address(args.sender)
            receiver_shard = self.node.blockchain.master_chain.get_shard_for_address(args.receiver)
            print(f"\nTransaction details:")
            print(f"Sender shard: {sender_shard}")
            print(f"Receiver shard: {receiver_shard}")
            if sender_shard != receiver_shard:
                print("This is a cross-shard transaction")
        else:
            print("Failed to add transaction")

    def chain(self, args):
        """Display the current blockchain."""
        if not self.node:
            print("Node not started. Please start the node first.")
            return
            
        chain_data = self.node.blockchain.to_dict()
        print(json.dumps(chain_data, indent=2))

    def pending(self, args):
        """Display pending transactions."""
        if not self.node:
            print("Node not started. Please start the node first.")
            return
            
        transactions = self.node.blockchain.transaction_pool.get_transactions()
        if transactions:
            print(json.dumps([t.to_dict() for t in transactions], indent=2))
        else:
            print("No pending transactions")

    def balance(self, args):
        """Get the balance of an address."""
        if not self.node:
            print("Node not started. Please start the node first.")
            return
            
        balance = self.node.blockchain.get_balance(args.address)
        print(f"Balance for {args.address}: {balance}")
        
        # Show validator info if applicable
        validator_info = self.node.blockchain.get_validator_info(args.address)
        if validator_info:
            print("\nValidator information:")
            print(json.dumps(validator_info, indent=2))
            
        # Show shard information
        shard_id = self.node.blockchain.master_chain.get_shard_for_address(args.address)
        print(f"\nAddress belongs to shard: {shard_id}")

    def validators(self, args):
        """List active validators."""
        if not self.node:
            print("Node not started. Please start the node first.")
            return
            
        validators = self.node.blockchain.get_active_validators()
        if validators:
            print(json.dumps(validators, indent=2))
        else:
            print("No active validators")

    def shards(self, args):
        """Display information about all shards."""
        if not self.node:
            print("Node not started. Please start the node first.")
            return
            
        shard_info = self.node.blockchain.get_all_shard_info()
        if shard_info:
            print(json.dumps(shard_info, indent=2))
        else:
            print("No shard information available")

    def shard(self, args):
        """Display information about a specific shard."""
        if not self.node:
            print("Node not started. Please start the node first.")
            return
            
        shard_info = self.node.blockchain.get_shard_info(args.shard_id)
        if shard_info:
            print(json.dumps(shard_info, indent=2))
        else:
            print(f"No information available for shard {args.shard_id}")

    def peers(self, args):
        """List connected peers."""
        if not self.node:
            print("Node not started. Please start the node first.")
            return
            
        if self.node.peers:
            for peer in self.node.peers:
                print(f"{peer[0]}:{peer[1]}")
        else:
            print("No connected peers")


def main():
    """Main CLI entry point."""
    cli = VernaChainCLI()
    
    parser = argparse.ArgumentParser(description="VernaChain CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Bootstrap node command
    bootstrap_parser = subparsers.add_parser("bootstrap", help="Start a bootstrap node")
    bootstrap_parser.add_argument("--host", default="localhost", help="Host address to bind to")
    bootstrap_parser.add_argument("--port", type=int, default=5000, help="Port to listen on")
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start a blockchain node")
    start_parser.add_argument("--host", default="localhost", help="Host address to bind to")
    start_parser.add_argument("--port", type=int, default=5001, help="Port to listen on")
    start_parser.add_argument("--bootstrap-host", help="Bootstrap node host address")
    start_parser.add_argument("--bootstrap-port", type=int, help="Bootstrap node port")
    start_parser.add_argument("--num-shards", type=int, default=4, help="Number of shards to create")
    
    # Deploy contract command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy a smart contract")
    deploy_parser.add_argument("file", help="Contract source file")
    deploy_parser.add_argument("--args", help="Constructor arguments as JSON array")
    deploy_parser.add_argument("--sender", required=True, help="Deployer's address")
    deploy_parser.add_argument("--value", default="0.0", help="Amount to send with deployment")
    
    # Call contract command
    call_parser = subparsers.add_parser("call", help="Call a smart contract function")
    call_parser.add_argument("address", help="Contract address")
    call_parser.add_argument("function", help="Function name to call")
    call_parser.add_argument("--args", help="Function arguments as JSON array")
    call_parser.add_argument("--sender", required=True, help="Caller's address")
    call_parser.add_argument("--value", default="0.0", help="Amount to send with call")
    
    # Get contract command
    get_contract_parser = subparsers.add_parser("contract", help="Get contract information")
    get_contract_parser.add_argument("address", help="Contract address")
    
    # Connect command
    connect_parser = subparsers.add_parser("connect", help="Connect to a peer")
    connect_parser.add_argument("host", help="Peer host address")
    connect_parser.add_argument("port", type=int, help="Peer port")
    
    # Stake command
    stake_parser = subparsers.add_parser("stake", help="Stake tokens to become a validator")
    stake_parser.add_argument("address", help="Address to stake tokens from")
    stake_parser.add_argument("amount", type=float, help="Amount to stake")
    
    # Unstake command
    unstake_parser = subparsers.add_parser("unstake", help="Remove stake and validator status")
    unstake_parser.add_argument("address", help="Validator address to unstake")
    
    # Create block command
    create_parser = subparsers.add_parser("create", help="Create a new block as a validator")
    create_parser.add_argument("address", help="Validator's address")
    
    # Transaction command
    tx_parser = subparsers.add_parser("transaction", help="Create a new transaction")
    tx_parser.add_argument("sender", help="Sender's address")
    tx_parser.add_argument("receiver", help="Receiver's address")
    tx_parser.add_argument("amount", type=float, help="Amount to transfer")
    
    # Chain command
    subparsers.add_parser("chain", help="Display the blockchain")
    
    # Pending command
    subparsers.add_parser("pending", help="Display pending transactions")
    
    # Balance command
    balance_parser = subparsers.add_parser("balance", help="Get address balance")
    balance_parser.add_argument("address", help="Address to check")
    
    # Validators command
    subparsers.add_parser("validators", help="List active validators")
    
    # Shards command
    subparsers.add_parser("shards", help="Display information about all shards")
    
    # Shard command
    shard_parser = subparsers.add_parser("shard", help="Display information about a specific shard")
    shard_parser.add_argument("shard_id", type=int, help="ID of the shard to display")
    
    # Peers command
    subparsers.add_parser("peers", help="List connected peers")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Call the appropriate method based on the command
    command_method = getattr(cli, args.command if args.command != "bootstrap" else "start_bootstrap")
    command_method(args)


if __name__ == "__main__":
    main()