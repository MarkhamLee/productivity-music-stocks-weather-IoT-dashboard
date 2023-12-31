import os
import logging
from finnhub_utilities import FinnHubUtilities
from influx_client import InfluxClient  # noqa: E402

# instantiate utilities class
finn_util = FinnHubUtilities()

# setup logging for static methods
logging.basicConfig(filename='stock_error.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s\
                        : %(message)s')


def get_prices(symbol: str):

    try:

        return finn_util.get_stock_data(symbol)

    except Exception as e:
        logging.info(f'stock price data retrieval error: {e}')


def parse_data(data: dict) -> dict:

    return finn_util.parse_stock_data(data)


def write_data(data: dict):

    influx = InfluxClient()

    # Influx DB variables
    INFLUX_KEY = os.environ['INFLUX_KEY']
    ORG = os.environ['INFLUX_ORG']
    URL = os.environ['INFLUX_URL']
    BUCKET = os.environ['BUCKET']

    # get the client for connecting to InfluxDB
    client = influx.create_influx_client(INFLUX_KEY, ORG, URL)

    # base payload
    payload = {
        "measurement": "finnhub_quotes",
        "tags": {
                "finnhub_API": "stock_prices",
        }
    }

    try:
        # write data to InfluxDB
        influx.write_influx_data(client, payload, data, BUCKET)

    except Exception as e:
        logging.info(f'influx write error: {e}')


def main():

    STOCK_SYMBOL = os.environ['STOCK_SYMBOL']
    stock_data = get_prices(STOCK_SYMBOL)

    # parse data into a json payload
    stock_payload = parse_data(stock_data)

    # write data to InfluxDB
    write_data(stock_payload)


if __name__ == '__main__':
    main()
