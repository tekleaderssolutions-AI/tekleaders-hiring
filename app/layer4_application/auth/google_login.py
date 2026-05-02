from app.layer5_domain.entities.user import User
from app.layer5_domain.repositories.user_repository import UserRepository
from app.layer3_ports.auth_port import AuthPort
from app.layer7_crosscutting.auth import TokenProvider
from app.schemas.auth_schemas import GoogleLoginRequest, TokenResponse

class GoogleLoginUseCase:
    def __init__(self, user_repo: UserRepository, auth_port: AuthPort):
        self.user_repo = user_repo
        self.auth_port = auth_port

    async def execute(self, request: GoogleLoginRequest) -> TokenResponse:
        user_info = await self.auth_port.verify_google_token(request.id_token)
        if not user_info:
            raise ValueError("Invalid or expired Google token")

        email = user_info["email"]
        user = await self.user_repo.get_by_email(email)

        if not user:
            new_user = User(
                id=None,
                email=email,
                hashed_password=None,
                first_name=user_info.get("first_name", ""),
                last_name=user_info.get("last_name", ""),
                google_id=user_info.get("google_id")
            )
            user = await self.user_repo.create(new_user)
        elif not user.google_id:
            user.google_id = user_info.get("google_id")
            await self.user_repo.update(user)

        access_token = TokenProvider.create_access_token(data={"sub": user.email, "id": user.id})
        refresh_token = TokenProvider.create_refresh_token(data={"sub": user.email, "id": user.id})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
