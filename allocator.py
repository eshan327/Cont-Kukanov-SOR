from typing import List, Tuple
import math
import config
import numpy as np
import random

def compute_cost(split, venues, order_size, lambda_over, lambda_under, theta_queue):
    executed = 0
    cash_spent = 0.0
    for i in range(len(venues)):
        queue_priority = venues[i].get('queue_priority', config.QUEUE_PRIORITY)
        max_fill = min(split[i], int(venues[i]['ask_sz_00'] * queue_priority))
        slippage_factor = 1 + config.SLIPPAGE_BPS / 10000
        exe = max_fill
        executed += exe
        fill_price = (venues[i]['ask_px_00'] + venues[i].get('fee', 0.0)) * slippage_factor
        cash_spent += exe * fill_price
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

def cont_kukanov_allocator(
    order_size: int,
    venues: List[dict],
    lambda_over: float,
    lambda_under: float,
    theta_queue: float,
    allocation_step: int = 100,
    queue_priority: float = None,
    slippage_bps: int = None,
    latency_ms: int = None,
    adverse_selection_prob: float = None,
    adverse_selection_bps: int = None
) -> Tuple[List[int], float, int]:
    # Override config with function arguments if provided
    q_priority = queue_priority if queue_priority is not None else config.QUEUE_PRIORITY
    slip_bps = slippage_bps if slippage_bps is not None else config.SLIPPAGE_BPS
    lat_ms = latency_ms if latency_ms is not None else config.LATENCY_MS
    adv_sel_prob = adverse_selection_prob if adverse_selection_prob is not None else config.ADVERSE_SELECTION_PROB
    adv_sel_bps = adverse_selection_bps if adverse_selection_bps is not None else config.ADVERSE_SELECTION_BPS

    # Copy venues and inject realism parameters
    venues_real = []
    for v in venues:
        v_real = v.copy()
        v_real['queue_priority'] = v.get('queue_priority', q_priority)
        v_real['slippage_bps'] = v.get('slippage_bps', slip_bps)
        venues_real.append(v_real)

    venues_sim = []
    for v in venues_real:
        v_sim = v.copy()
        if lat_ms > 0 and random.random() < adv_sel_prob:
            # Adverse selection: price up, size down
            v_sim['ask_px_00'] += v_sim['ask_px_00'] * (adv_sel_bps / 10000)
            v_sim['ask_sz_00'] = max(1, int(v_sim['ask_sz_00'] * 0.8))
        venues_sim.append(v_sim)

    split, cost = allocate(order_size, venues_sim, lambda_over, lambda_under, theta_queue)
    total_fill = sum(split)
    return split, cost, total_fill

if __name__ == "__main__":
    venues = [
        {'ask_px_00': 100.0, 'ask_sz_00': 300, 'fee': 0.01, 'rebate': 0.0},
        {'ask_px_00': 100.2, 'ask_sz_00': 300, 'fee': 0.01, 'rebate': 0.0},
        {'ask_px_00': 99.9, 'ask_sz_00': 200, 'fee': 0.01, 'rebate': 0.0},
    ]
    order_size = 500
    split, cost, total_fill = cont_kukanov_allocator(order_size, venues, lambda_over=0.1, lambda_under=0.1, theta_queue=0.05)
    print(f"Best split: {split}")
    print(f"Best cost: {cost}")
    print(f"Total fill: {total_fill}") 