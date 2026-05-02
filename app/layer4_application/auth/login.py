from app.layer5_domain.repositories.user_repository import UserRepository
from app.layer7_crosscutting.security import PasswordHasher
from app.layer7_crosscutting.auth import TokenProvider
from app.schemas.auth_schemas import UserLogin, TokenResponse

class LoginUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, login_data: UserLogin) -> TokenResponse:
        user = await self.user_repo.get_by_email(login_data.email)

        if not user or not user.hashed_password:
            raise ValueError("Invalid email or password")

        if not PasswordHasher.verify(login_data.password, user.hashed_password):
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("Account is deactivated")

        access_token = TokenProvider.create_access_token(data={"sub": user.email, "id": user.id})
        refresh_token = TokenProvider.create_refresh_token(data={"sub": user.email, "id": user.id})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
