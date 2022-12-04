from typing import List

from pydantic import BaseModel, Extra

from .room_rank import RoomRank


# noinspection NonAsciiCharacters
class PlayerExtendedStats(BaseModel):
    id: int
    count: int
    played_modes: List[RoomRank]
    和牌率: float
    自摸率: float
    默听率: float
    放铳率: float
    副露率: float
    立直率: float
    平均打点: int
    # 最大连庄: int
    和了巡数: float
    平均铳点: int
    流局率: float
    流听率: float
    # 一发率: float
    # 里宝率: float
    # 被炸率: float
    # 平均被炸点数: int
    # 放铳时立直率: float
    # 放铳时副露率: float
    # 立直后放铳率: float
    # 立直后非瞬间放铳率: float
    # 副露后放铳率: float
    # 立直后和牌率: float
    # 副露后和牌率: float
    # 立直后流局率: float
    # 副露后流局率: float
    # 放铳至立直: int
    # 放铳至副露: int
    # 放铳至默听: int
    # 立直和了: int
    # 副露和了: int
    # 默听和了: int
    立直巡目: float
    # 立直收支: int
    # 立直收入: int
    # 立直支出: int
    先制率: float
    追立率: float
    # 被追率: float
    # 振听立直率: float
    # 立直好型: float
    # 立直多面: float
    # 立直好型2: float
    # 最大累计番数: int
    # W立直: int
    打点效率: int
    # 铳点损失: int
    净打点效率: int
    # 平均起手向听: float
    # 平均起手向听亲: float
    # 平均起手向听子: float

    class Config:
        extra = Extra.ignore
