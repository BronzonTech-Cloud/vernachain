"""Logging utility functions for Vernachain."""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    format_string: Optional[str] = None
) -> logging.Logger:
    """Set up a logger with consistent formatting.
    
    Args:
        name: Logger name
        log_file: Optional file path for logging
        level: Logging level
        format_string: Optional custom format string
        
    Returns:
        logging.Logger: Configured logger
    """
    if format_string is None:
        format_string = '[%(asctime)s] %(levelname)s [%(name)s] %(message)s'
        
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(format_string)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if log file specified
    if log_file:
        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_blockchain_logger() -> logging.Logger:
    """Get logger for blockchain operations.
    
    Returns:
        logging.Logger: Blockchain logger
    """
    return setup_logger(
        'blockchain',
        f'logs/blockchain_{datetime.now().strftime("%Y%m%d")}.log'
    )

def get_networking_logger() -> logging.Logger:
    """Get logger for networking operations.
    
    Returns:
        logging.Logger: Networking logger
    """
    return setup_logger(
        'networking',
        f'logs/networking_{datetime.now().strftime("%Y%m%d")}.log'
    )

def get_consensus_logger() -> logging.Logger:
    """Get logger for consensus operations.
    
    Returns:
        logging.Logger: Consensus logger
    """
    return setup_logger(
        'consensus',
        f'logs/consensus_{datetime.now().strftime("%Y%m%d")}.log'
    )

def get_contract_logger() -> logging.Logger:
    """Get logger for smart contract operations.
    
    Returns:
        logging.Logger: Smart contract logger
    """
    return setup_logger(
        'contracts',
        f'logs/contracts_{datetime.now().strftime("%Y%m%d")}.log'
    )

# Create default loggers
blockchain_logger = get_blockchain_logger()
networking_logger = get_networking_logger()
consensus_logger = get_consensus_logger()
contract_logger = get_contract_logger() 