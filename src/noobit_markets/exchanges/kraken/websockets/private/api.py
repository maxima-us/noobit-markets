# noobit base
from noobit_markets.base.websockets import subscribe, BaseWsPrivate 

# noobit kraken ws
from noobit_markets.exchanges.kraken.websockets.private import trades as user_trades
from noobit_markets.exchanges.kraken.websockets.private import orders as user_orders



class KrakenWsPrivate(BaseWsPrivate):
    
    
    async def trade(self):
        super()._ensure_dispatch()

        valid_sub_model = user_trades.validate_sub(self.auth_token)
        if valid_sub_model.is_err():
            print(valid_sub_model)
            yield valid_sub_model

        sub_result = await subscribe(self.client, valid_sub_model.value)
        if sub_result.is_err():
            yield sub_result

        self._subd_feeds["user_trades"] = True
        

        async for msg in self.aiter_usertrade():
        # async for msg in self.iterq(self._data_queues, "user_trades"):
            yield msg

    
    async def order(self):            
        super()._ensure_dispatch()

        valid_sub_model = user_orders.validate_sub(self.auth_token)
        if valid_sub_model.is_err():
            print(valid_sub_model)
            yield valid_sub_model

        sub_result = await subscribe(self.client, valid_sub_model.value)
        if sub_result.is_err():
            yield sub_result

        self._subd_feeds["user_orders"] = True
        
        # async for msg in self.iterq(self._data_queues, "user_orders"):
        async for msg in self.aiter_userorder():
            yield msg
