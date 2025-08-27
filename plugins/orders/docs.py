from typing import Dict, Any

# Documentation for Orders API endpoints
order_docs: Dict[str, Dict[str, Any]] = {
    "order_create": {
        "summary": "Create a new order",
        "description": """
        Create a new order in the system.
        
        The order will be associated with the authenticated user as the buyer.
        The system validates:
        - Product existence
        - Maximum orders per user limit
        - Total amount calculation
        
        Returns the created order with its assigned ID and status.
        """,
        "responses": {
            "201": {
                "description": "Order created successfully",
                "content": {
                    "application/json": {
                        "examples": {
                            "success": {
                                "summary": "Successfully created order",
                                "value": {
                                    "id": 1,
                                    "buyer_id": 123,
                                    "seller_id": 456,
                                    "product_items": [
                                        {"product_id": 1, "quantity": 2, "price": 29.99},
                                        {"product_id": 3, "quantity": 1, "price": 49.99}
                                    ],
                                    "total_amount": 109.97,
                                    "status": "pending",
                                    "shipping_address": {
                                        "street": "123 Main St",
                                        "city": "Anytown",
                                        "state": "CA",
                                        "zip": "12345",
                                        "country": "USA"
                                    },
                                    "notes": "Please deliver to the back door",
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
                            "invalid_product": {
                                "summary": "Invalid product ID",
                                "value": {"detail": "Product with ID 999 not found"}
                            },
                            "order_limit": {
                                "summary": "Order limit exceeded",
                                "value": {"detail": "Maximum orders limit reached for this user"}
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
    
    "order_get_by_id": {
        "summary": "Get order by ID",
        "description": """
        Retrieve a specific order by its ID.
        
        Only the buyer who created the order can access it.
        """,
        "responses": {
            "200": {
                "description": "Order details"
            },
            "404": {
                "description": "Order not found",
                "content": {
                    "application/json": {
                        "example": {"detail": "Order not found"}
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
    
    "order_update": {
        "summary": "Update an order",
        "description": """
        Update an existing order.
        
        Only the buyer who created the order can update it.
        Status transitions are validated according to business rules.
        """,
        "responses": {
            "200": {
                "description": "Order updated successfully"
            },
            "400": {
                "description": "Bad Request",
                "content": {
                    "application/json": {
                        "examples": {
                            "invalid_status": {
                                "summary": "Invalid status transition",
                                "value": {"detail": "Cannot transition from 'completed' to 'pending'"}
                            }
                        }
                    }
                }
            },
            "404": {
                "description": "Order not found",
                "content": {
                    "application/json": {
                        "example": {"detail": "Order not found"}
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
    
    "order_delete": {
        "summary": "Delete an order",
        "description": """
        Delete an existing order.
        
        Only the buyer who created the order can delete it.
        Orders can only be deleted if they are in certain statuses (e.g., pending).
        """,
        "responses": {
            "200": {
                "description": "Order deleted successfully",
                "content": {
                    "application/json": {
                        "example": {"detail": "Order deleted successfully"}
                    }
                }
            },
            "404": {
                "description": "Order not found",
                "content": {
                    "application/json": {
                        "example": {"detail": "Order not found"}
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
    
    "order_list": {
        "summary": "List orders",
        "description": """
        List all orders for the authenticated user.
        
        Results are paginated with skip and limit parameters.
        Only orders where the authenticated user is the buyer are returned.
        """,
        "responses": {
            "200": {
                "description": "List of orders"
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
    }
}