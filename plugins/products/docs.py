from typing import Dict, Any

# Documentation for Products API endpoints
product_docs: Dict[str, Dict[str, Any]] = {
    "product_create": {
        "summary": "Create a new product",
        "description": """
        Create a new product in the marketplace.
        
        The product will be associated with the authenticated user as the seller.
        The system enforces product limits per seller based on configuration.
        
        Returns the created product with its assigned ID.
        """,
        "responses": {
            "201": {
                "description": "Product created successfully",
                "content": {
                    "application/json": {
                        "examples": {
                            "success": {
                                "summary": "Successfully created product",
                                "value": {
                                    "id": 1,
                                    "name": "Premium Widget",
                                    "description": "High-quality widget for industrial use",
                                    "price": 29.99,
                                    "stock": 100,
                                    "seller_id": 123,
                                    "category": "industrial",
                                    "created_at": "2023-06-15T10:30:00Z",
                                    "updated_at": "2023-06-15T10:30:00Z"
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
                            "product_limit": {
                                "summary": "Product limit exceeded",
                                "value": {"detail": "Maximum product limit reached for this seller"}
                            },
                            "invalid_data": {
                                "summary": "Invalid product data",
                                "value": {"detail": "Price must be greater than zero"}
                            }
                        }
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
    
    "product_get_by_id": {
        "summary": "Get product by ID",
        "description": """
        Retrieve a specific product by its ID.
        
        This endpoint is publicly accessible and does not require authentication.
        """,
        "responses": {
            "200": {
                "description": "Product details"
            },
            "404": {
                "description": "Product not found",
                "content": {
                    "application/json": {
                        "example": {"detail": "Product not found"}
                    }
                }
            }
        }
    },
    
    "product_update": {
        "summary": "Update a product",
        "description": """
        Update an existing product.
        
        Only the seller who created the product can update it.
        All fields are optional and only provided fields will be updated.
        """,
        "responses": {
            "200": {
                "description": "Product updated successfully"
            },
            "404": {
                "description": "Product not found or permission denied",
                "content": {
                    "application/json": {
                        "example": {"detail": "Product not found or permission denied"}
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
    
    "product_delete": {
        "summary": "Delete a product",
        "description": """
        Delete an existing product.
        
        Only the seller who created the product can delete it.
        Products with active orders cannot be deleted.
        """,
        "responses": {
            "200": {
                "description": "Product deleted successfully",
                "content": {
                    "application/json": {
                        "example": {"detail": "Product deleted successfully"}
                    }
                }
            },
            "404": {
                "description": "Product not found or permission denied",
                "content": {
                    "application/json": {
                        "example": {"detail": "Product not found or permission denied"}
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
                "description": "Conflict - Product has active orders",
                "content": {
                    "application/json": {
                        "example": {"detail": "Cannot delete product with active orders"}
                    }
                }
            }
        }
    },
    
    "product_list": {
        "summary": "List or search products",
        "description": """
        List all products with pagination, sorting, and optional search filtering.
        
        This endpoint is publicly accessible and does not require authentication.
        Results can be filtered by search term matching product names.
        """,
        "responses": {
            "200": {
                "description": "List of products"
            }
        }
    }
}