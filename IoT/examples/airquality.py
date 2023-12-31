# !/usr/bin/env python
# Markham Lee (C) 2023
# Python script for receiving Air Quality data from
# a Nova PM SDS011 air quality sensor
# Productivity/Personal Dashboard:
# https://github.com/MarkhamLee/personal_dashboard

import serial


class AirQuality:

    def __init__(self):

        # create variables
        self.defineVariables()

    def defineVariables(self):

        self.serialConnection = serial.Serial('/dev/ttyUSB0')

        self.pm2Bytes = 2
        self.pm10Bytes = 4
        self.deviceID = 6

    def getAirQuality(self):

        message = self.serialConnection.read(10)

        # outputs have to be scaled by 0.1 to properly capture the
        # sensor's precision as it returns integers that are actually
        # decimals I.e. 15 is really 1.5

        pm2 = round((self.parse_value(message, self.pm2Bytes) * 0.1), 4)
        pm10 = round((self.parse_value(message, self.pm10Bytes) * 0.1), 4)

        return pm2, pm10

    def parse_value(self, message, start_byte, num_bytes=2,
                    byte_order='little', scale=None):

        """Returns a number from a sequence of bytes."""
        value = message[start_byte: start_byte + num_bytes]
        value = int.from_bytes(value, byteorder=byte_order)
        value = value * scale if scale else value

        return value
