#!/usr/bin/python
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt

def on_message(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))
    print("message topic: ", message.topic)
    print("message received: ", msg)

def on_connect(client, userdata, flags, rc):
    client.subscribe('/inkplate/#')

BROKER_ADDRESS = "localhost"

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER_ADDRESS)

print("Connected to MQTT Broker: " + BROKER_ADDRESS)

client.loop_forever()

