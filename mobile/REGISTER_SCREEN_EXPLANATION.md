# 📱 Register Screen - Simple Explanation for Viva

## 🎯 What Does This Screen Do?

The register screen allows new users to create an account for PricePilot by providing their email, password, and optionally their full name.

---

## 📋 Components & Features

### 1. **Form Inputs**

```typescript
const [fullName, setFullName] = useState('');      // Optional
const [email, setEmail] = useState('');            // Required
const [password, setPassword] = useState('');      // Required
const [confirmPassword, setConfirmPassword] = useState('');  // Required
```

**What it does**: Stores user input  
**Why**: React tracks what user types  
**Simple explanation**: Like a form with 4 fields

### 2. **Password Visibility Toggles**

```typescript
const [showPassword, setShowPassword] = useState(false);
const [showConfirmPassword, setShowConfirmPassword] = useState(false);
```

**What it does**: Two separate toggles for password and confirm password  
**Why**: User can show/hide each password independently  
**Simple explanation**: Two eye icons, one for each password field

### 3. **Email Validation Regex**

```typescript
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
```

**What it does**: Checks if email format is valid  
**Why**: Prevents invalid emails like "test" or "test@"  
**Simple explanation**: Makes sure email has @ and domain (e.g., user@example.com)

---

## 🔍 Validation Rules (Frontend)

### **1. Email Validation**
```typescript
if (!email.trim()) {
  setEmailError('Email is required');
} else if (!emailRegex.test(email.trim())) {
  setEmailError('Please enter a valid email address');
}
```

**Checks**:
- Email not empty
- Email has valid format (contains @ and domain)

### **2. Password Validation**
```typescript
if (!password) {
  setPasswordError('Password is required');
} else if (password.length < 8) {
  setPasswordError('Password must be at least 8 characters');
} else if (!/\d/.test(password)) {
  setPasswordError('Password must contain at least one number');
}
```

**Checks**:
- Password not empty
- Minimum 8 characters
- Contains at least one number (0-9)

### **3. Confirm Password Validation**
```typescript
if (!confirmPassword) {
  setConfirmPasswordError('Please confirm your password');
} else if (password !== confirmPassword) {
  setConfirmPasswordError('Passwords do not match');
}
```

**Checks**:
- Confirm password not empty
- Matches password exactly

### **4. Full Name Validation**
- **Optional field** - no validation required
- Can be left empty

---

## 🔄 How Registration Works (Step by Step)

### **Step 1: User Fills Form**
- User enters full name (optional)
- User enters email
- User enters password
- User confirms password

### **Step 2: User Clicks Register**
- `handleRegister` function is called

### **Step 3: Frontend Validation**
```typescript
if (!validateForm()) {
  return; // Stop if validation fails
}
```
- Check email format
- Check password length
- Check password has number
- Check passwords match
- If errors, show messages and stop

### **Step 4: Call Backend API**
```typescript
const response = await fetch(`${API_URL}/auth/register`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: email.trim(),
    password: password,
    full_name: fullName.trim() || undefined,
  }),
});
```

**What happens**:
1. Send email, password, full_name to backend
2. Backend creates new user in database
3. Backend hashes password with bcrypt
4. Backend generates JWT token
5. Backend sends back token or error

### **Step 5: Handle Response**

**If Success (response.ok = true)**:
```typescript
await SecureStore.setItemAsync('token', data.token);
await SecureStore.setItemAsync('email', email);
router.replace('/(tabs)/home');
```
- Store JWT token securely
- Store email
- Navigate to home screen
- User is now logged in

**If Failure (response.ok = false)**:
```typescript
setApiError(data.detail);
setPassword('');
setConfirmPassword('');
```
- Show error message (e.g., "Email already registered")
- Clear both password fields
- Keep email and full name
- User can fix and try again

---

## 🔒 Security Features

### 1. **Passwords Never Logged**
```typescript
// ❌ NEVER DO THIS:
console.log(password);
console.log(confirmPassword);

// ✅ WE DO THIS:
// Passwords only sent to API, never logged
```

### 2. **Passwords Never Stored**
```typescript
// ❌ NEVER DO THIS:
await SecureStore.setItemAsync('password', password);

// ✅ WE DO THIS:
await SecureStore.setItemAsync('token', data.token);
// Only store JWT token, not passwords
```

