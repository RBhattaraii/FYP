# PricePilot Folder Structure

## Overview

This document explains the folder structure of the PricePilot project. The structure is designed to be simple, beginner-friendly, and easy to explain to instructors. The mobile app uses Expo Router for file-based routing, and the backend uses python-dotenv for environment variable management without a separate config file.

## Root Structure

```
PricePilot/
├── mobile/            # React Native mobile app (Expo Router)
├── backend/           # FastAPI Python server
├── docs/              # Documentation
├── .gitignore         # Git ignore rules
└── README.md          # Project overview
```

## Mobile Structure (React Native + Expo Router + TypeScript)

```
mobile/
├── app/                      # Expo Router file-based routing
│   ├── _layout.tsx          # Root layout
│   ├── (auth)/              # Auth group (not in URL)
│   │   ├── login.tsx        # Login screen
│   │   └── register.tsx     # Register screen
│   └── (tabs)/              # Tab navigation group
│       ├── _layout.tsx      # Tab layout
│       ├── home.tsx         # Home tab
│       ├── wishlist.tsx     # Wishlist tab
│       ├── notifications.tsx # Notifications tab
│       └── profile.tsx      # Profile tab
├── components/              # Reusable UI components
├── constants/               # App constants
│   └── api.ts              # API configuration & endpoints
├── assets/                  # Images, fonts, icons
├── app.json                 # Expo configuration
├── package.json             # Dependencies
└── tsconfig.json            # TypeScript config
```

### Mobile Folders Explained

