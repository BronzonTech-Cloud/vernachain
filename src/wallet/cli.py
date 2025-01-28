import argparse
import json
from typing import Optional
from .wallet import Wallet
from ..networking.node import Node

class WalletCLI:
    """CLI interface for Vernachain wallet operations."""
    
    def __init__(self):
        self.wallet = Wallet()
        self.node: Optional[Node] = None
        
    def create_address(self, args):
        """Create a new wallet address."""
        address = self.wallet.create_address(args.label)
        print(f"Created new address: {address}")
        if args.label:
            print(f"Label: {args.label}")
            
    def list_addresses(self, args):
        """List all addresses in wallet."""
        addresses = self.wallet.list_addresses()
        print("\nWallet Addresses:")
        print("-" * 80)
        for addr in addresses:
            print(f"Address: {addr['address']}")
            if addr['label']:
                print(f"Label: {addr['label']}")
            print(f"Balance: {addr['balance']} VERNA")
            print(f"Staked: {addr['stake']} VERNA")
            print("-" * 80)
            
    def send_transaction(self, args):
        """Send a transaction."""
        try:
            tx = self.wallet.create_transaction(
                args.from_address,
                args.to_address,
                float(args.amount),
                args.data
            )
            
            if self.node:
                # Send to network if connected
                self.node.broadcast_transaction(tx)
                print("Transaction sent to network")
            else:
                print("Warning: Not connected to network, transaction created but not broadcast")
                
            print("\nTransaction Details:")
            print(json.dumps(tx, indent=2))
            
        except ValueError as e:
            print(f"Error: {e}")
            
    def stake_tokens(self, args):
        """Stake tokens for PoS."""
        try:
            tx = self.wallet.stake_tokens(args.address, float(args.amount))
            
            if self.node:
                self.node.broadcast_transaction(tx)
                print("Stake transaction sent to network")
            else:
                print("Warning: Not connected to network, transaction created but not broadcast")
                
            print("\nStake Transaction Details:")
            print(json.dumps(tx, indent=2))
            
        except ValueError as e:
            print(f"Error: {e}")
            
    def unstake_tokens(self, args):
        """Unstake tokens from PoS."""
        try:
            tx = self.wallet.unstake_tokens(args.address, float(args.amount))
            
            if self.node:
                self.node.broadcast_transaction(tx)
                print("Unstake transaction sent to network")
            else:
                print("Warning: Not connected to network, transaction created but not broadcast")
                
            print("\nUnstake Transaction Details:")
            print(json.dumps(tx, indent=2))
            
        except ValueError as e:
            print(f"Error: {e}")
            
    def get_balance(self, args):
        """Get balance for an address."""
        try:
            balance = self.wallet.get_balance(args.address)
            stake = self.wallet.get_stake(args.address)
            print(f"\nAddress: {args.address}")
            print(f"Balance: {balance} VERNA")
            print(f"Staked: {stake} VERNA")
            print(f"Total: {balance + stake} VERNA")
        except ValueError as e:
            print(f"Error: {e}")
            
    def connect_node(self, args):
        """Connect to a Vernachain node."""
        self.node = Node(args.host, args.port)
        try:
            self.node.start()
            print(f"Connected to node at {args.host}:{args.port}")
        except Exception as e:
            print(f"Failed to connect to node: {e}")
            self.node = None

def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Vernachain Wallet CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Create address
    create_parser = subparsers.add_parser("create", help="Create new address")
    create_parser.add_argument("-l", "--label", help="Label for the address")
    
    # List addresses
    subparsers.add_parser("list", help="List addresses")
    
    # Send transaction
    send_parser = subparsers.add_parser("send", help="Send transaction")
    send_parser.add_argument("from_address", help="Sender address")
    send_parser.add_argument("to_address", help="Recipient address")
    send_parser.add_argument("amount", help="Amount to send")
    send_parser.add_argument("-d", "--data", help="Transaction data", default="")
    
    # Stake tokens
    stake_parser = subparsers.add_parser("stake", help="Stake tokens")
    stake_parser.add_argument("address", help="Address to stake from")
    stake_parser.add_argument("amount", help="Amount to stake")
    
    # Unstake tokens
    unstake_parser = subparsers.add_parser("unstake", help="Unstake tokens")
    unstake_parser.add_argument("address", help="Address to unstake from")
    unstake_parser.add_argument("amount", help="Amount to unstake")
    
    # Get balance
    balance_parser = subparsers.add_parser("balance", help="Get address balance")
    balance_parser.add_argument("address", help="Address to check")
    
    # Connect to node
    connect_parser = subparsers.add_parser("connect", help="Connect to node")
    connect_parser.add_argument("--host", default="localhost", help="Node host")
    connect_parser.add_argument("--port", type=int, default=5000, help="Node port")
    
    args = parser.parse_args()
    cli = WalletCLI()
    
    if args.command == "create":
        cli.create_address(args)
    elif args.command == "list":
        cli.list_addresses(args)
    elif args.command == "send":
        cli.send_transaction(args)
    elif args.command == "stake":
        cli.stake_tokens(args)
    elif args.command == "unstake":
        cli.unstake_tokens(args)
    elif args.command == "balance":
        cli.get_balance(args)
    elif args.command == "connect":
        cli.connect_node(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 