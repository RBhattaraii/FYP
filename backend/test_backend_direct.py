"""
Test backend directly to diagnose 500 errors
Run this to see what's causing the login/register failures
"""

import asyncio
import asyncpg
from app.auth.password import hash_password, verify_password
from app.auth.jwt_handler import create_access_token
from app.database.postgres import create_pool, close_pool, pool
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_database_connection():
    """Test if we can connect to PostgreSQL"""
    print("\n=== Testing Database Connection ===")
    try:
        db_pool = await create_pool()
        async with db_pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
            print(f"✅ Database connection successful! Result: {result}")
            
            # Check if users table exists
            table_exists = await conn.fetchval(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'users'
                )
                """
            )
            print(f"✅ Users table exists: {table_exists}")
            
            if table_exists:
                # Count users
                user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
                print(f"✅ Number of users in database: {user_count}")
        
        await close_pool()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def test_password_hashing():
    """Test if password hashing works"""
    print("\n=== Testing Password Hashing ===")
    try:
        test_password = "testpass123"
        
        # Test hashing
        hashed = hash_password(test_password)
        print(f"✅ Password hashing successful!")
        print(f"   Original: {test_password}")
        print(f"   Hashed: {hashed[:50]}...")
        
        # Test verification
        is_correct = verify_password(test_password, hashed)
        print(f"✅ Password verification: {is_correct}")
        
        # Test wrong password
        is_wrong = verify_password("wrongpassword", hashed)
        print(f"✅ Wrong password rejected: {not is_wrong}")
        
        return True
    except Exception as e:
        print(f"❌ Password hashing failed: {e}")
        return False


def test_jwt_token():
    """Test if JWT token generation works"""
    print("\n=== Testing JWT Token Generation ===")
    try:
        test_user_id = "123e4567-e89b-12d3-a456-426614174000"
        
        # Test token creation
        token = create_access_token(test_user_id)
        print(f"✅ JWT token generation successful!")
        print(f"   User ID: {test_user_id}")
        print(f"   Token: {token[:50]}...")
        
        return True
    except Exception as e:
        print(f"❌ JWT token generation failed: {e}")
        return False


async def test_login_flow():
    """Test the complete login flow"""
    print("\n=== Testing Login Flow ===")
    try:
        db_pool = await create_pool()
        async with db_pool.acquire() as conn:
            # Look up test user
            user = await conn.fetchrow(
                """
                SELECT id, email, password_hash, full_name, role, is_active
                FROM users
                WHERE email = $1
                """,
                "testuser@pricepilot.com"
            )
            
            if not user:
                print("❌ Test user not found in database!")
                print("   Run: python create_test_user.py")
                return False
            
            print(f"✅ Test user found!")
            print(f"   Email: {user['email']}")
            print(f"   Full Name: {user['full_name']}")
            print(f"   Role: {user['role']}")
            print(f"   Active: {user['is_active']}")
            
            # Test password verification
            is_correct = verify_password("testpass123", user["password_hash"])
            print(f"✅ Password verification: {is_correct}")
            
            if not is_correct:
                print("❌ Password verification failed!")
                print("   The stored password hash doesn't match 'testpass123'")
                print("   Run: python create_test_user.py")
                return False
            
            # Test token generation
            token = create_access_token(str(user["id"]))
            print(f"✅ Token generation successful!")
            print(f"   Token: {token[:50]}...")
            
        await close_pool()
        return True
    except Exception as e:
        print(f"❌ Login flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_register_flow():
    """Test the complete register flow"""
    print("\n=== Testing Register Flow ===")
    try:
        db_pool = await create_pool()
        async with db_pool.acquire() as conn:
            test_email = "testregister@test.com"
            
            # Check if test email already exists
            existing = await conn.fetchrow(
                "SELECT id FROM users WHERE email = $1",
                test_email
            )
            
            if existing:
                print(f"⚠️  Test email already exists, deleting...")
                await conn.execute(
                    "DELETE FROM users WHERE email = $1",
                    test_email
                )
            
            # Test registration
            password_hash = hash_password("testpass123")
            
            new_user = await conn.fetchrow(
                """
                INSERT INTO users (email, password_hash, full_name, role)
                VALUES ($1, $2, $3, $4)
                RETURNING id, email, full_name, role, created_at
                """,
                test_email,
                password_hash,
                "Test User",
                "user"
            )
            
            print(f"✅ User registration successful!")
            print(f"   Email: {new_user['email']}")
            print(f"   Full Name: {new_user['full_name']}")
            print(f"   Role: {new_user['role']}")
            
            # Test token generation
            token = create_access_token(str(new_user["id"]))
            print(f"✅ Token generation successful!")
            
            # Clean up
            await conn.execute(
                "DELETE FROM users WHERE email = $1",
                test_email
            )
            print(f"✅ Test user cleaned up")
            
        await close_pool()
        return True
    except Exception as e:
        print(f"❌ Register flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("=" * 60)
    print("BACKEND DIAGNOSTIC TEST")
    print("=" * 60)
    
    # Test 1: Database connection
    db_ok = await test_database_connection()
    
    # Test 2: Password hashing
    pwd_ok = test_password_hashing()
    
    # Test 3: JWT token
    jwt_ok = test_jwt_token()
    
    # Test 4: Login flow
    login_ok = await test_login_flow()
    
    # Test 5: Register flow
    register_ok = await test_register_flow()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Database Connection: {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"Password Hashing:    {'✅ PASS' if pwd_ok else '❌ FAIL'}")
    print(f"JWT Token:           {'✅ PASS' if jwt_ok else '❌ FAIL'}")
    print(f"Login Flow:          {'✅ PASS' if login_ok else '❌ FAIL'}")
    print(f"Register Flow:       {'✅ PASS' if register_ok else '❌ FAIL'}")
    print("=" * 60)
    
    if all([db_ok, pwd_ok, jwt_ok, login_ok, register_ok]):
        print("\n✅ ALL TESTS PASSED!")
        print("   Backend is working correctly.")
        print("   The issue might be with the mobile app or network.")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("   Check the errors above to diagnose the issue.")


if __name__ == "__main__":
    asyncio.run(main())
