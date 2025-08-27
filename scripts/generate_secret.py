import secrets
import base64

def generate_secret_key(length: int = 32) -> str:
    """Generate a secure secret key suitable for cryptographic use."""
    return base64.urlsafe_b64encode(secrets.token_bytes(length)).decode('utf-8')

def main():
    # Generate a secure secret key
    secret_key = generate_secret_key()
    
    print("\nGenerated Secret Key (save this securely):\n")
    print(secret_key)
    print("\nAdd this to your .env file as:")
    print(f"SECRET_KEY={secret_key}\n")
    
    # Additional security recommendations
    print("Security Recommendations:")
    print("1. Store this key securely in your environment variables")
    print("2. Never commit this key to version control")
    print("3. Use different keys for development and production")
    print("4. Rotate this key periodically for enhanced security\n")

if __name__ == "__main__":
    main()