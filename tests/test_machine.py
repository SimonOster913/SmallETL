import unittest
import sys
import threading
import time
import random

sys.path.append("/home/simon/Python/ETL-1/virtual_machine")
from machine import Machine


class TestMachineMethods(unittest.TestCase):
    def test_machine_initiation(self):
        number_sensors = random.randint(0, 5)
        sensor_output = ["analog_0to5V", "analog_4to20mA", "digital_8bit"]
        sensor_measurand = ["pressure", "temperature", "oxygen"]

        sensor_list = []
        for i in range(number_sensors):
            idx = random.randint(0, 2)
            sensor_list.append(
                (sensor_output[idx], random.randint(1, 100), sensor_measurand[idx])
            )

        machine_instance = Machine(sensor_list)

        expected_result = len(machine_instance.sensors_machine)
        self.assertEqual(number_sensors, expected_result)


if __name__ == "__main__":
    unittest.main()
