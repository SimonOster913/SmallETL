import time
import random
from multiprocessing import Process, Value


class Sensor:
    def __init__(self, output: str, measurand: str) -> None:
        self.output = output
        self.measurand = measurand
        self.running = Value("b", False)
        if self.output == "analog_0to5V" or self.output == "analog_4to20mA":
            self.measured_value = Value("d", 0.0)
        elif self.output == "digital_8bit":
            self.measured_value = Value("i", 0)

    def generate_data(self, running, measured_value):
        """Create output depending on the sensor type in a separate thread."""

        running.value = True
        out = 0

        while running.value:
            if self.output == "analog_0to5V":
                measured_value.value = random.random() * 5

            elif self.output == "analog_4to20mA":
                measured_value.value = random.random() * 16 + 4

            elif self.output == "digital_8bit":
                measured_value.value = random.randint(0, 255)

            else:
                measured_value.value = out

    def start_data_stream(self):
        self.process = Process(
            target=self.generate_data, args=(self.running, self.measured_value)
        )
        self.process.start()

    def stop_data_stream(self):
        self.running.value = False
        self.process.join()
