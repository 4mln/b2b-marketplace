from passlib.context import CryptContext

# Configure password hashing
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Generate a secure hash from a password."""
    return password_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return password_context.verify(plain_password, hashed_password)