from .request import *
from .response import *

from noobit_markets.base.request import *
from noobit_markets.base import ntypes
from noobit_markets.base.models.rest.response import NoobitResponseBalances

from noobit_markets.exchanges.kraken import endpoints
from noobit_markets.exchanges.kraken.rest.base import *

from noobit_markets.exchanges.kraken.rest import auth



@retry_request(retries=10, logger= lambda *args: print("===x=x=x=x@ : ", *args))
async def get_balances_kraken(
        loop,
        client,
        asset_to_exchange: ntypes.ASSET_TO_EXCHANGE,
        logger_func,
        auth=auth.KrakenAuth(),
        # FIXME get from endpoint dict
        base_url="https://api.kraken.com/0/private/",
        endpoint="Balance"
    ) -> Result[NoobitResponseBalances, Exception]:

    # step 1: validate base request ==> output: Result[NoobitRequestTradeBalance, ValidationError]
    # step 2: parse valid base req ==> output: pmap
    # step 3: validate parsed request ==> output: Result[KrakenRequestTradeBalance, ValidationError]


    # get nonce right away since there is noother param
    data = {"nonce": auth.nonce}

    #! we do not need to validate, as there are no params
    #!      and type checking a nonce is useless
    #!      if invalid nonce: error_content will inform us
    # step 4: make actual request to be sent ==> output: pmap
    make_req = make_httpx_post_request(base_url, endpoint, auth.headers(endpoint, data), data)

    # step 5: send request and retrieve resp ==> output: pmap
    resp = await send_private_request(client, make_req)

    # step 6: check if we received an error HTTP code
    valid_status = get_response_status_code(resp)
    if valid_status.is_err():
        return valid_status

    # step 7: check if we received an error result
    err_content = get_error_content(resp)
    if err_content:
        parsed_err_content = (err_content, get_sent_request(resp))
        return parsed_err_content


    # setp 8: get result content ==> output: pmap
    result_content_balances = get_result_content(resp)

    # step 9: compare received symbol to passed symbol (!!!!! Not Applicable)

    # step 10: validate result content ==> output: Result[KrakenResponseBalances, ValidationError]
    valid_result_content = validate_raw_result_content_balances(result_content_balances)
    if valid_result_content.is_err():
        return valid_result_content

    # step 11: get result data from result content ==> output: pmap
    #   example of pmap: {"eb":"46096.0029","tb":"29020.9951","m":"0.0000","n":"0.0000","c":"0.0000","v":"0.0000","e":"29020.9951","mf":"29020.9951"}
    result_data_balances = get_result_data_balances(valid_result_content.value)

    # step 12: parse result data ==> output: pmap
    parsed_result_data = parse_result_data_balances(result_data_balances, asset_to_exchange)

    # step 13: validate parsed result data ==> output: Result[NoobitResponseTradeBalance, ValidationError]
    valid_parsed_result_data = validate_parsed_result_data_balances(parsed_result_data)

    return valid_parsed_result_data