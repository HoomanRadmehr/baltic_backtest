from pathlib import Path
import requests
import json
import datetime
import logging
import csv
import os
import pandas as pd
import datetime

logging.basicConfig(level=logging.INFO)


def gather_prices():
    start_time = int(datetime.datetime.timestamp(datetime.datetime(2023,9,1,0,0,0))*1000)
    end_time = int(datetime.datetime.timestamp(datetime.datetime(2023,11,1,0,0,0))*1000)
    while start_time <= end_time:
        logging.info(f"start gather prices from timestamp:{datetime.datetime.fromtimestamp(start_time/1000)}")
        btc_datas = json.loads(requests.get(f"https://api.binance.com/api/v3/klines?symbol=BTCUSDT&startTime={start_time}&endTime={end_time}&interval=1h").content)
        btc_closes = {}
        for data in btc_datas:
            btc_closes[datetime.datetime.fromtimestamp((float(data[6])/1000)+1).strftime('%Y-%m-%d %H:%M:%S')] = float(data[4])
            
        eth_datas = json.loads(requests.get(f"https://api.binance.com/api/v3/klines?symbol=ETHUSDT&startTime={start_time}&endTime={end_time}&interval=1h").content)
        eth_closes = {}
        for data in eth_datas:
            eth_closes[datetime.datetime.fromtimestamp((float(data[6])/1000)+1).strftime('%Y-%m-%d %H:%M:%S')] = float(data[4])
        last_time = list(eth_closes.keys())[-1]
        start_time = int(datetime.datetime.timestamp(datetime.datetime.strptime(last_time,'%Y-%m-%d %H:%M:%S')))*1000
        with open(f'btc.csv','a') as hist_file:        
            closes_btc_eth = {}
            for key ,value in btc_closes.items():
                if eth_closes[key]:
                    closes_btc_eth[key]=btc_closes[key]/eth_closes[key]
            writer = csv.writer(hist_file)
            for key, value in closes_btc_eth.items():
                writer.writerow([key, value])
    hist_file.close()        
    return btc_closes,eth_closes
        
        
def resample_timeframe(time_frame):
    path = Path("./btc.csv")
    try:
        os.remove(f"prices/btc-eth-{time_frame}h.csv")
    except:pass
    if not path.is_file():
        btc_closes,eth_closes = gather_prices()
        with open(f'prices/btc-eth-{time_frame}h.csv','a') as hist_file:        
            closes_btc_eth = {}
            i=0
            for key ,value in btc_closes.items():
                if i%time_frame == 0:
                    if eth_closes[key]:
                        closes_btc_eth[key]=btc_closes[key]/eth_closes[key]
                i+=1
            
            writer = csv.writer(hist_file)
            for key, value in closes_btc_eth.items():
                writer.writerow([key, value])
        hist_file.close()        
    else:
        datas = pd.read_csv("btc.csv")
        dates = datas.iloc[:,0].tolist()
        prices = datas.iloc[:,1].tolist()
        closes_btc_eth = {}
        i = 0
        for i in range(len(prices)):
            if i%time_frame == 0:
                closes_btc_eth[dates[i]]=prices[i]
            i+=1        
        with open(f'prices/btc-eth-{time_frame}h.csv','a') as hist_file:        
            writer = csv.writer(hist_file)
            for key, value in closes_btc_eth.items():
                writer.writerow([key, value])
        hist_file.close()        
