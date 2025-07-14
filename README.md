# SmallETL

This project is a simple **Python ETL pipeline** to process real‑time sensor data.  
Sensor data is generated, sent via **Mosquitto** (MQTT broker), received with **Paho MQTT**, buffered, transformed, and finally stored in a **SQLite** database.

---

## ⚙️ Overview

- **Machine**
  - Simulates multiple sensors (analog and digital).
  - Publishes sensor data continuously via MQTT.
- **ETLPipeline**
  - Receives data as a subscriber.
  - Stores incoming values in topic‑specific buffers.
  - Computes simple statistics (e.g., mean values).
  - Loads the transformed data into a SQLite database.
- **MQTTPipeline**
  - Extends ETLPipeline with MQTT connectivity using Paho.
  - Handles subscriptions to multiple topics in parallel.

---

## 🧰 Technologies Used

- [Mosquitto](https://mosquitto.org/) – lightweight open source MQTT broker
- [Paho MQTT](https://www.eclipse.org/paho/) – Python client library for MQTT
- [SQLite](https://www.sqlite.org/) – file‑based SQL database

---

## 🚀 Getting Started

1. Make sure Mosquitto is installed and running locally.
2. Install Python dependencies:
   ```bash
   pip install paho-mqtt
3. Run the scripts

Run the scripts to:
- Simulate sensors and publish data (`Machine`)
- Subscribe, transform, and store data (`MQTTPipeline`)

## 📦 Project Structure

```text
├── main.py              # Entry point to start publishing & ETL pipeline
├── machine.py           # Simulates sensors and publishes data
├── sensor.py            # Defines Sensor class
├── pipeline.py          # ETL pipeline logic (buffering, transform, load)
└── sensor_data.db       # SQLite database (created at runtime)

