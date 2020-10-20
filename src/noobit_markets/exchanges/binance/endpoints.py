from pydantic import ValidationError
from noobit_markets.base.models.rest import endpoints


BINANCE_ENDPOINTS = endpoints.RESTEndpoints(**{
    "public": {
        "url": "https://api.binance.com/api/v3/",

        "endpoints": {
            "time": "time",
            # ? needed, now that symbols returns both assets and asset_pairs mappings ?
            "assets": "exchangeInfo",
            "symbols": "exchangeInfo",
            "instrument": "ticker/24hr",
            "ohlc": "klines",
            "orderbook": "depth",
            "trades": "trades",
            "spread": "ticker/bookTicker",

            #kraken api does not have it
            "historical_trades": "historicalTrades"
        }

    },

    "private": {
        "url": "https://api.binance.com/",

        "endpoints": {
            # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#account-information-user_data
            'balances': "api/v3/account",

            #deprecated
            "account_balance": "None",

            # https://binance-docs.github.io/apidocs/spot/en/#daily-account-snapshot-user_data
            "exposure": "sapi/v1/accountSnapshot",

            # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#all-orders-user_data
            "closed_orders": "api/v3/allOrders", #get only canceled orders #requires symbol
            # "trades_history": "api/v3/allOrders", #get only filled order #requires symbol
            "trades_history": "api/v3/myTrades", #get only filled order #requires symbol

            # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#current-open-orders-user_data 
            "open_orders": "api/v3/openOrders", #requires symbol

            # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#query-order-user_data 
            "order_info": "api/v3/order", #check single order

            # not updated yet 
            "open_positions": "OpenPositions",
            "closed_positions": "TradesHistory",
            "ledger": "Ledgers",
            "trades_info": "QueryTrades",
            "ledger_info": "QueryLedgers",
            "volume": "TradeVolume", #trade volume (for maker/taker fees)

            # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#new-order--trade 
            "new_order": "api/v3/order", #POST

            # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#cancel-order-trade
            "remove_order": "api/v3/order", #DELETE

            # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#start-user-data-stream-user_stream 
            "ws_token": "api/v3/userDataStream" #for SPOT wallet
        }
    }
})