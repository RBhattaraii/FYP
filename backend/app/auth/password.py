"""
Password Hashing Utilities
Uses bcrypt for secure password hashing
"""

from passlib.context import CryptContext

# Create password context with bcrypt
# bcrypt is a secure hashing algorithm designed for passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    
    Hashing is a one-way function - you can't reverse it to get the original password.
    Each time you hash the same password, you get a different hash (due to salt).
    
    Args:
        password: Plain text password (e.g., "mypassword123")
    
    Returns:
        str: Hashed password (e.g., "$2b$12$KIXxLV...")
    
    Example:
        hashed = hash_password("mypassword123")
        # Returns: "$2b$12$KIXxLVz9..."
        # This is what we store in the database
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.
    
    This checks if the plain password, when hashed, matches the stored hash.
    
    Args:
        plain_password: Password entered by user (e.g., "mypassword123")
        hashed_password: Hashed password from database (e.g., "$2b$12$KIXxLV...")
    
    Returns:
        bool: True if password matches, False otherwise
    
    Example:
        is_correct = verify_password("mypassword123", "$2b$12$KIXxLV...")
        # Returns: True if password is correct, False if wrong
    """
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================================
# EXPLANATION FOR VIVA
# ============================================================================

"""
Q: What is password hashing?
A: Password hashing is converting a plain text password into a scrambled
   string that can't be reversed back to the original password.
   
   Example:
   - Plain password: "mypassword123"
   - Hashed password: "$2b$12$KIXxLVz9eN7P.FZJL5FZ0.Xw8Z..."
   
   Think of it like making a smoothie - you can't un-blend it back to fruits!

Q: Why hash passwords?
A: Security! If someone hacks the database, they can't see actual passwords.
   They only see hashed values which are useless without the original password.
   
   Without hashing:
   - Database stores: "mypassword123"
   - Hacker sees: "mypassword123" ❌ BAD!
   
   With hashing:
   - Database stores: "$2b$12$KIXxLVz9eN7P..."
   - Hacker sees: "$2b$12$KIXxLVz9eN7P..." ✅ SAFE!

Q: Can you reverse a hash to get the password?
A: No! Hashing is a one-way function. You can't reverse it.
   The only way to check if a password is correct is to:
   1. Hash the entered password
   2. Compare it with the stored hash
   3. If they match, password is correct

Q: What is bcrypt?
A: bcrypt is a password hashing algorithm specifically designed for passwords.
   It's slow on purpose (makes brute-force attacks harder) and includes
   a "salt" (random data) to make each hash unique.

Q: What is a salt?
A: A salt is random data added to the password before hashing.
   This means the same password gets different hashes each time.
   
   Example:
   - Hash "password123" → "$2b$12$abc..."
   - Hash "password123" again → "$2b$12$xyz..." (different!)
   
   This prevents attackers from using pre-computed hash tables (rainbow tables).

Q: How does verify_password work?
A: 
   1. User enters password: "mypassword123"
   2. We get stored hash from database: "$2b$12$KIXxLV..."
   3. bcrypt extracts the salt from the stored hash
   4. bcrypt hashes the entered password with the same salt
   5. bcrypt compares the new hash with the stored hash
   6. If they match → password is correct ✅
   7. If they don't match → password is wrong ❌

Q: Why use passlib instead of hashlib?
A: passlib is specifically designed for password hashing and handles:
   - Salt generation automatically
   - Multiple hashing algorithms (bcrypt, argon2, etc.)
   - Secure defaults
   - Easy verification
   
   hashlib is for general hashing (files, data) not passwords.

Q: What does "$2b$12$" mean in the hash?
A: It's the hash format:
   - $2b$ → bcrypt algorithm version
   - $12$ → Cost factor (how many rounds of hashing, 2^12 = 4096 rounds)
   - Rest → Salt + Hash combined

Q: Can two users have the same password hash?
A: No! Even if two users have the same password, their hashes will be
   different because each hash uses a unique random salt.
   
   User 1: password "test123" → "$2b$12$abc..."
   User 2: password "test123" → "$2b$12$xyz..." (different!)
"""
