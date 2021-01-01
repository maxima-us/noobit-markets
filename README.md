[![Build Status](https://travis-ci.com/maxima-us/noobit-markets.svg?branch=master)](https://travis-ci.com/maxima-us/noobit-markets)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/e458a34c61974b11be17c4babf08c444)](https://www.codacy.com/gh/maxima-us/noobit-markets/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=maxima-us/noobit-markets&amp;utm_campaign=Badge_Grade)

# noobit-markets

### Overview

Building Blocks for connecting and trading with cryptocurrency exchanges under a unified format. Primarily meant to be  integrated within larger applications, but also provides a basic CLI app.
<br/>
### Design Considerations

#### Domains and Models

Particular emphasis has been put on very clearning defining domains, as such we rely very heavily on (pydantic) models.
`noobit models` for both requests and responses ensure that across different exchanges, the user experience and data are exactly the same (e.g wether a user makes a GET request for orderbook data on Binance or streams it over WebSocket on Kraken, the data will be of the same format). 
Exchange responses get parsed into `noobit responses` and validated against the corresponding model.


#### Result

To provide the user with more explicit returns, responses are wrapped in a rust like Result object, which can either be of type Ok or Err.
The Result object's `.value()` method gives access to the value it holds, which will either be a noobit response or an exception.


#### Typing

We aim to be fully MyPy compliant.
<br/>

###Usage

####Api 

You can access the coroutines and ws apis via the exchange's interface , for ex : `get_ohlc = interface.KRAKEN.rest.public.ohlc`

Every coroutine requires a `symbols` argument to be passed, which should be the noobit response received from the symbols endpoint.

You can check out code examples for each exchange in the examples folder.

####Cli

From the ui folder, run `python cli.py` to start the CLI app. As a prerequisite for subsequent commands, run the `symbols` command on each startup.