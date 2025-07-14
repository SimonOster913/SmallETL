import random
from paho.mqtt import client as mqtt_client
import sqlite3
import threading
import queue
import statistics
import os
import time


class ETLPipeline:
    def __init__(self, topics: list):
        self.topics = topics
        self.subscriber = None
        self.broker_adress: str = ""
        self.last_values: dict = {}
        self.port: int = 0
        self.init_buffer()

    def init_buffer(self):
        """Build a queue for each topic."""

        self.buffer_dict = {topic: queue.Queue() for topic in self.topics}

    def move_to_buffer(self, topic: str, value):
        """Add a value to a topic-specific buffer."""

        self.buffer_dict[topic].put(value)

    def remove_all_from_buffer(self, topic: str):
        """Return all values to from a topic-specific buffer. Empty the buffer."""

        items = []
        buffer = self.buffer_dict[topic]
        while not buffer.empty():
            try:
                items.append(buffer.get())
            except buffer.empty():
                break

        return items

    def init_db(self):
        """Initiate a SQLite database for starters to store the acquired sensor data."""

        # create db
        self.con = sqlite3.connect("sensor_data.db")
        self.cur = self.con.cursor()

        # create columns based on subscribed topics
        columns = ", ".join([topic.split("/")[1] + " REAL" for topic in self.topics])
        self.cur.execute("DROP TABLE IF EXISTS sensor_data")
        self.cur.execute(f"CREATE TABLE sensor_data({columns})")

    def write_into_db(self, values):
        """Add a new row in the SQLite db with last values.

        Args:
            values (str): Received messages from broker
        """
        insert_topics = ", ".join([topic.split("/")[1] for topic in self.topics])
        placeholders = ", ".join(["?"] * len(values))

        self.cur.execute(
            f"INSERT INTO sensor_data({insert_topics}) VALUES({placeholders})", values
        )

        self.con.commit()

    def delete_db(self):
        """Delete SQLite database permanently"""

        os.remove("sensor_data.db")

    def transform_data(self):
        """Get all topic-wise values from the subscrition buffers.
        Do simple temporal statistics over discrete timestep and
        store result in SQLite db."""

        self.init_db()

        time_start = time.time()
        self.perform_tl = True

        while self.perform_tl:
            time_diff = time.time() - time_start

            if time_diff >= 1:
                mean_value_list = []

                for topic in self.topics:
                    items = self.remove_all_from_buffer(topic)

                    if items:
                        mean_value_list.append(statistics.fmean(items))
                        # std_value = math.stdev(items)
                        # median_value = math.median(items)

                if len(mean_value_list) == len(self.topics):
                    self.write_into_db(mean_value_list)

                time_start = time.time()

    def start_transform_and_load(self):
        """Start transform and load thread."""

        self.tl_thread = threading.Thread(target=self.transform_data)
        self.tl_thread.start()

    def stop_transform_and_load(self):
        """Stop transform and load thread."""

        self.perform_tl = False
        self.tl_thread.join()


class MQTTPipeline(ETLPipeline):
    """ETL pipeline using mqtt protocoll."""

    def __init__(self, topics):
        super().__init__(topics)

    def init_subscriber(self):
        """Define a general paho mqtt subscriber."""

        subscriber_id = f"mqtt_subscriber-{random.randint(0, 1000)}"

        # callback for subscription
        def on_subscribe(client, userdata, mid, reason_code_list, properties):
            if reason_code_list[0].is_failure:
                print(f"Broker rejected you subscription: {reason_code_list[0]}")
            else:
                print(f"Broker granted the following QoS: {reason_code_list[0].value}")

        # callback for unsubscription
        def on_unsubscribe(client, userdata, mid, reason_code_list, properties):
            if len(reason_code_list) == 0 or not reason_code_list[0].is_failure:
                print(
                    "unsubscribe succeeded (if SUBACK is received in MQTTv3 it success)"
                )
            else:
                print(f"Broker replied with failure: {reason_code_list[0]}")
            client.disconnect()

        # callback for messages
        def on_message(client, userdata, message):
            topic = message.topic
            payload = message.payload.decode()
            # print(f"Received from {topic}: {payload}")

            # Beispiel: letzten Wert pro Topic speichern
            self.last_values[topic] = float(payload)
            self.move_to_buffer(topic, float(payload))

            # ADD HERE: Put incoming values into queue

        # callback function when client receives a CONNACK response from the server
        def on_connect(client, userdata, flags, reason_code, properties):
            if reason_code.is_failure:
                print(
                    f"Failed to connect: {reason_code}. loop_forever() will retry connection"
                )
            else:
                print("Connect succesfully to broker.")

        # callback for when client receives a disconnect response from server
        def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
            if reason_code == 0:
                print("Disconnected from MQTT Broker")
            else:
                print("Failed to disconnect, return code %d/n", reason_code)

        subscriber = mqtt_client.Client(
            client_id=subscriber_id,
            callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2,
        )
        subscriber.on_connect = on_connect
        subscriber.on_message = on_message
        subscriber.on_subscribe = on_subscribe
        subscriber.on_unsubscribe = on_unsubscribe
        subscriber.on_disconnect = on_disconnect

        return subscriber

    def init_broker(self, broker_adress: str, port: int):
        """Set mqtt broker."""

        self.broker_adress = broker_adress
        self.broker_port = port

    def subscribe_to_topic(self):
        """Connect mqtt client to a topic and start to listen."""

        self.subscriber = self.init_subscriber()
        self.subscriber.user_data_set([])
        self.subscriber.connect(self.broker_adress, self.broker_port)

        for topic in self.topics:
            self.subscriber.subscribe(topic)

        self.subscriber.loop_start()

    def start_to_listen(self):
        """Connect all subscribers with the broker and start to listen to incoming messages."""

        self.listening_thread = threading.Thread(target=self.subscribe_to_topic)
        self.listening_thread.start()

    def stop_listening(self):
        if hasattr(self, "listening_thread"):
            self.listening_thread.join()

        # close mqtt connection
        self.subscriber.loop_stop()
        self.subscriber.disconnect()
