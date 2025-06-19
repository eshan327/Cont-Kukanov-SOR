# Smart Order Router (SOR) Backtesting System

## Project Summary
This project implements a backtesting system for a Smart Order Router (SOR) using the Cont & Kukanov cost model. It simulates real-time market data streaming with Kafka, benchmarks the SOR against standard execution strategies, and supports deployment on EC2. The system is modular, reproducible, and extensible for research or production use.

## Quickstart (Local Testing)
1. Place your `l1_day.csv` in the project root.
2. Install dependencies:
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Run the producer in dry-run mode:
   ```sh
   python kafka_producer.py --dry-run
   ```
4. Run the backtester in dry-run mode:
   ```sh
   python backtest.py --dry-run
   ```
5. Check `output.json` and `results.png` for results.

## Approach & Tuning Logic
- **Market Data Simulation:**
  - `kafka_producer.py` streams each row of `l1_day.csv` as a JSON snapshot to Kafka, simulating real-time with `time.sleep()` or in dry-run mode (stdout).
- **Allocator Logic:**
  - `allocator.py` implements the static Cont & Kukanov allocation model, searching all possible splits in 100-share increments to minimize total expected cost. The cost includes execution, over/underfill penalties, queue risk, queue priority, slippage, and latency/adverse selection.
- **Backtesting & Baselines:**
  - `backtest.py` consumes the Kafka stream (or mock data), groups venue snapshots by timestamp, and applies the allocator for each batch.
  - Baseline strategies (Best Ask, TWAP, VWAP) are implemented in `utils.py` and benchmarked against the allocator.
- **Parameter Tuning:**
  - The allocator is tuned via grid search over `lambda_over`, `lambda_under`, and `theta_queue` (see `config.py`).
  - For each parameter set, the backtester computes total cost and fill. The best set is selected based on lowest total cost.
  - All parameters are configurable in `config.py` for reproducibility.
- **Results & Output:**
  - Results are printed as a JSON object and saved to `output.json` (see sample format below).
  - A bar plot of total cost per strategy is saved as `results.png`.

## Output Interpretation
- `output.json` contains, for each strategy:
  - `total_cash`: Total cash spent to fill the order.
  - `avg_fill_px`: Average price per share filled.
  - `total_fill`: Total shares filled.
- `results.png` is a bar plot comparing total cost for each strategy.
- Use these outputs to compare the SOR allocator to baseline strategies under identical market conditions.

## Reproducibility
- All random seeds (for latency/adverse selection) are set in code for reproducibility.
- All parameters are controlled via `config.py` and command-line arguments.
- Dry-run mode allows full testing without Kafka or EC2.

## EC2 Deployment Instructions

### 1. Launch EC2 Instance
- Recommended type: `t3.micro` (for testing) or larger for full dataset.
- OS: Ubuntu 24.04 LTS (or similar).
- Open ports 22 (SSH), 9092 (Kafka), 2181 (Zookeeper) in AWS Security Group.

### 2. Install System Dependencies
```sh
sudo apt update && sudo apt install -y python3 python3-venv python3-pip openjdk-11-jre-headless wget unzip
```

### 3. Install and Start Kafka/Zookeeper
```sh
wget https://downloads.apache.org/kafka/3.6.0/kafka_2.13-3.6.0.tgz
 tar -xzf kafka_2.13-3.6.0.tgz
 export KAFKA_DIR=$(pwd)/kafka_2.13-3.6.0
 # Start Zookeeper
 $KAFKA_DIR/bin/zookeeper-server-start.sh -daemon $KAFKA_DIR/config/zookeeper.properties
 # Start Kafka
 $KAFKA_DIR/bin/kafka-server-start.sh -daemon $KAFKA_DIR/config/server.properties
 # Create topic
 $KAFKA_DIR/bin/kafka-topics.sh --create --topic mock_l1_stream --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

### 4. Clone This Repo and Prepare Python
```sh
git clone https://github.com/eshan327/Cont-Kukanov-SOR
cd Cont-Kukanov-SOR
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 5. Upload Dataset
- Use `scp` or AWS S3 to copy `l1_day.csv` to the EC2 instance root directory.

### 6. Run the Producer and Backtester
```sh
# In one terminal (producer):
python kafka_producer.py
# In another terminal (backtester):
python backtest.py
```

### 7. Verify Output
- Check for `output.json` and `results.png` in the project directory.