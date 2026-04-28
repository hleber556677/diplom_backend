
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.content import MODULES
from app.core.config import settings
from app.core.db import get_db
from app.dependencies import get_admin_user, get_current_user
from app.models import ModuleProgress, User
from app.schemas import (
    AdminUserProgress,
    LeaderboardEntry,
    ModuleSubmitRequest,
    ModuleSubmitResponse,
    StudentProfile,
)
from app.services import (
    get_achievements,
    get_level_title,
    get_modules_with_progress,
    get_reward_points_for_module_order,
    serialize_progress,
)


router = APIRouter(prefix="/academy", tags=["academy"])


@router.get("/modules")
def get_modules(
    current_user: User = Depends(get_current_user),
):
    return get_modules_with_progress(current_user.module_progresses)


@router.get("/profile", response_model=StudentProfile)
def get_profile(
    current_user: User = Depends(get_current_user),
):
    progresses = current_user.module_progresses
    return StudentProfile(
        display_name=current_user.display_name,
        email=current_user.email,
        is_admin=current_user.email.lower() in settings.admin_emails,
        total_points=current_user.total_points,
        level_title=get_level_title(current_user.total_points),
        completed_modules=sum(1 for progress in progresses if progress.completed),
        total_modules=len(MODULES),
        achievements=get_achievements(current_user, progresses),
        progress=[serialize_progress(progress, progress.module_slug) for progress in progresses],
    )


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
def get_leaderboard(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.total_points.desc(), User.display_name.asc()).limit(10).all()

    return [
        LeaderboardEntry(
            place=index,
            display_name=user.display_name,
            email=user.email,
            total_points=user.total_points,
            level_title=get_level_title(user.total_points),
        )
        for index, user in enumerate(users, start=1)
    ]


@router.get("/admin/users-progress", response_model=list[AdminUserProgress])
def get_users_progress(
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    users = db.query(User).order_by(User.display_name.asc(), User.email.asc()).all()
    result: list[AdminUserProgress] = []

    for user in users:
        progresses = user.module_progresses
        result.append(
            AdminUserProgress(
                id=user.id,
                display_name=user.display_name,
                email=user.email,
                is_admin=user.email.lower() in settings.admin_emails,
                total_points=user.total_points,
                level_title=get_level_title(user.total_points),
                completed_modules=sum(1 for progress in progresses if progress.completed),
                total_modules=len(MODULES),
                progress=[serialize_progress(progress, progress.module_slug) for progress in progresses],
            )
        )

    return result


@router.delete("/admin/users/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user.email.lower() == settings.admin_email:
        raise HTTPException(status_code=400, detail="Admin user cannot be deleted")

    db.delete(user)
    db.commit()


@router.post("/modules/{module_slug}/submit", response_model=ModuleSubmitResponse)
def submit_module(
    module_slug: str,
    payload: ModuleSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    module = next((item for item in MODULES if item.slug == module_slug), None)
    if module is None:
        raise HTTPException(status_code=404, detail="Module not found")

    progress = next(
        (item for item in current_user.module_progresses if item.module_slug == module_slug),
        None,
    )
    if progress is None:
        progress = ModuleProgress(
            module_slug=module_slug,
            user_id=current_user.id,
            attempts=0,
            best_score=0,
            completed=False,
            earned_points=0,
        )
        db.add(progress)
        current_user.module_progresses.append(progress)

    progress.attempts = (progress.attempts or 0) + 1

    correct = payload.selected_index == module.minigame.correct_index
    earned_points = 0
    unlocked_achievements = []
    before_achievements = {
        item.code for item in get_achievements(current_user, current_user.module_progresses) if item.unlocked
    }

    if correct:
        was_completed = progress.completed
        progress.completed = True
        progress.best_score = 100

        if not was_completed:
            completed_count = sum(1 for item in current_user.module_progresses if item.completed)
            earned_points = get_reward_points_for_module_order(completed_count - 1)
            progress.earned_points = earned_points
            current_user.total_points = (current_user.total_points or 0) + earned_points
        else:
            progress.earned_points = progress.earned_points or 0
    else:
        progress.best_score = max(progress.best_score or 0, 30)

    db.commit()
    db.refresh(current_user)
    db.refresh(progress)

    if correct:
        after_achievements = get_achievements(current_user, current_user.module_progresses)
        unlocked_achievements = [
            item for item in after_achievements if item.unlocked and item.code not in before_achievements
        ]

    return ModuleSubmitResponse(
        correct=correct,
        explanation=module.minigame.explanation,
        earned_points=earned_points,
        total_points=current_user.total_points,
        progress=serialize_progress(progress, module_slug),
        level_title=get_level_title(current_user.total_points),
        unlocked_achievements=unlocked_achievements,
    )
