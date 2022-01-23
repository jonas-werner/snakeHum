###############################################################
#                      __        __  __
#    _________  ____ _/ /_____  / / / /_  ______ ___
#   / ___/ __ \/ __ `/ //_/ _ \/ /_/ / / / / __ `__ \
#  (__  ) / / / /_/ / ,< /  __/ __  / /_/ / / / / / /
# /____/_/ /_/\__,_/_/|_|\___/_/ /_/\__,_/_/ /_/ /_/
#
###############################################################
# Filename: snakeHum.py
# Author: Jonas Werner (https://jonamiki.com)
# Version: 3.0
###############################################################

import os
import glob
import time
import json
from influxdb import InfluxDBClient
import redis
from datetime import datetime
import sys, Adafruit_DHT

# InfluxDB connection details
host        =   "127.0.0.1"
port        =   "8086"
user        =   "someuser"
password    =   "somepass"
dbname      =   "somedb"

# Redis connection details
redisHost   =   "127.0.0.1"
redisPort   =   "6379"


def influxDBconnect():
   influxDBConnection = InfluxDBClient(host, port, user, password, dbname)
   return influxDBConnection


def redisDBconnect():
   redisDBConnection = redis.Redis(host=redisHost, port=redisPort)
   return redisDBConnection


def influxDBwrite(measurement, sensorName, sensorValue):

   timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

   measurementData = [
       {
           "measurement": measurement,
           "tags": {
               "gateway": "snakePi2",
               "location": "Tokyo"
           },
           "time": timestamp,
           "fields": {
               sensorName: sensorValue
           }
       }
   ]

   influxDBConnection.write_points(measurementData, time_precision='ms')



def readDht22():

    rawHum, rawTmp = Adafruit_DHT.read_retry(22, 19)

    humval  = float("{:.2f}".format(rawHum))
    tempval = float("{:.2f}".format(rawTmp))

    return humval, tempval
    # return formHum, formTmp



if __name__ == "__main__":
    influxDBConnection  = influxDBconnect()
    redisDBConnection   = redisDBconnect()


    while True:
        hum, temp = readDht22()
        # Sometimes the DHT11 sensor provides ridiculous spike values which we will ignore as they are invalid
        print("%s: %s   %s: %s" % ("snakeAirTemp", temp, "snakeAirHum", hum))
        if 80 > float(temp) > 14:
           influxDBwrite("DHT22_AirTemp", "Temperature", temp)
           redisDBConnection.mset({"DHT22_AirTemp": temp})
        if 10 < int(hum) < 100:
           influxDBwrite("DHT22_AirHum", "Humidity", hum)
           redisDBConnection.mset({"DHT22_AirHum": hum})
        time.sleep(10)
