# Smart Order Router (SOR) Backtesting System

## EC2 Deployment Instructions

### 1. Launch EC2 Instance
- Recommended type: `t3.micro` or `t4g.micro` (for testing; use larger for production)
- OS: Ubuntu 20.04+ or Amazon Linux 2

### 2. Install Java, Kafka, and Zookeeper
```sh
sudo apt update && sudo apt install -y openjdk-11-jre-headless wget
wget https://downloads.apache.org/kafka/3.6.0/kafka_2.13-3.6.0.tgz
 tar -xzf kafka_2.13-3.6.0.tgz
cd kafka_2.13-3.6.0
# Start Zookeeper (in background)
bin/zookeeper-server-start.sh config/zookeeper.properties &
# Start Kafka (in background)
bin/kafka-server-start.sh config/server.properties &
```

### 3. Python Environment Setup
```sh
sudo apt install -y python3 python3-venv python3-pip
cd /path/to/Cont-Kukanov-SOR
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Running the Pipeline
- Start Zookeeper & Kafka (see above)
- In one terminal:
```sh
python kafka_producer.py
```
- In another terminal:
```sh
python backtest.py
```

### 5. Verification
- Use Kafka console consumer to check messages:
```sh
cd kafka_2.13-3.6.0
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic mock_l1_stream --from-beginning
```
- Check `output.json` and stdout for results.
- For system info:
```sh
uname -a
uptime
```

## Verification Screenshots

### Kafka Console Consumer
![Kafka Console Screenshot](screenshots/kafka_console.png)

### Backtest JSON Stdout
![Backtest JSON Screenshot](screenshots/backtest_json.png)

### System Info (uptime)
![Uptime Screenshot](screenshots/uptime.png)