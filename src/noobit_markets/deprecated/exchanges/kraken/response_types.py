
ENDPOINTS = endpoints.RootMapping(
    rest={
            "public": {
                "url": "https://api.kraken.com/0/public/",

                "endpoints": {
                    "time": "Time",
                    "assets": "Assets",
                    "symbols": "AssetPairs",
                    "instrument": {
                        "return_type": frozendict,
                        # None key = assume key is <symbol>
                        "main_key": None
                    },
                    "ohlc": {
                        "return_type": tuple,
                        # None key = assume key is <symbol>
                        "main_key": None
                    },
                    "orderbook": {
                        "return_type": frozendict,
                        "main_key": None
                    }
                    ,
                    "trades": {
                        "return_type": tuple,
                        "main_key": None,
                        "secondary_keys": ("last",)
                    },
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