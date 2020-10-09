from pydantic import ValidationError
from noobit_markets.base.models.rest import endpoints


KRAKEN_ENDPOINTS = endpoints.RESTEndpoints(**{
    "public": {
        "url": "https://api.kraken.com/0/public/",

        "endpoints": {
            "time": "Time",
            # ? needed, now that symbols returns both assets and asset_pairs mappings ?
            "assets": "Assets",
            "symbols": "AssetPairs",
            "instrument": "Ticker",
            "ohlc": "OHLC",
            "orderbook": "Depth",
            "trades": "Trades",
            "spread": "Spread"
        }

    },

    "private": {
        "url": "https://api.kraken.com/0/private/",

        "endpoints": {
            'balances': "Balance",
            "account_balance": "Balance",
            # "exposure": "TradeBalance",
            "open_positions": "OpenPositions",
            "open_orders": "OpenOrders",
            "closed_orders": "ClosedOrders",
            "trades_history": "TradesHistory",
            "closed_positions": "TradesHistory",
            "ledger": "Ledgers",
            "order_info": "QueryOrders",
            "trades_info": "QueryTrades",
            "ledger_info": "QueryLedgers",
            "volume": "TradeVolume",
            "new_order": "AddOrder",
            "remove_order": "CancelOrder",
            "ws_token": "GetWebSocketsToken"
        }
    }
})