### 3. **Password Validation**
- Minimum 8 characters (harder to guess)
- Must contain number (increases complexity)
- Passwords must match (prevents typos)

### 4. **Email Validation**
- Valid format required
- Backend checks if email already exists
- Prevents duplicate accounts

### 5. **Secure Storage**
- JWT token stored in SecureStore
- Encrypted on device
- Cannot be accessed by other apps

---

## 🎨 UI Features

### 1. **ScrollView**
```typescript
<ScrollView contentContainerStyle={styles.scrollContent}>
```
**What it does**: Makes screen scrollable  
**Why**: 4 inputs + button might not fit on small screens  
**Simple explanation**: Can scroll if content is too long

### 2. **KeyboardAvoidingView**
```typescript
<KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
```
**What it does**: Adjusts layout when keyboard appears  
**Why**: So keyboard doesn't hide inputs  
**Simple explanation**: Screen moves up when you type

### 3. **SafeAreaView**
```typescript
<SafeAreaView style={styles.safeArea}>
```
**What it does**: Respects notch/status bar  
**Why**: Content doesn't go under notch  
**Simple explanation**: Works on all phone shapes

### 4. **Password Hints**
```typescript
<Text style={styles.hint}>
  Must be at least 8 characters and contain a number
</Text>
```
**What it does**: Shows password requirements  
**Why**: User knows what to enter  
**Simple explanation**: Helpful text under password field

### 5. **Conditional Styling**
```typescript
style={[styles.input, emailError ? styles.inputError : null]}
```
**What it does**: Red border if error  
**Why**: Visual feedback  
**Simple explanation**: Input turns red when wrong

---

## 📡 API Integration

### **Request Format**
```typescript
POST http://192.168.1.69:8000/auth/register
Content-Type: application/json

{
  "email": "newuser@example.com",
  "password": "password123",
  "full_name": "John Doe"  // Optional
}
```

### **Success Response (200)**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "uuid-here",
  "email": "newuser@example.com",
  "role": "user"
}
```

### **Error Response (400)**
```json
{
  "detail": "Email already registered"
}
```

### **Validation Error Response (422)**
```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "Password must contain at least one number",
      "type": "value_error"
    }
  ]
}
```

---

## 🎓 Viva Questions & Answers

### **Q1: Why validate email format on frontend?**
**A**: 
- Fast feedback (no network delay)
- Prevents obvious mistakes
- Better user experience
- But we still validate on backend for security

### **Q2: Why require password to have a number?**
**A**: 
- Increases password complexity
- Harder to guess
- More secure
- Industry best practice

### **Q3: Why confirm password field?**
**A**: 
- Prevents typos
- User types password twice
- If they don't match, user made a mistake
- Better UX than wrong password on first login

### **Q4: Why is full name optional?**
**A**: 
- Not required for authentication
- Reduces friction (easier signup)
- Can be added later in profile
- Email and password are sufficient

### **Q5: What happens if email already exists?**
**A**: 
- Backend checks database
- Returns 400 error: "Email already registered"
- Frontend shows error message
- User can try different email or go to login

### **Q6: Why clear passwords on error but not email?**
**A**: 
- Passwords are sensitive (should be re-entered)
- Email is not sensitive (user can see it)
- Better UX - user doesn't retype email
- Security best practice

### **Q7: Why use ScrollView?**
**A**: 
- Register form has 4 inputs (more than login)
- Might not fit on small screens
- ScrollView makes it scrollable
- Better mobile UX

### **Q8: How does password regex work?**
**A**: 
```typescript
!/\d/.test(password)
```
- `/\d/` = matches any digit (0-9)
- `!` = NOT
- So `!/\d/.test(password)` = true if NO digit found
- We show error if true (no digit)

### **Q9: Why two separate show/hide toggles?**
**A**: 
- User might want to see password but not confirm
- Or vice versa
- More flexible
- Better UX

### **Q10: What's the difference between login and register?**
**A**: 
- **Login**: Checks if user exists, verifies password
- **Register**: Creates new user, hashes password, stores in database
- Both return JWT token on success
- Both navigate to home screen

---

## 🔍 Code Flow Diagram

```
User opens register screen
    ↓
