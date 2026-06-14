"""
Script to create a test user in the database
Run this script independently: python create_test_user.py
"""

import asyncio
import asyncpg
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Password hashing context (same as what we'll use in the auth system)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_test_user():
    """Create a test user in the database"""
    
    # Get database URL from .env
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL not found in .env file")
        return
    
    # Test user details
    email = "testuser@pricepilot.com"
    password = "testpass123"
    full_name = "Test User"
    role = "user"
    
    try:
        # Connect to database
        print("🔄 Connecting to database...")
        conn = await asyncpg.connect(database_url)
        print("✅ Connected to database")
        
        # Hash the password
        print("🔄 Hashing password...")
        password_hash = pwd_context.hash(password)
        print("✅ Password hashed")
        
        # Check if user already exists
        print(f"🔄 Checking if user {email} already exists...")
        existing_user = await conn.fetchrow(
            "SELECT * FROM users WHERE email = $1",
            email
        )
        
        if existing_user:
            print(f"⚠️  User {email} already exists!")
            print(f"   User ID: {existing_user['id']}")
            print(f"   Full Name: {existing_user['full_name']}")
            print(f"   Role: {existing_user['role']}")
            print(f"   Created: {existing_user['created_at']}")
            
            # Ask if user wants to update password
            update = input("\n🤔 Do you want to update the password? (yes/no): ").lower()
            if update == 'yes':
                await conn.execute(
                    "UPDATE users SET password_hash = $1, updated_at = NOW() WHERE email = $2",
                    password_hash,
                    email
                )
                print("✅ Password updated successfully!")
        else:
            # Insert new user
            print(f"🔄 Creating user {email}...")
            result = await conn.fetchrow(
                """
                INSERT INTO users (email, password_hash, full_name, role)
                VALUES ($1, $2, $3, $4)
                RETURNING id, email, full_name, role, created_at
                """,
                email,
                password_hash,
                full_name,
                role
            )
            
            print("\n✅ Test user created successfully!")
            print(f"   User ID: {result['id']}")
            print(f"   Email: {result['email']}")
            print(f"   Full Name: {result['full_name']}")
            print(f"   Role: {result['role']}")
            print(f"   Created: {result['created_at']}")
        
        # Display login credentials
        print("\n" + "="*50)
        print("📋 TEST USER CREDENTIALS")
        print("="*50)
        print(f"Email:    {email}")
        print(f"Password: {password}")
        print("="*50)
        print("\n💡 Use these credentials to test login in your app!")
        
        # Close connection
        await conn.close()
        print("\n✅ Database connection closed")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def list_all_users():
    """List all users in the database"""
    
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL not found in .env file")
        return
    
    try:
        conn = await asyncpg.connect(database_url)
        
        users = await conn.fetch("SELECT * FROM users ORDER BY created_at DESC")
        
        if not users:
            print("\n📭 No users found in database")
        else:
            print(f"\n👥 Found {len(users)} user(s):")
            print("="*80)
            for user in users:
                print(f"ID:        {user['id']}")
                print(f"Email:     {user['email']}")
                print(f"Name:      {user['full_name']}")
                print(f"Role:      {user['role']}")
                print(f"Active:    {user['is_active']}")
                print(f"Created:   {user['created_at']}")
                print("-"*80)
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def delete_test_user():
    """Delete the test user from database"""
    
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL not found in .env file")
        return
    
    email = "testuser@pricepilot.com"
    
    try:
        conn = await asyncpg.connect(database_url)
        
        # Check if user exists
        user = await conn.fetchrow("SELECT * FROM users WHERE email = $1", email)
        
        if not user:
            print(f"⚠️  User {email} not found")
        else:
            # Delete user
            await conn.execute("DELETE FROM users WHERE email = $1", email)
            print(f"✅ User {email} deleted successfully")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Main menu"""
    
    print("\n" + "="*50)
    print("🔧 PricePilot Test User Manager")
    print("="*50)
    print("1. Create test user")
    print("2. List all users")
    print("3. Delete test user")
    print("4. Exit")
    print("="*50)
    
    choice = input("\nEnter your choice (1-4): ")
    
    if choice == "1":
        await create_test_user()
    elif choice == "2":
        await list_all_users()
    elif choice == "3":
        await delete_test_user()
    elif choice == "4":
        print("👋 Goodbye!")
        return
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    asyncio.run(main())
