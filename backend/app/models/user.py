"""
User models for authentication
Pydantic models for request/response validation
"""

import re
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator


class RegisterRequest(BaseModel):
    """
    Request model for user registration
    
    Fields:
        email: User's email address (validated as proper email format)
        password: User's password (must meet security requirements)
        first_name: User's first name (required)
        last_name: User's last name (required)
    """
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """
        Validate password meets security requirements
        
        Requirements:
        - At least 8 characters long
        - Contains at least one uppercase letter
        - Contains at least one special character
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character (e.g. @)")
        return v

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, v):
        """Ensure names are not empty strings"""
        if not v or not str(v).strip():
            raise ValueError("Name cannot be empty")
        return str(v).strip()


class LoginRequest(BaseModel):
    """
    Request model for user login
    
    Fields:
        email: User's email address
        password: User's password
    """
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """
    Response model for successful authentication
    
    Fields:
        token: JWT access token
        token_type: Type of token (always "bearer")
        user_id: User's unique ID (UUID)
        email: User's email address
        role: User's role (e.g., "user", "admin")
        full_name: User's full name (optional)
        phone: User's phone number (optional)
    """
    token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    role: str
    full_name: Optional[str] = None
    phone: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    """
    Request model for changing password
    """
    current_password: str
    new_password: str
    
    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v


class DeleteAccountRequest(BaseModel):
    """
    Request model for deleting an account
    """
    password: str

class PushTokenRequest(BaseModel):
    """
    Request model for storing expo push token
    """
    token: str


# ============================================================================
# EXPLANATION FOR VIVA
# ============================================================================

"""
Q: What is a Pydantic model?
A: Pydantic models are Python classes that automatically validate data.
   When a request comes in, Pydantic checks if the data is correct
   (e.g., email is valid, password meets requirements).
   If validation fails, FastAPI automatically returns a 422 error.

Q: Why validate password on the client side?
A: We validate on the server side (here) for security. Client-side validation
   can be bypassed. Server-side validation ensures all passwords meet
   requirements before being stored.

Q: What is EmailStr?
A: EmailStr is a special Pydantic type that validates email format.
   It checks if the email has @ symbol, domain, etc.
   Example: "user@example.com" is valid, "userexample.com" is invalid.

Q: Why is full_name Optional?
A: Optional means the field is not required. Users can register with just
   email and password. Full name can be added later in profile settings.

Q: What happens if password is too short?
A: The @field_validator decorator checks the password. If it's less than
   8 characters or doesn't have a number, it raises ValueError.
   FastAPI catches this and returns a 422 error with the error message.
"""
