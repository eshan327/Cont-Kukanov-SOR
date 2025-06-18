# allocator.py
# Implements static Cont-Kukanov allocation logic for SOR backtesting 
from typing import List, Tuple
import math

def compute_cost(split, venues, order_size, lambda_over, lambda_under, theta_queue):
    executed = 0
    cash_spent = 0.0
    for i in range(len(venues)):
        exe = min(split[i], venues[i]['ask_sz_00'])
        executed += exe
        cash_spent += exe * (venues[i]['ask_px_00'] + venues[i].get('fee', 0.0))
        maker_rebate = max(split[i] - exe, 0) * venues[i].get('rebate', 0.0)
        cash_spent -= maker_rebate
    underfill = max(order_size - executed, 0)
    overfill = max(executed - order_size, 0)
    risk_pen = theta_queue * (underfill + overfill)
    cost_pen = lambda_under * underfill + lambda_over * overfill
    return cash_spent + risk_pen + cost_pen

def allocate(order_size: int, venues: List[dict], lambda_over: float, lambda_under: float, theta_queue: float) -> Tuple[List[int], float]:
    step = 100
    splits = [[]]
    for v in range(len(venues)):
        new_splits = []
        for alloc in splits:
            used = sum(alloc)
            max_v = min(order_size - used, venues[v]['ask_sz_00'])
            for q in range(0, max_v + 1, step):
                new_splits.append(alloc + [q])
        splits = new_splits
    best_cost = math.inf
    best_split = []
    found_exact = False
    for alloc in splits:
        if sum(alloc) == order_size:
            found_exact = True
            cost = compute_cost(alloc, venues, order_size, lambda_over, lambda_under, theta_queue)
            if cost < best_cost:
                best_cost = cost
                best_split = alloc
    if found_exact:
        return best_split, best_cost
    # If no exact fill, allow underfill: pick split with max fill
    max_fill = -1
    for alloc in splits:
        fill = sum(alloc)
        if fill > max_fill:
            max_fill = fill
            best_split = alloc
            best_cost = compute_cost(alloc, venues, order_size, lambda_over, lambda_under, theta_queue)
    return best_split, best_cost

if __name__ == "__main__":
    # Mock test case for demonstration
    venues = [
        {'ask_px_00': 100.0, 'ask_sz_00': 300, 'fee': 0.01, 'rebate': 0.0},
        {'ask_px_00': 100.2, 'ask_sz_00': 300, 'fee': 0.01, 'rebate': 0.0},
        {'ask_px_00': 99.9, 'ask_sz_00': 200, 'fee': 0.01, 'rebate': 0.0},
    ]
    order_size = 500
    split, cost = allocate(order_size, venues, lambda_over=0.1, lambda_under=0.1, theta_queue=0.05)
    print(f"Best split: {split}")
    print(f"Best cost: {cost}") 