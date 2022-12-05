from nonebot import get_driver
from pydantic import BaseSettings


class Config(BaseSettings):
    majsoul_font: str

    class Config:
        extra = "ignore"


conf = Config(**get_driver().config.dict())
