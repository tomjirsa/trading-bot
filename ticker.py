from datetime import datetime
from database.sqlite import Database
from rest.bitfinex import BitfinexREST
import json
import os
import inspect


def main():
    path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    config={}
    with open(path + '/config.json', 'r') as f:
            config = json.load(f)


    conn = BitfinexREST()
    pair = config["common"]["trading_pair"]

    # Get ticker
    ticker = conn.query('GET', 'pubticker/' + pair)
    ticker_json = ticker.json()

    # Output for log
    date, asdf = ticker_json["timestamp"].split('.')
    print(datetime.fromtimestamp(int(date)).strftime('%Y-%m-%d %H:%M:%S') + "  Collecting ticker for pair " + pair)

    # Insert into DB
    database = Database(path + "/" + config["common"]["database"])
    database.createTable(pair,config["ticker"]["table_definition"])
    database.insertRecord(pair,ticker_json)
    database.closeConnection()


if __name__ == '__main__':
    main()
