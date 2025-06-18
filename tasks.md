# Project Task Breakdown: SOR Backtesting System

---

## 🛠️ PHASE 1: Setup & Scaffolding

### Task 1: Create Initial File Structure

* **Description:** Generate empty files with top-level comments.
* **Files:** `allocator.py`, `kafka_producer.py`, `backtest.py`, `config.py`, `utils.py`, `README.md`, `requirements.txt`
* **Done when:** All files exist and import without errors.

### Task 2: Write `requirements.txt`

* **Description:** List dependencies: `numpy`, `pandas`, `kafka-python`, `matplotlib`, `tqdm`.
* **Done when:** `pip install -r requirements.txt` succeeds.

### Task 3: Implement `config.py`

* **Description:** Define constants:

  * `KAFKA_TOPIC`, `ORDER_SIZE`, `CSV_PATH`, `PARAM_GRID`, `START_TIME`, `END_TIME`
* **Done when:** `import config` works and constants are accessible.

---

## 🧩 PHASE 2: Kafka Producer

### Task 4: Parse CSV Data

* **Description:** Read `l1_day.csv` using pandas.
* **Deliverable:** Print first 5 rows and unique timestamps.

### Task 5: Format JSON Snapshots

* **Description:** Convert each row to a JSON-ready dict with required fields.
* **Deliverable:** Print a sample list of dicts.

### Task 6: Publish to Kafka

* **Description:** Stream JSON snapshots to topic `mock_l1_stream` with pacing.
* **Deliverable:** Verify messages via Kafka console consumer.

---

## 📊 PHASE 3: Allocator Logic

### Task 7: Translate Allocator Pseudocode

* **Description:** Implement `allocate(order_size, venues, λ_over, λ_under, θ_queue)` in `allocator.py`.
* **Deliverable:** Function returns a split and cost for supplied mock data.

### Task 8: Write Unit Tests for Allocator

* **Description:** Create 3 test cases in `test_allocator.py`.
* **Deliverable:** All tests pass using `pytest`.

---

## 🧪 PHASE 4: Backtester Core

### Task 9: Build Kafka Consumer

* **Description:** Subscribe to `mock_l1_stream`, group snapshots by timestamp.
* **Deliverable:** Print batches of venue data per timestamp.

### Task 10: Integrate Allocator into Consumer

* **Description:** For each batch, call `allocate()` and accumulate fills.
* **Deliverable:** Print running totals of cash spent and shares filled.

### Task 11: Implement Baselines (TWAP, VWAP, Best Ask)

* **Deliverable:** Functions that, given snapshots, return cost and avg price.

### Task 12: Parameter Grid Search

* **Description:** Loop over parameter grid in `config.PARAM_GRID`, store results.
* **Deliverable:** Print best parameters and corresponding cost.

### Task 13: Compute Savings in bps

* **Description:** Compare optimized cost to each baseline.
* **Deliverable:** Print savings in basis points for Best Ask, TWAP, VWAP.

### Task 14: Serialize Final JSON

* **Description:** Dump results to `output.json` matching spec.
* **Deliverable:** Valid JSON file with `best_parameters`, `optimized`, `baselines`, `savings_vs_baselines_bps`.

---

## ☁️ PHASE 5: EC2 Deployment & Documentation

### Task 15: Write EC2 Setup in `README.md`

* **Description:** Document instance type, Kafka/Zookeeper install, Python setup, run commands.
* **Deliverable:** `README.md` updated with clear instructions.

### Task 16: Add Verification Screenshots

* **Description:** Capture and embed Kafka console, backtest JSON stdout, `uptime`.
* **Deliverable:** Screenshots in `README.md`.

### Task 17 (Bonus): Generate `results.png`

* **Description:** Plot total cost per strategy.
* **Deliverable:** `results.png` saved in repo.
