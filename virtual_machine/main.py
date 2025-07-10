import time
from machine import Machine

if __name__ == "__main__":
    # define sensors
    # sensor_output = ["analog_0to5V", "analog_4to20mA", "digital_8bit"]
    # sensor_frequency = [1, 5, 10]
    # sensor_measurand = ["pressure", "pressure_fine", "temperature"]

    sensor_output = ["digital_8bit"]
    sensor_frequency = [10]
    sensor_measurand = ["temperature"]

    sensor_list = []
    for output, frequency, measurand in zip(
        sensor_output, sensor_frequency, sensor_measurand
    ):
        sensor_list.append((output, frequency, measurand))

    # build machine
    machine_instance = Machine(sensor_list)
    machine_instance.init_client()
    machine_instance.init_broker("127.0.0.1", 1883)

    # produce data
    machine_instance.start_measurement()
    time.sleep(6)
    machine_instance.stop_measurement()