- **app/**: File-based routing - each file is automatically a route
  - Files with `()` are route groups (don't appear in URL)
  - `_layout.tsx` files define layouts for their directory
  - Example: `app/(tabs)/home.tsx` becomes the `/` route
- **components/**: Reusable pieces like buttons, cards, search bars
- **constants/api.ts**: API base URL, endpoints, and HTTP client (Axios) configuration
- **assets/**: Images, fonts, and other static files

## Backend Structure (FastAPI + Python)

```
backend/
├── app/
│   ├── routers/       # API endpoints (routes)
│   │   ├── products.py
│   │   ├── users.py
│   │   ├── scraping.py
│   │   └── auth.py    # Authentication endpoints & JWT logic
│   ├── models/        # Data models
│   │   ├── product.py
│   │   ├── user.py
│   │   └── scraped_data.py
│   └── database/      # Database connections
│       ├── postgres.py
│       └── mongodb.py
├── main.py            # FastAPI app entry point
├── requirements.txt   # Python dependencies
└── .env.example       # Environment variables template
```

### Backend Folders Explained

- **routers/**: API endpoints organized by feature
  - `products.py` - Product CRUD operations
  - `users.py` - User management
  - `scraping.py` - Web scraping triggers
  - `auth.py` - Login, register, JWT token creation/verification
- **models/**: Define data structure for database and validation
- **database/**: Connect to PostgreSQL and MongoDB
  - Each file loads environment variables directly using python-dotenv
  - No separate config.py file needed

## Why This Structure?

### Simple and Clear
- Only essential folders (no unnecessary complexity)
- Each folder has a single, clear purpose
- Easy to find where code belongs

### File-Based Routing (Mobile)
- Expo Router automatically creates routes from files
- No separate navigation configuration needed
- Folder structure = app navigation structure

### No Service Layer (Backend)
- Routers call database directly
- Fewer files to manage
- Easier to understand for beginners

### No Config File (Backend)
- Environment variables loaded directly using python-dotenv
- Each module loads only what it needs
- Simpler and more straightforward

### Separation of Concerns
- Mobile and backend are completely separate
- Each folder has a specific responsibility
- Easy to work on one part without affecting others

## Database Organization

### PostgreSQL (Supabase)
- Stores structured data (products, users)
- Defined in `backend/app/models/`
- Connected via `backend/app/database/postgres.py`

### MongoDB Atlas
- Stores raw scraped data
- Flexible schema for HTML and parsed data
- Connected via `backend/app/database/mongodb.py`

## Key Files

| File | Purpose |
|------|---------|
| `backend/main.py` | Starts the FastAPI server |
| `backend/.env.example` | Template for secrets |
| `backend/app/routers/auth.py` | Authentication logic and JWT handling |
| `backend/app/database/postgres.py` | PostgreSQL connection with dotenv |
| `backend/app/database/mongodb.py` | MongoDB connection with dotenv |
| `mobile/app/_layout.tsx` | Root layout for the app |
| `mobile/constants/api.ts` | API configuration and endpoints |
| `mobile/app.json` | Expo configuration |
| `mobile/package.json` | Mobile dependencies |
| `backend/requirements.txt` | Backend dependencies |

## Adding New Features

### Adding a New API Endpoint
1. Create or update router file in `backend/app/routers/`
2. Define models in `backend/app/models/`
3. Import router in `backend/main.py`
4. Load any needed environment variables using `python-dotenv` in the router

### Adding a New Screen
1. Create screen file in `mobile/app/` directory (e.g., `product-detail.tsx`)
2. Expo Router automatically creates the route
3. For grouped routes, create folders with `()` (e.g., `(auth)/login.tsx`)
4. Create any needed components in `mobile/components/`

### Adding API Endpoints to Mobile
1. Add endpoint constants to `mobile/constants/api.ts`
2. Use the configured axios instance from `api.ts` in your screens

## Best Practices

1. **Keep it simple**: Don't add folders until you need them
2. **One responsibility**: Each file should do one thing
3. **Clear naming**: Use descriptive names (ProductCard, not Card)
4. **Group by feature**: Related files stay together
5. **Document as you go**: Add comments for complex logic

## Questions for Your Teacher

1. Why do we separate mobile and backend?
2. What is the purpose of the models folder?
3. Why do we use two different databases?
4. What is the benefit of TypeScript in the mobile app?
5. Why don't we commit the .env file to git?
6. How does Expo Router's file-based routing work?
7. Why do we load environment variables directly instead of using a config file?
8. What is the advantage of keeping authentication logic in a single router file?

---

## Complete Corrected Folder Structure

```
PricePilot/
├── mobile/                              # React Native mobile app
│   ├── app/                            # Expo Router file-based routing
│   │   ├── _layout.tsx                 # Root layout component
│   │   ├── (auth)/                     # Authentication group (not in URL)
│   │   │   ├── login.tsx              # Login screen (/login)
│   │   │   └── register.tsx           # Register screen (/register)
│   │   └── (tabs)/                    # Tab navigation group (not in URL)
│   │       ├── _layout.tsx            # Tab layout configuration
│   │       ├── home.tsx               # Home tab (/)
│   │       ├── wishlist.tsx           # Wishlist tab (/wishlist)
│   │       ├── notifications.tsx      # Notifications tab (/notifications)
│   │       └── profile.tsx            # Profile tab (/profile)
│   ├── components/                     # Reusable UI components
│   │   ├── ProductCard.tsx
│   │   ├── PriceChart.tsx
│   │   ├── SearchBar.tsx
│   │   └── LoadingSpinner.tsx
│   ├── constants/                      # App-wide constants
│   │   └── api.ts                     # API config, endpoints, axios instance
│   ├── assets/                         # Images, fonts, icons
│   ├── app.json                        # Expo configuration
│   ├── package.json                    # Dependencies
│   └── tsconfig.json                   # TypeScript configuration
│
├── backend/                             # FastAPI Python server
│   ├── app/
│   │   ├── routers/                    # API endpoints
│   │   │   ├── products.py            # Product CRUD endpoints
│   │   │   ├── users.py               # User management endpoints
│   │   │   ├── scraping.py            # Web scraping endpoints
│   │   │   └── auth.py                # Auth endpoints + JWT logic
│   │   ├── models/                     # Data models
│   │   │   ├── product.py             # Product models (SQLAlchemy + Pydantic)
│   │   │   ├── user.py                # User models
│   │   │   └── scraped_data.py        # Scraped data models (MongoDB)
│   │   └── database/                   # Database connections
│   │       ├── postgres.py            # PostgreSQL connection (with dotenv)
│   │       └── mongodb.py             # MongoDB connection (with dotenv)
│   ├── main.py                         # FastAPI app entry point
│   ├── requirements.txt                # Python dependencies
│   └── .env.example                    # Environment variables template
│
├── docs/                                # Documentation
│   └── FOLDER_STRUCTURE.md            # This file
│
├── .gitignore                          # Git ignore rules
└── README.md                           # Project overview
```

### Key Changes from Traditional Structure

1. **`frontend/` → `mobile/`**: Clearer naming for mobile app
2. **`src/` removed**: Expo Router uses `app/` directory directly
3. **`screens/` + `navigation/` → `app/`**: File-based routing replaces manual navigation
4. **`services/` → `constants/api.ts`**: Centralized API configuration
5. **`app/auth/` folder → `routers/auth.py`**: Single file for authentication
6. **`config.py` removed**: Environment variables loaded directly with python-dotenv
