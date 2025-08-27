from typing import Dict, Any

# Documentation for User API endpoints
user_docs: Dict[str, Dict[str, Any]] = {
    "create_user_endpoint": {
        "summary": "Create a new user",
        "description": """
        Create a new user account in the system.
        
        This endpoint is typically used by administrators or for system integration.
        For regular user registration, use the /auth/signup endpoint instead.
        
        Returns the created user profile (without password).
        """,
        "responses": {
            "201": {
                "description": "User created successfully",
                "content": {
                    "application/json": {
                        "examples": {
                            "success": {
                                "summary": "Successfully created user",
                                "value": {
                                    "id": 1,
                                    "email": "user@example.com",
                                    "full_name": "John Doe",
                                    "is_active": true,
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
                            "invalid_data": {
                                "summary": "Invalid user data",
                                "value": {"detail": "Invalid email format"}
                            }
                        }
                    }
                }
            }
        }
    },
    
    "get_user_endpoint": {
        "summary": "Get user by ID",
        "description": """
        Retrieve a specific user by their ID.
        
        Returns the user profile without sensitive information.
        """,
        "responses": {
            "200": {
                "description": "User details"
            },
            "404": {
                "description": "User not found",
                "content": {
                    "application/json": {
                        "example": {"detail": "User not found"}
                    }
                }
            }
        }
    },
    
    "update_user_endpoint": {
        "summary": "Update a user",
        "description": """
        Update an existing user's profile.
        
        Users can only update their own profile unless they have admin privileges.
        All fields are optional and only provided fields will be updated.
        """,
        "responses": {
            "200": {
                "description": "User updated successfully"
            },
            "404": {
                "description": "User not found or permission denied",
                "content": {
                    "application/json": {
                        "example": {"detail": "User not found or permission denied"}
                    }
                }
            },
            "401": {
                "description": "Unauthorized",
                "content": {
                    "application/json": {
                        "example": {"detail": "Not authenticated"}
                    }
                }
            }
        }
    },
    
    "delete_user_endpoint": {
        "summary": "Delete a user",
        "description": """
        Delete an existing user account.
        
        Users can only delete their own account unless they have admin privileges.
        Account deletion may be restricted if the user has active orders or products.
        """,
        "responses": {
            "200": {
                "description": "User deleted successfully",
                "content": {
                    "application/json": {
                        "example": {"detail": "User deleted successfully"}
                    }
                }
            },
            "404": {
                "description": "User not found or permission denied",
                "content": {
                    "application/json": {
                        "example": {"detail": "User not found or permission denied"}
                    }
                }
            },
            "401": {
                "description": "Unauthorized",
                "content": {
                    "application/json": {
                        "example": {"detail": "Not authenticated"}
                    }
                }
            },
            "409": {
                "description": "Conflict - User has active resources",
                "content": {
                    "application/json": {
                        "example": {"detail": "Cannot delete user with active orders or products"}
                    }
                }
            }
        }
    },
    
    "list_users_endpoint": {
        "summary": "List or search users",
        "description": """
        List all users with pagination, sorting, and optional search filtering.
        
        Results can be filtered by search term matching user names or emails.
        This endpoint typically requires admin privileges.
        """,
        "responses": {
            "200": {
                "description": "List of users"
            },
            "401": {
                "description": "Unauthorized",
                "content": {
                    "application/json": {
                        "example": {"detail": "Not authenticated"}
                    }
                }
            },
            "403": {
                "description": "Forbidden",
                "content": {
                    "application/json": {
                        "example": {"detail": "Not enough permissions"}
                    }
                }
            }
        }
    }
}