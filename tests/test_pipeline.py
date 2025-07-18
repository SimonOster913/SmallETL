import unittest
import sys
import random
import string
import subprocess
import time
import threading
from paho.mqtt import client as mqtt_client

sys.path.append("/home/simon/Python/ETL-1/ETL_pipeline")
from pipeline import MQTTPipeline


def start_mosquitto():
    """Start the Mosquitto broker."""

    try:
        process = subprocess.Popen(
            ["mosquitto", "-v"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )
        print("Mosquitto broker started.")

    except FileNotFoundError:
        print("Error: Mosquitto not found. Make sure it's installed and in your PATH.")
    except Exception as e:
        print(f"An error occurred: {e}")


def define_mqtt_client():
    """Initialize an MQTT client.

    Returns:
        MQTT client: Client that can be connected to Mosquitto broker.
    """

    client_id = f"python-mqtt-{random.randint(0, 1000)}"
    client = mqtt_client.Client(
        client_id=client_id,
        callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2,
    )
    return client


def publish_value_in_topic(adress: str, port: int, topic: str, value: int):
    """Publish single value in topic.

    Args:
        adress (str): MQTT broker TCP/IP adress
        port (int): MQTT broker port
        topic (str): Topic to publish in
        value (int): Value to publish
    """

    client = define_mqtt_client()
    client.connect(adress, port)
    client.loop_start()
    client.publish(topic, value)
    time.sleep(0.1)
    client.loop_stop()


def random_sqlite_column_name(length=8):
    first_char = random.choice(string.ascii_letters + "_")
    other_chars = "".join(
        random.choices(string.ascii_letters + string.digits + "_", k=length - 1)
    )
    return first_char + other_chars


class TestPipelineMethods(unittest.TestCase):
    def test_basic_subscription(self):
        """Test if a basic subscription from MQTT broker is succesfull."""

        # create a random topic and value
        subtopic = "".join(random.choices(string.ascii_letters + string.digits, k=8))
        topic = "test_topic/" + subtopic
        value_to_publish = random.randint(0, 1000)

        # set up broker
        adress = "127.0.0.1"
        port = 1883

        # setup pipeline
        pipeline_instance = MQTTPipeline([topic])
        pipeline_instance.init_subscriber()
        pipeline_instance.init_broker(adress, port)
        pipeline_instance.start_to_listen()

        # run mqtt client
        thread = threading.Thread(
            target=publish_value_in_topic,
            args=(
                adress,
                port,
                topic,
                value_to_publish,
            ),
        )
        thread.start()
        thread.join()

        pipeline_instance.stop_listening()

        output = pipeline_instance.last_values[topic]

        # check result
        self.assertEqual(value_to_publish, int(output))

    def test_buffers(self):
        "Test for writing and removing values for a buffer based on topic."

        # get random values and topics
        topics = []
        values = []
        for i in range(random.randint(1, 3)):
            subtopic = random_sqlite_column_name()
            topic = "test_topic/" + subtopic
            topics.append(topic)
            values.append(random.randint(0, 1000))

        # init buffers and write values to specific topics
        pipeline_instance = MQTTPipeline(topics)
        for value, topic in zip(values, topics):
            pipeline_instance.move_to_buffer(topic, value)

        # get all values from each buffer
        items = []
        for topic in topics:
            items.append(pipeline_instance.remove_all_from_buffer(topic))

        expected_output = []
        for value in values:
            expected_output.append([value])

        self.assertListEqual(expected_output, items)

    def test_init_db(self):
        "Test for setting up SQLite db based on topics."

        # create a random topic
        topics = []
        for i in range(random.randint(1, 3)):
            subtopic = random_sqlite_column_name()
            topic = "test_topic/" + subtopic
            topics.append(topic)

        pipeline_instance = MQTTPipeline(topics)
        pipeline_instance.init_db()

        # return all columns in table
        pipeline_instance.cur.execute("PRAGMA table_info(sensor_data)")
        columns = pipeline_instance.cur.fetchall()
        pipeline_instance.con.close()

        # generate expected table content
        expected_output = []
        for idx, topic in enumerate(topics):
            expected_output.append((idx, topic.split("/")[1], "REAL", 0, None, 0))

        # check result
        self.assertListEqual(expected_output, columns)

    def test_write_into_db(self):
        "Test for writing new values into a row in SQLite db based on topics."

        # create a random topic and value
        topics = []
        values = []
        for i in range(random.randint(1, 3)):
            subtopic = random_sqlite_column_name()
            topic = "test_topic/" + subtopic
            topics.append(topic)
            values.append(random.randint(0, 1000))

        pipeline_instance = MQTTPipeline(topics)
        pipeline_instance.init_db()
        pipeline_instance.write_into_db(values)

        # return values from first column
        pipeline_instance.cur.execute("SELECT * FROM sensor_data LIMIT 1")
        columns = pipeline_instance.cur.fetchone()
        pipeline_instance.con.close()

        # check result
        self.assertTupleEqual(tuple(values), columns)


if __name__ == "__main__":
    start_mosquitto()
    unittest.main()
