from typing import Dict, Optional
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from app.layer3_ports.auth_port import AuthPort
from app.config import settings

class GoogleAuthAdapter(AuthPort):
    async def verify_google_token(self, token: str) -> Optional[Dict]:
        try:
            id_info = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
            return {
                "email": id_info["email"],
                "first_name": id_info.get("given_name", ""),
                "last_name": id_info.get("family_name", ""),
                "google_id": id_info["sub"]
            }
        except ValueError:
            return None
