def screen_stock(data, thresholds):
    if data['roe'] is None or data['peg_ratio'] is None:
        return False
    return data['roe'] > thresholds['roe'] and data['peg_ratio'] < thresholds['peg']

def rank_stocks(stocks, top_n=5):
    for stock in stocks:
        roe = stock.get('roe', 0)
        peg = stock.get('peg_ratio', 1)
        stock['score'] = (roe * 0.6) + ((1 / peg) * 0.4)
    return sorted(stocks, key=lambda x: x['score'], reverse=True)[:top_n]
