from abc import ABC, abstractmethod
from typing import Dict, Optional

class AuthPort(ABC):
    @abstractmethod
    async def verify_google_token(self, id_token: str) -> Optional[Dict]:
        """Verify Google ID token and return user info."""
        pass
