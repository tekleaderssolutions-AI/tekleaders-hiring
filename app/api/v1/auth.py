from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth_schemas import (
    UserSignUp, UserLogin, GoogleLoginRequest, TokenResponse, UserRead
)
from app.layer4_application.auth.signup import SignUpUseCase
from app.layer4_application.auth.login import LoginUseCase
from app.layer4_application.auth.google_login import GoogleLoginUseCase
from app.layer6_data.repositories_impl.postgres_user_repo import PostgresUserRepository
from app.layer2_adapters.auth.google_auth_adapter import GoogleAuthAdapter
from app.dependencies import get_db, get_current_user
from app.layer5_domain.entities.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ─── Sign Up ──────────────────────────────────────────────────────────────────
@router.post(
    "/signup",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user with email & password"
)
async def signup(
    payload: UserSignUp,
    db: AsyncSession = Depends(get_db)
):
    repo = PostgresUserRepository(db)
    use_case = SignUpUseCase(user_repo=repo)
    try:
        user = await use_case.execute(payload)
        return UserRead(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

# ─── Email/Password Login ─────────────────────────────────────────────────────
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email and password"
)
async def login(
    payload: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    repo = PostgresUserRepository(db)
    use_case = LoginUseCase(user_repo=repo)
    try:
        return await use_case.execute(payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )

# ─── Google OAuth Login ───────────────────────────────────────────────────────
@router.post(
    "/google",
    response_model=TokenResponse,
    summary="Sign in / Sign up with Google OAuth ID token"
)
async def google_login(
    payload: GoogleLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    repo = PostgresUserRepository(db)
    adapter = GoogleAuthAdapter()
    use_case = GoogleLoginUseCase(user_repo=repo, auth_port=adapter)
    try:
        return await use_case.execute(payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

# ─── Get Current User (Protected) ────────────────────────────────────────────
@router.get(
    "/me",
    response_model=UserRead,
    summary="Get the currently authenticated user's profile"
)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserRead(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        is_active=current_user.is_active
    )
