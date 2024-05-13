"""
Read the telemetry data sent to the Azure IoT Hub
Reference: github.com/Azure-Samples/azure-iot-samples-python/blob/master/iot-hub/Quickstarts/read-d2c-messages/read_device_to_cloud_messages_sync.py
"""
import json

from azure.eventhub import TransportType
from azure.eventhub import EventHubConsumerClient

import local_config


CONNECTION_STR = local_config.connection_str


def on_event_batch(partition_context, events):
    for event in events:
        print(json.loads(event.body_as_str().replace("\'", "\"")))

    partition_context.update_checkpoint()

def on_error(partition_context, error):
    # Put your code here. partition_context can be None in the on_error callback.
    if partition_context:
        print("An exception: {} occurred during receiving from Partition: {}.".format(
            error,
            partition_context.partition_id
        ))
    else:
        print("An exception: {} occurred during the load balance process.".format(error))


def reader():
    client = EventHubConsumerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        consumer_group="$default",
    )
    while True:
        with client:
            client.receive_batch(
                on_event_batch=on_event_batch,
                on_error=on_error
            )


def main():

    reader()

if __name__ == '__main__':
    main()