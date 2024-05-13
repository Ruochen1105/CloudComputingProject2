"""
Simulated IoT Device and functions to interact with Azure IoT Hub
Reference: github.com/Azure-Samples/azure-iot-samples-python/blob/master/iot-hub/Quickstarts/simulated-device/SimulatedDeviceSync.py
"""
import os
import random
from datetime import datetime
from time import sleep

from azure.iot.device import IoTHubDeviceClient, Message
from google.cloud import storage

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


class IoT_object():
    def __init__(self):
        storage_client = storage.Client.from_service_account_json(os.getenv("path_to_cred"))
        self._wd = os.getenv("wd")
        self._bucket = storage_client.bucket(os.getenv("bucket_name"))
        self._bucket_name = os.getenv("bucket_name")
        self._connection_string = os.getenv("CONNECTION_STRING")


    def generate_data(self) -> dict:
        generated_data = {"image": None, "longitude": None, "latitude": None}

        all_images = [f"accidents/{i}.png" for i in range(10)] + [f"no_accidents/{i}.png" for i in range(10)]
        selected_image = os.path.join(self._wd, "assets", random.sample(population=all_images, k=1)[0])
        blob_name = str(hash(str(datetime.now()))) + ".png"
        blob = self._bucket.blob(blob_name)
        blob.upload_from_filename(selected_image)

        simulated_latitude = (random.random() - 0.5) * 180    # -90 - 90
        simulated_longitude = (random.random() - 0.5) * 360    # -180 - 180

        generated_data["image"] = blob_name
        generated_data["longitude"] = simulated_longitude
        generated_data["latitude"] = simulated_latitude

        return generated_data


    def upload_to_iot_hub(self):
        client = IoTHubDeviceClient.create_from_connection_string(self._connection_string)

        client.connect()

        MSG_TXT = str(self.generate_data())
        message = Message(MSG_TXT)
        client.send_message(message)
        client.shutdown()
        sleep(10)


def main():
    my_iot_object = IoT_object()
    my_iot_object.upload_to_iot_hub()


if __name__ == '__main__':
    main()