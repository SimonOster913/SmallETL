import random
import threading
import time
from paho.mqtt import client as mqtt_client


class machine:
    def __init__(self, sensor_list):
        self.sensor_list = sensor_list
        self.publishing = False
        self.init_sensors(self.sensor_list)

    def init_sensors(self, sensor_list):
        """Instanciate sensor objects.

        Args:
            sensor_list (list of tuples): Hold information about sensors in the form (type, frequency).
        """

        self.sensors_machine = list()

        for output, frequency, measurand in sensor_list:
            sensor_instance = sensor(output, frequency, measurand)
            self.sensors_machine.append(sensor_instance)

    def init_client(self):
        """Set up mqtt client for connection with broker."""

        client_id = f"python-mqtt-{random.randint(0, 1000)}"

        # callback function when client receives a CONNACK response from the server
        def on_connect(client, userdata, flags, reason_code, properties):
            if reason_code == 0:
                print("Connected to MQTT Broker")
            else:
                print("Failed to connect, return code %d/n", rc)

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

    def connect_to_broker(self):
        """Connect client to broker."""

        broker = "127.0.0.1"
        port = 1883
        if hasattr(self, "client"):
            self.client.connect(broker, port)
        else:
            AttributeError("Client not initiated yet")

    def disconnect_from_broker(self):
        """Disconnect client from broker."""

        if hasattr(self, "client"):
            self.client.disconnect()
        else:
            AttributeError("Client not initiated yet")

    def publish_data(self):
        """Generate virtual sensor data and publish it in topic via mqtt broker."""

        while self.publishing:
            for sensor, thread, topic in self.workers:
                sensor_value = sensor.sensor_value
                print(sensor_value)
                self.client.publish(topic, sensor_value)

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


class sensor:
    def __init__(self, output, data_frequency, measurand):
        self.output = output
        self.data_frequency = data_frequency
        self.measurand = measurand
        self.running = False
        self.sensor_value = None

    def generate_data(self):
        """Create output depending on the sensor type."""

        pause = 1 / self.data_frequency  # in sec
        self.running = True

        while self.running:
            out = 0

            if self.output == "analog_0to5V":
                self.sensor_value = random.random() * 5

            elif self.output == "analog_4to20mA":
                self.sensor_value = random.random() * 16 + 4

            elif self.output == "digital_8bit":
                self.sensor_value = random.randint(0, 255)

            else:
                self.sensor_value = out

            time.sleep(pause)


# main
if __name__ == "__main__":
    # define sensors
    sensor_output = ["analog_0to5V", "analog_4to20mA", "digital_8bit"]
    sensor_frequency = [1, 10, 100]
    sensor_measurand = ["pressure", "pressure_fine", "temperature"]

    sensor_list = []
    for output, frequency, measurand in zip(
        sensor_output, sensor_frequency, sensor_measurand
    ):
        sensor_list.append((output, frequency, measurand))

    # build machine
    machine_1 = machine(sensor_list)
    machine_1.init_client()

    # produce data
    machine_1.start_measurement()
    time.sleep(3)
    machine_1.stop_measurement()
