from app.content import MODULES
from app.models import ModuleProgress, User
from app.schemas import Achievement, LearningModule, ModuleProgressInfo


LEVELS = [
    (0, "Новичок"),
    (120, "Юный исследователь"),
    (260, "Цифровой мастер"),
]

ACHIEVEMENT_DEFS = [
    {
        "code": "module_1_guard",
        "title": "Первый дозор",
        "description": "Ты завершил первый модуль и стал настоящим помощником цифрового города.",
        "reward_points": 100,
        "modules_required": 1,
    },
    {
        "code": "module_2_detective",
        "title": "Детектив поиска",
        "description": "Ты завершил второй модуль и научился лучше ориентироваться в цифровых заданиях.",
        "reward_points": 200,
        "modules_required": 2,
    },
    {
        "code": "module_3_guardian",
        "title": "Хранитель уважения",
        "description": "Ты завершил третий модуль и стал увереннее в цифровом общении и правилах сети.",
        "reward_points": 300,
        "modules_required": 3,
    },
    {
        "code": "module_4_defender",
        "title": "Защитник цифрового города",
        "description": "Ты прошёл все четыре модуля и стал настоящим защитником ЦифроГрада.",
        "reward_points": 400,
        "modules_required": 4,
    },
]


def get_level_title(total_points: int) -> str:
    title = LEVELS[0][1]
    for threshold, current_title in LEVELS:
        if total_points >= threshold:
            title = current_title
    return title


def build_progress_map(progresses: list[ModuleProgress]) -> dict[str, ModuleProgress]:
    return {progress.module_slug: progress for progress in progresses}


def serialize_progress(progress: ModuleProgress | None, module_slug: str) -> ModuleProgressInfo:
    if progress is None:
        return ModuleProgressInfo(
            module_slug=module_slug,
            completed=False,
            best_score=0,
            attempts=0,
            earned_points=0,
        )

    return ModuleProgressInfo(
        module_slug=progress.module_slug,
        completed=progress.completed,
        best_score=progress.best_score,
        attempts=progress.attempts,
        earned_points=progress.earned_points,
    )


def get_modules_with_progress(progresses: list[ModuleProgress]) -> list[LearningModule]:
    progress_map = build_progress_map(progresses)
    modules: list[LearningModule] = []

    for index, module in enumerate(MODULES):
        modules.append(
            module.model_copy(
                update={
                    "reward_points": ACHIEVEMENT_DEFS[index]["reward_points"],
                    "progress": serialize_progress(progress_map.get(module.slug), module.slug),
                }
            )
        )

    return modules


def get_achievements(user: User, progresses: list[ModuleProgress]) -> list[Achievement]:
    completed_count = sum(1 for progress in progresses if progress.completed)
    achievements: list[Achievement] = []

    for item in ACHIEVEMENT_DEFS:
        achievements.append(
            Achievement(
                code=item["code"],
                title=item["title"],
                description=item["description"],
                reward_points=item["reward_points"],
                modules_required=item["modules_required"],
                unlocked=completed_count >= item["modules_required"],
            )
        )

    return achievements


def get_reward_points_for_module_order(module_index: int) -> int:
    if 0 <= module_index < len(ACHIEVEMENT_DEFS):
        return ACHIEVEMENT_DEFS[module_index]["reward_points"]
    return 0
