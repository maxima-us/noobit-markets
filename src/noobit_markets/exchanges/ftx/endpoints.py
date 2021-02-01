from noobit_markets.base.models.rest import endpoints


FTX_ENDPOINTS = endpoints.RESTEndpoints(
    **{
        "public": {
            "url": "https://ftx.com/api",
            "endpoints": {
                "time": None,
                "symbols": "markets",  # GET /markets
                "instrument": None,
                "ohlc": "candles",  # GET /markets/{market_name}/candles?resolution={resolution}&limit={limit}&start_time={start_time}&end_time={end_time}
                "orderbook": "orderbook",  # GET /markets/{market_name}/orderbook?depth={depth}
                "trades": "trades",  # GET /markets/{market_name}/trades?limit={limit}&start_time={start_time}&end_time={end_time}
            },
        },
        "private": {
            "url": "https://ftx.com/api",
            "endpoints": {
                "balances": "wallet/balances",
                "open_positions": "positions",  # GET /positions
                "open_orders": "orders",  # GET /orders?market={market}
                # ? which one is accurate ?
                "trades_history": "orders/history",  # GET /orders/history?market={market}
                "closed_orders": "orders/history",  # GET /orders/history?market={market}
                "order_info": "orders",  # GET /orders/{order_id} or /orders/by_client_id/{client_order_id}
                "trades_info": "fills",  # GET /fills?market={market}
                "new_order": "orders",  # POST /orders
                "remove_order": "orders",  # DELETE /orders/{order_id} or /orders/by_client_id/{client_order_id} or /orders to delete all
                # ---- Missing
                # "trades_history": "",
                # "closed_positions": "",
                # "ledger": "Ledgers",
                # "ledger_info": "",
                # "volume": "",
                # "ws_token": "",
            },
        },
    }
)
