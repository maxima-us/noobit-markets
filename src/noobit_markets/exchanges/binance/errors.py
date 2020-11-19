import typing

from noobit_markets.base.errors import *


ERRORS_FROM_EXCHANGE: typing.Mapping[int, typing.Type[Exception]] = {
    1000: UndefinedError, #unknown error occured while processing the request
    1001: ExchangeNotAvailable,
    1002: PermissionDenied, #?AuthenticationError or PermissionDenied
    1003: RateLimitExceeded,
    1004: ExchangeNotAvailable, # server busy
    1006: BadResponse,
    1007: RequestTimeout,
    1014: InvalidOrder,
    1015: RateLimitExceeded, #not sur
    1016: Deprecated, 
    1020: NotSupported,
    1021: InvalidNonce, #invalid timestamp requested
    1022: InvalidSignature,

    1100: BadRequest, #illegal parameters
    1101: BadRequest, #too many parameters
    1102: BadRequest, #mandatory param empty or malformed
    1103: BadRequest, #unknown param
    1104: UndefinedError, #!unread param (???)
    1105: BadRequest, #param emtpy
    1106: BadRequest, #param not required (extra param)
    1111: BadRequest, #bad precision
    1112: UndefinedError, #!no depth (???)
    1114: BadRequest, #TIF not required
    1115: BadRequest, #Invalid TIF
    1116: InvalidOrder, #Invalid OrderType
    1117: InvalidOrder, #Invalid side
    1118: UndefinedError,  #!new client order ID was empty
    1119: UndefinedError, #! original client order ID was empty
    1120: BadRequest, #Bad Interval
    1121: BadSymbol, #Bad Symbol
    1125: UndefinedError, #invalid Listen key
    1127: BadRequest, #lookup interval is too big
    1128: BadRequest, # combination of optional params is invalid
    1130: BadRequest, #Invalid data for a parameter
    1131: BadRequest, #bad recv window
    2010: InvalidOrder, #new order rejected
    2011: InvalidOrder, #cancel rejected
    2013: OrderNotFound, #no such order
    2014: AuthenticationError, #bad api key format
    2015: AuthenticationError, #rejected mbx key / invalid api key or permission denied
    2016: UndefinedError, #!no trading window / try ticker/24hrs instead.
    
    3000: ExchangeError, #?internal server error
    3001: PermissionDenied, #?please enable 2FA first
    3002: BadSymbol, #we dont have this asset
    3003: UndefinedError, #?no margin account
    3004: PermissionDenied, #?trade not allowed
    3005: PermissionDenied, #?transfer out not allowed
    3006: UndefinedError, #! you have exceeded max borrow amount
    3007: UndefinedError, #! pending transaction, please try again later
    3008: UndefinedError, #! borrow not allowed
    3009: UndefinedError, #! This asset are not allowed to transfer into margin account currently
    3010: UndefinedError, #! repay not allowed
    3011: UndefinedError, #! invalid input date
    3012: UndefinedError, #! borrow is banned for this asset
    3013: UndefinedError, #! borrow amount less than minimum borrow amount.
    3014: UndefinedError, #! Borrow is banned for this account.
    3015: UndefinedError, #! repay amount exceeds borrow amount
    3016: UndefinedError, #! repay amount less than minimum repay amount.
    3017: UndefinedError, #! this asset are not allowed to transfer into margin account currently.
    3018: UndefinedError, #! transferring in has been banned for this account
    3019: UndefinedError, #! transferring out has been banned for this account.
    3020: UndefinedError, #! Transfer out amount exceeds max amount
    3021: UndefinedError, #! Margin account are not allowed to trade this trading pair.
    3022: UndefinedError, #! You account's trading is banned.
    3023: UndefinedError, #! You can't transfer out/place order under current margin level.
    3024: UndefinedError, #! The unpaid debt is too small after this repayment.
    3025: BadRequest, #? Your input date is invalid.
    3026: BadRequest, #? Your input param is invalid.
    3027: BadRequest, #? Not a valid margin asset.
    3028: BadRequest, #? Not a valid margin pair.
    3029: UndefinedError, #! transfer failed
    3036: UndefinedError, #! This account is not allowed to repay.
    3037: UndefinedError, #! PNL is clearing. Wait a second.
    3038: UndefinedError, #! Listen key not found.
    3041: InsufficientFunds, # Balance is not enough
    3042: UndefinedError, #! PriceIndex not available for this margin pair.
    3043: PermissionDenied, #? transfer not allowed
    3044: ExchangeNotAvailable, #? system busy
    3999: PermissionDenied, #? This function is only available for invited users.
    4001: BadRequest, # invalid operation
    4002: BadRequest, # invalid get
    4004: PermissionDenied, #? you dont login or auth 
    4005: RateLimitExceeded, #too many new requests
    4006: UndefinedError, #support main account only
    4007: InvalidAddress, # address validation is not passed
    4008: UndefinedError, #! Address tag validation not passed
    4010: UndefinedError, #! white list mail has been confirmed
    4011: UndefinedError, #! white list mail is invalid
    4012: UndefinedError, #! white list is not opened
    4013: UndefinedError, #! 2FA is not opened
    4014: PermissionDenied, #? withdrawal is not allowed withing 2 mins
    4015: UndefinedError, #! withdrawal is limited (capital)
    4016: PermissionDenied, #! withdrawal prohibited with 24h after password modification
    4017: PermissionDenied, #! withdrawal prohibited within 24h after release of 2FA
    4018: BadSymbol, # asset does not exist
    4019: BadRequest, # asset not open for withdrawal
    4021: BadRequest, # asset amount withdrawal must a multiple of X
    4022: BadRequest, # withdrawal does not mean the minimum
    4023: BadRequest, # withdrawal exceeds the max amount
    4024: BadRequest, # no balance for this asset, withdrawal impossible
    4025: BadRequest, # balance is negative for asset, withdrawal impossible
    4026: InsufficientFunds, # insufficient balance to process withdrawal req
    # ...
    4033: InvalidAddress, # illegal withdrawal destination address
    4034: InvalidAddress, # address is supect or fake
    4035: InvalidAddress, # address is not on the whitelist
    # ...
    5002: InsufficientFunds, # insufficient balance
    5003: InsufficientFunds, # empty balance for this asset 

    5007: UndefinedError, #! quantity must be greater than 0

    # ...
    6012: InsufficientFunds, # insufficient balance
    #...
    6015: ArgumentsRequired, # empty request body
    6016: BadRequest, # params error
    6018: InsufficientFunds, # insufficient asset




    ## skip




}


