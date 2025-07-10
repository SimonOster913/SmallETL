import time
import random


class Sensor:
    def __init__(self, output: str, data_frequency: int, measurand: str) -> None:
        self.output = output
        self.data_frequency = data_frequency
        self.measurand = measurand
        self.running = False
        self.sensor_value = None

    def generate_data(self):
        """Create output depending on the sensor type."""

        pause = 1 / self.data_frequency  # in sec
        self.running = True
        out = 0

        while self.running:
            if self.output == "analog_0to5V":
                self.sensor_value = random.random() * 5

            elif self.output == "analog_4to20mA":
                self.sensor_value = random.random() * 16 + 4

            elif self.output == "digital_8bit":
                self.sensor_value = random.randint(0, 255)

            else:
                self.sensor_value = out
            print(pause)
            time.sleep(pause)
