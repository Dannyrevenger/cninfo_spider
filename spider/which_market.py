def get_stock_market(stock_code):
    """
    根据股票代码判断所属证券市场：
    - 以8开头的股票代码归属于北交所。
    - 以6开头的股票代码归属于沪交所。
    - 以0或3开头的股票代码归属于深交所。
    - 其他代码未知。
    """
    stock_code_str = str(stock_code)

    if stock_code_str.startswith("8"):
        return f"bj{stock_code}"
    elif stock_code_str.startswith("6"):
        return f"sh{stock_code}"
    elif stock_code_str.startswith("0") or stock_code_str.startswith("3"):
        return f"sz{stock_code}"
    else:
        return f"该股票代码 {stock_code} 不属于已知的证券交易所规则。"