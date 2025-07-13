import time
import sys

sys.path.append("/home/simon/Python/ETL-1/ETL_pipeline/")
sys.path.append("/home/simon/Python/ETL-1/virtual_machine/")
from machine import Machine
from pipeline import MQTTPipeline

if __name__ == "__main__":
    # define sensors
    sensor_output = ["analog_0to5V", "analog_4to20mA", "digital_8bit"]
    sensor_measurand = ["pressure", "oxygen", "temperature"]

    topics = []
    for topic in sensor_measurand:
        topics.append("sensor_data/" + topic)

    sensor_list = []
    for output, measurand in zip(sensor_output, sensor_measurand):
        sensor_list.append((output, measurand))

    # build machine
    machine_instance = Machine(sensor_list)
    print(machine_instance.sensors_machine)
    machine_instance.init_client()
    machine_instance.init_broker("127.0.0.1", 1883)

    # build ETL pipeline
    pipeline_instance = MQTTPipeline(topics)
    pipeline_instance.init_subscriber()
    pipeline_instance.init_broker("127.0.0.1", 1883)

    # produce data
    machine_instance.start_measurement()
    pipeline_instance.start_to_listen()
    time.sleep(6)
    machine_instance.stop_measurement()
    pipeline_instance.stop_listening()
