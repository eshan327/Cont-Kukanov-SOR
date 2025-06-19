import pandas as pd
import json
import time
from kafka import KafkaProducer
import config
import argparse
from kafka.errors import NoBrokersAvailable

def parse_csv(path):
    df = pd.read_csv(path)
    return df

def format_row(row):
    return {
        'timestamp': row['ts_event'],
        'venue': row['publisher_id'],
        'ask_px_00': row['ask_px_00'],
        'ask_sz_00': row['ask_sz_00'],
        'fee': 0.0,    # Placeholder, update if fee column exists
        'rebate': 0.0  # Placeholder, update if rebate column exists
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='Run without Kafka publishing')
    args = parser.parse_args()

    df = parse_csv("l1_day.csv")
    print("First 5 rows:")
    print(df.head())
    print("\nUnique timestamps:")
    print(df['ts_event'].unique())

    sample_dicts = [format_row(row) for _, row in df.head(5).iterrows()]
    print("\nSample JSON-ready dicts:")
    print(sample_dicts)

    if args.dry_run:
        print("\n[DRY RUN] Skipping Kafka publishing.")
    else:
        try:
            producer = KafkaProducer(
                bootstrap_servers='localhost:9092',
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
        except NoBrokersAvailable:
            print("[ERROR] No Kafka brokers available at localhost:9092. Run with --dry-run to skip publishing.")
            exit(1)
        last_ts = None
        for i, row in df.iterrows():
            d = format_row(row)
            ts = pd.to_datetime(row['ts_event'])
            if last_ts is not None:
                delta = (ts - last_ts).total_seconds()
                if delta > 0:
                    time.sleep(min(delta, 0.1))
            last_ts = ts
            producer.send(config.KAFKA_TOPIC, d)
            if i < 3:
                print(f"Published: {d}")
        producer.flush()
        print("\nFinished publishing to Kafka.")

if __name__ == "__main__":
    main() 