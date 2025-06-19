import pytest
import config
from allocator import allocate

def test_simple_split():
    venues = [
        {'ask_px_00': 100.0, 'ask_sz_00': 300, 'fee': 0.01, 'rebate': 0.0},
        {'ask_px_00': 100.2, 'ask_sz_00': 300, 'fee': 0.01, 'rebate': 0.0},
        {'ask_px_00': 99.9, 'ask_sz_00': 200, 'fee': 0.01, 'rebate': 0.0},
    ]
    order_size = 500
    split, cost = allocate(order_size, venues, 0.1, 0.1, 0.05)
    assert sum(split) == order_size
    assert isinstance(cost, float)

def test_allocation_exact_capacity():
    venues = [
        {'ask_px_00': 100.0, 'ask_sz_00': 200, 'fee': 0.0, 'rebate': 0.0},
        {'ask_px_00': 101.0, 'ask_sz_00': 300, 'fee': 0.0, 'rebate': 0.0},
    ]
    order_size = 500
    split, cost = allocate(order_size, venues, 0.0, 0.0, 0.0)
    print(f"Split: {split}")
    print(f"Cost returned: {cost}")
    expected_cost = 200 * 100.0 + 300 * 101.0
    print(f"Expected cost: {expected_cost}")
    assert split == [200, 300]
    assert abs(cost - expected_cost) < 1e-6, f"Expected {expected_cost}, got {cost}"

def test_penalty_for_underfill():
    venues = [
        {'ask_px_00': 100.0, 'ask_sz_00': 100, 'fee': 0.0, 'rebate': 0.0},
        {'ask_px_00': 101.0, 'ask_sz_00': 100, 'fee': 0.0, 'rebate': 0.0},
    ]
    order_size = 500
    split, cost = allocate(order_size, venues, 0.0, 1.0, 0.0)
    # Only 200 shares available, so 300 underfill, penalty should apply
    assert sum(split) == 200
    assert cost > 200*100.0 + 0  # Penalty included 

def test_exact_fill():
    venues = [
        {'ask_px_00': 100.0, 'ask_sz_00': 200, 'fee': 0.0, 'rebate': 0.0},
        {'ask_px_00': 101.0, 'ask_sz_00': 300, 'fee': 0.0, 'rebate': 0.0},
    ]
    order_size = 500
    split, cost = allocate(order_size, venues, 0.0, 0.0, 0.0)
    assert split == [200, 300]
    assert cost == 200*100.0 + 300*101.0
    assert sum(split) == order_size, "Allocator should fill exactly 500 shares."

def test_underfill_penalty():
    venues = [
        {'ask_px_00': 100.0, 'ask_sz_00': 100, 'fee': 0.0, 'rebate': 0.0},
        {'ask_px_00': 101.0, 'ask_sz_00': 100, 'fee': 0.0, 'rebate': 0.0},
    ]
    order_size = 500
    split, cost = allocate(order_size, venues, 0.0, 1.0, 0.0)
    # Only 200 shares available, so 300 underfill, penalty should apply
    assert sum(split) == 200
    assert cost > 200*100.0 + 0  # Penalty included 
    assert sum(split) < order_size, "Allocator should underfill when not enough liquidity."
    assert cost > 0, "Cost should be positive when underfilling."

def test_overfill_penalty():
    venues = [
        {'ask_px_00': 100.0, 'ask_sz_00': 200, 'fee': 0.0, 'rebate': 0.0},
        {'ask_px_00': 101.0, 'ask_sz_00': 300, 'fee': 0.0, 'rebate': 0.0},
    ]
    order_size = 500
    split, cost = allocate(order_size, venues, 0.0, 0.0, 0.0)
    assert sum(split) <= order_size, "Allocator should not overfill beyond order size."
    assert sum(split) == 500, "Allocator should fill exactly 500 shares."
    assert cost == 200*100.0 + 300*101.0, "Allocator should allocate exactly to capacity." 