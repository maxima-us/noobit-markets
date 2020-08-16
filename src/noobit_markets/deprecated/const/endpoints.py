# from types import MappingProxyType
from noobit_markets.models import endpoints



ENDPOINTS = endpoints.RootMapping(
    rest={
        "KRAKEN": {
            "public": {
                "url": "https://api.kraken.com/0/public/",

                "endpoints": {
                    "time": "Time",
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
                "url": "https://api/kraken/com/0/private/",

                "endpoints": {
                    'balance': "Balance",
                    "account_balance": "Balance",
                    "exposure": "TradeBalance",
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
                    "add_order": "AddOrder",
                    "remove_order": "CancelOrder",
                    "ws_token": "GetWebSocketsToken"
                }
            }
        }
    }
)