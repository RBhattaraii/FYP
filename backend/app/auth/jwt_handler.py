"""
JWT Token Handler
Creates and verifies JWT tokens for authentication
"""

import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from dotenv import load_dotenv
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import asyncpg

# Load environment variables
load_dotenv()

# Get JWT configuration from environment variables
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 60))
ALGORITHM = "HS256"  # HMAC with SHA-256

# Security scheme for FastAPI
security = HTTPBearer()


def create_access_token(user_id: str, additional_claims: dict = None) -> str:
    """
    Create a JWT access token for a user.
    
    The token contains:
    - sub (subject): User's ID
    - exp (expiry): When the token expires
    - any additional claims (e.g., role, email)
    
    Args:
        user_id: User's unique ID (UUID as string)
        additional_claims: Optional dict of additional claims to include in token
    
    Returns:
        str: Encoded JWT token
    
    Example:
        token = create_access_token("550e8400-e29b-41d4-a716-446655440000")
        # Returns: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        
        token = create_access_token("admin", {"role": "admin", "email": "admin@example.com"})
        # Returns token with role claim
    """
    # Calculate expiry time
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    
    # Create token payload
    # Only include essential data (user_id and expiry)
    payload = {
        "sub": user_id,  # Subject: who the token is for
        "exp": expire    # Expiry: when the token expires
    }
    
    # Add additional claims if provided
    if additional_claims:
        payload.update(additional_claims)
    
    # Encode the payload into a JWT token
    token = jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)
    
    return token


def verify_access_token(token: str) -> str:
    """
    Verify a JWT token and extract the user ID.
    
    Args:
        token: JWT token string
    
    Returns:
        str: User ID if token is valid
    
    Raises:
        JWTError: If token is invalid or expired
    
    Example:
        user_id = verify_access_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
        # Returns: "550e8400-e29b-41d4-a716-446655440000"
    """
    try:
        # Decode the token
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        
        # Extract user ID from payload
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise JWTError("Token payload invalid")
        
        return user_id
        
    except JWTError:
        raise JWTError("Could not validate credentials")


def decode_access_token(token: str) -> dict:
    """
    Decode a JWT token and return the full payload.
    
    This is similar to verify_access_token but returns the entire payload
    instead of just the user_id. Useful when you need access to all token data.
    
    Args:
        token: JWT token string
    
    Returns:
        dict: Token payload containing all claims (sub, exp, etc.)
    
    Raises:
        JWTError: If token is invalid or expired
    
    Example:
        payload = decode_access_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
        # Returns: {"sub": "user-id", "exp": 1234567890}
        user_id = payload.get("user_id") or payload.get("sub")
    """
    try:
        # Decode the token
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        
        # Add user_id to payload for convenience (copy of sub)
        if "sub" in payload:
            payload["user_id"] = payload["sub"]
        
        return payload
        
    except JWTError as e:
        raise JWTError(f"Could not validate credentials: {str(e)}")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    FastAPI dependency to get current user from JWT token.
    This is used for protected endpoints that require authentication.
    
    Usage:
        @app.get("/protected")
        async def protected_endpoint(current_user: dict = Depends(get_current_user)):
            user_id = current_user["user_id"]
    
    Returns:
        dict: User data including user_id
    
    Raises:
        HTTPException: 401 if token is invalid or missing
    """
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[dict]:
    """
    FastAPI dependency to optionally get current user from JWT token.
    This is used for endpoints that work for both authenticated and anonymous users.
    
    Usage:
        @app.get("/optional-auth")
        async def optional_endpoint(current_user: Optional[dict] = Depends(get_current_user_optional)):
            if current_user:
                user_id = current_user["user_id"]
                # Do something for authenticated user
            else:
                # Do something for anonymous user
    
    Returns:
        dict or None: User data if authenticated, None if anonymous
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        return payload
    except JWTError:
        # Don't raise error for optional auth - just return None
        return None


# ============================================================================
# EXPLANATION FOR VIVA
# ============================================================================

"""
Q: What is JWT?
A: JWT (JSON Web Token) is a secure way to transmit information between
   the client and server. It's like a digital ID card that proves who you are.
   
   Structure: JWT has 3 parts separated by dots (.)
   1. Header: Algorithm used (HS256)
   2. Payload: Data (user_id, expiry)
   3. Signature: Verification code
   
   Example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c

Q: How does JWT work?
A: 
   1. User logs in with email/password
   2. Server verifies credentials
   3. Server creates JWT token with user_id
   4. Server sends token to client
   5. Client stores token (localStorage, cookies)
   6. Client sends token with every request (Authorization header)
   7. Server verifies token and identifies user
   8. Server processes request

Q: Why use JWT instead of sessions?
A: 
   - Stateless: Server doesn't need to store session data
   - Scalable: Works across multiple servers
   - Mobile-friendly: Easy to use in mobile apps
   - Secure: Signed with secret key, can't be tampered with

Q: What is the "sub" field?
A: "sub" stands for "subject" - it identifies who the token is for.
   In our case, it's the user's ID (UUID).

Q: What is the "exp" field?
A: "exp" stands for "expiry" - it's the timestamp when the token expires.
   After expiry, the token is no longer valid and user must login again.

Q: What is JWT_SECRET?
A: JWT_SECRET is a secret key used to sign the token. It's like a password
   that only the server knows. Without this secret, no one can create or
   verify tokens. That's why we store it in .env file (never in code).

Q: What is HS256?
A: HS256 is the algorithm used to sign the token. It stands for:
   - HMAC: Hash-based Message Authentication Code
   - SHA-256: Secure Hash Algorithm with 256-bit output
   It creates a signature that proves the token hasn't been tampered with.

Q: Can someone fake a JWT token?
A: No, because the token is signed with JWT_SECRET. If someone changes
   the payload (e.g., changes user_id), the signature won't match and
   verification will fail.

Q: What happens when token expires?
A: When the token expires, verify_access_token() raises JWTError.
   The API returns 401 Unauthorized. User must login again to get a new token.
"""
