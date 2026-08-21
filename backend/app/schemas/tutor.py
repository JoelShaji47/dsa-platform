from pydantic import BaseModel


class HintLevelInfo(BaseModel):
    level: int
    label: str
    revealed: bool


class HintMetaOut(BaseModel):
    total_levels: int
    xp_forfeit_applies: bool
    levels: list[HintLevelInfo]


class HintRevealOut(BaseModel):
    level: int
    label: str
    content: str


class ReviewOut(BaseModel):
    verdict: str
    bug_type: str
    explanation: str
    fix_hint: str
