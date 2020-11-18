from decimal import Decimal
import typing
from noobit_markets.base.models.result import Ok, Err
from pydantic import ValidationError, BaseModel
import pydantic
from pydantic.main import validate_custom_root_type

from tabulate import tabulate



# ============================================================
# PYDANTIC TO TABULATE
# ============================================================


class Person(BaseModel):
    
    name: str
    age: int
    address: str
    hobbies: typing.List[str]


class Family(BaseModel):

    members: typing.List[Person]



try:
    chad = Person(
        name="Chad",
        age=21,
        address="1 Chad Avenue",
        hobbies=["Chadding", "Longing DOT"]
    )

    stacy = Person(
        name="Stacy",
        age=20,
        address="Dumb Cunt Street",
        hobbies=["Twerking",]
    )
except ValidationError as e:
    raise e

try:
    couple = Family(
        members=[chad, stacy]
    )
    # table = [(k, v) for k, v in (person.dict() for person in couple.members)]
    table = [list(person.dict().items()) for person in couple.members]
    # print(table)
except ValidationError as e:
    raise e

# print(couple.members)



#? ============================================================
#! OHLC EXAMPLE
#? ============================================================

# pb: we can validate upon instantiation, but in that case we cant take the "railway programming" approach
#   ==> we need a `Result` returned


class PydanticOHLC(BaseModel):

    ohlc: typing.List[typing.Tuple[Decimal, Decimal, Decimal, Decimal]]


class OHLC:

    model = PydanticOHLC

    def __init__(self):
        pass

    def cast(self, ohlc: typing.List[typing.Tuple[float, float, float, float]]):
        self.raw_ohlc = ohlc
        try:
            self.vser = self.model(ohlc=self.raw_ohlc)
            return Ok(self)
        except ValidationError as e:
            return Err(e)


    @property
    def table(self):
        table = tabulate(
            {
                "High": [person[0] for person in self.vser.ohlc],
                "Open": [person[1] for person in self.vser.ohlc],
                "Low": [person[2] for person in self.vser.ohlc],
                "Close": [person[3] for person in self.vser.ohlc]
            },
            headers="keys"
        )
        return table

    
    def __str__(self):
        return self.table


ohlc_data = [
    [1,2,4,5],
    [6,7,8,9]
]


ohlc_data_2 = [
    [22.2, 4.4, 5, 6],
    [8,3,3,0]
]


#====================
# USAGE
#====================

if __name__ == "__main__":

    # `model` attribute references the pydantic model
    # `vser` attribute will hold validated model
    ohlc = OHLC()

    # passes the raw data to the classes `model` (pydantic model) attribute
    # if its valid, we bind the model to the class `vser` (for validate serialize) attribute, and return the class instance wrapped in an OK Result
    # if its not valid, it returns an ERR Result (ValidationError)
    valid = ohlc.cast(ohlc_data)


    print("valid.value :\n", valid.value, "\nType :\n", type(valid))
    # valid.value.table ==> type = str
    # valid.value.vser ==> __main__.PydanticOHLC
    # valid.value.model ==> pydantic.main.ModelMetaclass
    # valid.value ==> type __main__.OHLC
    # valid ==> noobit_markets.base.models.result.Ok


    ohlc2 = OHLC()
    valid2 = ohlc2.cast(ohlc_data_2)

    if valid2.is_ok():
        print(valid2.value)
    else:
        print(valid2.value)




#? ============================================================
#! ORDERBOOK EXAMPLE
#? ============================================================

class PydanticOBook(BaseModel):

    symbol: str
    asks: typing.Dict[Decimal, Decimal]
    bids: typing.Dict[Decimal, Decimal]


class OBook:

    model = PydanticOBook

    def __init__(self):
        pass

    # in practice the input would be for ex `KrakenResponseOrderBook`
    def cast(self, symbol:str, asks: typing.Dict[float, float], bids: typing.Dict[float, float]):
        try:
            self.vser = self.model(symbol=symbol, asks=asks, bids=bids)
            return Ok(self)
        except ValidationError as e:
            return Err(e)



    @property
    def table(self):
        table = tabulate(
            {
                "Ask Price": [k for k, v in self.vser.asks.items()],
                "Ask Volume": [v for k, v in self.vser.asks.items()],
                "Bid Price": [k for k, v in self.vser.bids.items()],
                "Bid Volume": [v for k, v in self.vser.bids.items()],
            },
            headers="keys"
        )
        return table

    
    def __str__(self):
        return self.table

if __name__ == "__main__":
    book_asks = {
        1000:1,
        2000:2,
        3000:3
    }

    book_bids = {
        500:5,
        200:10,
        100:1000
    }

    book = OBook()

    valid = book.cast("XBT-USD", book_asks, book_bids)

    if valid.is_ok():
        print(valid.value)
    else:
        print(valid.value)



#? ============================================================
#! UTILS (GENERAL FUNCTIONS)
#? ============================================================

def pylist_table(data: typing.List[BaseModel]):

    keys = [tuple(item.dict().keys()) for item in data]
    values = [list(item.dict().values()) for item in data]

    if not len(set(keys)) == 1:
        raise ValueError

    else:
        return tabulate(values, headers=keys[0])

# fam_table = pydantic_table(couple.members)
# print(fam_table)


def pymap_table(data: typing.Mapping[typing.Any, typing.Any], headers):

    table = [(k, v) for k, v in data.items()]

    return tabulate(table, headers)



