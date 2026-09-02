"""
Authentication routes
Handles user registration and login
"""

from fastapi import APIRouter, Request, Depends, HTTPException, status
import asyncpg
import os
import secrets

from app.limiter import limiter
from app.models.user import RegisterRequest, LoginRequest, AuthResponse, ChangePasswordRequest, DeleteAccountRequest, PushTokenRequest
from app.auth.password import hash_password, verify_password
from app.auth.jwt_handler import create_access_token
from app.database.postgres import get_db
from app.auth.jwt_handler import decode_access_token

# Create router
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

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
        user_data: Registration data (email, password, first_name, last_name)
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
        # Combine first_name and last_name into full_name for database
        full_name = f"{user_data.first_name} {user_data.last_name}"
        
        # RETURNING clause gets the created user data
        new_user = await db.fetchrow(
            """
            INSERT INTO users (email, password_hash, full_name, role)
            VALUES ($1, $2, $3, $4)
            RETURNING id, email, full_name, role, created_at
            """,
            user_data.email,
            password_hash,
            full_name,
            "user"  # Default role
        )
        
        # Step 4: Generate JWT token
        # Token contains user_id and expiry
        token = create_access_token(str(new_user["id"]))
        
        # Step 6: Return response
        # Never return password_hash!
        return AuthResponse(
            token=token,
            token_type="bearer",
            user_id=str(new_user["id"]),
            email=new_user["email"],
            role=new_user["role"],
            full_name=new_user["full_name"],
            phone=new_user.get("phone")
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
            role=user["role"],
            full_name=user["full_name"],
            phone=user.get("phone")
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


@router.post("/admin-login", response_model=AuthResponse)
@limiter.limit("3/minute")
async def admin_login(
    request: Request,
    credentials: LoginRequest,
    db: asyncpg.Connection = Depends(get_db)
):
    """
    Admin login with environment-based credentials.
    
    This endpoint authenticates administrators using credentials stored in
    environment variables (not in the database). Admin authentication is
    separate from regular user authentication for enhanced security.
    
    Security measures:
    - Rate limited to 3 attempts per minute to prevent brute-force attacks
    - Credentials stored in environment variables (never in database)
    - Constant-time comparison to prevent timing attacks
    - Generic error messages to prevent credential enumeration
    - JWT token contains role="admin" claim for authorization
    
    Steps:
    1. Load admin credentials from environment variables
    2. Validate that admin credentials are configured
    3. Compare provided credentials using constant-time comparison
    4. Generate JWT token with admin role claim
    5. Return token and admin user details
    
    Rate limit: 3 requests per minute
    
    Args:
        request: FastAPI request object (for rate limiting)
        credentials: Login credentials (email, password)
        db: Database connection (injected by FastAPI, not used but kept for consistency)
    
    Returns:
        AuthResponse: JWT token with admin role and admin user information
    
    Raises:
        HTTPException 500: If admin credentials not configured in environment
        HTTPException 401: If provided credentials don't match environment credentials
    """
    try:
        # Step 1: Load admin credentials from environment variables
        admin_username = os.getenv("ADMIN_USERNAME")
        admin_password = os.getenv("ADMIN_PASSWORD")
        
        # Step 2: Ensure admin credentials are configured
        if not admin_username or not admin_password:
            # This should never happen in production
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Admin credentials not configured"
            )
        
        # Step 3: Constant-time comparison to prevent timing attacks
        # We compare both credentials before deciding, so attackers can't
        # determine which credential is wrong based on response time
        username_match = secrets.compare_digest(
            credentials.email.encode('utf-8'),
            admin_username.encode('utf-8')
        )
        password_match = secrets.compare_digest(
            credentials.password.encode('utf-8'),
            admin_password.encode('utf-8')
        )
        
        # Both must match
        if not (username_match and password_match):
            # Generic error message - don't reveal which credential is wrong
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Step 4: Generate JWT token with admin role claim
        token_claims = {
            "user_id": "admin",
            "role": "admin",
            "email": admin_username
        }
        token = create_access_token("admin", additional_claims=token_claims)
        
        # Step 5: Return admin authentication response
        return AuthResponse(
            token=token,
            token_type="bearer",
            user_id="admin",
            email=admin_username,
            role="admin",
            full_name="Administrator",
            phone=None
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error and return generic error message
        print(f"Admin login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin login failed"
        )


# ============================================================================
# ADMIN LOGIN EXPLANATION FOR VIVA
# ============================================================================

"""
Q: Why is admin login separate from regular user login?
A: Security! Admin credentials are:
   - Stored in environment variables (not database)
   - Only accessible to system administrators
   - Never exposed through registration endpoints
   - Separate from user data for security isolation
   
   If database is compromised, admin access remains secure.

Q: What is constant-time comparison?
A: secrets.compare_digest() compares strings in constant time, meaning
   it takes the same amount of time whether strings match or not.
   
   ❌ UNSAFE (timing attack vulnerable):
   if credentials.email == admin_username:
       # Takes different time for different inputs
       # Attacker can guess correct characters by measuring response time
   
   ✅ SAFE (constant-time comparison):
   username_match = secrets.compare_digest(email, admin_username)
   # Always takes same time, regardless of input

Q: Why check both credentials before returning error?
A: To prevent information leakage. If we checked username first and
   returned immediately on failure, attacker could determine valid usernames.
   
   ❌ BAD:
   if username != admin_username:
       return "Invalid username"  # Attacker knows username is wrong
   if password != admin_password:
       return "Invalid password"  # Attacker knows username is correct!
   
   ✅ GOOD:
   username_match = check(username)
   password_match = check(password)
   if not (username_match and password_match):
       return "Invalid credentials"  # Attacker doesn't know what's wrong

Q: What is role="admin" in the token?
A: The JWT token contains a "role" claim that identifies the user's role.
   - Regular users: role="user"
   - Administrators: role="admin"
   
   Protected admin endpoints check this claim to verify admin access.

Q: Why rate limit to 3 requests per minute?
A: Admin accounts are high-value targets. Strict rate limiting (3/min)
   prevents brute-force attacks while still allowing legitimate admins to
   login (even if they mistype password once or twice).

Q: What happens if ADMIN_USERNAME or ADMIN_PASSWORD is not set?
A: We return HTTP 500 Internal Server Error. This indicates a server
   configuration problem (admin can't login if credentials aren't configured).
   This should be caught during deployment/setup.

Q: Can we have multiple admins?
A: Currently, no. This design uses a single admin account from environment
   variables. To support multiple admins, we would need to:
   - Store admin users in database with is_admin flag
   - Or use a separate admins table
   - Still keep separate from regular users for security
"""


@router.post("/change-password")
async def change_password(
    request: Request,
    password_data: ChangePasswordRequest,
    db: asyncpg.Connection = Depends(get_db)
):
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid authorization header")
        token = auth_header.split(" ")[1]
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

        user = await db.fetchrow("SELECT password_hash FROM users WHERE id = $1", int(user_id))
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        if not verify_password(password_data.current_password, user["password_hash"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect current password")
            
        new_hash = hash_password(password_data.new_password)
        await db.execute("UPDATE users SET password_hash = $1 WHERE id = $2", new_hash, int(user_id))
        
        return {"message": "Password updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.post("/delete-account")
async def delete_account(
    request: Request,
    delete_data: DeleteAccountRequest,
    db: asyncpg.Connection = Depends(get_db)
):
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid authorization header")
        token = auth_header.split(" ")[1]
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

        user = await db.fetchrow("SELECT password_hash FROM users WHERE id = $1", int(user_id))
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            
        if not verify_password(delete_data.password, user["password_hash"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
            
        await db.execute("DELETE FROM users WHERE id = $1", int(user_id))
        return {"message": "Account deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# ============================================================================
# EXPLANATION FOR VIVA
# ============================================================================

"""
Q: What happens step-by-step during registration?
A: 
   1. User sends POST request to /auth/register with email, password, first_name, last_name
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



@router.get("/me")
async def get_current_user(
    request: Request,
    db: asyncpg.Connection = Depends(get_db)
):
    """
    Get logged-in user's profile information.
    
    Requires valid JWT token in Authorization header:
    Authorization: Bearer <token>
    
    Used by frontend to:
    - Display user's name in header greeting
    - Show profile information
    - Verify user is still logged in
    
    Args:
        request: FastAPI request object
        db: Database connection (injected by FastAPI)
    
    Returns:
        User profile: id, email, full_name, created_at
    
    Raises:
        HTTPException 401: If token missing, invalid, or expired
        HTTPException 404: If user not found
        HTTPException 500: If database error occurs
    """
    try:
        # Step 1: Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header"
            )
        
        token = auth_header.split(" ")[1]
        
        # Step 2: Decode and verify token
        try:
            payload = decode_access_token(token)
            user_id = payload.get("user_id")
            
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token verification failed: {str(e)}"
            )
        
        # Step 3: Get user from database
        user = await db.fetchrow(
            """
            SELECT id, email, full_name, created_at, phone
            FROM users
            WHERE id = $1 AND is_active = TRUE
            """,
            user_id
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or account deactivated"
            )
        
        # Step 4: Return user profile
        # Convert to dict for JSON serialization
        return {
            "id": str(user["id"]),
            "email": user["email"],
            "full_name": user["full_name"],
            "phone": user.get("phone"),
            "created_at": user["created_at"].isoformat() if user["created_at"] else None
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error and return generic error message
        print(f"Get user profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )


@router.post("/push-token")
async def save_push_token(
    request: Request,
    token_data: PushTokenRequest,
    db: asyncpg.Connection = Depends(get_db)
):
    """
    Save the user's Expo push token
    """
    try:
        # Step 1: Verify token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header"
            )
        
        token_str = auth_header.split(" ")[1]
        payload = decode_access_token(token_str)
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Step 2: Save the push token
        await db.execute(
            "UPDATE users SET expo_push_token = $1 WHERE id = $2",
            token_data.token, user_id
        )
        
        return {"status": "success", "message": "Push token saved successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Save push token error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save push token"
        )



@router.put("/me")
@limiter.limit("10/minute")
async def update_current_user(
    request: Request,
    db: asyncpg.Connection = Depends(get_db)
):
    """
    Update logged-in user's profile information.
    
    Requires valid JWT token in Authorization header:
    Authorization: Bearer <token>
    
    Allows updating:
    - full_name: User's display name
    - phone: Phone number (optional)
    
    Email cannot be changed (use it for login)
    
    Rate limit: 10 requests per minute
    
    Args:
        request: FastAPI request object
        db: Database connection (injected by FastAPI)
    
    Returns:
        Updated user profile
    
    Raises:
        HTTPException 401: If token missing, invalid, or expired
        HTTPException 404: If user not found
        HTTPException 400: If validation fails
        HTTPException 500: If database error occurs
    """
    try:
        # Step 1: Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header"
            )
        
        token = auth_header.split(" ")[1]
        
        # Step 2: Decode and verify token
        try:
            payload = decode_access_token(token)
            user_id = payload.get("user_id")
            
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token verification failed: {str(e)}"
            )
        
        # Step 3: Parse request body
        body = await request.json()
        full_name = body.get("full_name")
        phone = body.get("phone")
        
        # Step 4: Validate input
        if full_name is not None and (len(full_name.strip()) < 2 or len(full_name.strip()) > 100):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Full name must be between 2 and 100 characters"
            )
        
        if phone is not None and phone != "" and len(phone) > 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number is too long"
            )
        
        # Step 5: Update user in database
        updated_user = await db.fetchrow(
            """
            UPDATE users
            SET full_name = COALESCE($1, full_name),
                phone = COALESCE($2, phone),
                updated_at = NOW()
            WHERE id = $3 AND is_active = TRUE
            RETURNING id, email, full_name, phone, created_at
            """,
            full_name.strip() if full_name else None,
            phone.strip() if phone else None,
            user_id
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or account deactivated"
            )
        
        # Step 6: Return updated profile
        return {
            "id": str(updated_user["id"]),
            "email": updated_user["email"],
            "full_name": updated_user["full_name"],
            "phone": updated_user.get("phone"),
            "created_at": updated_user["created_at"].isoformat() if updated_user["created_at"] else None,
            "message": "Profile updated successfully"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error and return generic error message
        print(f"Update user profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )
