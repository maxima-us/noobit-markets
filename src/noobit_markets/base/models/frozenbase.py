from pydantic import BaseModel


class FrozenBaseModel(BaseModel):


    class Config:
        allow_mutation = False