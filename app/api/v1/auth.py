from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.schemas.auth_schemas import (
    UserSignUp, UserLogin, GoogleLoginRequest, TokenResponse, UserRead
)
from app.layer4_application.auth.login import LoginUseCase
from app.layer4_application.auth.google_login import GoogleLoginUseCase
from app.layer6_data.repositories_impl.postgres_user_repo import PostgresUserRepository
from app.layer6_data.models.company_model import CompanyModel
from app.layer2_adapters.auth.google_auth_adapter import GoogleAuthAdapter
from app.layer7_crosscutting.security import PasswordHasher
from app.layer7_crosscutting.auth import TokenProvider
from app.dependencies import get_db, get_current_user
from app.layer5_domain.entities.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ─── Sign Up ──────────────────────────────────────────────────────────────────
@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new company admin — creates company and auto-logs in"
)
async def signup(
    payload: UserSignUp,
    db: AsyncSession = Depends(get_db)
):
    repo = PostgresUserRepository(db)

    existing = await repo.get_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")

    if payload.password != payload.re_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

    # Create company for this admin
    company_id = str(uuid.uuid4())
    company_name = payload.company_name.strip() if payload.company_name else f"{payload.first_name}'s Company"
    db.add(CompanyModel(id=company_id, name=company_name))
    await db.flush()

    # Create admin user
    user = User(
        id=None,
        email=payload.email,
        hashed_password=PasswordHasher.hash(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        company_id=company_id,
        role="admin",
    )
    created = await repo.create(user)

    access_token = TokenProvider.create_access_token(data={"sub": created.email, "id": created.id})
    refresh_token = TokenProvider.create_refresh_token(data={"sub": created.email, "id": created.id})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

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
async def get_me(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    company_name = None
    if current_user.company_id:
        res = await db.execute(select(CompanyModel).where(CompanyModel.id == current_user.company_id))
        company = res.scalar_one_or_none()
        company_name = company.name if company else None
    return UserRead(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role,
        company_id=current_user.company_id,
        company_name=company_name,
        is_active=current_user.is_active
    )
