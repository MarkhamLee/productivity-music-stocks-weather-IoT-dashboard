# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# This script retrieves the next day forecast from the Openweather API

from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.models import Variable


default_args = {
    "owner": "airflow",
    "start_date": datetime(2023, 10, 30),
    "retries": 1,
}


def send_alerts(context: dict):

    from plugins.slack_utilities import SlackUtilities
    slack_utilities = SlackUtilities()

    webhook_url = Variable.get('slack_hook_alerts')

    slack_utilities.send_slack_webhook(webhook_url, context)


@dag(schedule=timedelta(hours=12), default_args=default_args, catchup=False,
     on_failure_callback=send_alerts)
def openweather_weather_forecast_dag():

    from open_weather.weather_utilities import WeatherUtilities  # noqa: E402
    utilities = WeatherUtilities()

    @task
    def get_forecast():

        ENDPOINT = 'forecast?'
        # key for OpenWeather API
        WEATHER_KEY = Variable.get('open_weather_secret')

        # create URL
        url = utilities.build_url_weather(WEATHER_KEY, ENDPOINT)

        # get data from API
        return utilities.get_weather_data(url)

    @task(multiple_outputs=True)
    def parse_forecast_data(data: dict) -> dict:

        # split off next day's forecast
        tomorrow_forecast = data['list'][0]

        # forecast two days out, commenting out for now
        # may use this later.
        # two_day_forecast = data['list'][1]

        # parse out forecast data
        return utilities.weather_parser(tomorrow_forecast)

    @task(retries=2)
    def write_data(data: dict):

        from plugins.influx_client import InfluxClient  # noqa: E402
        influx = InfluxClient()

        from influxdb_client import Point  # noqa: E402

        # influx DB variables
        INFLUX_KEY = Variable.get('influx_db_key_secret')
        ORG = Variable.get('influx_org')
        URL = Variable.get('influx_url')
        BUCKET = Variable.get('dashboard_bucket')

        # get the client for connecting to InfluxDB
        client = influx.influx_client(INFLUX_KEY, ORG, URL)

        # not the most elegant solution, will change later
        # to write json directly
        point = (
            Point("weather_forecasts")
            .tag("OpenWeatherAPI", "weather_forecast")
            .field("predicted_temp", data['temp'])
            .field("predicted_weather", data['weather'])
            .field("predicted_low", data['temp_low'])
            .field("predicted_high", data['temp_high'])
            .field("predicted_barometric_pressure", data['pressure'])
            .field("predicted_humidity", data['humidity'])
            .field("predicted_wind", data['wind_speed'])
            .field("time_stamp", data['timestamp'])
        )

        client.write(bucket=BUCKET, org=ORG, record=point)

    # nesting the methods establishes the hiearchy and creates the tasks
    write_data(parse_forecast_data(get_forecast()))


openweather_weather_forecast_dag()
