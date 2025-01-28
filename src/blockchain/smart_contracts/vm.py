from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import ast
import inspect
import hashlib
import time


@dataclass
class ContractState:
    """Represents the state of a smart contract."""
    address: str
    balance: float = 0.0
    storage: Dict[str, Any] = field(default_factory=dict)
    code: str = ""
    abi: Dict[str, Any] = field(default_factory=dict)


class GasCounter:
    """Tracks gas usage during contract execution."""
    # Gas costs for different operations
    COSTS = {
        'LOAD': 1,
        'STORE': 5,
        'CALL': 10,
        'MATH': 2,
        'TRANSFER': 20,
    }
    
    def __init__(self, gas_limit: int):
        self.gas_limit = gas_limit
        self.gas_used = 0
        
    def charge(self, operation: str, amount: int = 1) -> bool:
        """
        Charge gas for an operation.
        
        Args:
            operation: Type of operation
            amount: Number of operations
            
        Returns:
            bool: True if gas limit not exceeded
        """
        cost = self.COSTS.get(operation, 1) * amount
        if self.gas_used + cost > self.gas_limit:
            raise Exception("Out of gas")
            
        self.gas_used += cost
        return True


class ContractVisitor(ast.NodeVisitor):
    """AST visitor to validate and transform contract code."""
    ALLOWED_BUILTINS = {'len', 'range', 'str', 'int', 'float', 'bool', 'list', 'dict'}
    
    def __init__(self):
        self.errors = []
        self.has_constructor = False
        self.public_functions = set()
        
    def visit_FunctionDef(self, node):
        """Visit function definitions to collect public functions."""
        # Check for constructor
        if node.name == '__init__':
            self.has_constructor = True
            
        # Check for public functions (no underscore prefix)
        if not node.name.startswith('_'):
            self.public_functions.add(node.name)
            
        self.generic_visit(node)
        
    def visit_Call(self, node):
        """Visit function calls to check for unauthorized access."""
        if isinstance(node.func, ast.Name):
            if node.func.id not in self.ALLOWED_BUILTINS:
                self.errors.append(f"Unauthorized function call: {node.func.id}")
        self.generic_visit(node)
        
    def visit_Import(self, node):
        """Disallow import statements."""
        self.errors.append("Import statements are not allowed")
        
    def visit_ImportFrom(self, node):
        """Disallow import from statements."""
        self.errors.append("Import statements are not allowed")


class SmartContractVM:
    """Python-based virtual machine for smart contract execution."""
    def __init__(self, gas_limit: int = 1000000):
        self.contracts: Dict[str, ContractState] = {}
        self.gas_limit = gas_limit
        
    def deploy_contract(self, code: str, constructor_args: List[Any] = None) -> Optional[str]:
        """
        Deploy a new smart contract.
        
        Args:
            code: Contract source code
            constructor_args: Arguments for the constructor
            
        Returns:
            str: Contract address if deployment successful
        """
        try:
            # Parse and validate contract code
            tree = ast.parse(code)
            visitor = ContractVisitor()
            visitor.visit(tree)
            
            if visitor.errors:
                raise Exception(f"Contract validation failed: {visitor.errors}")
                
            # Generate contract address
            address = hashlib.sha256(
                f"{code}{time.time()}".encode()
            ).hexdigest()
            
            # Create contract state
            contract = ContractState(
                address=address,
                code=code,
                abi={
                    "constructor": "__init__" if visitor.has_constructor else None,
                    "functions": list(visitor.public_functions)
                }
            )
            
            # Compile and execute contract code
            contract_globals = {}
            exec(code, contract_globals)
            
            # Initialize contract if constructor exists
            if visitor.has_constructor and constructor_args:
                gas_counter = GasCounter(self.gas_limit)
                contract_instance = contract_globals['Contract'](*constructor_args)
                contract.storage = contract_instance.__dict__
                
            self.contracts[address] = contract
            return address
            
        except Exception as e:
            print(f"Contract deployment failed: {e}")
            return None
            
    def call_contract(self, address: str, function: str, args: List[Any] = None,
                     sender: str = None, value: float = 0.0) -> Any:
        """
        Call a contract function.
        
        Args:
            address: Contract address
            function: Function name to call
            args: Function arguments
            sender: Caller's address
            value: Amount of tokens to transfer
            
        Returns:
            Any: Function result
        """
        if address not in self.contracts:
            raise Exception("Contract not found")
            
        contract = self.contracts[address]
        if function not in contract.abi["functions"]:
            raise Exception("Function not found")
            
        try:
            # Create gas counter for this call
            gas_counter = GasCounter(self.gas_limit)
            
            # Set up contract environment
            contract_globals = {
                'gas_counter': gas_counter,
                'sender': sender,
                'value': value,
                'contract_address': address,
                'storage': contract.storage
            }
            
            # Execute contract code
            exec(contract.code, contract_globals)
            contract_instance = contract_globals['Contract']()
            
            # Restore contract state
            contract_instance.__dict__.update(contract.storage)
            
            # Call the function
            func = getattr(contract_instance, function)
            result = func(*(args or []))
            
            # Update contract state
            contract.storage = contract_instance.__dict__
            
            # Handle value transfer
            if value > 0:
                gas_counter.charge('TRANSFER')
                contract.balance += value
                
            return result
            
        except Exception as e:
            print(f"Contract call failed: {e}")
            raise
            
    def get_contract_state(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Get the current state of a contract.
        
        Args:
            address: Contract address
            
        Returns:
            Dict containing contract state if found
        """
        if address not in self.contracts:
            return None
            
        contract = self.contracts[address]
        return {
            "address": contract.address,
            "balance": contract.balance,
            "storage": contract.storage,
            "abi": contract.abi
        }
        
    def get_contract_balance(self, address: str) -> float:
        """
        Get the balance of a contract.
        
        Args:
            address: Contract address
            
        Returns:
            float: Contract balance
        """
        if address not in self.contracts:
            return 0.0
            
        return self.contracts[address].balance
        
    def transfer_to_contract(self, address: str, amount: float) -> bool:
        """
        Transfer tokens to a contract.
        
        Args:
            address: Contract address
            amount: Amount to transfer
            
        Returns:
            bool: True if transfer successful
        """
        if address not in self.contracts:
            return False
            
        self.contracts[address].balance += amount
        return True 