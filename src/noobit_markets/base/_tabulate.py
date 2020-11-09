import typing
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



