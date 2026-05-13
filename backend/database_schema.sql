-- ============================================================================
-- PricePilot Database Schema
-- Run this SQL in Supabase SQL Editor to create the users table
-- ============================================================================

-- Create users table
CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name     TEXT,
    role          TEXT NOT NULL DEFAULT 'user',
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to call update_updated_at function before every update
CREATE TRIGGER trigger_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();

-- Create index on email for faster lookups
CREATE INDEX idx_users_email ON users(email);

-- Create index on role for faster filtering
CREATE INDEX idx_users_role ON users(role);

-- ============================================================================
-- Explanation of Each Part
-- ============================================================================

/*
1. CREATE TABLE users
   - Creates a new table called "users" to store user information

2. id UUID PRIMARY KEY DEFAULT gen_random_uuid()
   - id: Unique identifier for each user
   - UUID: Universal Unique Identifier (128-bit number, looks like: 550e8400-e29b-41d4-a716-446655440000)
   - PRIMARY KEY: This column uniquely identifies each row
   - DEFAULT gen_random_uuid(): Automatically generates a random UUID when a new user is created

3. email TEXT NOT NULL UNIQUE
   - email: User's email address
   - TEXT: Can store any length of text
   - NOT NULL: Email is required (cannot be empty)
   - UNIQUE: No two users can have the same email

4. password_hash TEXT NOT NULL
   - password_hash: Encrypted password (never store plain passwords!)
   - TEXT: Stores the hashed password string
   - NOT NULL: Password is required

5. full_name TEXT
   - full_name: User's full name
   - TEXT: Can store any length of text
   - No NOT NULL: This field is optional

6. role TEXT NOT NULL DEFAULT 'user'
   - role: User's role (e.g., 'user', 'admin')
   - NOT NULL: Role is required
   - DEFAULT 'user': If no role is specified, default to 'user'

7. is_active BOOLEAN NOT NULL DEFAULT TRUE
   - is_active: Whether the user account is active
   - BOOLEAN: Can only be TRUE or FALSE
   - DEFAULT TRUE: New accounts are active by default

8. created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
   - created_at: When the user was created
   - TIMESTAMPTZ: Timestamp with timezone
   - DEFAULT NOW(): Automatically set to current time when user is created

9. updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
   - updated_at: When the user was last updated
   - TIMESTAMPTZ: Timestamp with timezone
   - DEFAULT NOW(): Initially set to current time
   - Automatically updated by trigger (see below)

10. CREATE OR REPLACE FUNCTION update_updated_at()
    - Creates a reusable function that updates the updated_at timestamp
    - OR REPLACE: If function exists, replace it with this new version

11. RETURNS TRIGGER
    - This function is designed to be called by a trigger
    - Returns the modified row

12. NEW.updated_at = NOW()
    - NEW: Refers to the new version of the row being updated
    - Sets updated_at to the current timestamp

13. RETURN NEW
    - Returns the modified row so the update can proceed

14. $$ LANGUAGE plpgsql
    - plpgsql: PostgreSQL's procedural language
    - $$: Delimiter for the function body

15. CREATE TRIGGER trigger_users_updated_at
    - Creates a trigger (automatic action) on the users table
    - Trigger name: trigger_users_updated_at

16. BEFORE UPDATE ON users
    - BEFORE: Run this trigger before the update happens
    - UPDATE: Only run on UPDATE operations (not INSERT or DELETE)
    - ON users: Apply this trigger to the users table

17. FOR EACH ROW
    - Run this trigger for every row that gets updated
    - (As opposed to once per UPDATE statement)

18. EXECUTE FUNCTION update_updated_at()
    - Call the update_updated_at() function when trigger fires

19. CREATE INDEX idx_users_email ON users(email)
    - Creates an index on the email column
    - Makes searching by email much faster
    - Like an index in a book - helps find things quickly

20. CREATE INDEX idx_users_role ON users(role)
    - Creates an index on the role column
    - Makes filtering by role faster (e.g., "find all admins")
*/

-- ============================================================================
-- Example Queries
-- ============================================================================

-- Insert a new user (id, created_at, updated_at are automatic)
-- INSERT INTO users (email, password_hash, full_name, role)
-- VALUES ('user@example.com', 'hashed_password_here', 'John Doe', 'user');

-- Select all users
-- SELECT * FROM users;

-- Select user by email
-- SELECT * FROM users WHERE email = 'user@example.com';

-- Update user's full name (updated_at will be automatically updated by trigger)
-- UPDATE users SET full_name = 'Jane Doe' WHERE email = 'user@example.com';

-- Deactivate a user
-- UPDATE users SET is_active = FALSE WHERE email = 'user@example.com';

-- Delete a user
-- DELETE FROM users WHERE email = 'user@example.com';

-- Count total users
-- SELECT COUNT(*) FROM users;

-- Get all admin users
-- SELECT * FROM users WHERE role = 'admin';

-- Get active users only
-- SELECT * FROM users WHERE is_active = TRUE;
