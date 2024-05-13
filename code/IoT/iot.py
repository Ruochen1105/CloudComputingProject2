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

import local_config


class IoT_object():
    def __init__(self):
        path_to_cred = local_config.path_to_cred
        storage_client = storage.Client.from_service_account_json(path_to_cred)
        self._wd = local_config.wd
        self._bucket = storage_client.bucket(local_config.bucket_name)
        self._bucket_name = local_config.bucket_name
        self._connection_string = local_config.CONNECTION_STRING


    @property
    def wd(self):
        return self._wd


    @property
    def bucket_name(self):
        return self._bucket_name


    @property
    def connection_string(self):
        return self._connection_string


    @property
    def bucket(self):
        return self._bucket


    def generate_data(self) -> dict:
        generated_data = {"image": None, "longtitude": None, "latitude": None}

        all_images = [f"accidents/{i}.png" for i in range(10)] + [f"no_accidents/{i}.png" for i in range(10)]
        selected_image = os.path.join(self.wd, "assets", random.sample(population=all_images, k=1)[0])
        blob_name = str(hash(str(datetime.now()))) + ".png"
        blob = self.bucket.blob(blob_name)
        blob.upload_from_filename(selected_image)

        simulated_latitude = (random.random() - 0.5) * 180    # -90 - 90
        simulated_longtitude = (random.random() - 0.5) * 360    # -180 - 180

        generated_data["image"] = f"https://storage.cloud.google.com/{self.bucket_name}/{blob_name}"
        generated_data["longtitude"] = simulated_longtitude
        generated_data["latitude"] = simulated_latitude

        return generated_data


    def upload_to_iot_hub(self):
        client = IoTHubDeviceClient.create_from_connection_string(self.connection_string)

        client.connect()

        for i in range(5):
            MSG_TXT = str(self.generate_data())
            message = Message(MSG_TXT)
            client.send_message(message)
            print("Message successfully sent")
            sleep(10)

        client.shutdown()


def main():
    my_iot_object = IoT_object()
    my_iot_object.upload_to_iot_hub()


if __name__ == '__main__':
    main()