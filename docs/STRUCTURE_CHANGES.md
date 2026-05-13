# PricePilot Folder Structure Changes

## Summary of Corrections Applied

This document summarizes all the corrections made to the PricePilot folder structure design and documentation.

---

## 1. Renamed `frontend/` to `mobile/`

**Reason**: More accurate naming for a React Native mobile application

**Before**:
```
PricePilot/
├── frontend/
```

**After**:
```
PricePilot/
├── mobile/
```

---

## 2. Replaced `src/` with Expo Router `app/` Structure

**Reason**: Expo Router uses file-based routing with the `app/` directory

**Before**:
```
frontend/
├── src/
│   ├── screens/
│   ├── navigation/
│   ├── components/
│   ├── services/
│   ├── types/
│   ├── utils/
│   └── App.tsx
```

**After**:
```
mobile/
├── app/                      # File-based routing
│   ├── _layout.tsx          # Root layout
│   ├── (auth)/              # Auth group
│   │   ├── login.tsx
│   │   └── register.tsx
│   └── (tabs)/              # Tab navigation
│       ├── _layout.tsx
│       ├── home.tsx
│       ├── wishlist.tsx
│       ├── notifications.tsx
│       └── profile.tsx
├── components/              # Reusable components
└── constants/
    └── api.ts              # API configuration
```

**Key Changes**:
- `screens/` → Files in `app/` directory (automatic routing)
- `navigation/` → Removed (Expo Router handles this via file structure)
- `services/` → `constants/api.ts` (centralized API config)
- `types/` and `utils/` → Removed from initial structure (can be added later if needed)
- `App.tsx` → `_layout.tsx` (root layout component)

---

## 3. Removed `services/` Folder from Mobile

**Reason**: API calls centralized in `constants/api.ts` for simplicity

**Before**:
```
src/
├── services/
│   ├── api.ts
│   ├── productService.ts
│   └── authService.ts
```

**After**:
```
constants/
└── api.ts              # All API config and endpoints
```

**Example `constants/api.ts`**:
```typescript
import axios from 'axios';

export const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const endpoints = {
  products: '/products',
  users: '/users',
  auth: {
    login: '/auth/login',
    register: '/auth/register',
  },
};
```

---

## 4. Changed `app/auth/` Folder to `routers/auth.py` File

**Reason**: Simpler structure with authentication logic in a single router file

**Before**:
```
backend/
├── app/
│   ├── auth/
│   │   ├── jwt_handler.py
│   │   └── auth_bearer.py
│   └── routers/
│       ├── products.py
│       ├── users.py
│       └── scraping.py
```

**After**:
```
backend/
├── app/
│   └── routers/
│       ├── products.py
│       ├── users.py
│       ├── scraping.py
│       └── auth.py          # All auth logic here
```

**What `routers/auth.py` Contains**:
- JWT token creation (`create_access_token()`)
- JWT token verification (`verify_token()`)
- Password hashing and verification
- Authentication endpoints (`/login`, `/register`, `/me`)
- FastAPI security dependencies

---

## 5. Removed `config.py` from Backend

**Reason**: Environment variables loaded directly using `python-dotenv` for simplicity

**Before**:
```
backend/
├── app/
│   ├── config.py          # Centralized config
│   ├── database/
│   │   ├── postgres.py    # imports from config
│   │   └── mongodb.py     # imports from config
│   └── routers/
│       └── auth.py        # imports from config
```

**After**:
```
backend/
├── app/
│   ├── database/
│   │   ├── postgres.py    # loads env vars directly
│   │   └── mongodb.py     # loads env vars directly
│   └── routers/
│       └── auth.py        # loads env vars directly
```

**Example - Before (with config.py)**:
```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_URL: str
    SECRET_KEY: str
    
    class Config:
        env_file = ".env"

settings = Settings()

# database/postgres.py
from app.config import settings
engine = create_engine(settings.POSTGRES_URL)
```

**Example - After (with python-dotenv)**:
```python
# database/postgres.py
import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_URL = os.getenv("POSTGRES_URL")
engine = create_engine(POSTGRES_URL)
```

---

## Updated Dependencies

### Mobile (package.json)

