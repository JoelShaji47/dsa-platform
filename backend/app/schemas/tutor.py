from pydantic import BaseModel, Field


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


class AssistantHistoryItem(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=2000)


class AssistantLastResult(BaseModel):
    status: str = Field(max_length=40)
    passed: int = Field(ge=0, default=0)
    total: int = Field(ge=0, default=0)
    failing: str = Field(max_length=2000, default="")


class AssistantRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    language: str = Field(max_length=20, default="python")
    code: str = Field(max_length=12000, default="")
    include_code: bool = True
    history: list[AssistantHistoryItem] = Field(default_factory=list, max_length=8)
    last_result: AssistantLastResult | None = None


class AssistantResponse(BaseModel):
    reply: str
    provider: str
