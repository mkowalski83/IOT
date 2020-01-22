# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import random
import time
import threading
import RPi.GPIO as GPIO

from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse

sensor1=12
light1=False
light2=False
light3=False
diode1=16
diode2=18
diode3=22

GPIO.setmode(GPIO.BOARD)
GPIO.setup(sensor1,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(diode1,GPIO.OUT)
GPIO.setup(diode2,GPIO.OUT)
GPIO.setup(diode3,GPIO.OUT)

# az iot hub device-identity show-connection-string --hub-name {YourIoTHubName} --device-id MyNodeDevice --output table
CONNECTION_STRING = "HostName=cdv-iothub.azure-devices.net;DeviceId=raspberryID;SharedAccessKey=K2oPGnEotVIgEw8ohQ2P17u4SjRbHP6K5FZwbVaoGwk="

# Define the JSON message to send to IoT Hub.
TEMPERATURE = 20.0
SENSORS_TXT = '{{"temperature": {temperature}'
OBSTACLE_TXT = 'Obstacle detected'
INTERVAL = 60


def obstacle_listener(client):
    while True:
        if GPIO.input(sensor1) == 0:
            time.sleep(2)
            if GPIO.input(sensor1) == 0:
                print("Obstacle detected")
                message = Message(OBSTACLE_TXT)
                client.send_message(message)
                time.sleep(5)

def iothub_client_init():
    # Create an IoT Hub client
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    return client


def device_method_listener(device_client):
    global INTERVAL
    global light1
    global light2
    global light3
    while True:
        method_request = device_client.receive_method_request()
        print (
            "\nMethod callback called with:\nmethodName = {method_name}\npayload = {payload}".format(
                method_name=method_request.name,
                payload=method_request.payload
            )
        )
        if method_request.name == "set_interval":
            try:
                INTERVAL = int(method_request.payload)
            except ValueError:
                response_payload = {"Response": "Invalid parameter"}
                response_status = 400
            else:
                response_payload = {"Response": "Executed direct method {}".format(method_request.name)}
                response_status = 200
        #
        elif method_request.name == "diode1":
            try:
                if(light1 == False):
                    GPIO.output(diode1,GPIO.HIGH)
                    light1=True
                else:
                    GPIO.output(diode1,GPIO.LOW)
                    light1=False
            except ValueError:
                response_payload = {"Response": "Invalid parameter"}
                response_status = 400
            else:
                response_payload = {"Response": "Executed direct method {}".format(method_request.name)}
                response_status = 200
        #
        elif method_request.name == "diode2":
            try:
                if(light2 == False):
                    GPIO.output(diode2,GPIO.HIGH)
                    light2=True
                else:
                    GPIO.output(diode2,GPIO.LOW)
                    light2=False
            except ValueError:
                response_payload = {"Response": "Invalid parameter"}
                response_status = 400
            else:
                response_payload = {"Response": "Executed direct method {}".format(method_request.name)}
                response_status = 200
        #
        elif method_request.name == "diode3":
            try:
                if(light3 == False):
                    GPIO.output(diode3,GPIO.HIGH)
                    light3=True
                else:
                    GPIO.output(diode3,GPIO.LOW)
                    light3=False
            except ValueError:
                response_payload = {"Response": "Invalid parameter"}
                response_status = 400
            else:
                response_payload = {"Response": "Executed direct method {}".format(method_request.name)}
                response_status = 200
        else:
            response_payload = {"Response": "Direct method {} not defined".format(method_request.name)}
            response_status = 404

        method_response = MethodResponse(method_request.request_id, response_status, payload=response_payload)
        device_client.send_method_response(method_response)



def iothub_client_telemetry_sample_run():

    try:
        client = iothub_client_init()
        print ( "IoT Hub device sending periodic messages, press Ctrl-C to exit" )

        # Start a thread to listen 
        device_method_thread = threading.Thread(target=device_method_listener, args=(client,))
        device_method_thread.daemon = True
        device_method_thread.start()

        # sensor
        device_method_thread = threading.Thread(target=obstacle_listener, args=(client,))
        device_method_thread.daemon = True
        device_method_thread.start()

        while True:
            temperature = TEMPERATURE + (random.random() * 15)
            SENSORS_TXT_formatted = SENSORS_TXT.format(temperature=temperature)
            message = Message(SENSORS_TXT_formatted)
            message.custom_properties["temperature"] = str(temperature)
            print( "Sending message: {}".format(message) )
            client.send_message(message)
            print( "Message sent" )
            time.sleep(INTERVAL)

    except KeyboardInterrupt:
        print ( "IoTHubClient sample stopped" )

if __name__ == '__main__':
    print ( "IoT Hub Quickstart #2 - Simulated device" )
    print ( "Press Ctrl-C to exit" )
    GPIO.output(diode1,GPIO.LOW)
    GPIO.output(diode2,GPIO.LOW)
    GPIO.output(diode3,GPIO.LOW)
    iothub_client_telemetry_sample_run()