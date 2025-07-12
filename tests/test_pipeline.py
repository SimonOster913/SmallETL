import unittest
import sys
import subprocess

sys.path.append("/home/simon/Python/ETL-1/ETL_pipeline")
from pipeline import mqtt_pipeline


def start_mosquitto():
    """Starts the Mosquitto broker."""
    try:
        process = subprocess.Popen(
            ["mosquitto", "-v"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )
        print("Mosquitto broker started.")

    except FileNotFoundError:
        print("Error: Mosquitto not found. Make sure it's installed and in your PATH.")
    except Exception as e:
        print(f"An error occurred: {e}")


class TestMachineMethods(unittest.TestCase):
    def test_machine_initiation(self):
        pass


if __name__ == "__main__":
    start_mosquitto()
    # unittest.main()
