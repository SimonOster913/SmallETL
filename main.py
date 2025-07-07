import random
import threading
import time


class machine:
    def __init__(self, sensor_list, frequencies_hertz):
        self.sensor_list = sensor_list
        self.frequencies_hertz = frequencies_hertz
        self.init_sensors(self.sensor_list, self.frequencies_hertz)

    def init_sensors(self, sensor_list, frequencies_hertz):
        """Instanciate sensor objects.

        Args:
            sensor_list (list): Hold information about number of sensors and their type.
        """

        self.sensors_machine = list()

        for sensor_type, frequency in zip(sensor_list, frequencies_hertz):
            sensor_instance = sensor(sensor_type, frequency)
            self.sensors_machine.append(sensor_instance)

    def start_measurement(self):
        """Start a thread for each sensor. Call the thread depending on the sensor frequency."""

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
    sensor_list = ["analog_0to5V", "analog_4to20mA", "digital_8bit"]
    frequencies_hertz = [1, 10, 100]
    machine_1 = machine(sensor_list, frequencies_hertz)
    machine_1.start_measurement()
    time.sleep(3)
    machine_1.stop_measurement()
