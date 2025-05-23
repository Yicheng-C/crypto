from configparser import ConfigParser
from esun_marketdata import EsunMarketdata
import pandas as pd
import time
import os
from tabulate import tabulate

# 讀取設定檔
config = ConfigParser()
config.read(r'C:\Users\chrischang\Desktop\crypto\config.ini')
sdk = EsunMarketdata(config)

# 登入
sdk.login()

# 取得市場快照的函式
def fetch_market_data(market):
    rest_stock = sdk.rest_client.stock
    response = rest_stock.snapshot.quotes(market=market)

    # 整理成 DataFrame
    data_list = []
    for stock in response['data']:
        # 檢查漲幅條件
        change_percent = stock.get('changePercent', 'N/A')
        if change_percent == 'N/A':
            continue
        
        try:
            change_percent = float(change_percent)
            if change_percent >= 9:  # 修改成大於等於 9%
                data_list.append({
                    '市場': market,
                    '股票名稱': stock.get('name', 'N/A'),
                    '股票代號': stock.get('symbol', 'N/A'),
                   # '開盤價': stock.get('openPrice', 'N/A'),
                   # '最高價': stock.get('highPrice', 'N/A'),
                   # '最低價': stock.get('lowPrice', 'N/A'),
                    '收盤價': stock.get('closePrice', 'N/A'),
                   # '漲跌': stock.get('change', 'N/A'),
                    '漲跌幅 (%)': f"{change_percent:.2f}%",
                    '成交量': f"{int(stock.get('tradeVolume', 0)):,}",
                   # '成交金額': f"{int(stock.get('tradeValue', 0)):,}"
                })
        except ValueError:
            continue

    # 轉換成 DataFrame
    df = pd.DataFrame(data_list)
    return df

# 每 5 秒更新一次
while True:
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=== 台股漲幅超過 9% 排行榜 ===")

    # 抓取上市和上櫃資料
    tse_df = fetch_market_data('TSE')
    otc_df = fetch_market_data('OTC')

    # 合併兩個市場的資料
    result_df = pd.concat([tse_df, otc_df])

    # 排序並顯示
    if not result_df.empty:
        result_df = result_df.sort_values(by='漲跌幅 (%)', ascending=False)
        
        # 使用 tabulate 進行格式化顯示
        print(f"\n總共有 {len(result_df)} 檔漲幅超過 9%：\n")
        print(tabulate(result_df, headers='keys', tablefmt='fancy_grid', showindex=False))

    else:
        print("目前沒有超過 9% 漲幅的股票。")

    # 等待 5 秒後刷新
    time.sleep(5)
