from kafka import KafkaConsumer
import json as _json
from collections import defaultdict
import config
from allocator import allocate
import argparse
from kafka.errors import NoBrokersAvailable
from utils import best_ask, twap, vwap
import itertools
import matplotlib.pyplot as plt
import random
import time

def group_snapshots_by_timestamp(messages):
    batches = defaultdict(list)
    for msg in messages:
        data = _json.loads(msg.value.decode('utf-8'))
        batches[data['timestamp']].append(data)
    return batches

def accumulate_fills_and_cash(batches, order_size, lambda_over, lambda_under, theta_queue):
    total_cash = 0.0
    total_filled = 0
    for ts, venues in batches.items():
        time.sleep(config.LATENCY_MS / 1000)
        perturbed_venues = []
        for v in venues:
            v = v.copy()
            # 10% chance price moves up by 1-2 ticks, size drops by 10-30%
            if random.random() < 0.1:
                v['ask_px_00'] += random.choice([0.01, 0.02])
                v['ask_sz_00'] = int(v['ask_sz_00'] * random.uniform(0.7, 0.9))
            perturbed_venues.append(v)
        split, cost = allocate(order_size, perturbed_venues, lambda_over, lambda_under, theta_queue)
        filled = sum(split)
        total_cash += cost
        total_filled += filled
        print(f"Timestamp: {ts}")
        print(f"Venues: {perturbed_venues}")
        print(f"Split: {split}, Cost: {cost}, Filled: {filled}")
        print(f"Running totals - Cash: {total_cash}, Shares filled: {total_filled}\n")
    return total_cash, total_filled

def run_baselines(batches, order_size):
    # Best Ask on all venues at first timestamp
    first_ts = next(iter(batches))
    best_ask_cost, best_ask_avg = best_ask(batches[first_ts], order_size)
    twap_cost, twap_avg = twap(batches, order_size)
    vwap_cost, vwap_avg = vwap(batches, order_size)
    print(f"Best Ask: cost={best_ask_cost}, avg_px={best_ask_avg}")
    print(f"TWAP: cost={twap_cost}, avg_px={twap_avg}")
    print(f"VWAP: cost={vwap_cost}, avg_px={vwap_avg}")
    return {
        'best_ask': (best_ask_cost, best_ask_avg),
        'twap': (twap_cost, twap_avg),
        'vwap': (vwap_cost, vwap_avg)
    }

def run_param_grid(batches, order_size, param_grid):
    best_cost = float('inf')
    best_params = None
    for lo, lu, tq in itertools.product(param_grid['lambda_over'], param_grid['lambda_under'], param_grid['theta_queue']):
        total_cost, total_filled = accumulate_fills_and_cash(batches, order_size, lo, lu, tq)
        if total_cost < best_cost:
            best_cost = total_cost
            best_params = {'lambda_over': lo, 'lambda_under': lu, 'theta_queue': tq}
    print(f"Best parameters: {best_params}, cost: {best_cost}")
    return best_params, best_cost

def compute_savings_bps(optimized_cost, baselines):
    savings = {}
    for name, (base_cost, _) in baselines.items():
        if base_cost == 0:
            bps = 0.0
        else:
            bps = 10000 * (base_cost - optimized_cost) / base_cost
        savings[name] = bps
        print(f"Savings vs {name}: {bps:.2f} bps")
    return savings

def serialize_results(best_params, best_cost, baselines, savings, best_avg_px):
    result = {
        'best_parameters': best_params,
        'optimized': {
            'total_cash': best_cost,
            'avg_fill_px': best_avg_px
        },
        'baselines': {k: {'total_cash': v[0], 'avg_fill_px': v[1]} for k, v in baselines.items()},
        'savings_vs_baselines_bps': savings
    }
    with open('output.json', 'w') as f:
        _json.dump(result, f, indent=2)
    print("\nFinal JSON output:")
    print(_json.dumps(result, indent=2))
    print("\nResults written to output.json")
    return result

def plot_results(best_cost, baselines):
    strategies = ['optimized'] + list(baselines.keys())
    costs = [best_cost] + [baselines[k][0] for k in baselines]
    plt.figure(figsize=(6,4))
    bars = plt.bar(strategies, costs, color=['#4CAF50', '#2196F3', '#FFC107', '#FF5722'])
    plt.ylabel('Total Cost')
    plt.title('Total Cost per Strategy')
    for bar, cost in zip(bars, costs):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{cost:.0f}', ha='center', va='bottom')
    plt.tight_layout()
    plt.savefig('results.png')
    print('results.png saved.')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='Run with mock data instead of Kafka')
    args = parser.parse_args()

    if args.dry_run:
        mock_messages = []
        for ts in ["2024-08-01T13:36:32.491911683Z", "2024-08-01T13:36:32.491911684Z"]:
            for venue in [
                {'timestamp': ts, 'venue': 1, 'ask_px_00': 100.0, 'ask_sz_00': 300, 'fee': 0.01, 'rebate': 0.0},
                {'timestamp': ts, 'venue': 2, 'ask_px_00': 100.2, 'ask_sz_00': 300, 'fee': 0.01, 'rebate': 0.0},
                {'timestamp': ts, 'venue': 3, 'ask_px_00': 99.9, 'ask_sz_00': 200, 'fee': 0.01, 'rebate': 0.0},
            ]:
                class MockMsg:
                    def __init__(self, value):
                        self.value = _json.dumps(venue).encode('utf-8')
                mock_messages.append(MockMsg(venue))
        messages = mock_messages
    else:
        try:
            consumer = KafkaConsumer(
                config.KAFKA_TOPIC,
                bootstrap_servers='localhost:9092',
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id='backtest-group',
                consumer_timeout_ms=5000
            )
            print("Consuming from Kafka topic... (Ctrl+C to stop)")
            messages = list(consumer)
        except NoBrokersAvailable:
            print("[ERROR] No Kafka brokers available at localhost:9092. Run with --dry-run to skip consuming.")
            exit(1)
    batches = group_snapshots_by_timestamp(messages)
    print("\n--- Baseline Strategies ---")
    baselines = run_baselines(batches, config.ORDER_SIZE)
    print("\n--- Parameter Grid Search ---")
    best_params, best_cost = run_param_grid(batches, config.ORDER_SIZE, config.PARAM_GRID)
    print("\n--- Savings vs Baselines (bps) ---")
    savings = compute_savings_bps(best_cost, baselines)
    best_avg_px = 0.0
    for ts, venues in batches.items():
        split, _ = allocate(config.ORDER_SIZE, venues, best_params['lambda_over'], best_params['lambda_under'], best_params['theta_queue'])
        filled = sum(split)
        if filled > 0:
            # Weighted average price for this batch
            batch_cost = sum([split[i] * (venues[i]['ask_px_00'] + venues[i].get('fee', 0.0)) for i in range(len(split))])
            best_avg_px += batch_cost
    if len(batches) > 0 and config.ORDER_SIZE > 0:
        best_avg_px = best_avg_px / (config.ORDER_SIZE * len(batches))
    else:
        best_avg_px = 0.0
    serialize_results(best_params, best_cost, baselines, savings, best_avg_px)
    plot_results(best_cost, baselines)

if __name__ == "__main__":
    main() 