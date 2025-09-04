from typing import Dict, Any

# Documentation for Auth API endpoints
auth_docs: Dict[str, Dict[str, Any]] = {
    "signup": {
        "summary": "Register a new user",
        "description": """
        Register a new user account in the system.
        
        Validates that the email is not already registered.
        Password is automatically hashed before storage.
        
        Returns the created user profile (without password).
        """,
        "responses": {
            "201": {
                "description": "User registered successfully",
                "content": {
                    "application/json": {
                        "examples": {
                            "success": {
                                "summary": "Successfully registered user",
                                "value": {
                                    "id": 1,
                                    "email": "user@example.com",
                                    "full_name": "John Doe",
                                    "is_active": True,
                                    "created_at": "2023-06-15T10:30:00Z"
                                }
                            }
                        }
                    }
                }
            },
            "400": {
                "description": "Bad Request",
                "content": {
                    "application/json": {
                        "examples": {
                            "email_exists": {
                                "summary": "Email already registered",
                                "value": {"detail": "Email already registered"}
                            },
                            "invalid_password": {
                                "summary": "Invalid password format",
                                "value": {"detail": "Password must be at least 8 characters long"}
                            }
                        }
                    }
                }
            }
        }
    },
    
    "login_for_access_token": {
        "summary": "Login for access token",
        "description": """
        Authenticate a user and issue a JWT access token.
        
        Uses OAuth2 password flow with username (email) and password.
        Returns a JWT token that expires after 30 minutes.
        """,
        "responses": {
            "200": {
                "description": "Successful authentication",
                "content": {
                    "application/json": {
                        "examples": {
                            "success": {
                                "summary": "Successfully authenticated",
                                "value": {
                                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                                    "token_type": "bearer"
                                }
                            }
                        }
                    }
                }
            },
            "401": {
                "description": "Authentication failed",
                "content": {
                    "application/json": {
                        "examples": {
                            "invalid_credentials": {
                                "summary": "Invalid credentials",
                                "value": {"detail": "Invalid credentials"}
                            },
                            "inactive_user": {
                                "summary": "Inactive user",
                                "value": {"detail": "Inactive user"}
                            }
                        }
                    }
                }
            }
        }
    },
    
    "read_current_user": {
        "summary": "Get current user",
        "description": """
        Retrieve the profile of the currently authenticated user.
        
        Requires a valid JWT token in the Authorization header.
        Returns the user profile without sensitive information.
        """,
        "responses": {
            "200": {
                "description": "Current user profile"
            },
            "401": {
                "description": "Not authenticated",
                "content": {
                    "application/json": {
                        "examples": {
                            "missing_token": {
                                "summary": "Missing token",
                                "value": {"detail": "Not authenticated"}
                            },
                            "invalid_token": {
                                "summary": "Invalid token",
                                "value": {"detail": "Could not validate credentials"}
                            },
                            "expired_token": {
                                "summary": "Expired token",
                                "value": {"detail": "Token has expired"}
                            }
                        }
                    }
                }
            }
        }
    }
}