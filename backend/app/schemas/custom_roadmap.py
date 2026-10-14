from pydantic import BaseModel, Field


class BuildRoadmapPayload(BaseModel):
    level: str = Field(default="basics", pattern="^(never_started|basics|50_plus|interview_ready)$")
    goal: str = Field(default="fundamentals", pattern="^(interview_soon|fundamentals|company|curious)$")
    company: str | None = Field(default=None, max_length=100)
    mins_per_day: int = Field(default=60, ge=15, le=480)
    total_days: int = Field(default=21, ge=1, le=180)
    target_count: int | None = Field(default=None, ge=1, le=200)
    kind: str = Field(default="dsa_build", pattern="^(dsa_build|learn_anything|video)$")
    title: str | None = Field(default=None, max_length=200)


class JoinPayload(BaseModel):
    share_code: str = Field(min_length=6, max_length=6)


class StepOut(BaseModel):
    id: str
    position: int
    problem_slug: str | None
    title: str
    kind: str
    pattern_key: str | None
    difficulty: str | None
    est_mins: int
    day_index: int
    done: bool = False
    video_url: str | None = None


class RoadmapOut(BaseModel):
    id: str
    title: str
    kind: str
    level: str
    goal: str
    company: str | None
    mins_per_day: int
    total_days: int
    share_code: str
    owner: bool
    steps: list[StepOut]
    me_done: int
    total: int
    friend_done: int | None = None
