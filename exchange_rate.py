import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import redis
import json
import redis
import pickle

def crawl_data():
    url = 'https://rate.bot.com.tw/xrt?Lang=zh-TW'

    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    # 1.幣別
    currency = []
    for i in soup.find_all(class_='hidden-phone print_show xrt-cur-indent'):
        currency.append(i.text.strip('\r\n'))

    currency_list = []
    for i in range(len(currency)):
        currency_list.append(currency[i][32:(currency[i].index(')'))+1])


    # 2.現金匯率
    cash_exchange_rate = []
    for i in soup.find_all(class_='rate-content-cash text-right print_hide'):
        cash_exchange_rate.append(i.text)

    # 本行買入
    cash_buy = []
    for i in range(0, len(cash_exchange_rate), 2):
        cash_buy.append(cash_exchange_rate[i])

    # 本行賣出
    cash_sell = []
    for i in range(1, len(cash_exchange_rate), 2):
        cash_sell.append(cash_exchange_rate[i])

    df = pd.DataFrame({'Currency':currency_list, 'Cash_Buy':cash_buy, 'Cash_Sell':cash_sell})
    df['Data_Input_Date'] = datetime.today().strftime('%Y-%m-%d')

    return df


def store_data_in_redis():
    # 獲取資料
    df = crawl_data()

    # 連接到Redis服務器
    redis_client = redis.StrictRedis(host='localhost', port=7001)

    if not df.empty:
        # 將DataFrame轉換為bytes，使用pickle模組進行序列化
        data_bytes = pickle.dumps(df)
        # 將序列化的資料存入Redis，使用set命令將資料存入特定的key
        redis_client.set('exchange_rate_dataframe_key', data_bytes)
        print("DataFrame stored in Redis successfully.")
    else:
        print("No data to store.")


store_data_in_redis()



