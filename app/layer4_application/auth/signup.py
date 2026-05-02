from app.layer5_domain.entities.user import User
from app.layer5_domain.repositories.user_repository import UserRepository
from app.layer7_crosscutting.security import PasswordHasher
from app.schemas.auth_schemas import UserSignUp

class SignUpUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, signup_data: UserSignUp) -> User:
        # Check if user exists
        existing_user = await self.user_repo.get_by_email(signup_data.email)
        if existing_user:
            raise ValueError("User with this email already exists")

        # Hash password
        hashed_pw = PasswordHasher.hash(signup_data.password)

        # Create user entity
        new_user = User(
            id=None,
            email=signup_data.email,
            hashed_password=hashed_pw,
            first_name=signup_data.first_name,
            last_name=signup_data.last_name
        )

        # Persist
        return await self.user_repo.create(new_user)
