import unittest
import sys
import threading
import time

sys.path.append("/home/simon/Python/ETL-1/virtual_machine")
from sensor import Sensor


class TestSensorMethods(unittest.TestCase):
    def test_sensor_output(self):
        # sensor inputs
        sensor_instance_1 = Sensor("analog_0to5V", 1, "pressure")
        sensor_instance_2 = Sensor("analog_4to20mA", 7, "oxygen")
        sensor_instance_3 = Sensor("digital_8bit", 100, "temperature")

        sensor_list = [sensor_instance_1, sensor_instance_2, sensor_instance_3]

        # start thread to generate data
        threads = []
        for sensor in sensor_list:
            gererator_thread = threading.Thread(target=sensor.generate_data)
            threads.append((gererator_thread, sensor))

        for thread, sensor in threads:
            thread.start()

        time.sleep(1)

        output = []
        for thread, sensor in threads:
            sensor.running = False
            output.append(sensor.sensor_value)
            thread.join()

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
