# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import logging
from concurrent.futures import ThreadPoolExecutor
from azure.iot.hub.devicesdk.device_client import DeviceClient
from azure.iot.hub.devicesdk.auth.authentication_provider_factory import from_connection_string

logging.basicConfig(level=logging.ERROR)

# The connection string for a device should never be stored in code. For the sake of simplicity we're using an environment variable here.
conn_str = os.getenv("IOTHUB_DEVICE_CONNECTION_STRING")
# The "Authentication Provider" is the object in charge of creating authentication "tokens" for the device client.
auth_provider = from_connection_string(conn_str)
# For now, the SDK only supports MQTT as a protocol. the client object is used to interact with your Azure IoT hub.
# It needs an Authentication Provider to secure the communication with the hub, using either tokens or x509 certificates
device_client = DeviceClient.from_authentication_provider(auth_provider, "mqtt")


# The connection state callback allows us to detect when the client is connected and disconnected:
def connection_state_callback(status):
    print("connection status: " + status)


# background thread that listens to our queue
# todo: this thread holds a reference to our queue.  We have to figure out shutdown semantics.  The braindead-simple way would be
# # to do a del on the queue which would force the iterable to throw, which is kinda what we want.
def c2d_listener():
    for c2d_message in device_client.messages():
        print("the data in the message received was ")
        print(c2d_message.data)
        print("custom properties are")
        print(c2d_message.custom_properties)


# Register the connection state callback with the client...
device_client.on_connection_state = connection_state_callback

# ... and connect the client.
device_client.connect()

# enable the device to receive c2d messages
device_client.enable_feature("c2d")


executor = ThreadPoolExecutor()
executor.submit(c2d_listener)

while True:
    selection = input("Press Q: Quit for exiting\n")
    if selection is "Q" or selection is "q":
        print("Quitting")
        break

# finally, disconnect
device_client.disconnect()


# The output looks like
#
# connection status: connected
# Press Q: Quit for exiting
# the data in the message received was
# b'weather conditions are windy'
# custom properties are
# {'tornado-alert': 'yes', 'coverage': 'limited'}
# the data in the message received was
# b'weather conditions are windy with chances of snow'
# custom properties are
# {}
# q
# Quitting
# connection status: disconnected
#
# Process finished with exit code 0
