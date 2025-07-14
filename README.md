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
