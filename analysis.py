def screen_stock(data, thresholds):
    """
    Robust screening:
    - Treat missing ROE as 0
    - Treat missing PEG as very high (so missing PEG doesn't filter stock)
    """
    roe = data.get('roe', 0) or 0
    peg = data.get('peg_ratio', 999) or 999  # default high if missing
    passed = roe >= thresholds['roe'] and peg <= thresholds['peg']
    # Debug log
    print(f"Screening {data['symbol']} -> ROE: {roe}, PEG: {peg} -> Passed: {passed}")
    return passed

def rank_stocks(stocks, top_n=5):
    """
    Rank stocks by a weighted score:
    score = 0.6 * ROE + 0.4 * (1/PEG)
    """
    for stock in stocks:
        roe = stock.get('roe', 0)
        peg = stock.get('peg_ratio', 1)  # default to 1 if missing
        stock['score'] = (roe * 0.6) + ((1 / peg) * 0.4)
    return sorted(stocks, key=lambda x: x['score'], reverse=True)[:top_n]
