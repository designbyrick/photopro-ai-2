"""
API Documentation and OpenAPI schema customization for PhotoPro AI.
Enhanced documentation with examples, descriptions, and interactive features.
"""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from typing import Dict, Any

def custom_openapi(app: FastAPI) -> Dict[str, Any]:
    """Generate custom OpenAPI schema with enhanced documentation"""
    
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="PhotoPro AI API",
        version="1.0.0",
        description="""
        # PhotoPro AI - Professional Photo Generation API
        
        Transform your photos into professional headshots using advanced AI technology.
        
        ## Features
        
        - **AI Photo Generation**: Convert photos to professional headshots
        - **Multiple Styles**: Corporate, Creative, Formal, and Casual styles
        - **User Authentication**: Secure JWT-based authentication
        - **Credit System**: Flexible credit-based pricing
        - **Real-time Updates**: WebSocket support for live processing status
        - **Admin Dashboard**: User management and analytics
        
        ## Authentication
        
        All protected endpoints require a JWT token in the Authorization header:
        ```
        Authorization: Bearer <your_jwt_token>
        ```
        
        ## Rate Limiting
        
        - 100 requests per minute per IP
        - Photo generation: 1 credit per photo
        - File upload: Max 10MB per file
        
        ## WebSocket Support
        
        Connect to `/ws/{user_id}` for real-time updates on photo processing.
        
        ## Support
        
        For API support and questions, please contact our support team.
        """,
        routes=app.routes,
    )
    
    # Add custom examples and descriptions
    openapi_schema["info"]["x-logo"] = {
        "url": "https://via.placeholder.com/200x200/667eea/ffffff?text=PhotoPro+AI"
    }
    
    # Add server information
    openapi_schema["servers"] = [
        {
            "url": "https://photopro-ai-backend.railway.app",
            "description": "Production server"
        },
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        }
    ]
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token"
        }
    }
    
    # Add global security
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    # Enhance endpoint documentation
    for path, path_item in openapi_schema["paths"].items():
        for method, operation in path_item.items():
            if method in ["get", "post", "put", "delete", "patch"]:
                # Add common responses
                if "responses" not in operation:
                    operation["responses"] = {}
                
                # Add common error responses
                operation["responses"]["401"] = {
                    "description": "Unauthorized - Invalid or missing token",
                    "content": {
                        "application/json": {
                            "example": {
                                "detail": "Could not validate credentials"
                            }
                        }
                    }
                }
                
                operation["responses"]["422"] = {
                    "description": "Validation Error",
                    "content": {
                        "application/json": {
                            "example": {
                                "detail": [
                                    {
                                        "loc": ["body", "field_name"],
                                        "msg": "field required",
                                        "type": "value_error.missing"
                                    }
                                ]
                            }
                        }
                    }
                }
                
                operation["responses"]["500"] = {
                    "description": "Internal Server Error",
                    "content": {
                        "application/json": {
                            "example": {
                                "detail": "Internal server error. Please try again later."
                            }
                        }
                    }
                }
    
    # Add specific endpoint enhancements
    if "/auth/signup" in openapi_schema["paths"]:
        openapi_schema["paths"]["/auth/signup"]["post"]["requestBody"] = {
            "content": {
                "application/json": {
                    "example": {
                        "email": "user@example.com",
                        "username": "johndoe",
                        "full_name": "John Doe",
                        "password": "securepassword123"
                    }
                }
            }
        }
    
    if "/photos/upload" in openapi_schema["paths"]:
        openapi_schema["paths"]["/photos/upload"]["post"]["requestBody"] = {
            "content": {
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "file": {
                                "type": "string",
                                "format": "binary",
                                "description": "Image file (JPG, PNG, WEBP)"
                            }
                        }
                    }
                }
            }
        }
    
    if "/photos/generate" in openapi_schema["paths"]:
        openapi_schema["paths"]["/photos/generate"]["post"]["requestBody"] = {
            "content": {
                "application/x-www-form-urlencoded": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "original_url": {
                                "type": "string",
                                "description": "URL of the uploaded image"
                            },
                            "style": {
                                "type": "string",
                                "enum": ["corporate", "creative", "formal", "casual"],
                                "description": "Photo generation style"
                            }
                        },
                        "required": ["original_url", "style"]
                    }
                }
            }
        }
    
    # Add tags for better organization
    openapi_schema["tags"] = [
        {
            "name": "Authentication",
            "description": "User registration, login, and authentication"
        },
        {
            "name": "Photos",
            "description": "Photo upload, generation, and management"
        },
        {
            "name": "Credits",
            "description": "Credit system and transactions"
        },
        {
            "name": "Users",
            "description": "User profile and account management"
        },
        {
            "name": "Admin",
            "description": "Administrative functions and analytics"
        },
        {
            "name": "Health",
            "description": "System health and status checks"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def add_examples_to_schema():
    """Add detailed examples to the OpenAPI schema"""
    
    examples = {
        "UserResponse": {
            "id": 1,
            "email": "john@example.com",
            "username": "johndoe",
            "full_name": "John Doe",
            "plan": "pro",
            "credits": 45,
            "is_active": True,
            "is_verified": True,
            "created_at": "2024-01-15T10:30:00Z"
        },
        "PhotoResponse": {
            "id": 123,
            "user_id": 1,
            "style": "corporate",
            "original_url": "https://bucket.s3.amazonaws.com/uploads/1/image.jpg",
            "processed_url": "https://bucket.s3.amazonaws.com/processed/1/result.jpg",
            "thumbnail_url": "https://bucket.s3.amazonaws.com/thumbnails/1/thumb.jpg",
            "credits_used": 1,
            "status": "completed",
            "created_at": "2024-01-15T10:35:00Z"
        },
        "CreditTransaction": {
            "id": 456,
            "user_id": 1,
            "amount": -1,
            "transaction_type": "photo_generation",
            "description": "Photo generation - corporate style",
            "created_at": "2024-01-15T10:35:00Z"
        },
        "ErrorResponse": {
            "detail": "Insufficient credits. Please purchase more credits."
        },
        "SuccessResponse": {
            "message": "Photo generated successfully!",
            "photo_id": 123,
            "credits_remaining": 44
        }
    }
    
    return examples


# API Documentation constants
API_TAGS = [
    {
        "name": "Authentication",
        "description": "User authentication and registration endpoints"
    },
    {
        "name": "Photos", 
        "description": "Photo upload, generation, and management"
    },
    {
        "name": "Credits",
        "description": "Credit system and transaction management"
    },
    {
        "name": "Users",
        "description": "User profile and account management"
    },
    {
        "name": "Admin",
        "description": "Administrative functions and system analytics"
    },
    {
        "name": "Health",
        "description": "System health checks and status monitoring"
    }
]

# Common response schemas
COMMON_RESPONSES = {
    400: {
        "description": "Bad Request",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Invalid request parameters"
                }
            }
        }
    },
    401: {
        "description": "Unauthorized",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Could not validate credentials"
                }
            }
        }
    },
    403: {
        "description": "Forbidden",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Insufficient permissions"
                }
            }
        }
    },
    404: {
        "description": "Not Found",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Resource not found"
                }
            }
        }
    },
    422: {
        "description": "Validation Error",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "loc": ["body", "field"],
                            "msg": "field required",
                            "type": "value_error.missing"
                        }
                    ]
                }
            }
        }
    },
    429: {
        "description": "Rate Limit Exceeded",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Rate limit exceeded. Please try again later."
                }
            }
        }
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Internal server error. Please try again later."
                }
            }
        }
    }
}
