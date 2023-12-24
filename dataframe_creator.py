import pandas as pd 
import os
import csv
import numpy as np
from collections import defaultdict


def equalization(price,btc_amount,eth_amount):
    btc_value_in_eth = btc_amount * price
    all_assets_value = btc_value_in_eth + eth_amount
    half_value = all_assets_value / 2 
    equalize_btc_amount = half_value / price
    equalize_eth_amount = half_value
    return equalize_btc_amount , equalize_eth_amount

def create_compelete_excel(leverage,time_frame):
    try:
        os.remove(f"prices/btc-eth-lev:{leverage}-timeframe:{time_frame}.csv")
    except:
        pass
    
    df = pd.read_csv(f"prices/btc-eth-{time_frame}h.csv")
    df_new = pd.DataFrame(columns=range(6))
    new_headers = ['time','price','change','btc_amount','eth_amount','value_in_eth']
    df_new.columns = new_headers
    prices = df.iloc[:,1].values.tolist()
    price_changes = [prices[i]-prices[i-1] for i  in range(1,len(prices))]
    price_changes.insert(0,0)
    df_new['time'] = df.iloc[:,0]
    df_new['price'] = df.iloc[:,1]
    df_new['change'].iloc[:] = price_changes
    eth_amounts = []
    for i in range(len(price_changes)):
        if i == 0 :
            eth_amounts=[prices[0]]
            btc_amounts = [1]
        else:
            eth_amount = eth_amounts[i-1]+leverage*price_changes[i]
            btc_amount = btc_amounts[i-1]-leverage*(price_changes[i]/prices[i])
            if eth_amount < 0 or btc_amount < 0:
                btc_amount,eth_amount = equalization(prices[i],btc_amounts[i-1],eth_amounts[i-1])
            eth_amounts.append(eth_amount)
            btc_amounts.append(btc_amount)    
    df_new['eth_amount'] = eth_amounts
    df_new['btc_amount'] = btc_amounts
    values_in_eth = [btc_amounts[i]*prices[i]+eth_amounts[i] for i in range(len(prices))]
    df_new['value_in_eth'] = values_in_eth
    df_new.to_csv(f"reports/btc-eth-lev:{leverage}-timeframe:{time_frame}.csv")

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def get_results():
    dir_path = "./reports"
    # Get list of all files and directories
    entries = os.listdir(dir_path)
    # Filter out directories, only keep files
    reports = [entry for entry in entries if os.path.isfile(os.path.join(dir_path, entry))]
    last_results = defaultdict(dict)
    leverages = []
    time_frames = []
    for report in reports:
        leverages.append(int(find_between(report,"lev:","-timeframe")))
        time_frames.append(int(find_between(report,"timeframe:",".csv")))
    sorted_levarages = list(set(sorted(leverages)))
    sorted_time_frames = list(set(sorted(time_frames)))
    df = pd.DataFrame(np.zeros((len(sorted_time_frames),len(sorted_levarages))),columns=sorted_levarages)
    df.index = sorted_time_frames
    for leverage in sorted_levarages:
        for time_frame in sorted_time_frames:
            data = pd.read_csv(f"reports/btc-eth-lev:{leverage}-timeframe:{time_frame}.csv")
            last_eth_value = data.iloc[-1,-1]
            last_results[leverage][time_frame]=last_eth_value
            df[leverage][time_frame] = last_eth_value
    print(df)
    df.to_csv("./result.csv")
    