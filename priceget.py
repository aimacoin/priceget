# このプログラムは単独で動く（1ファイルで完結し、他に独自のライブラリ等なし）
# 単独で動かし続けるため。

import hashlib
import hmac
import requests
import urllib.parse
import datetime
import json
import os
import time
import math
from collections import deque
from pprint import pprint
import sys

import pandas as pd
import matplotlib.pyplot as plt

#現在の価格を取得
def zaifPublicApi_trades(currency_pair):

    for _ in range(3):  # 最大3回実行
        try:
            response = requests.get('https://api.zaif.jp/api/1/trades/{0}'.format(currency_pair))
            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            print("trades取得にてエラー 1秒待ってリトライします。　エラーコメント：", e)
            time.sleep(1)

        else:
            j = response.json()
            break  # 失敗しなかった時はループを抜ける
    else:
        print("currency_pair", "trades取得にてエラー Retry orver")
        j=0
        pass  # リトライが全部失敗した時の処理

    return j

#現在の板情報を取得
def zaifPublicApi_depth(currency_pair):
    for _ in range(3):  # 最大3回実行
        try:
            response = requests.get('https://api.zaif.jp/api/1/depth/{0}'.format(currency_pair))
            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            print("currency_pair", "depth取得にてエラー  1秒待ってリトライします。　エラーコメント: ", e)
            time.sleep(1)

        else:
            j = response.json()
            break  # 失敗しなかった時はループを抜ける

    else:
        print("depth取得にてエラー Retry orver")
        j = 0
        pass  # リトライが全部失敗した時の処理

    return j


#
# main

currency_pair = "btc_jpy"
currency_pair2 = "eth_jpy"
currency_pair3 = "zaif_jpy"

# 空のデータフレーム作成
cols = ['last_price_date','price', 'ask', 'ask_amount', 'bid', 'bid_amount', 'get_time']
price_log_pandas = pd.DataFrame(index=[], columns=cols)
btc_price_log_pandas = pd.DataFrame(index=[], columns=cols)
eth_price_log_pandas = pd.DataFrame(index=[], columns=cols)
zaif_price_log_pandas = pd.DataFrame(index=[], columns=cols)


loop =1 # loopするしないをするフラグの初期化（１でループする）

# args = sys.argv # 引数を取得　args = [file名, 引数１,　引数２。。。]

btc_args = "./price_data/btcjpy_zaif_priceget_now.pkl"
eth_args = "./price_data/etcjpy_zaif_priceget_now.pkl"
zaif_args = "./price_data/zaifjpy_zaif_priceget_now.pkl"


if(os.path.exists(btc_args)):
    btc_price_log_pandas = pd.read_pickle(btc_args)
    eth_price_log_pandas = pd.read_pickle(eth_args)
    zaif_price_log_pandas = pd.read_pickle(zaif_args)

    print("取得中のデータ(_now.pkl)があるので読み出し、追記します")

else:
    print("データがないので新規作成します")


while(loop== 1):

    dt_now = datetime.datetime.now()
    date_now = dt_now.strftime("%m%d")

    btc_trade_data = zaifPublicApi_trades(currency_pair)
    eth_trade_data = zaifPublicApi_trades(currency_pair2)
    zaif_trade_data = zaifPublicApi_trades(currency_pair3)

    btc_depth_data = zaifPublicApi_depth(currency_pair)
    eth_depth_data = zaifPublicApi_depth(currency_pair2)
    zaif_depth_data = zaifPublicApi_depth(currency_pair3)

    get_time = int(time.time())

    #log情報の形に整形

    btc_price_log = [{"last_price_date": btc_trade_data[0]["date"],
                 "price": btc_trade_data[0]["price"],
                 "ask": btc_depth_data["asks"][0][0],
                 "ask_amount": btc_depth_data["asks"][0][1],
                 "bid": btc_depth_data["bids"][0][0],
                 "bid_amount": btc_depth_data["bids"][0][1],
                 "get_time": get_time}]

    new_row = pd.DataFrame(data=btc_price_log, columns=cols)
    btc_price_log_pandas = btc_price_log_pandas.append(new_row, ignore_index=True)


    eth_price_log = [{"last_price_date": eth_trade_data[0]["date"],
                 "price": eth_trade_data[0]["price"],
                 "ask": eth_depth_data["asks"][0][0],
                 "ask_amount": eth_depth_data["asks"][0][1],
                 "bid": eth_depth_data["bids"][0][0],
                 "bid_amount": eth_depth_data["bids"][0][1],
                 "get_time": get_time}]

    new_row = pd.DataFrame(data=eth_price_log, columns=cols)
    eth_price_log_pandas = eth_price_log_pandas.append(new_row, ignore_index=True)


    zaif_price_log = [{"last_price_date": zaif_trade_data[0]["date"],
                 "price": zaif_trade_data[0]["price"],
                 "ask": zaif_depth_data["asks"][0][0],
                 "ask_amount": zaif_depth_data["asks"][0][1],
                 "bid": zaif_depth_data["bids"][0][0],
                 "bid_amount": zaif_depth_data["bids"][0][1],
                 "get_time": get_time}]

    new_row = pd.DataFrame(data=zaif_price_log, columns=cols)
    zaif_price_log_pandas = zaif_price_log_pandas.append(new_row, ignore_index=True)


    print("btc price log length = ", len(btc_price_log_pandas))
    print("eth price log length = ", len(eth_price_log_pandas))
    print("zaif price log length = ", len(zaif_price_log_pandas))


    if len(btc_price_log_pandas)== 1 + (60 * 24 * 1):
        btc_price_log_pandas = btc_price_log_pandas.drop([0])

    if len(eth_price_log_pandas) == 1 + (60 * 24 * 1):
        eth_price_log_pandas = eth_price_log_pandas.drop([0])

    if len(zaif_price_log_pandas) == 1 + (60 * 24 * 1):
        zaif_price_log_pandas = zaif_price_log_pandas.drop([0])

    btc_price_log_pandas.to_pickle(btc_args)
    btc_price_log_pandas.to_pickle(btc_args + "_" + date_now)

    eth_price_log_pandas.to_pickle(eth_args)
    eth_price_log_pandas.to_pickle(eth_args + "_" + date_now)

    zaif_price_log_pandas.to_pickle(zaif_args)
    zaif_price_log_pandas.to_pickle(zaif_args + "_" + date_now)

    time.sleep(60)
