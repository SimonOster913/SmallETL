import random
import threading
import time
from paho.mqtt import client as mqtt_client


class machine:
    def __init__(self, sensor_list):
        self.sensor_list = sensor_list
        self.init_sensors(self.sensor_list)

    def init_sensors(self, sensor_list):
        """Instanciate sensor objects.

        Args:
            sensor_list (list of tuples): Hold information about sensors in the form (type, frequency).
        """

        self.sensors_machine = list()

        for sensor_type, frequency in sensor_list:
            sensor_instance = sensor(sensor_type, frequency)
            self.sensors_machine.append(sensor_instance)

    def connect_to_broker(self):
        broker = "127.0.0.1"
        port = 1883
        topic = "python/mqtt"
        client_id = f"python-mqtt-{random.randint(0, 1000)}"

        # callback function when client receives a CONNACK response from the server
        def on_connect(client, userdata, flags, rc, properties):
            if rc == 0:
                print("Connected to MQTT Broker")
            else:
                print("Failed to connect, return code %d/n", rc)

        # callback for when a PUBLISH message is received from the server
        def on_message(client, userdata, msg):
            print(msg.topic + " " + str(msg.payload))

        self.client = mqtt_client.Client(
            client_id=client_id,
            callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2,
        )
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.connect(broker, port)
        self.client.loop_start()

    def disconnect_from_broker(self):
        if hasattr(self, "client"):
            self.client.loop_stop()
            print("Disconnected from MQTT Broker")
        else:
            AttributeError("Client not initiated yet")

    def publish_data(self):
        pass

    def start_measurement(self):
        """Start a thread for each sensor."""

        self.workers = []
        for sensor in self.sensors_machine:
            thread = threading.Thread(target=sensor.generate_data)
            self.workers.append((sensor, thread))

        for sensor, thread in self.workers:
            thread.start()

    def stop_measurement(self):
        for sensor, thread in self.workers:
            sensor.running = False

        for sensor, thread in self.workers:
            thread.join()


class sensor:
    def __init__(self, type, data_frequency):
        self.type = type
        self.data_frequency = data_frequency
        self.running = False
        self.sensor_value = None

    def generate_data(self):
        """Create output depending on the sensor type."""

        pause = 1 / self.data_frequency  # in sec
        self.running = True

        while self.running:
            out = 0

            if self.type == "analog_0to5V":
                self.sensor_value = random.random() * 5

            elif self.type == "analog_4to20mA":
                self.sensor_value = random.random() * 16 + 4

            elif self.type == "digital_8bit":
                self.sensor_value = random.randint(0, 255)

            else:
                self.sensor_value = out

            time.sleep(pause)
            print(self.sensor_value)


# main
if __name__ == "__main__":
    sensor_list = [("analog_0to5V", 1), ("analog_4to20mA", 10), ("digital_8bit", 100)]
    machine_1 = machine(sensor_list)
    # machine_1.connect_to_broker()
    machine_1.disconnect_from_broker()
    print(machine_1.client)
    # machine_1.start_measurement()
    # time.sleep(3)
    # machine_1.stop_measurement()
