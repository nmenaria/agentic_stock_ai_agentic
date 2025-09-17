def screen_stock(data, thresholds):
    """
    Robust screening:
    - ROE >= threshold
    - PEG <= threshold if PEG exists
    - If PEG is missing, only ROE is checked
    """
    roe = data.get('roe', 0) or 0
    peg = data.get('peg_ratio')  # None if missing

    if peg is None:
        passed = roe >= thresholds['roe']
    else:
        passed = roe >= thresholds['roe'] and peg <= thresholds['peg']

    # Debug log
    print(f"Screening {data['symbol']} -> ROE: {roe}, PEG: {peg} -> Passed: {passed}")
    return passed

def rank_stocks(stocks, top_n=5):
    """
    Rank stocks by a weighted score:
    score = 0.6 * ROE + 0.4 * (1/PEG) if PEG exists
    """
    for stock in stocks:
        roe = stock.get('roe', 0)
        peg = stock.get('peg_ratio')
        if peg is None or peg == 0:
            stock['score'] = roe * 0.6
        else:
            stock['score'] = (roe * 0.6) + ((1 / peg) * 0.4)
    return sorted(stocks, key=lambda x: x['score'], reverse=True)[:top_n]
