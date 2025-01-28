"""Tests for the Validator Management System."""

import pytest
from datetime import datetime, timedelta
from src.consensus.validator_manager import ValidatorManager, ValidatorStats, DelegatorInfo

@pytest.fixture
def manager():
    """Create a validator manager instance for testing."""
    return ValidatorManager()

@pytest.fixture
def validator_address():
    """Return a test validator address."""
    return "0x1234567890abcdef1234567890abcdef12345678"

@pytest.fixture
def delegator_address():
    """Return a test delegator address."""
    return "0xabcdef1234567890abcdef1234567890abcdef12"

def test_validator_registration(manager, validator_address):
    """Test validator registration process."""
    # Test successful registration
    assert manager.register_validator(validator_address, 2000.0)
    assert validator_address in manager.validators
    assert validator_address in manager.active_set
    
    # Test duplicate registration
    assert not manager.register_validator(validator_address, 2000.0)
    
    # Test registration with insufficient stake
    new_address = "0xabcdef1234567890abcdef1234567890abcdef12"
    assert manager.register_validator(new_address, 500.0)
    assert new_address not in manager.active_set

def test_reputation_updates(manager, validator_address):
    """Test validator reputation updates."""
    manager.register_validator(validator_address, 2000.0)
    initial_score = manager.validators[validator_address].reputation_score
    
    # Test block proposal
    manager.update_reputation(validator_address, 1, 'block_proposed')
    assert manager.validators[validator_address].blocks_proposed == 1
    
    # Test missed block penalty
    manager.update_reputation(validator_address, 2, 'missed_block')
    assert manager.validators[validator_address].reputation_score < initial_score
    assert manager.validators[validator_address].missed_blocks == 1

def test_validator_jailing(manager, validator_address):
    """Test validator jailing mechanism."""
    manager.register_validator(validator_address, 2000.0)
    
    # Trigger jailing through missed blocks
    for _ in range(manager.penalty_thresholds['missed_blocks']):
        manager.update_reputation(validator_address, 1, 'missed_block')
    
    assert validator_address in manager.jailed_validators
    assert validator_address not in manager.active_set

def test_reward_calculation(manager, validator_address):
    """Test staking rewards calculation."""
    manager.register_validator(validator_address, 10000.0)  # 10x minimum stake
    
    # Calculate initial reward
    initial_reward = manager.calculate_rewards(validator_address, 1)
    assert initial_reward > 0
    
    # Test reward with perfect uptime
    for _ in range(100):
        manager.update_reputation(validator_address, 1, 'block_proposed')
    
    perfect_uptime_reward = manager.calculate_rewards(validator_address, 101)
    assert perfect_uptime_reward > initial_reward

def test_validator_unjailing(manager, validator_address):
    """Test validator unjailing process."""
    manager.register_validator(validator_address, 2000.0)
    
    # Jail the validator
    manager.jail_validator(validator_address)
    assert validator_address in manager.jailed_validators
    
    # Attempt unjailing with low reputation
    manager.validators[validator_address].reputation_score = 40.0
    assert not manager.unjail_validator(validator_address)
    
    # Attempt unjailing with sufficient reputation
    manager.validators[validator_address].reputation_score = 60.0
    assert manager.unjail_validator(validator_address)
    assert validator_address not in manager.jailed_validators
    assert validator_address in manager.active_set

def test_uptime_calculation(manager, validator_address):
    """Test validator uptime calculation."""
    manager.register_validator(validator_address, 2000.0)
    
    # Test perfect uptime
    for _ in range(10):
        manager.update_reputation(validator_address, 1, 'block_proposed')
    assert manager._calculate_uptime(manager.validators[validator_address]) == 1.0
    
    # Test with some missed blocks
    for _ in range(2):
        manager.update_reputation(validator_address, 1, 'missed_block')
    assert manager._calculate_uptime(manager.validators[validator_address]) == 10/12

def test_loyalty_rewards(manager, validator_address):
    """Test loyalty-based reward multipliers."""
    manager.register_validator(validator_address, 2000.0)
    
    # Get initial reward
    initial_reward = manager.calculate_rewards(validator_address, 1)
    
    # Simulate passage of time for loyalty bonus
    stats = manager.validators[validator_address]
    stats.stake_time = datetime.now() - timedelta(days=31)
    
    loyalty_reward = manager.calculate_rewards(validator_address, 2)
    assert loyalty_reward > initial_reward

def test_double_sign_penalty(manager, validator_address):
    """Test severe penalty for double signing."""
    manager.register_validator(validator_address, 2000.0)
    initial_score = manager.validators[validator_address].reputation_score
    
    manager.update_reputation(validator_address, 1, 'double_sign')
    assert manager.validators[validator_address].reputation_score < initial_score
    assert validator_address in manager.jailed_validators

def test_validator_set_management(manager):
    """Test validator set management."""
    addresses = [f"0x{i:040x}" for i in range(3)]
    
    # Register multiple validators
    for addr in addresses:
        manager.register_validator(addr, 2000.0)
    
    assert len(manager.get_validator_set()) == 3
    
    # Jail one validator
    manager.jail_validator(addresses[0])
    assert len(manager.get_validator_set()) == 2
    
    # Test validator stats retrieval
    stats = manager.get_validator_stats(addresses[0])
    assert isinstance(stats, ValidatorStats)
    assert stats.total_stake == 2000.0

def test_validator_registration_with_security(manager, validator_address):
    """Test validator registration with security deposit."""
    # Test registration with security deposit
    assert manager.register_validator(validator_address, 2000.0, 100.0)
    assert manager.validators[validator_address].security_deposit == 100.0
    
    # Test stake ratio limit
    large_stake = 1_000_000.0
    new_address = "0x" + "1" * 40
    assert not manager.register_validator(new_address, large_stake)  # Should fail due to max stake ratio

