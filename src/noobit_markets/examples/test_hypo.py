from typing_extensions import TypedDict
import hypothesis
import pydantic


class User(pydantic.BaseModel):

    name: str
    age: int
    city: str


class AnonUser(pydantic.BaseModel):

    age: int
    city: str


class Map(TypedDict):

    first: int
    second: int
    third: int


# gen = hypothesis.strategies.from_type(User)
# print(gen.name)


@hypothesis.given(hypothesis.strategies.from_type(AnonUser))
def test_me(person: AnonUser):
    user = User("Max", person.age, person.city)
    assert isinstance(user, User)


# gen = hypothesis.strategies.decimals(min_value=10, max_value=100)
# print(gen)


@hypothesis.given(hypothesis.strategies.decimals(min_value=10, max_value=100))
def test_me(num):
    assert num < 101