**Added**:
- `expo-router`: ^2.0.0 (file-based routing)

**Removed**:
- `react-navigation`: ^6.0.0 (replaced by Expo Router)

### Backend (requirements.txt)

**No changes** - `python-dotenv` was already included

---

## File-Based Routing Explanation

### How Expo Router Works

1. **Files = Routes**: Each file in `app/` becomes a route automatically
2. **Route Groups**: Folders with `()` don't appear in the URL
3. **Layouts**: `_layout.tsx` files define layouts for their directory level

### Examples

| File Path | URL Route | Description |
|-----------|-----------|-------------|
| `app/(tabs)/home.tsx` | `/` | Home screen (root) |
| `app/(tabs)/wishlist.tsx` | `/wishlist` | Wishlist screen |
| `app/(auth)/login.tsx` | `/login` | Login screen |
| `app/(auth)/register.tsx` | `/register` | Register screen |
| `app/_layout.tsx` | N/A | Root layout (wraps all routes) |
| `app/(tabs)/_layout.tsx` | N/A | Tab layout (wraps tab routes) |

### Benefits

- **No manual navigation config**: File structure defines routes
- **Type-safe navigation**: TypeScript knows all routes
- **Automatic deep linking**: URLs work automatically
- **Simpler to understand**: Folder structure = app structure

---

## Benefits of These Changes

### 1. Simpler Mobile Structure
- Fewer folders to manage
- File-based routing is more intuitive
- No separate navigation configuration

### 2. Simpler Backend Structure
- Authentication in one file instead of two
- No config file to maintain
- Direct environment variable loading

### 3. Easier to Explain
- Clearer naming (`mobile/` vs `frontend/`)
- Fewer concepts to understand
- More beginner-friendly

### 4. Modern Best Practices
- Expo Router is the recommended approach for Expo apps
- Direct environment variable loading is simpler for small projects
- Single-file authentication is easier to maintain

---

## Migration Checklist

If migrating from old structure to new:

### Mobile
- [ ] Rename `frontend/` to `mobile/`
- [ ] Create `app/` directory
- [ ] Move screen files to `app/` with proper grouping
- [ ] Create `_layout.tsx` files for root and tabs
- [ ] Move API logic to `constants/api.ts`
- [ ] Remove `src/`, `screens/`, `navigation/`, `services/` folders
- [ ] Update imports in all files
- [ ] Install `expo-router` package
- [ ] Update `app.json` for Expo Router

### Backend
- [ ] Move `app/auth/jwt_handler.py` and `app/auth/auth_bearer.py` logic to `routers/auth.py`
- [ ] Delete `app/auth/` folder
- [ ] Delete `app/config.py`
- [ ] Update `database/postgres.py` to load env vars directly
- [ ] Update `database/mongodb.py` to load env vars directly
- [ ] Update `routers/auth.py` to load env vars directly
- [ ] Update all imports that referenced `app.config`
- [ ] Test all endpoints

---

## Questions & Answers

### Q: Why not keep the services folder?
**A**: For a beginner project, centralizing API configuration in one file (`constants/api.ts`) is simpler and easier to understand than splitting it across multiple service files.

### Q: Why remove config.py?
**A**: For small projects, loading environment variables directly with `python-dotenv` is simpler and more straightforward than creating a separate configuration class.

### Q: What if we need more complex navigation?
**A**: Expo Router supports complex navigation patterns (modals, nested stacks, etc.) through its file-based system. You can add more route groups and layouts as needed.

### Q: Can we add back types/ and utils/ folders?
**A**: Yes! These can be added when needed. The initial structure focuses on essential folders only.

---

## Documentation Updated

The following files have been updated with these changes:

1. ✅ `.kiro/specs/pricepilot-folder-structure/design.md`
   - Updated architecture diagram
   - Updated component descriptions
   - Updated dependencies
   - Updated correctness properties

2. ✅ `docs/FOLDER_STRUCTURE.md`
   - Updated all folder structures
   - Updated explanations
   - Added complete corrected structure
   - Added new questions for teachers

3. ✅ `docs/STRUCTURE_CHANGES.md` (this file)
   - Comprehensive change documentation
   - Migration checklist
   - Examples and explanations
