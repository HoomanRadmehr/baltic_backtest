import pandas as pd 
import os

def create_compelete_excel(leverage,time_frame):
    try:
        os.remove(f"btc-eth-lev:{leverage}-timeframe:{time_frame}.csv")
    except:
        pass
    
    df = pd.read_csv("btc.csv")
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
        else:
            eth_amounts.append(eth_amounts[i-1]+leverage*price_changes[i])
    df_new['eth_amount'] = eth_amounts
    btc_amounts = [1]
    for i in range(1,len(price_changes)):
        btc_amounts.append(btc_amounts[i-1]-leverage*(price_changes[i]/prices[i]))
    df_new['btc_amount'] = btc_amounts
    values_in_eth = [btc_amounts[i]*prices[i]+eth_amounts[i] for i in range(len(prices))]
    df_new['value_in_eth'] = values_in_eth
    df_new.to_csv(f"btc-eth-lev:{leverage}-timeframe:{time_frame}.csv")
