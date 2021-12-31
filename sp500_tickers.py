import json

def sp500_ticker_list():
    f = open('../data/sp500_tickers/sp500.json')
    # f = open('../../sp500.json')
    data = json.load(f)
    # tickers = data[0]['ticker']
    tickers = []
    for j in data:
        tick = j['ticker']
        tickers.append(tick)
    
    f.close()
    return tickers 