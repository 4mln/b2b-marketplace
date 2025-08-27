import os
import sys
import secrets
import base64
from pathlib import Path

def generate_secret_key(length: int = 32) -> str:
    return base64.urlsafe_b64encode(secrets.token_bytes(length)).decode('utf-8')

def create_env_file():
    env_example = Path('.env.example')
    env_file = Path('.env')
    
    if not env_example.exists():
        print("Error: .env.example file not found!")
        sys.exit(1)
    
    if env_file.exists():
        response = input(".env file already exists. Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    # Generate secure values
    secret_key = generate_secret_key()
    
    # Read .env.example and replace placeholder values
    with open(env_example, 'r') as f:
        env_content = f.read()
    
    # Replace placeholders with secure values
    env_content = env_content.replace('your-secret-key-here', secret_key)
    
    # Write the new .env file
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("\nSecurity Configuration Setup Complete!")
    print("\nImportant Security Reminders:")
    print("1. Keep your .env file secure and never commit it to version control")
    print("2. Use different secret keys for development and production")
    print("3. Regularly rotate your secret keys")
    print("4. Ensure proper file permissions on your .env file")
    print("5. Back up your configuration securely")

def main():
    print("Setting up secure configuration...\n")
    create_env_file()

if __name__ == "__main__":
    main()