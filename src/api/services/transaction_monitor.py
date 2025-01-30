"""
Transaction monitoring service for tracking blockchain transactions.
"""

import asyncio
from typing import Dict, Any, List
import logging
from ..database import SessionLocal, DBTransaction, DBToken, DBTokenHolder, TransactionStatus
from ..blockchain.client import BlockchainClient
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class TransactionMonitor:
    def __init__(self):
        self.blockchain = BlockchainClient()
        self.check_interval = 15  # seconds

    async def start(self):
        """Start the transaction monitor"""
        while True:
            try:
                await self.check_pending_transactions()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in transaction monitor: {e}")
                await asyncio.sleep(self.check_interval)

    async def check_pending_transactions(self):
        """Check status of pending transactions"""
        db = SessionLocal()
        try:
            # Get all pending transactions
            pending_txs = db.query(DBTransaction).filter(
                DBTransaction.status == TransactionStatus.PENDING
            ).all()

            for tx in pending_txs:
                # Get transaction receipt
                receipt = self.blockchain.web3.eth.get_transaction_receipt(tx.tx_hash)
                if receipt:
                    # Update transaction status
                    if receipt["status"] == 1:
                        tx.status = TransactionStatus.CONFIRMED
                        tx.confirmed_at = datetime.utcnow()
                        tx.block_number = receipt["blockNumber"]
                        tx.gas_used = str(receipt["gasUsed"])
                        
                        # Update token contract address for token creation
                        if tx.type == "create":
                            token = db.query(DBToken).filter(
                                DBToken.id == tx.token_id
                            ).first()
                            if token:
                                # Get contract address from event logs
                                token.contract_address = self._get_token_address_from_logs(receipt["logs"])
                                
                        # Update token holder balances
                        await self._update_token_balances(db, tx)
                    else:
                        tx.status = TransactionStatus.FAILED
                        tx.error_message = "Transaction reverted"
                    
                    db.commit()
                    
        except Exception as e:
            logger.error(f"Error checking transactions: {e}")
            db.rollback()
        finally:
            db.close()

    def _get_token_address_from_logs(self, logs: List[Dict[str, Any]]) -> str:
        """Extract token address from event logs"""
        # Implement based on your token factory contract events
        # This is just a placeholder
        return logs[0]["address"] if logs else None

    async def _update_token_balances(self, db, tx: DBTransaction):
        """Update token holder balances after confirmed transaction"""
        try:
            token = db.query(DBToken).filter(DBToken.id == tx.token_id).first()
            if not token or not token.contract_address:
                return

            # Get token contract
            token_contract = self.blockchain.web3.eth.contract(
                address=token.contract_address,
                abi=self.blockchain.token_abi
            )

            # Update sender balance
            if tx.from_address != "0x0000000000000000000000000000000000000000":
                from_balance = token_contract.functions.balanceOf(tx.from_address).call()
                self._update_holder_balance(db, token.id, tx.from_address, str(from_balance))

            # Update receiver balance
            if tx.to_address != "0x0000000000000000000000000000000000000000":
                to_balance = token_contract.functions.balanceOf(tx.to_address).call()
                self._update_holder_balance(db, token.id, tx.to_address, str(to_balance))

            # Update total supply
            token.total_supply = str(token_contract.functions.totalSupply().call())
            
            db.commit()
        except Exception as e:
            logger.error(f"Error updating balances: {e}")
            db.rollback()

    def _update_holder_balance(self, db, token_id: str, holder_address: str, balance: str):
        """Update or create token holder balance"""
        holder = db.query(DBTokenHolder).filter(
            DBTokenHolder.token_id == token_id,
            DBTokenHolder.holder_address == holder_address
        ).first()

        if holder:
            holder.balance = balance
            holder.last_updated = datetime.utcnow()
        else:
            holder = DBTokenHolder(
                id=str(uuid.uuid4()),
                token_id=token_id,
                holder_address=holder_address,
                balance=balance
            )
            db.add(holder) 