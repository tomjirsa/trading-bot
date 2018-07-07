from database.sqlite import Database
from strategy.basic import BasicStrategy
from datetime import datetime
import json
import os
import inspect


def main():

    path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    config={}
    with open(path + '/config.json', 'r') as f:
        config = json.load(f)

    log_record = datetime.now().isoformat()

    strategy = BasicStrategy(config["common"]["database"])
    trend = strategy.getFutureTrend(config["common"]["trading_pair"],config["strategy"]["basic"])

    investment_coef = 0.5

    # Ledger
    table_name = "ledger_"+ config["common"]["trading_pair"]

    conn = Database(path + "/" + config["common"]["database"])
    if config["trading"]["ledger"]["init"] == 0:
        conn.createTable(table_name, config["trading"]["ledger"]["table_definition"])
        conn.insertRecord(table_name,config["trading"]["ledger"]["table_init"])
        config["trading"]["ledger"]["init"] = 1
        with open(path + '/config.json', "w") as jsonFile:
            jsonFile.write(json.dumps(config, indent=4, sort_keys=True))
        jsonFile.close()

    last_ledger = conn.getLastInserted(table_name)
    last_ticker = conn.getLastInserted(config["common"]["trading_pair"])



    if last_ledger["position"] == "wait_buy" and last_ticker["bid"] < last_ledger["btc_usd"] and trend == 1:
        log_record = log_record + " Buy "
        usd_to_spend = last_ledger["usd_current"]*investment_coef
        btc_to_buy = usd_to_spend/last_ticker["bid"]
        usd_current = last_ledger["usd_current"] - usd_to_spend
        btc_current = last_ledger["btc_current"] + btc_to_buy
        current_value = usd_current + btc_current * last_ledger["mid"]

        leder_record = {
            "timestamp": last_ticker["timestamp"],
            "btc": btc_to_buy,
            "btc_current": btc_current,
            "usd": -1*usd_to_spend,
            "usd_current": usd_current,
            "btc_usd": last_ticker["bid"],
            "position": "wait_sell",
            "current_value": current_value
          }
        conn.insertRecord(table_name,leder_record)
    elif last_ledger["position"] == "wait_sell" and last_ticker["ask"] > last_ledger["btc_usd"] and trend == -1:
        log_record = log_record + " Sell "
        btc_to_spend = last_ledger["btc_current"]
        usd_to_buy = last_ticker["bid"] * btc_to_spend
        usd_current = last_ledger["usd_current"] + usd_to_buy
        btc_current = last_ledger["btc_current"] - btc_to_spend
        current_value = usd_current + btc_current * last_ledger["mid"]

        leder_record = {
            "timestamp": last_ticker["timestamp"],
            "btc": -1*btc_to_spend,
            "btc_current": btc_current,
            "usd": usd_to_buy,
            "usd_current": usd_current,
            "btc_usd": last_ticker["bid"],
            "position": "wait_buy",
            "current_value": current_value
        }
        conn.insertRecord(table_name,leder_record)
    else:
        log_record = log_record + " Wait "

    log_record = log_record + ", Ledger " + str(last_ledger) + " Ticker " + str(last_ticker) + " Trend "  + str(trend)
    print log_record

    conn.closeConnection()

if __name__ == '__main__':
    main()