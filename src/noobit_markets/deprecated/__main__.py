from noobit_markets.rest.request import make_httpx_get_request, send_public_request
from noobit_markets.rest.request.parsers import kraken as kraken_req
from noobit_markets.rest.response.parsers import kraken as kraken_resp

import json
import asyncio
import httpx

client = httpx.AsyncClient()
base_url = "https://api.kraken.com/0/public/"
endpoint = "Ticker"

# TODO this needs to be returned from a function
symbol_mapping = {"XBT-USD": "XXBTZUSD"}

#============================================================
# MAKING REQUEST
#============================================================

# parse request to kraken format
parsed_req = kraken_req.instrument(symbol="XBT-USD", symbol_mapping=symbol_mapping)
print(parsed_req)

# make request dict
make_req = make_httpx_get_request(
    base_url=base_url,
    endpoint=endpoint,
    headers={},
    payload=parsed_req
)
print(make_req)

# send request to kraken and get back raw response
resp = asyncio.run(send_public_request(client, make_req))
print(resp)


#============================================================
# HANDLING RESPONSE
#============================================================
# TODO this needs to be returned from a function
symbol_from_exchange = {"XXBTZUSD": "XBT-USD"}

# load response from json
# TODO should be a function: handle response that returns either Ok or Error
# if error => we return directly, if not we continue chaining
result = json.loads(resp["_content"])["result"]
print(result)

# confirm symbol we requested == index of response result
valid = kraken_resp.verify_symbol(result, "XBT-USD", symbol_from_exchange)

# parse if previous step is confirmed
if valid:
    parsed = kraken_resp.instrument(result, "XBT-USD")
    print(parsed)


