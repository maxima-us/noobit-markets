[![Build Status](https://travis-ci.com/maxima-us/noobit-markets.svg?branch=master)](https://travis-ci.com/maxima-us/noobit-markets)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/e458a34c61974b11be17c4babf08c444)](https://www.codacy.com/gh/maxima-us/noobit-markets/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=maxima-us/noobit-markets&amp;utm_campaign=Badge_Grade)

# noobit-markets

### Overview

Building Blocks for connecting and trading with cryptocurrency exchanges under a unified format.\
Primarily meant to be  integrated within larger applications, but also provides a basic CLI app.
<br/>
Presently supported exchanges:
- Kraken
- Binance
- Ftx
<br/>
<br/>

For now we restrict instruments to spot pairs.

<br/>

### Features 

-	Unified API, independent of exchange
-	Fully typed with annotations and checked with mypy
-	Fully modeled domains relying on Pydantic models (for validation and serialization)
-	Safe and explicit function returns thanks to a railway oriented approach and Result containers
-	CLI app that bundles all lower level coroutines and websocket streams in a user friendly manner

<br/>

### Models & Pydantic:

-	We rely heavily on Pydantic to check the user input and what he receives, against what we expected\
(that is, the models we have defined and should represent our domains)
-	It is important to know that pydantic not only handles validation, but also serialization.
-	As such, it will serialize data to the declared type of the field before validation, if possible\
(e.g if the field “price” is declared as a `Decimal`, passing a float will not throw any `ValidationError` as a float can be cast to a `Decimal`)
-	You can browse our unified models [here](https://github.com/maxima-us/noobit-markets/tree/master/src/noobit_markets/base/models/rest)

<br/>

### Result Container:

-	To provide the user with more explicit returns, responses are wrapped in a `Result` object, which can either be of type `Ok` or `Err`.\
The Result object's `.value()` method gives access to the value it holds, which will either be a response (validated against its expected model) or an exception.
-	This allows to avoid having to raise Exceptions and stopping the program from running. 

<br/>

### Railway oriented approach:

-	This approach seeks to ensure every function or method returns a success or a failure.\
When chaining multiple functions, in case of a failure, we immediately return the failure to the user and “stop the chain”.
-	See [this article](https://fsharpforfunandprofit.com/posts/recipe-part2/#railway-oriented-programming) for a more detailed explanation.

<br/>

### Usage

-	For each exchange, an interface maps keys to coroutines or websocket APIs. For an example of Krakens interface see [here](https://github.com/maxima-us/noobit-markets/blob/master/src/noobit_markets/exchanges/kraken/interface.py)
-	For how to use coroutines and websocket APIs within an async app, examples are available for each exchange [here](https://github.com/maxima-us/noobit-markets/tree/master/src/noobit_markets/examples)
-	To start the CLI app, run the `noobit-cli` command. As a prerequisite for subsequent CLI command, run the `symbols` command in the CLI on each startup.