User fills form (name, email, password, confirm)
    ↓
User clicks Register button
    ↓
Frontend validation
    ├─ Email empty? → Show error, stop
    ├─ Email invalid format? → Show error, stop
    ├─ Password < 8 chars? → Show error, stop
    ├─ Password no number? → Show error, stop
    ├─ Passwords don't match? → Show error, stop
    └─ All valid → Continue
        ↓
    Show loading spinner
        ↓
    Call backend API (fetch)
        ↓
    Backend checks if email exists
        ├─ Email exists → Return 400 error
        └─ Email new → Continue
            ↓
        Backend validates password
            ├─ Invalid → Return 422 error
            └─ Valid → Continue
                ↓
            Backend creates user
            Backend hashes password (bcrypt)
            Backend stores in database
            Backend generates JWT token
            Backend returns token
                ↓
    Frontend receives response
        ├─ Success (200)
        │   ↓
        │   Store JWT token (SecureStore)
        │   Store email (SecureStore)
        │   Navigate to home screen
        │   User is logged in
        │
        └─ Error (400/422)
            ↓
            Show error message
            Clear password fields
            User can try again
```

---

## 📊 State Variables Explained

| Variable | Type | Purpose | Example Value |
|----------|------|---------|---------------|
| `fullName` | string | User's full name (optional) | "John Doe" |
| `email` | string | User's email input | "user@example.com" |
| `password` | string | User's password input | "password123" |
| `confirmPassword` | string | Password confirmation | "password123" |
| `showPassword` | boolean | Toggle password visibility | true/false |
| `showConfirmPassword` | boolean | Toggle confirm password visibility | true/false |
| `fullNameError` | string | Full name validation error | "" |
| `emailError` | string | Email validation error | "Email is required" |
| `passwordError` | string | Password validation error | "Must be 8 characters" |
| `confirmPasswordError` | string | Confirm password error | "Passwords do not match" |
| `loading` | boolean | API call in progress | true/false |
| `apiError` | string | Backend error message | "Email already registered" |

---

## 🎯 Key Differences from Login Screen

| Feature | Login | Register |
|---------|-------|----------|
| **Inputs** | 2 (email, password) | 4 (name, email, password, confirm) |
| **Validation** | Empty check only | Email format, password rules, match check |
| **ScrollView** | No | Yes (more inputs) |
| **Password toggles** | 1 | 2 (password + confirm) |
| **Hints** | No | Yes (password requirements) |
| **API endpoint** | /auth/login | /auth/register |
| **Error handling** | Simple | Complex (validation errors) |

---

## 🧪 Testing the Register Screen

### **Test Case 1: Empty Fields**
1. Click Register without entering anything
2. Should show: "Email is required", "Password is required", "Please confirm your password"

### **Test Case 2: Invalid Email**
1. Enter: "notanemail"
2. Click Register
3. Should show: "Please enter a valid email address"

### **Test Case 3: Short Password**
1. Enter email: test@test.com
2. Enter password: "short"
3. Should show: "Password must be at least 8 characters"

### **Test Case 4: Password Without Number**
1. Enter password: "password"
2. Should show: "Password must contain at least one number"

### **Test Case 5: Passwords Don't Match**
1. Enter password: "password123"
2. Enter confirm: "password456"
3. Should show: "Passwords do not match"

### **Test Case 6: Successful Registration**
1. Enter name: "Test User"
2. Enter email: "newuser@test.com"
3. Enter password: "testpass123"
4. Enter confirm: "testpass123"
5. Click Register
6. Should: Show spinner → Navigate to home

### **Test Case 7: Duplicate Email**
1. Enter email that already exists
2. Should show: "Email already registered"

---

## 🎓 Key Takeaways

1. **More validation than login** = Better data quality
2. **Email format check** = Prevents invalid emails
3. **Password requirements** = More secure accounts
4. **Confirm password** = Prevents typos
5. **Optional full name** = Reduces friction
6. **ScrollView** = Works on all screen sizes
7. **Two password toggles** = Better UX
8. **Clear passwords on error** = Security
9. **Same styling as login** = Consistent design
10. **Backend also validates** = Security (never trust client)

---

**This register screen is production-ready with comprehensive validation and security!** ✅
