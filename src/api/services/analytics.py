"""
Token analytics service for tracking and analyzing token metrics.
"""

from typing import Dict, Any, List, Optional
import logging
from ..database import SessionLocal, DBToken, DBTransaction, DBTokenHolder
from ..blockchain.client import BlockchainClient
from datetime import datetime, timedelta
from sqlalchemy import func, and_
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class TokenAnalytics:
    def __init__(self):
        self.blockchain = BlockchainClient()

    def get_token_metrics(self, token_id: str, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive token metrics"""
        db = SessionLocal()
        try:
            token = db.query(DBToken).filter(DBToken.id == token_id).first()
            if not token:
                return {}

            # Time range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            # Get transactions in time range
            transactions = db.query(DBTransaction).filter(
                and_(
                    DBTransaction.token_id == token_id,
                    DBTransaction.created_at >= start_date,
                    DBTransaction.created_at <= end_date,
                    DBTransaction.status == "confirmed"
                )
            ).all()

            # Calculate metrics
            metrics = {
                "general": self._calculate_general_metrics(token, db),
                "holders": self._analyze_holder_distribution(token, db),
                "volume": self._calculate_volume_metrics(transactions, days),
                "transactions": self._analyze_transactions(transactions),
                "price": self._calculate_price_metrics(token, transactions),
                "liquidity": self._analyze_liquidity(token),
            }

            return metrics
        except Exception as e:
            logger.error(f"Error calculating token metrics: {e}")
            return {}
        finally:
            db.close()

    def _calculate_general_metrics(self, token: DBToken, db) -> Dict[str, Any]:
        """Calculate general token metrics"""
        holder_count = db.query(func.count(DBTokenHolder.id)).filter(
            DBTokenHolder.token_id == token.id,
            DBTokenHolder.balance > "0"
        ).scalar()

        return {
            "total_supply": token.total_supply,
            "holder_count": holder_count,
            "market_cap": self._get_market_cap(token),
            "creation_date": token.created_at.isoformat(),
            "contract_address": token.contract_address
        }

    def _analyze_holder_distribution(self, token: DBToken, db) -> Dict[str, Any]:
        """Analyze token holder distribution"""
        holders = db.query(DBTokenHolder).filter(
            DBTokenHolder.token_id == token.id,
            DBTokenHolder.balance > "0"
        ).all()

        if not holders:
            return {}

        balances = [int(h.balance) for h in holders]
        total = sum(balances)

        # Calculate concentration metrics
        sorted_balances = sorted(balances, reverse=True)
        top_10_share = sum(sorted_balances[:10]) / total if len(balances) >= 10 else 1
        
        return {
            "distribution": {
                "top_10_holders": top_10_share,
                "gini_coefficient": self._calculate_gini(balances),
                "holder_brackets": self._calculate_holder_brackets(balances)
            }
        }

    def _calculate_volume_metrics(self, transactions: List[DBTransaction], days: int) -> Dict[str, Any]:
        """Calculate volume metrics"""
        if not transactions:
            return {"daily_volumes": [], "total_volume": "0"}

        # Group transactions by day
        df = pd.DataFrame([{
            'date': tx.created_at.date(),
            'amount': int(tx.amount)
        } for tx in transactions if tx.type in ['transfer', 'swap']])

        if df.empty:
            return {"daily_volumes": [], "total_volume": "0"}

        daily_volumes = df.groupby('date')['amount'].sum().to_dict()
        
        return {
            "daily_volumes": [
                {"date": date.isoformat(), "volume": str(volume)}
                for date, volume in daily_volumes.items()
            ],
            "total_volume": str(df['amount'].sum()),
            "average_daily_volume": str(df['amount'].sum() // days)
        }

    def _analyze_transactions(self, transactions: List[DBTransaction]) -> Dict[str, Any]:
        """Analyze transaction patterns"""
        if not transactions:
            return {}

        tx_types = {}
        unique_addresses = set()
        gas_used = []

        for tx in transactions:
            # Count transaction types
            tx_types[tx.type] = tx_types.get(tx.type, 0) + 1
            # Track unique addresses
            unique_addresses.add(tx.from_address)
            unique_addresses.add(tx.to_address)
            # Track gas usage
            if tx.gas_used:
                gas_used.append(int(tx.gas_used))

        return {
            "transaction_count": len(transactions),
            "unique_addresses": len(unique_addresses),
            "transaction_types": tx_types,
            "average_gas_used": str(sum(gas_used) // len(gas_used)) if gas_used else "0"
        }

    def _calculate_price_metrics(self, token: DBToken, transactions: List[DBTransaction]) -> Dict[str, Any]:
        """Calculate price metrics"""
        try:
            # This would typically integrate with a price feed or DEX
            # For now, we'll return placeholder data
            return {
                "current_price": "0",
                "price_change_24h": "0",
                "price_change_7d": "0",
                "highest_price_30d": "0",
                "lowest_price_30d": "0"
            }
        except Exception as e:
            logger.error(f"Error calculating price metrics: {e}")
            return {}

    def _analyze_liquidity(self, token: DBToken) -> Dict[str, Any]:
        """Analyze token liquidity"""
        try:
            # This would typically integrate with DEX contracts
            # For now, we'll return placeholder data
            return {
                "total_liquidity": "0",
                "liquidity_pairs": [],
                "liquidity_change_24h": "0"
            }
        except Exception as e:
            logger.error(f"Error analyzing liquidity: {e}")
            return {}

    def _calculate_gini(self, values: List[int]) -> float:
        """Calculate Gini coefficient for token distribution"""
        if not values:
            return 0
        values = sorted(values)
        n = len(values)
        index = np.arange(1, n + 1)
        return (np.sum((2 * index - n - 1) * values)) / (n * np.sum(values))

    def _calculate_holder_brackets(self, balances: List[int]) -> Dict[str, int]:
        """Calculate holder distribution brackets"""
        if not balances:
            return {}

        total = sum(balances)
        brackets = {
            "0-0.1%": 0,
            "0.1-1%": 0,
            "1-5%": 0,
            "5-10%": 0,
            ">10%": 0
        }

        for balance in balances:
            percentage = (balance / total) * 100
            if percentage <= 0.1:
                brackets["0-0.1%"] += 1
            elif percentage <= 1:
                brackets["0.1-1%"] += 1
            elif percentage <= 5:
                brackets["1-5%"] += 1
            elif percentage <= 10:
                brackets["5-10%"] += 1
            else:
                brackets[">10%"] += 1

        return brackets

    def _get_market_cap(self, token: DBToken) -> str:
        """Calculate token market cap"""
        try:
            # This would typically integrate with a price feed
            # For now, we'll return the total supply
            return token.total_supply
        except Exception as e:
            logger.error(f"Error calculating market cap: {e}")
            return "0" 