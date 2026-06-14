"""
Authentication routes
Handles user registration and login
"""

from fastapi import APIRouter, Request, Depends, HTTPException, status
from slowapi import Limiter
from slowapi.util import get_remote_address
import asyncpg

from app.models.user import RegisterRequest, LoginRequest, AuthResponse
from app.auth.password import hash_password, verify_password
from app.auth.jwt_handler import create_access_token
from app.database.postgres import get_db

# Create router
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@router.post("/register", response_model=AuthResponse)
@limiter.limit("3/minute")
async def register(
    request: Request,
    user_data: RegisterRequest,
    db: asyncpg.Connection = Depends(get_db)
):
    """
    Register a new user
    
    Steps:
    1. Validate email and password (done by Pydantic)
    2. Check if email already exists
    3. Hash the password using bcrypt
    4. Store user in PostgreSQL database
    5. Generate JWT token
    6. Return token and user info
    
    Rate limit: 3 requests per minute
    
    Args:
        request: FastAPI request object (for rate limiting)
        user_data: Registration data (email, password, full_name)
        db: Database connection (injected by FastAPI)
    
    Returns:
        AuthResponse: JWT token and user information
    
    Raises:
        HTTPException 400: If email already exists
        HTTPException 500: If database error occurs
    """
    try:
        # Step 1: Check if email already exists
        # Using parameterized query ($1) to prevent SQL injection
        existing_user = await db.fetchrow(
            "SELECT id FROM users WHERE email = $1",
            user_data.email
        )
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Step 2: Hash the password
        # Never store plain text passwords!
        password_hash = hash_password(user_data.password)
        
        # Step 3: Insert user into database
        # Using parameterized query ($1, $2, $3) for security
        # RETURNING clause gets the created user data
        new_user = await db.fetchrow(
            """
            INSERT INTO users (email, password_hash, full_name, role)
            VALUES ($1, $2, $3, $4)
            RETURNING id, email, full_name, role, created_at
            """,
            user_data.email,
            password_hash,
            user_data.full_name,
            "user"  # Default role
        )
        
        # Step 4: Generate JWT token
        # Token contains user_id and expiry
        token = create_access_token(str(new_user["id"]))
        
        # Step 5: Return response
        # Never return password_hash!
        return AuthResponse(
            token=token,
            token_type="bearer",
            user_id=str(new_user["id"]),
            email=new_user["email"],
            role=new_user["role"]
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (like email already exists)
        raise
    except Exception as e:
        # Log the error and return generic error message
        print(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=AuthResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    credentials: LoginRequest,
    db: asyncpg.Connection = Depends(get_db)
):
    """
    Login with email and password
    
    Steps:
    1. Look up user by email
    2. Check if user exists
    3. Verify password against stored hash
    4. Generate JWT token
    5. Return token and user info
    
    Rate limit: 5 requests per minute
    
    Args:
        request: FastAPI request object (for rate limiting)
        credentials: Login credentials (email, password)
        db: Database connection (injected by FastAPI)
    
    Returns:
        AuthResponse: JWT token and user information
    
    Raises:
        HTTPException 401: If email not found or password is wrong
        HTTPException 500: If database error occurs
    """
    try:
        # Step 1: Look up user by email
        # Using parameterized query ($1) to prevent SQL injection
        user = await db.fetchrow(
            """
            SELECT id, email, password_hash, full_name, role, is_active
            FROM users
            WHERE email = $1
            """,
            credentials.email
        )
        
        # Step 2: Check if user exists
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Step 3: Check if account is active
        if not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )
        
        # Step 4: Verify password
        # Compare entered password with stored hash
        is_password_correct = verify_password(
            credentials.password,
            user["password_hash"]
        )
        
        if not is_password_correct:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Step 5: Generate JWT token
        token = create_access_token(str(user["id"]))
        
        # Step 6: Return response
        # Never return password_hash!
        return AuthResponse(
            token=token,
            token_type="bearer",
            user_id=str(user["id"]),
            email=user["email"],
            role=user["role"]
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (like invalid credentials)
        raise
    except Exception as e:
        # Log the error and return generic error message
        print(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


# ============================================================================
# EXPLANATION FOR VIVA
# ============================================================================

"""
Q: What happens step-by-step during registration?
A: 
   1. User sends POST request to /auth/register with email, password, full_name
   2. Pydantic validates the data (email format, password length, etc.)
   3. Rate limiter checks if user exceeded 3 requests per minute
   4. Check if email already exists in database (parameterized query)
   5. If email exists → return 400 error "Email already registered"
   6. Hash the password using bcrypt (one-way encryption)
   7. Insert user into database with hashed password (parameterized query)
   8. Generate JWT token with user_id
   9. Return token and user info to client
   10. Client stores token for future requests

Q: What happens step-by-step during login?
A: 
   1. User sends POST request to /auth/login with email and password
   2. Pydantic validates the data
   3. Rate limiter checks if user exceeded 5 requests per minute
   4. Look up user by email in database (parameterized query)
   5. If user not found → return 401 error "Invalid email or password"
   6. Check if account is active
   7. If account deactivated → return 401 error "Account is deactivated"
   8. Verify password using bcrypt (compare with stored hash)
   9. If password wrong → return 401 error "Invalid email or password"
   10. Generate JWT token with user_id
   11. Return token and user info to client
   12. Client stores token for future requests

Q: Why use parameterized queries?
A: To prevent SQL injection attacks. Parameterized queries treat user input
   as data, not as SQL commands.
   
   ❌ UNSAFE (SQL injection vulnerable):
   query = f"SELECT * FROM users WHERE email = '{email}'"
   # Attacker can input: "'; DROP TABLE users; --"
   
   ✅ SAFE (parameterized query):
   query = "SELECT * FROM users WHERE email = $1"
   await db.fetchrow(query, email)
   # User input is treated as data, not SQL code

Q: Why return 401 for both "user not found" and "wrong password"?
A: Security! If we return different errors, attackers can enumerate
   which emails are registered.
   
   ❌ BAD:
   - "Email not found" → Attacker knows email isn't registered
   - "Wrong password" → Attacker knows email IS registered
   
   ✅ GOOD:
   - "Invalid email or password" → Attacker doesn't know which is wrong

Q: What is rate limiting?
A: Rate limiting restricts how many requests a user can make in a time period.
   This prevents brute-force attacks (trying many passwords).
   
   - Register: 3 requests per minute (prevents spam accounts)
   - Login: 5 requests per minute (prevents password guessing)

Q: What is Depends(get_db)?
A: Depends is FastAPI's dependency injection. It automatically:
   1. Calls get_db() to get a database connection
   2. Passes the connection to the route function
   3. Closes the connection after the request
   
   This ensures we always have a database connection and it's properly closed.

Q: Why never return password_hash?
A: Security! Even though it's hashed, we should never expose it.
   If an attacker gets the hash, they can try to crack it offline.
   Only return data that the client needs (token, user_id, email, role).

Q: What is HTTPException?
A: HTTPException is FastAPI's way of returning error responses.
   - status_code: HTTP status code (400, 401, 500, etc.)
   - detail: Error message shown to client
   
   Example:
   raise HTTPException(status_code=401, detail="Invalid credentials")
   Returns: {"detail": "Invalid credentials"} with 401 status

Q: How does the client use the token?
A: After login/register, the client:
   1. Stores the token (localStorage, cookies, secure storage)
   2. Sends token with every request in Authorization header:
      Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   3. Server verifies token and identifies the user
   4. Server processes the request
"""
