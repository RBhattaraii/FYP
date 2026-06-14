from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.database.postgres import create_pool, close_pool
from app.database.mongo import connect_mongodb, close_mongodb
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Load environment variables from .env file
load_dotenv()

# Initialize rate limiter
# Uses client's IP address to track request counts
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app instance
app = FastAPI(
    title="PricePilot API",
    description="Price comparison API for PricePilot mobile app",
    version="1.0.0"
)

# Add rate limiter to app state
app.state.limiter = limiter

# Add rate limit exceeded handler
# Returns 429 (Too Many Requests) when limit is exceeded
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Startup event: Create database connection pool
@app.on_event("startup")
async def startup():
    """
    Called when the FastAPI app starts.
    Creates the PostgreSQL connection pool and connects to MongoDB.
    """
    # Connect to PostgreSQL (async)
    await create_pool()
    
    # Connect to MongoDB (synchronous)
    mongodb_connected = connect_mongodb()
    if not mongodb_connected:
        print("⚠️  Warning: MongoDB connection failed, but API will continue")
    
    print("🚀 PricePilot API started successfully")

# Shutdown event: Close database connection pool
@app.on_event("shutdown")
async def shutdown():
    """
    Called when the FastAPI app shuts down.
    Closes the PostgreSQL connection pool and MongoDB connection.
    """
    await close_pool()
    close_mongodb()
    print("👋 PricePilot API shut down")

# Configure CORS to allow React Native app to connect
# Restricted to specific Expo development ports for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8081",   # Expo default port
        "http://localhost:19006",  # Expo web port
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Middleware to add security headers to every response
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """
    Add security headers to every HTTP response.
    
    Security headers:
    - X-Content-Type-Options: nosniff
      Prevents browsers from MIME-sniffing (guessing file types)
      Protects against drive-by download attacks
    
    - X-Frame-Options: DENY
      Prevents the page from being displayed in an iframe
      Protects against clickjacking attacks
    
    - X-XSS-Protection: 1; mode=block
      Enables browser's XSS filter
      Blocks page if XSS attack is detected
    """
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# Test route - Root endpoint
@app.get("/")
async def root():
    """
    Test endpoint to verify API is working
    Returns a simple message
    """
    return {"message": "PricePilot API is working"}

# Import and include routers
from app.routers import auth, products
app.include_router(auth.router)
app.include_router(products.router)

# Run with: uvicorn main:app --reload
