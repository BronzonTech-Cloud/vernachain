"""Token factory contract for deploying various token types."""

from typing import Dict

class Contract:
    """Factory contract for deploying token contracts."""
    
    def __init__(self):
        """Initialize token factory."""
        globals()['gas_counter'].charge('STORE', 2)
        self.owner = globals()['sender']
        self.deployed_tokens = {}  # address -> token type
        
    def create_token(self, name: str, symbol: str, initial_supply: float,
                    decimals: int = 18, is_mintable: bool = True,
                    is_burnable: bool = True, is_pausable: bool = True) -> str:
        """
        Create new ERC20 token.
        
        Args:
            name: Token name
            symbol: Token symbol
            initial_supply: Initial token supply
            decimals: Token decimals
            is_mintable: Whether token can be minted
            is_burnable: Whether token can be burned
            is_pausable: Whether token can be paused
            
        Returns:
            str: New token contract address
        """
        globals()['gas_counter'].charge('COMPUTE', 2)
        
        # Deploy token contract
        contract_code = self._get_token_code(
            name, symbol, initial_supply, decimals,
            is_mintable, is_burnable, is_pausable
        )
        
        address = globals()['vm'].deploy_contract(
            code=contract_code,
            constructor_args=[name, symbol, initial_supply]
        )
        
        if address:
            self.deployed_tokens[address] = "ERC20"
            
        return address
        
    def create_nft_collection(self, name: str, symbol: str, base_uri: str,
                            is_burnable: bool = True, is_pausable: bool = True) -> str:
        """
        Create new ERC721 NFT collection.
        
        Args:
            name: Collection name
            symbol: Collection symbol
            base_uri: Base URI for token metadata
            is_burnable: Whether tokens can be burned
            is_pausable: Whether collection can be paused
            
        Returns:
            str: New NFT contract address
        """
        globals()['gas_counter'].charge('COMPUTE', 2)
        
        # Deploy NFT contract
        contract_code = self._get_nft_code(
            name, symbol, base_uri,
            is_burnable, is_pausable
        )
        
        address = globals()['vm'].deploy_contract(
            code=contract_code,
            constructor_args=[name, symbol, base_uri]
        )
        
        if address:
            self.deployed_tokens[address] = "ERC721"
            
        return address
        
    def create_multi_token(self, name: str, uri: str,
                          is_burnable: bool = True,
                          is_pausable: bool = True) -> str:
        """
        Create new ERC1155 multi-token collection.
        
        Args:
            name: Collection name
            uri: Metadata URI with {id} placeholder
            is_burnable: Whether tokens can be burned
            is_pausable: Whether collection can be paused
            
        Returns:
            str: New multi-token contract address
        """
        globals()['gas_counter'].charge('COMPUTE', 2)
        
        # Deploy multi-token contract
        contract_code = self._get_multi_token_code(
            name, uri,
            is_burnable, is_pausable
        )
        
        address = globals()['vm'].deploy_contract(
            code=contract_code,
            constructor_args=[name, uri]
        )
        
        if address:
            self.deployed_tokens[address] = "ERC1155"
            
        return address
        
    def get_deployed_tokens(self) -> Dict[str, str]:
        """Get list of deployed tokens and their types."""
        return self.deployed_tokens
        
    def _get_token_code(self, name: str, symbol: str, initial_supply: float,
                       decimals: int, is_mintable: bool, is_burnable: bool,
                       is_pausable: bool) -> str:
        """Get customized token contract code."""
        with open('src/blockchain/smart_contracts/token.py', 'r') as f:
            code = f.read()
            
        # Customize features
        if not is_mintable:
            code = code.replace('def mint', 'def _disabled_mint')
        if not is_burnable:
            code = code.replace('def burn', 'def _disabled_burn')
            
        return code
        
    def _get_nft_code(self, name: str, symbol: str, base_uri: str,
                      is_burnable: bool, is_pausable: bool) -> str:
        """Get customized NFT contract code."""
        with open('src/blockchain/smart_contracts/erc721.py', 'r') as f:
            code = f.read()
            
        # Customize features
        if not is_burnable:
            code = code.replace('def burn', 'def _disabled_burn')
            
        return code
        
    def _get_multi_token_code(self, name: str, uri: str,
                             is_burnable: bool, is_pausable: bool) -> str:
        """Get customized multi-token contract code."""
        with open('src/blockchain/smart_contracts/erc1155.py', 'r') as f:
            code = f.read()
            
        # Customize features
        if not is_burnable:
            code = code.replace('def burn', 'def _disabled_burn')
            code = code.replace('def burn_batch', 'def _disabled_burn_batch')
            
        return code