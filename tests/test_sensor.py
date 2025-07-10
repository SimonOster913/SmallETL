import unittest
import sys
import time

sys.path.append("/home/simon/Python/ETL-1/virtual_machine")
from sensor import Sensor


class TestSensorMethods(unittest.TestCase):
    def test_sensor_output(self):
        # sensor inputs
        sensor_instance_1 = Sensor("analog_0to5V", "pressure")
        sensor_instance_2 = Sensor("analog_4to20mA", "oxygen")
        sensor_instance_3 = Sensor("digital_8bit", "temperature")

        sensor_list = [sensor_instance_1, sensor_instance_2, sensor_instance_3]

        # start thread to generate data
        for sensor in sensor_list:
            sensor.start_data_stream()

        time.sleep(1)

        output = []
        for sensor in sensor_list:
            output.append(sensor.measured_value.value)
            sensor.stop_data_stream()

        # check type
        self.assertIsInstance(output[0], float)
        self.assertIsInstance(output[1], float)
        self.assertIsInstance(output[2], int)

        # check range
        self.assertGreaterEqual(output[0], 0)
        self.assertLessEqual(output[0], 5)
        self.assertGreaterEqual(output[1], 4)
        self.assertLessEqual(output[1], 20)
        self.assertGreaterEqual(output[2], 0)
        self.assertLessEqual(output[2], 255)


if __name__ == "__main__":
    unittest.main()
