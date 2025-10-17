from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_current_user
from app.db.session import get_db
from app.schemas.user import UserOut
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserOut)
async def me(user=Depends(get_current_user)):
    return UserOut(
        id=str(user.id),
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        full_name=user.full_name,
        created_at=user.created_at,
    )


@router.get("/", response_model=list[UserOut])
async def list_users(
    session: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    service = UserService(session)
    users = await service.list_users()
    return [
        UserOut(
            id=str(user.id),
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            full_name=user.full_name,
            created_at=user.created_at,
        )
        for user in users
    ]