def test_delegation(manager, validator_address, delegator_address):
    """Test delegation functionality."""
    manager.register_validator(validator_address, 2000.0)
    
    # Test successful delegation
    assert manager.delegate(validator_address, delegator_address, 500.0)
    stats = manager.validators[validator_address]
    assert stats.delegated_stake == 500.0
    assert stats.total_stake == 2500.0
    
    # Test minimum delegation requirement
    assert not manager.delegate(validator_address, "0x" + "2" * 40, 50.0)
    
    # Test maximum delegators limit
    for i in range(manager.max_delegators):
        addr = f"0x{i:040x}"
        manager.delegate(validator_address, addr, 500.0)
    
    # This delegation should fail due to max delegators limit
    assert not manager.delegate(validator_address, "0x" + "3" * 40, 500.0)

def test_undelegation(manager, validator_address, delegator_address):
    """Test undelegation process."""
    manager.register_validator(validator_address, 2000.0)
    manager.delegate(validator_address, delegator_address, 500.0)
    
    # Test partial undelegation
    assert manager.undelegate(validator_address, delegator_address, 200.0)
    stats = manager.validators[validator_address]
    assert stats.delegated_stake == 300.0
    assert stats.total_stake == 2300.0
    
    # Test unbonding queue
    assert len(manager.unbonding_queue[validator_address]) == 1
    
    # Test complete undelegation
    assert manager.undelegate(validator_address, delegator_address, 300.0)
    assert delegator_address not in stats.delegators

def test_unbonding_process(manager, validator_address, delegator_address):
    """Test processing of unbonding requests."""
    manager.register_validator(validator_address, 2000.0)
    manager.delegate(validator_address, delegator_address, 500.0)
    manager.undelegate(validator_address, delegator_address, 500.0)
    
    # Fast forward time
    unbonding_entry = manager.unbonding_queue[validator_address][0]
    manager.unbonding_queue[validator_address] = [
        (addr, amount, datetime.now() - timedelta(days=15))
        for addr, amount, _ in manager.unbonding_queue[validator_address]
    ]
    
    # Process unbonding
    completed = manager.process_unbonding()
    assert len(completed) == 1
    assert completed[0] == (validator_address, delegator_address, 500.0)
    assert len(manager.unbonding_queue[validator_address]) == 0

def test_progressive_rewards(manager, validator_address):
    """Test progressive reward calculation."""
    # Test different stake levels
    stake_levels = [5000.0, 20000.0, 75000.0, 200000.0, 1000000.0]
    rewards = []
    
    for stake in stake_levels:
        manager = ValidatorManager()  # Fresh instance for each test
        manager.register_validator(validator_address, stake)
        
        # Simulate perfect performance
        for _ in range(100):
            manager.update_reputation(validator_address, 1, 'block_proposed')
            
        reward, _ = manager.calculate_rewards(validator_address, 1)
        rewards.append(reward)
    
    # Verify progressive rewards
    for i in range(1, len(rewards)):
        ratio = rewards[i] / rewards[i-1] * (stake_levels[i-1] / stake_levels[i])
        assert ratio > 1.0  # Higher stakes should give proportionally higher rewards

def test_performance_tracking(manager, validator_address):
    """Test validator performance tracking and scoring."""
    manager.register_validator(validator_address, 2000.0)
    
    # Simulate mixed performance
    events = [
        ('block_proposed', 1.0),
        ('block_proposed', 1.0),
        ('missed_block', -2.0),
        ('block_proposed', 1.0),
        ('invalid_block', -5.0),
        ('block_proposed', 1.0)
    ]
    
    for event, _ in events:
        manager.update_reputation(validator_address, 1, event)
    
    stats = manager.validators[validator_address]
    score = manager._calculate_performance_score(stats)
    assert 0.0 <= score <= 1.0
    
    # Verify performance history pruning
    old_time = datetime.now() - timedelta(days=31)
    stats.performance_history[0] = (old_time, stats.performance_history[0][1], 
                                  stats.performance_history[0][2])
    manager._prune_performance_history(stats)
    assert len(stats.performance_history) == len(events) - 1

def test_security_features(manager, validator_address):
    """Test security-related features."""
    # Test security deposit
    manager.register_validator(validator_address, 2000.0, 50.0)
    assert manager.add_security_deposit(validator_address, 50.0)
    stats = manager.validators[validator_address]
    assert stats.security_deposit == 100.0
    
    # Test commission rate limits
    assert manager.update_commission_rate(validator_address, 0.15)  # Within max
    assert not manager.update_commission_rate(validator_address, 0.25)  # Exceeds max
    
    # Test double sign penalty
    manager.update_reputation(validator_address, 1, 'double_sign')
    assert validator_address in manager.jailed_validators
    assert stats.reputation_score < 80.0  # Significant penalty

def test_validator_info(manager, validator_address, delegator_address):
    """Test validator information retrieval."""
    manager.register_validator(validator_address, 2000.0, 100.0)
    manager.delegate(validator_address, delegator_address, 500.0)
    
    info = manager.get_validator_info(validator_address)
    assert info is not None
    assert info['total_stake'] == 2500.0
    assert info['self_stake'] == 2000.0
    assert info['delegated_stake'] == 500.0
    assert info['security_deposit'] == 100.0
    assert info['delegator_count'] == 1
    assert not info['is_jailed']
    
    # Test non-existent validator
    assert manager.get_validator_info("0x" + "0" * 40) is None 