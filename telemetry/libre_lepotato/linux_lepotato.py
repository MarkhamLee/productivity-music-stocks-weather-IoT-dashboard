# Markham Lee (C) 2023
# Class with data retrieval and utility methods to support pulling hardware
# data from a Libre LePotato Single Board Computer
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard


import psutil
import uuid
import logging
from paho.mqtt import client as mqtt


# setup logging for static methods
logging.basicConfig(filename='hardwareData.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s\
                        : %(message)s')


class LibreCpuData():

    def __init__(self):

        # get the # of cores, as we can use that to iterate through and
        # get things like current speed for all CPU cores
        self.coreCount = psutil.cpu_count(logical=False)

    # get average clock speed for all cores
    def getFreq(self, all_cpu=False):

        allFreq = psutil.cpu_freq(percpu=all_cpu)[0]
        allFreq = round(allFreq, 1)

        return allFreq, self.coreCount

    # CPU load
    def getCPUData(self):

        cpuUtil = (psutil.cpu_percent(interval=1))
        cpuUtil = round(cpuUtil, 1)

        return cpuUtil

    # get current RAM used
    def getRamData(self):

        ramUse = (psutil.virtual_memory()[3]) / 1073741824
        ramUse = round(ramUse, 2)

        return ramUse

    @staticmethod
    def libre_lepotato_temps():

        return psutil.sensors_temperatures()['scpi_sensors'][0].current

    @staticmethod
    def getClientID():

        clientID = str(uuid.uuid4())

        return clientID

    @staticmethod
    def mqttClient(clientID: str, username: str, pwd: str,
                   host: str, port: int):

        def connectionStatus(client, userdata, flags, code):

            if code == 0:
                print('connected')

            else:
                print(f'connection error: {code} retrying...')
                logging.DEBUG(f'connection error occured, return code: {code}')

        client = mqtt.Client(clientID)
        client.username_pw_set(username=username, password=pwd)
        client.on_connect = connectionStatus

        code = client.connect(host, port)

        # this is so that the client will attempt to reconnect automatically/
        # no need to add reconnect
        # logic.
        client.loop_start()

        return client, code
