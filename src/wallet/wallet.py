from typing import Dict, List, Optional
from nacl.signing import SigningKey, VerifyKey  # noqa
from nacl.encoding import HexEncoder
import json
import os
import time

class Wallet:
    """Manages cryptographic keys and transactions for a Vernachain wallet."""
    
    def __init__(self, keyfile_path: Optional[str] = None):
        self.keyfile_path = keyfile_path or "wallet.json"
        self.addresses: Dict[str, Dict] = {}
        self._load_wallet()
    
    def create_address(self, label: str = "") -> str:
        """Create a new wallet address."""
        # Generate signing keypair
        signing_key = SigningKey.generate()
        verify_key = signing_key.verify_key
        
        # Create address from public key
        address = verify_key.encode(encoder=HexEncoder).decode()
        
        # Store keys
        self.addresses[address] = {
            "label": label,
            "private_key": signing_key.encode(encoder=HexEncoder).decode(),
            "public_key": verify_key.encode(encoder=HexEncoder).decode(),
            "balance": 0.0,
            "stake": 0.0
        }
        self._save_wallet()
        return address
    
    def get_balance(self, address: str) -> float:
        """Get balance for an address."""
        if address not in self.addresses:
            raise ValueError(f"Address {address} not found in wallet")
        return self.addresses[address]["balance"]
    
    def get_stake(self, address: str) -> float:
        """Get staked amount for an address."""
        if address not in self.addresses:
            raise ValueError(f"Address {address} not found in wallet")
        return self.addresses[address]["stake"]
    
    def sign_transaction(self, address: str, transaction: Dict) -> bytes:
        """Sign a transaction with the private key."""
        if address not in self.addresses:
            raise ValueError(f"Address {address} not found in wallet")
            
        # Get signing key
        private_key = bytes.fromhex(self.addresses[address]["private_key"])
        signing_key = SigningKey(private_key)
        
        # Sign transaction data
        message = json.dumps(transaction, sort_keys=True).encode()
        return signing_key.sign(message)
    
    def stake_tokens(self, address: str, amount: float) -> Dict:
        """Create a staking transaction."""
        if address not in self.addresses:
            raise ValueError(f"Address {address} not found in wallet")
            
        if amount > self.get_balance(address):
            raise ValueError("Insufficient balance for staking")
            
        transaction = {
            "type": "stake",
            "from": address,
            "amount": amount,
            "timestamp": time.time()
        }
        
        signature = self.sign_transaction(address, transaction)
        transaction["signature"] = signature.hex()
        
        # Update local state
        self.addresses[address]["balance"] -= amount
        self.addresses[address]["stake"] += amount
        self._save_wallet()
        
        return transaction
    
    def unstake_tokens(self, address: str, amount: float) -> Dict:
        """Create an unstaking transaction."""
        if address not in self.addresses:
            raise ValueError(f"Address {address} not found in wallet")
            
        if amount > self.get_stake(address):
            raise ValueError("Insufficient staked amount")
            
        transaction = {
            "type": "unstake",
            "from": address,
            "amount": amount,
            "timestamp": time.time()
        }
        
        signature = self.sign_transaction(address, transaction)
        transaction["signature"] = signature.hex()
        
        # Update local state
        self.addresses[address]["stake"] -= amount
        self.addresses[address]["balance"] += amount
        self._save_wallet()
        
        return transaction
    
    def create_transaction(self, from_address: str, to_address: str, 
                         amount: float, data: str = "") -> Dict:
        """Create a new transaction."""
        if from_address not in self.addresses:
            raise ValueError(f"Address {from_address} not found in wallet")
            
        if amount > self.get_balance(from_address):
            raise ValueError("Insufficient balance")
            
        transaction = {
            "type": "transfer",
            "from": from_address,
            "to": to_address,
            "amount": amount,
            "data": data,
            "timestamp": time.time()
        }
        
        signature = self.sign_transaction(from_address, transaction)
        transaction["signature"] = signature.hex()
        
        # Update local state
        self.addresses[from_address]["balance"] -= amount
        self._save_wallet()
        
        return transaction
    
    def list_addresses(self) -> List[Dict]:
        """List all addresses in the wallet."""
        return [{
            "address": addr,
            "label": info["label"],
            "balance": info["balance"],
            "stake": info["stake"]
        } for addr, info in self.addresses.items()]
    
    def _load_wallet(self):
        """Load wallet data from file."""
        if os.path.exists(self.keyfile_path):
            with open(self.keyfile_path, 'r') as f:
                self.addresses = json.load(f)
    
    def _save_wallet(self):
        """Save wallet data to file."""
        with open(self.keyfile_path, 'w') as f:
            json.dump(self.addresses, f, indent=2) 