_ERROR_MSGS = {

    #1000 UNKNOWN
    "An unknown error occured while processing the request"
    
    #1001 DISCONNECTED
    "Internal error; unable to process your request. Please try again"
    
    #1002 UNAUTHORIZED
    "You are not authorized to execute this request"
    
    #1003 TOO_MANY_REQUESTS
    "Too many requests queued"
    "Too much request weight used; please use the websocket for live updates to avoid polling the API"
    "Too much request weight used; current limit is %s request weight per %s %s. Please use the websocket for live updates to avoid polling the API"
    "Way too much request weight used; IP banned until %s. Please use the websocket for live updates to avoid bans"
    
    #1006 UNEXPECTED_RESP
    "An unexpected response was received from the message bus. Execution status unknown"

    #1007 TIMEOUT
    "Timeout waiting for response from backend server. Send status unknown; execution status unknown"

    #1014 UNKNOWN_ORDER_COMPOSITION
    "Unsupported order combination"

    #1015 TOO_MANY_ORDERS
    "Too many new orders"
    "Too many new orders; current limit is %s orders per %s"

    #1016 SERVICE_SHUTTING_DOWN
    "This service is no longer available"

    #1020 UNSUPPORTED_OPERATION
    "This operation is not supported"

    #1021 INVALID_TIMESTAMP
   "Timestamp for this request is outside of the recvWindow"
    "Timestamp for this request was 1000ms ahead of the server's time"

    #1022 INVALID_SIGNATURE
    "Signature for this request is not valid"

    #1099 Not found, authenticated, or authorized
    

    #1100 ILLEGAL_CHARS
    "Illegal characters found in a parameter"
    "Illegal characters found in parameter %s; legal range is %s"

    #1101 TOO_MANY_PARAMETERS
    "Too many parameters sent for this endpoint"
    "Too many parameters; expected %s and received %s"
    "Duplicate values for a parameter detected"

    #1102 MANDATORY_PARAM_EMPTY_OR_MALFORMED
    "A mandatory parameter was not sent, was empty/null, or malformed"
    "Mandatory parameter %s was not sent, was empty/null, or malformed"
    "Param %s or %s must be sent, but both were empty/null!"

    #1103 UNKNOWN_PARAM
    "An unknown parameter was sent"

    #1104 UNREAD_PARAMETERS
    "Not all sent parameters were read"
    "Not all sent parameters were read; read %s parameter(s) but was sent %s"

    #1105 PARAM_EMPTY
    "A parameter was empty"
    "Parameter %s was empty"

    #1106 PARAM_NOT_REQUIRED
    "A parameter was sent when not required"
    "Parameter %s sent when not required"

    #1111 BAD_PRECISION
    "Precision is over the maximum defined for this asset"

    #1112 NO_DEPTH
    "No orders on book for symbol"

    #1114 TIF_NOT_REQUIRED
    "TimeInForce parameter sent when not required"

    #1115 INVALID_TIF
    "Invalid timeInForce"

    #1116 INVALID_ORDER_TYPE
    "Invalid orderType"

    #1117 INVALID_SIDE
    "Invalid side"

    #1118 EMPTY_NEW_CL_ORD_ID
    "New client order ID was empty"

    #1119 EMPTY_ORG_CL_ORD_ID
    "Original client order ID was empty"

    #1120 BAD_INTERVAL
    "Invalid interval"

    #1121 BAD_SYMBOL
    "Invalid symbol"

    #1125 INVALID_LISTEN_KEY
    "This listenKey does not exist"

    #1127 MORE_THAN_XX_HOURS
    "Lookup interval is too big"
    "More than %s hours between startTime and endTime"

    #1128 OPTIONAL_PARAMS_BAD_COMBO
    "Combination of optional parameters invalid"

    #1130 INVALID_PARAMETER
    "Invalid data sent for a parameter"
    "Data sent for paramter %s is not valid"

    #1131 BAD_RECV_WINDOW
    "recvWindow must be less than 60000"



}