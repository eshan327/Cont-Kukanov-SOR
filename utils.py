# utils.py
# Common helper functions for SOR backtesting 

def best_ask(snapshots, order_size):
    # Fill as much as possible at the best ask across venues
    sorted_venues = sorted(snapshots, key=lambda v: v['ask_px_00'])
    remaining = order_size
    cost = 0.0
    filled = 0
    for v in sorted_venues:
        take = min(remaining, v['ask_sz_00'])
        cost += take * (v['ask_px_00'] + v.get('fee', 0.0))
        filled += take
        remaining -= take
        if remaining <= 0:
            break
    avg_price = cost / filled if filled > 0 else 0.0
    return cost, avg_price

def twap(snapshots_by_time, order_size):
    # snapshots_by_time: dict[timestamp, List[venue dict]]
    # Evenly split order_size across all timestamps
    n = len(snapshots_by_time)
    if n == 0:
        return 0.0, 0.0
    per_slice = order_size // n
    total_cost = 0.0
    total_filled = 0
    for venues in snapshots_by_time.values():
        cost, filled = 0.0, 0
        # Use best_ask logic for each slice
        c, _ = best_ask(venues, per_slice)
        total_cost += c
        total_filled += per_slice
    avg_price = total_cost / total_filled if total_filled > 0 else 0.0
    return total_cost, avg_price

def vwap(snapshots_by_time, order_size):
    # VWAP: weight slices by total available size at each timestamp
    total_liquidity = sum(sum(v['ask_sz_00'] for v in venues) for venues in snapshots_by_time.values())
    if total_liquidity == 0:
        return 0.0, 0.0
    total_cost = 0.0
    total_filled = 0
    for venues in snapshots_by_time.values():
        slice_liquidity = sum(v['ask_sz_00'] for v in venues)
        if slice_liquidity == 0:
            continue
        slice_order = int(order_size * (slice_liquidity / total_liquidity))
        c, _ = best_ask(venues, slice_order)
        total_cost += c
        total_filled += slice_order
    avg_price = total_cost / total_filled if total_filled > 0 else 0.0
    return total_cost, avg_price 