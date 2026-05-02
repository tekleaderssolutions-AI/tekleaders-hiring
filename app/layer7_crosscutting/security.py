import bcrypt

class PasswordHasher:
    @staticmethod
    def hash(password: str) -> str:
        # Generate a salt and hash the password
        salt = bcrypt.gensalt()
        hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), salt)
        # Return the hashed password as a string
        return hashed_bytes.decode('utf-8')

    @staticmethod
    def verify(plain_password: str, hashed_password: str) -> bool:
        # Check the plain password against the hashed password
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
