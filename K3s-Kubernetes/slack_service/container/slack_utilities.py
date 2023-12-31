# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Utility script for connecting to the Slack API to post messages/alerts to a
# Slack channel.
# Current plan is to use this for alerting related to IoT devices,
# monitoring HW and to alert me if an Airflow pipeline fails.
# This file is basically a baseline Slack client, expect the variants used for
# Airflow vs say IoT to drift apart over time.

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import logging
import requests
import os


# setup logging for static methods
logging.basicConfig(filename='slack_alerts.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s\
                        : %(message)s')


class SlackUtilities():

    def __init__(self):

        # get secret
        self.secret = os.environ.get("SLACK_SECRET")

        # create client
        self.client = WebClient(self.secret)

    # generic method to send a slack message, to the specified channel
    def send_slack_message(self, message: str, channel: str) -> dict:

        try:
            response = self.client.chat_postMessage(text=message,
                                                    channel=channel)
            return {"Message sent status": response.get('ok', False)}

        except SlackApiError as e:
            logging.debug(f"an error occured with error {e.response['error']}")
            return {"Message sent status": response.get('ok', False),
                    "Error Message": e.response['error']}

    # the web hook only sends to a specific channel
    def send_slack_webhook(url: str, message: dict):

        headers = {
            'Content-type': 'application/json'

        }

        response = requests.post(url, headers=headers, json=message)

        if response.status_code != 200:
            logging.debug(f'publishing of slack alert failed, \
                status code: {response.status_code}')

        return response.status_code
