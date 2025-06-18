# Smart Order Router (SOR) Backtesting System Architecture

A modular system for backtesting and simulating real-time market data using Kafka, implementing the Cont & Kukanov allocation model, and benchmarking against standard execution strategies.

---

## 📁 File & Folder Structure

```
.
├── allocator.py            # Implements static Cont-Kukanov allocation logic
├── backtest.py             # Orchestrates parameter tuning, benchmarking, and result evaluation
├── kafka_producer.py       # Streams market snapshots from l1_day.csv into Kafka
├── config.py               # Global constants and parameters
├── utils.py                # Common helper functions (e.g., time deltas, JSON formatting)
├── requirements.txt        # Python dependencies
├── README.md               # Project overview, CLI commands, and EC2 deployment instructions
├── allocator_pseudocode.txt# Reference pseudocode for static Cont-Kukanov allocator
├── results.png             # Optional performance comparison plot
└── output.json             # Optional final JSON result dump
```

---

## 🔄 Data Flow & Service Connections

```text
            ┌────────────┐
            │ l1_day.csv │   ← Market snapshot data (ask, size, fee, rebate)
            └─────┬──────┘
                  │
                  ▼
         ┌────────────────────┐
         │ kafka_producer.py  │  ← Reads CSV and streams JSON snapshots to Kafka
         └────────────────────┘
                  │
                  ▼
        Kafka Topic: `mock_l1_stream`
                  │
                  ▼
         ┌────────────────────┐
         │   backtest.py      │  ← Consumes snapshots, runs allocator, computes baselines
         └────────────────────┘
                  │
                  ▼
         ┌────────────────────┐
         │  allocator.py      │  ← Computes optimal split per snapshot using static CK model
         └────────────────────┘
                  │
                  ▼
         ┌────────────────────┐
         │  output.json       │  ← Stores final performance summary as JSON
         └────────────────────┘
```

---

## 🧩 Component Responsibilities

* **allocator.py**

  * Implements the static Cont-Kukanov allocation algorithm.
  * Brute-force search in 100-share increments.
  * Cost model includes execution cost, under/overfill penalties, and queue-risk penalty.

* **kafka\_producer.py**

  * Parses `l1_day.csv`.
  * Formats each row into a JSON snapshot with fields: `timestamp`, `venue`, `ask_px_00`, `ask_sz_00`, `fee`, `rebate`.
  * Streams snapshots to topic `mock_l1_stream` using `kafka-python`.
  * Simulates real-time pacing via `time.sleep()` based on `ts_event` deltas.

* **backtest.py**

  * Subscribes to Kafka topic.
  * Groups snapshots by timestamp and passes venue data to allocator.
  * Runs parameter grid search on `(lambda_over, lambda_under, theta_queue)`.
  * Executes baseline strategies: Best Ask, TWAP (60s), and VWAP.
  * Calculates metrics: total cash, average fill price, savings in bps.
  * Outputs final JSON and (optionally) generates `results.png`.

* **config.py**

  * Centralizes constants: Kafka settings, order size (5,000), time window, parameter grids, CSV path.

* **utils.py**

  * Helper functions for parsing time, formatting JSON, computing VWAP/TWAP weights.

---

## 🚀 Deployment Outline (for README)

1. **EC2 Instance**

   * Type: `t3.micro` or `t4g.micro`.
2. **Kafka & Zookeeper Setup**

   * Install Java, Kafka, and Zookeeper via `apt` or `yum`.
   * Configure systemd services.
3. **Python Environment**

   * `python3.8+` virtual environment.
   * `pip install -r requirements.txt`.
4. **Running the Pipeline**

   * Start Zookeeper & Kafka.
   * Run `python kafka_producer.py`.
   * In parallel, run `python backtest.py`.
5. **Verification Screenshots**

   * Kafka console consumer showing messages.
   * Backtest stdout JSON.
   * `uname -a` / `uptime` for system info.
