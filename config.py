# config.py
# Global constants and parameters for SOR backtesting 

"""
Configuration constants for SOR backtesting system.
"""

KAFKA_TOPIC = "mock_l1_stream"  # Kafka topic for market snapshots
ORDER_SIZE = 5000               # Target shares to buy per backtest
CSV_PATH = "l1_day.csv"         # Path to market data CSV

# Example parameter grid for allocator tuning
PARAM_GRID = {
    "lambda_over": [0.0, 0.1, 0.5],
    "lambda_under": [0.0, 0.1, 0.5],
    "theta_queue": [0.0, 0.1, 0.5]
}

# Example time window (as string or integer, to be parsed as needed)
START_TIME = "09:30:00"
END_TIME = "16:00:00" 