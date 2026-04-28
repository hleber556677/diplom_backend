from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    display_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    display_name: str
    total_points: int

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class StoryFrame(BaseModel):
    title: str
    text: str


class LessonStep(BaseModel):
    title: str
    text: str


class MiniGameQuestion(BaseModel):
    prompt: str
    options: list[str]
    correct_index: int
    explanation: str


class ModuleProgressInfo(BaseModel):
    module_slug: str
    completed: bool
    best_score: int
    attempts: int
    earned_points: int


class LearningModule(BaseModel):
    slug: str
    title: str
    city_zone: str
    summary: str
    objective: str
    reward_points: int
    story_frames: list[StoryFrame]
    lesson_steps: list[LessonStep]
    minigame: MiniGameQuestion
    progress: ModuleProgressInfo | None = None


class ModuleSubmitRequest(BaseModel):
    selected_index: int


class ModuleSubmitResponse(BaseModel):
    correct: bool
    explanation: str
    earned_points: int
    total_points: int
    progress: ModuleProgressInfo
    level_title: str
    unlocked_achievements: list["Achievement"] = []


class Achievement(BaseModel):
    code: str
    title: str
    description: str
    reward_points: int
    modules_required: int
    unlocked: bool = False


class StudentProfile(BaseModel):
    display_name: str
    email: EmailStr
    is_admin: bool = False
    total_points: int
    level_title: str
    completed_modules: int
    total_modules: int
    achievements: list[Achievement]
    progress: list[ModuleProgressInfo]


class LeaderboardEntry(BaseModel):
    place: int
    display_name: str
    email: EmailStr
    total_points: int
    level_title: str


class AdminUserProgress(BaseModel):
    id: int
    display_name: str
    email: EmailStr
    is_admin: bool = False
    total_points: int
    level_title: str
    completed_modules: int
    total_modules: int
    progress: list[ModuleProgressInfo]
