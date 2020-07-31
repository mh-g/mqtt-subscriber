
#!/usr/bin/python
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
import os
import struct
import rrdtool

temperature = -40.0
pressure = 900.0
humidity = 0.0
battery = 2.5

def rtc_to_rrd(message):
    print ("rtc_to_rrd")
    if (message[0] == 0x12) and (message[1] == 0x34) and (message[2] == 0xcd) and (message[3] == 0xef):
        def get_float(message, index):
            return struct.unpack("f", message[index:(index + 3)])

        with open("/tmp/weather/rtc.bin", "wb") as f:
            f.write(message)

        print ("received valid rtc message")
#        COUNTERPTR = 4
#        STARTPTR = 6
#        ENDPTR = 7
#        DATAOFFSETPTR = 8
#        BUFSIZEINFLOATS = 120
#        i = message[STARTPTR]
#        print (message[STARTPTR], message[ENDPTR], BUFSIZEINFLOATS)
#        while (i < BUFSIZEINFLOATS) and (i != message[ENDPTR]):
#            print (i)
#            print (get_float (message, i * 4))
#            i = i + 1
#            if (i == BUFSIZEINFLOATS):
#                i = message[DATAOFFSETPTR]

    else:
        print ("rtc message malformed")

def on_message_rrd(name, message):
    try:
        global temperature
        global pressure
        global humidity
        global battery
        value = float(message)
        print ("rrd", name, value, flush=True)
        if name == "temperature":
            temperature = value
        if name == "pressure":
            pressure = value
        if name == "humidity":
            humidity = value
        if name == "battery":
            battery = value
        
        rrdtool.update("/srv/dev-disk-by-label-DISK1/localdata/weather.rrd", f"N:{temperature}:{pressure}:{humidity}:{battery}")
        rrdtool.update("/srv/dev-disk-by-label-DISK1/localdata/climate.rrd", f"N:{temperature}:{pressure}:{humidity}:{battery}")
    except ProgrammingError as e:
        print ("Programming error ({0}): {1}".format(e.errno, e.strerror), flush=True)
    except OperationalError as e:
        print ("Operational error ({0}): {1}".format(e.errno, e.strerror), flush=True)
    print ("rrd done", flush=True);
    
def on_message_file(name, message):
    try:
        if not os.path.exists ("/tmp/weather"):
            os.mkdir ("/tmp/weather")
        f = open ("/tmp/weather/"+name, "w")
        f.write (message)
        f.close()
    except IOError as e:
        print ("I/O error({0}): {1}".format(e.errno, e.strerror), flush=True)

def on_message(client, userdata, message):
    print ("incoming: ", message.topic, flush=True)
    name = message.topic.split("/")[2]
    print ("topic name:", name, flush=True)
    if (name != "rtc"):
        msg = str(message.payload.decode("utf-8"))
        print ("topic content:", msg, flush=True)
        on_message_file(name, msg)
        on_message_rrd(name, msg)
#    else:
#        rtc_to_rrd(message.payload)
    print ("topic processed")
    
def on_connect(client, userdata, flags, rc):
    print ("subscribed", flush=True)
    client.subscribe([('/weather/temperature', 0), ('/weather/humidity', 0), ('/weather/pressure', 0), ('/weather/battery', 0), ('/weather/rtc', 0)])

BROKER_ADDRESS = "localhost"

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER_ADDRESS)

print("Connected to MQTT Broker: " + BROKER_ADDRESS, flush=True)

client.loop_forever()

