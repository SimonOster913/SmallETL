import unittest
import sys
import random
import string
import subprocess
import time
import threading
from paho.mqtt import client as mqtt_client

sys.path.append("/home/simon/Python/ETL-1/ETL_pipeline")
from pipeline import mqtt_pipeline


def start_mosquitto():
    """Starts the Mosquitto broker."""
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


def publish_value_in_topic(adress: str, port: int, topic: str, value: int):
    """_summary_

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


class TestPipelineMethods(unittest.TestCase):
    def test_basic_subscription(self):
        """Test if a basic subscription from MQTT broker is succesfull."""

        # create a random topic
        subtopic = "".join(random.choices(string.ascii_letters + string.digits, k=8))
        topic = "test_topic/" + subtopic

        print(topic)
        # create random value
        value_to_publish = random.randint(0, 1000)

        # set up broker
        adress = "127.0.0.1"
        port = 1883

        # setup pipeline
        pipeline = mqtt_pipeline([topic])
        pipeline.init_subscriber()
        pipeline.init_broker(adress, port)
        pipeline.start_to_listen()

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

        pipeline.stop_listening()

        output = pipeline.last_values[topic]

        # check result
        self.assertEqual(value_to_publish, int(output))


if __name__ == "__main__":
    start_mosquitto()
    unittest.main()
