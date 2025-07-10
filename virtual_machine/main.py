import time
from machine import Machine

if __name__ == "__main__":
    # define sensors
    sensor_output = ["analog_0to5V", "analog_4to20mA", "digital_8bit"]
    sensor_measurand = ["pressure", "oxygen", "temperature"]

    sensor_list = []
    for output, measurand in zip(sensor_output, sensor_measurand):
        sensor_list.append((output, measurand))

    # build machine
    machine_instance = Machine(sensor_list)
    print(machine_instance.sensors_machine)
    machine_instance.init_client()
    machine_instance.init_broker("127.0.0.1", 1883)

    # produce data
    machine_instance.start_measurement()
    time.sleep(6)
    machine_instance.stop_measurement()
