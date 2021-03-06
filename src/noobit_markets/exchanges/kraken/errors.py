import typing

from noobit_markets.base.errors import *


# undocumented errors we encountered: 
#       'EGeneral:Invalid arguments:volume'
#       KeyError: 'EOrder:Invalid price:DOTUSD price can only be specified up to 4 decimals.' 

# see: https://support.kraken.com/hc/en-us/articles/360001491786-API-Error-Codes
# typing.Type makes mypy accept subclasses of Exception as well
ERRORS_FROM_EXCHANGE: typing.Mapping[str, typing.Type[Exception]] = {

        # Errors related to rate limits
        'EOrder:Rate limit exceeded': DDoSProtection,
        'EGeneral:Temporary lockout': DDoSProtection,
        'EAPI:Rate limit exceeded': RateLimitExceeded,

        # General usage errors
        'EQuery:Unknown asset pair': BadSymbol,
        'EGeneral:Invalid arguments': BadSymbol,
        'EGeneral:Internal error': ExchangeNotAvailable,
        'EGeneral:Permission denied': PermissionDenied,
        'EAPI:Invalid key': AuthenticationError,
        'EAPI:Invalid signature': InvalidSignature,
        'EAPI:Invalid nonce': InvalidNonce,
        'EAPI:Feature disabled': Deprecated,

        # Service status errors
        'EService:Unavailable': ExchangeNotAvailable,
        'EService:Busy': ExchangeNotAvailable,

        # Trading errors
        'ETrade:Locked': Exception,

        # Order placing errors
        'EOrder:Cannot open position': Exception,
        'EOrder:Cannot open opposing position': Exception,
        'EOrder:Margin allowance exceeded': Exception,
        'EOrder:Insufficient margin': Exception,
        'EOrder:Insufficient funds': InsufficientFunds,
        'EOrder:Order minimum not met': InvalidOrder,
        'EOrder:Orders limit exceeded': InvalidOrder,
        'EOrder:Positions limit exceeded': Exception,
        'EOrder:Trading agreement required': Exception,

        # Network timeout errors

        # Not documented by Kraken
        'EGeneral:Invalid arguments:volume': InvalidOrder,
        'EOrder:Invalid order': InvalidOrder,
        'EQuery:Invalid asset pair': BadSymbol,
        # 'EFunding:Unknown withdraw key': ExchangeError,
        # 'EFunding:Invalid amount': InsufficientFunds,
        # 'EDatabase:Internal error': ExchangeNotAvailable,
        'EQuery:Unknown asset': BadSymbol,

        "EOrder:Unknown order": InvalidOrder,
}

# in https://www.kraken.com/features/api#add-standard-order
# EGeneral:Invalid arguments
# EService:Unavailable
# ETrade:Invalid request
# EOrder:Cannot open position
# EOrder:Cannot open opposing position
# EOrder:Margin allowance exceeded
# EOrder:Margin level too low
# EOrder:Insufficient margin (exchange does not have sufficient funds to allow margin trading)
# EOrder:Insufficient funds (insufficient user funds)
# EOrder:Order minimum not met (volume too low)
# EOrder:Orders limit exceeded
# EOrder:Positions limit exceeded
# EOrder:Rate limit exceeded
# EOrder:Scheduled orders limit exceeded
# EOrder:Unknown position
