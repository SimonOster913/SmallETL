import random
import threading
from sensor import Sensor
import time
from paho.mqtt import client as mqtt_client


class Machine:
    def __init__(self, sensor_list: list[tuple[str, int, str]]) -> None:
        self.sensor_list = sensor_list
        self.publishing = False
        self.client = None
        self.publish_rate = 0.001
        self.init_sensors(self.sensor_list)

    def init_sensors(self, sensor_list):
        """Instanciate sensor objects.

        Args:
            sensor_list (list of tuples): Hold information about sensors in the form (type, frequency).
        """

        self.sensors_machine = list()

        for output, frequency, measurand in sensor_list:
            sensor_instance = Sensor(output, frequency, measurand)
            self.sensors_machine.append(sensor_instance)
            print(self.sensors_machine)

    def init_client(self):
        """Set up mqtt client for connection with broker."""

        client_id = f"python-mqtt-{random.randint(0, 1000)}"

        # callback function when client receives a CONNACK response from the server
        def on_connect(client, userdata, flags, reason_code, properties):
            if reason_code == 0:
                print("Connected to MQTT Broker")
            else:
                print("Failed to connect, return code %d/n", reason_code)

        # callback for when a PUBLISH message is received from the server
        def on_message(client, userdata, msg):
            print(msg.topic + " " + str(msg.payload))

        # callback for when client receives a disconnect response from server
        def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
            if reason_code == 0:
                print("Disconnected from MQTT Broker")
            else:
                print("Failed to disconnect, return code %d/n", reason_code)

        self.client = mqtt_client.Client(
            client_id=client_id,
            callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2,
        )
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.on_disconnect = on_disconnect

    def init_broker(self, adress: str, port: int):
        """Set mqtt broker.

        Args:
            adress (str): TCP adress of broker.
            port (int): Port of broker.
        """
        self.broker_adress = adress
        self.broker_port = port

    def connect_to_broker(self):
        """Connect client to broker."""

        if self.client is not None:
            self.client.connect(self.broker_adress, self.broker_port)
        else:
            raise AttributeError("Client not initiated yet")

    def disconnect_from_broker(self):
        """Disconnect client from broker."""

        if self.client is not None:
            self.client.disconnect()
        else:
            raise AttributeError("Client not initiated yet")

    def publish_data(self):
        """Generate virtual sensor data and publish it in topic via mqtt broker."""

        while self.publishing:
            for sensor, thread, topic in self.workers:
                sensor_value = sensor.sensor_value
                self.client.publish(topic, sensor_value)
                time.sleep(self.publish_rate)

    def start_measurement(self):
        """Start a thread for each sensor and publish data of each sensor in a seperate topic via mqtt."""

        # connect to mqtt broker
        self.connect_to_broker()
        self.client.loop_start()

        self.workers = []
        for sensor in self.sensors_machine:
            topic = "sensor_data/" + sensor.measurand
            thread = threading.Thread(target=sensor.generate_data)
            self.workers.append((sensor, thread, topic))

        for sensor, thread, topic in self.workers:
            thread.start()

        self.publishing = True
        self.publisher_thread = threading.Thread(target=self.publish_data)
        self.publisher_thread.start()

    def stop_measurement(self):
        """Stop all sensor and publishing threads and disconnect from mqtt broker."""

        self.publishing = False

        if hasattr(self, "publisher_thread"):
            self.publisher_thread.join()

        for sensor, thread, topic in self.workers:
            sensor.running = False

        for sensor, thread, topic in self.workers:
            thread.join()

        # close mqtt connection
        self.client.loop_stop()
        self.disconnect_from_broker()
