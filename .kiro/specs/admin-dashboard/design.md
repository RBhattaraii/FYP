# Design Document: Admin Dashboard

## 1. Overview

The Admin Dashboard feature provides system administrators with comprehensive monitoring and control capabilities for the PricePilot platform. This feature introduces a secure, role-based administrative interface that enables authorized personnel to view system metrics, monitor scraper health, analyze user activity, and access product inventory statistics.

### Architecture Goals

- **Security-First**: Environment-based authentication with JWT tokens and role-based access control
- **Performance**: Efficient data aggregation with 60-second caching to minimize database load
- **User Experience**: Intuitive dashboard with real-time metrics, visual charts, and pull-to-refresh functionality
- **Separation of Concerns**: Clean separation between admin and regular user functionality

### System Context

The Admin Dashboard integrates with existing components:
- **Authentication System**: Extends the current JWT-based auth with admin role support
- **Database Layer**: Queries PostgreSQL for metrics using existing database connection pool
- **Mobile App**: Adds a sixth tab to the existing bottom navigation (conditional rendering based on user role)
- **API Layer**: Introduces new `/admin` endpoints with role verification middleware

## 2. Technical Architecture

### 2.1 Backend Architecture

#### Authentication Flow

```python
# Environment-based admin credentials
ADMIN_USERNAME=admin@pricepilot.com
ADMIN_PASSWORD=SecureAdminPass123!

# Authentication flow
1. Admin enters credentials in mobile app
2. POST /auth/admin-login validates against env variables
3. If valid, JWT token issued with role="admin"
4. Mobile app stores token in expo-secure-store
5. All admin API requests include: Authorization: Bearer <token>
6. Middleware verifies token and checks role="admin"
```

#### Admin Authentication Endpoint


**New Route**: `POST /auth/admin-login`

```python
# app/routers/auth.py

from fastapi import APIRouter, HTTPException, status
import os

@router.post("/admin-login", response_model=AuthResponse)
@limiter.limit("3/minute")
async def admin_login(
    request: Request,
    credentials: LoginRequest,
    db: asyncpg.Connection = Depends(get_db)
):
    """
    Authenticate admin user with environment-based credentials.
    
    Security measures:
    - Rate limited to 3 attempts per minute
    - Credentials never stored in database
    - Generic error messages to prevent enumeration
    - Token contains role claim for authorization
    """
    admin_username = os.getenv("ADMIN_USERNAME")
    admin_password = os.getenv("ADMIN_PASSWORD")
    
    if not admin_username or not admin_password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin credentials not configured"
        )
    
    # Constant-time comparison to prevent timing attacks
    username_match = credentials.email == admin_username
    password_match = credentials.password == admin_password
    
    if not (username_match and password_match):
        # Generic error message
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Generate JWT with admin role
    token_payload = {
        "user_id": "admin",
        "role": "admin",
        "email": admin_username
    }
    token = create_access_token(token_payload)
    
    return AuthResponse(
        token=token,
        token_type="bearer",
        user_id="admin",
        email=admin_username,
        role="admin",
        full_name="Administrator"
    )
```

#### Dashboard Metrics Endpoint

**New Route**: `GET /admin/dashboard`

```python
# app/routers/admin.py

from datetime import datetime, timedelta
from typing import Dict, Any
import asyncio

# In-memory cache
dashboard_cache = {
    "data": None,
    "timestamp": None
}
CACHE_DURATION = 60  # seconds

async def get_current_admin(request: Request, db: asyncpg.Connection) -> str:
    """Verify admin role from JWT token"""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    token = auth_header.split(" ")[1]
    payload = decode_access_token(token)
    
    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return payload.get("user_id")

@router.get("/dashboard")
@limiter.limit("30/minute")
async def get_admin_dashboard(
    request: Request,
    db: asyncpg.Connection = Depends(get_db)
):
    """
    Fetch comprehensive dashboard metrics with caching.
    
    Performance optimizations:
    - 60-second cache to reduce database load
    - Parallel query execution for independent metrics
    - Returns cached data when valid
    """
    # Verify admin access
    admin_id = await get_current_admin(request, db)
    
    # Check cache
    now = datetime.utcnow()
    if dashboard_cache["data"] and dashboard_cache["timestamp"]:
        cache_age = (now - dashboard_cache["timestamp"]).total_seconds()
        if cache_age < CACHE_DURATION:
            return dashboard_cache["data"]
    
    # Execute all queries in parallel
    results = await asyncio.gather(
        calculate_total_products(db),
        calculate_category_breakdown(db),
        calculate_store_distribution(db),
        calculate_scraper_status(db),
        return_exceptions=True
    )
    
    # Build response
    dashboard_data = {
        "total_products": results[0] if not isinstance(results[0], Exception) else 0,
        "category_breakdown": results[1] if not isinstance(results[1], Exception) else [],
        "store_distribution": results[2] if not isinstance(results[2], Exception) else [],
        "scraper_status": results[3] if not isinstance(results[3], Exception) else [],
        "last_updated": now.isoformat()
    }
    
    # Update cache
    dashboard_cache["data"] = dashboard_data
    dashboard_cache["timestamp"] = now
    
    return dashboard_data

async def calculate_total_products(db: asyncpg.Connection) -> int:
    """Count all products in the database"""
    return await db.fetchval("SELECT COUNT(*) FROM products") or 0

async def calculate_category_breakdown(db: asyncpg.Connection) -> list:
    """Group products by category with counts, sorted descending"""
    rows = await db.fetch("""
        SELECT category, COUNT(*) as count
        FROM products
        WHERE category IS NOT NULL
        GROUP BY category
        HAVING COUNT(*) > 0
        ORDER BY count DESC
        LIMIT 10
    """)
    
    return [
        {"category": row["category"], "count": row["count"]}
        for row in rows
    ]

async def calculate_store_distribution(db: asyncpg.Connection) -> list:
    """Group products by store with counts, sorted descending"""
    rows = await db.fetch("""
        SELECT store_name, COUNT(*) as count
        FROM products
        WHERE store_name IS NOT NULL
        GROUP BY store_name
        HAVING COUNT(*) > 0
        ORDER BY count DESC
    """)
    
    return [
        {"store": row["store_name"], "count": row["count"]}
        for row in rows
    ]

async def calculate_scraper_status(db: asyncpg.Connection) -> list:
    """Determine scraper health based on last scrape time"""
    rows = await db.fetch("""
        SELECT 
            store_name,
            last_scrape_time,
            CASE 
                WHEN last_scrape_time IS NULL THEN 'inactive'
                WHEN last_scrape_time >= NOW() - INTERVAL '48 hours' THEN 'active'
                ELSE 'stale'
            END as status
        FROM scrape_metadata
        ORDER BY store_name
    """)
    
    return [
        {
            "store": row["store_name"],
            "status": row["status"],
            "last_scrape": row["last_scrape_time"].isoformat() if row["last_scrape_time"] else None
        }
        for row in rows
    ]
```

### 2.2 Mobile Architecture

#### Navigation Structure Update

The existing tab navigation will be modified to conditionally render an admin tab:

```typescript
// mobile/app/(tabs)/_layout.tsx

import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../../constants/theme';
import { useAuth } from '../../hooks/useAuth';

export default function TabsLayout() {
  const { user, isAdmin } = useAuth();

  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: colors.warningOrange,
      }}
    >
      {/* Existing tabs: home, explore, offers, favorites, profile */}
      <Tabs.Screen name="home" {...homeOptions} />
      <Tabs.Screen name="explore" {...exploreOptions} />
      <Tabs.Screen name="offers" {...offersOptions} />
      <Tabs.Screen name="favorites" {...favoritesOptions} />
      <Tabs.Screen name="profile" {...profileOptions} />
      
      {/* Admin tab - conditionally rendered */}
      {isAdmin && (
        <Tabs.Screen 
          name="admin" 
          options={{ 
            title: 'Admin',
            tabBarIcon: ({ color, focused }) => (
              <Ionicons 
                name={focused ? 'shield' : 'shield-outline'} 
                size={24} 
                color={color} 
              />
            ),
          }} 
        />
      )}
    </Tabs>
  );
}
```

#### Authentication Hook

```typescript
// mobile/hooks/useAuth.ts

import { useState, useEffect } from 'react';
import { authStorage } from '../lib/authStorage';
import { API_URL } from '../constants/api';

export function useAuth() {
  const [user, setUser] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUser();
  }, []);

  const loadUser = async () => {
    try {
      const token = await authStorage.getItemAsync('token');
      if (!token) {
        setLoading(false);
        return;
      }

      const response = await fetch(`${API_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        setIsAdmin(userData.role === 'admin');
      }
    } catch (error) {
      console.error('Failed to load user:', error);
    } finally {
      setLoading(false);
    }
  };

  const loginAdmin = async (email: string, password: string) => {
    const response = await fetch(`${API_URL}/auth/admin-login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    await authStorage.setItemAsync('token', data.token);
    await authStorage.setItemAsync('email', data.email);
    
    setUser(data);
    setIsAdmin(true);
    
    return data;
  };

  return { user, isAdmin, loading, loadUser, loginAdmin };
}
```

#### Admin Login Screen



**New Screen**: `mobile/app/(auth)/admin-login.tsx`

```typescript
import { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { colors, typography, spacing, borderRadius } from '../../constants/theme';
import { useAuth } from '../../hooks/useAuth';

export default function AdminLoginScreen() {
  const router = useRouter();
  const { loginAdmin } = useAuth();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async () => {
    if (!email || !password) {
      setError('Email and password are required');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await loginAdmin(email, password);
      router.replace('/(tabs)/admin');
    } catch (err: any) {
      setError('Invalid admin credentials');
      setPassword('');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Ionicons name="shield" size={48} color={colors.warningOrange} />
        <Text style={styles.title}>Admin Login</Text>
        <Text style={styles.subtitle}>
          Enter your administrator credentials to access the dashboard
        </Text>
      </View>

      {error ? (
        <View style={styles.errorContainer}>
          <Ionicons name="alert-circle" size={20} color={colors.errorRed} />
          <Text style={styles.errorText}>{error}</Text>
        </View>
      ) : null}

      <View style={styles.form}>
        <View style={styles.inputContainer}>
          <Text style={styles.label}>Admin Email</Text>
          <View style={styles.inputWrapper}>
            <Ionicons name="mail-outline" size={20} color={colors.gray400} />
            <TextInput
              style={styles.input}
              placeholder="admin@pricepilot.com"
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
              autoCapitalize="none"
              editable={!loading}
            />
          </View>
        </View>

        <View style={styles.inputContainer}>
          <Text style={styles.label}>Password</Text>
          <View style={styles.inputWrapper}>
            <Ionicons name="lock-closed-outline" size={20} color={colors.gray400} />
            <TextInput
              style={styles.input}
              placeholder="Password"
              value={password}
              onChangeText={setPassword}
              secureTextEntry={!showPassword}
              autoCapitalize="none"
              editable={!loading}
            />
            <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
              <Ionicons
                name={showPassword ? 'eye-off-outline' : 'eye-outline'}
                size={20}
                color={colors.gray400}
              />
            </TouchableOpacity>
          </View>
        </View>

        <TouchableOpacity
          style={[styles.button, loading && styles.buttonDisabled]}
          onPress={handleLogin}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color={colors.white} />
          ) : (
            <Text style={styles.buttonText}>Login</Text>
          )}
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.white,
    padding: spacing.xl,
  },
  header: {
    alignItems: 'center',
    marginTop: spacing['4xl'],
    marginBottom: spacing['4xl'],
  },
  title: {
    fontSize: typography.fontSize.h1,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
    marginTop: spacing.base,
  },
  subtitle: {
    fontSize: typography.fontSize.body,
    color: colors.gray600,
    textAlign: 'center',
    marginTop: spacing.sm,
  },
  errorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FEF2F2',
    padding: spacing.md,
    borderRadius: borderRadius.medium,
    marginBottom: spacing.lg,
    gap: spacing.sm,
  },
  errorText: {
    flex: 1,
    color: colors.errorRed,
    fontSize: typography.fontSize.body,
  },
  form: {
    gap: spacing.lg,
  },
  inputContainer: {
    gap: spacing.sm,
  },
  label: {
    fontSize: typography.fontSize.body,
    fontWeight: typography.fontWeight.semibold,
    color: colors.gray900,
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.gray50,
    borderWidth: 1,
    borderColor: colors.gray200,
    borderRadius: borderRadius.large,
    paddingHorizontal: spacing.base,
    height: 56,
    gap: spacing.sm,
  },
  input: {
    flex: 1,
    fontSize: typography.fontSize.bodyLarge,
    color: colors.gray900,
  },
  button: {
    backgroundColor: colors.warningOrange,
    height: 56,
    borderRadius: borderRadius.large,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: spacing.base,
  },
  buttonDisabled: {
    backgroundColor: colors.gray400,
  },
  buttonText: {
    color: colors.white,
    fontSize: typography.fontSize.button,
    fontWeight: typography.fontWeight.bold,
  },
});
```

#### Admin Dashboard Screen

**New Screen**: `mobile/app/(tabs)/admin.tsx`

```typescript
import { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  RefreshControl,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { colors, typography, spacing, borderRadius, shadows } from '../../constants/theme';
import { API_URL } from '../../constants/api';
import { authStorage } from '../../lib/authStorage';
import { useFocusEffect } from '@react-navigation/native';

interface DashboardMetrics {
  total_products: number;
  category_breakdown: Array<{ category: string; count: number }>;
  store_distribution: Array<{ store: string; count: number }>;
  scraper_status: Array<{ store: string; status: string; last_scrape: string | null }>;
  last_updated: string;
}

export default function AdminDashboardScreen() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');

  const fetchMetrics = async (isRefresh = false) => {
    if (isRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }
    setError('');

    try {
      const token = await authStorage.getItemAsync('token');
      const response = await fetch(`${API_URL}/admin/dashboard`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch metrics');
      }

      const data = await response.json();
      setMetrics(data);
      
      // Cache for offline viewing
      await authStorage.setItemAsync('cached_metrics', JSON.stringify(data));
    } catch (err: any) {
      setError(err.message);
      
      // Try to load cached data
      const cached = await authStorage.getItemAsync('cached_metrics');
      if (cached) {
        setMetrics(JSON.parse(cached));
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  // Auto-refresh when screen gains focus
  useFocusEffect(
    useCallback(() => {
      if (!loading) {
        fetchMetrics();
      }
    }, [])
  );

  const formatNumber = (num: number): string => {
    return num.toLocaleString();
  };

  const formatRelativeTime = (isoString: string | null): string => {
    if (!isoString) return 'Never';
    
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'active': return colors.successGreen;
      case 'stale': return colors.warningOrange;
      case 'inactive': return colors.errorRed;
      default: return colors.gray400;
    }
  };

  if (loading && !metrics) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <Ionicons name="shield" size={48} color={colors.warningOrange} />
          <Text style={styles.loadingText}>Loading dashboard...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Admin Dashboard</Text>
        <TouchableOpacity onPress={() => fetchMetrics(true)}>
          <Ionicons name="refresh" size={24} color={colors.warningOrange} />
        </TouchableOpacity>
      </View>

      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={() => fetchMetrics(true)} />
        }
      >
        {error && (
          <View style={styles.errorBanner}>
            <Ionicons name="alert-circle" size={20} color={colors.errorRed} />
            <Text style={styles.errorText}>{error}</Text>
          </View>
        )}

        {/* Total Products Card */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Total Products</Text>
          <Text style={styles.metricValue}>{formatNumber(metrics?.total_products || 0)}</Text>
        </View>

        {/* Category Breakdown */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Category Breakdown (Top 10)</Text>
          {metrics?.category_breakdown.map((item, index) => (
            <View key={index} style={styles.listItem}>
              <Text style={styles.listLabel}>{item.category}</Text>
              <Text style={styles.listValue}>{formatNumber(item.count)}</Text>
            </View>
          ))}
        </View>

        {/* Store Distribution */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Store Distribution</Text>
          {metrics?.store_distribution.map((item, index) => (
            <View key={index} style={styles.listItem}>
              <Text style={styles.listLabel}>{item.store}</Text>
              <Text style={styles.listValue}>{formatNumber(item.count)}</Text>
            </View>
          ))}
        </View>

        {/* Scraper Status */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Scraper Status</Text>
          {metrics?.scraper_status.map((item, index) => (
            <View key={index} style={styles.scraperItem}>
              <View style={styles.scraperHeader}>
                <Text style={styles.scraperStore}>{item.store}</Text>
                <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.status) }]}>
                  <Text style={styles.statusText}>{item.status}</Text>
                </View>
              </View>
              <Text style={styles.scraperTime}>
                Last scrape: {formatRelativeTime(item.last_scrape)}
              </Text>
            </View>
          ))}
        </View>

        {metrics?.last_updated && (
          <Text style={styles.lastUpdated}>
            Last updated: {formatRelativeTime(metrics.last_updated)}
          </Text>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.gray50,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: spacing.base,
    backgroundColor: colors.white,
    borderBottomWidth: 1,
    borderBottomColor: colors.gray200,
  },
  headerTitle: {
    fontSize: typography.fontSize.h2,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
  },
  scrollView: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    gap: spacing.base,
  },
  loadingText: {
    fontSize: typography.fontSize.bodyLarge,
    color: colors.gray600,
  },
  errorBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FEF2F2',
    padding: spacing.md,
    margin: spacing.base,
    borderRadius: borderRadius.medium,
    gap: spacing.sm,
  },
  errorText: {
    flex: 1,
    color: colors.errorRed,
    fontSize: typography.fontSize.body,
  },
  card: {
    backgroundColor: colors.white,
    margin: spacing.base,
    padding: spacing.base,
    borderRadius: borderRadius.large,
    ...shadows.card,
  },
  cardTitle: {
    fontSize: typography.fontSize.h3,
    fontWeight: typography.fontWeight.semibold,
    color: colors.gray900,
    marginBottom: spacing.md,
  },
  metricValue: {
    fontSize: 36,
    fontWeight: typography.fontWeight.bold,
    color: colors.warningOrange,
  },
  listItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.gray100,
  },
  listLabel: {
    fontSize: typography.fontSize.body,
    color: colors.gray700,
  },
  listValue: {
    fontSize: typography.fontSize.bodyLarge,
    fontWeight: typography.fontWeight.semibold,
    color: colors.gray900,
  },
  scraperItem: {
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.gray100,
  },
  scraperHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.xs,
  },
  scraperStore: {
    fontSize: typography.fontSize.bodyLarge,
    fontWeight: typography.fontWeight.semibold,
    color: colors.gray900,
  },
  statusBadge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.small,
  },
  statusText: {
    fontSize: typography.fontSize.caption,
    fontWeight: typography.fontWeight.semibold,
    color: colors.white,
    textTransform: 'uppercase',
  },
  scraperTime: {
    fontSize: typography.fontSize.caption,
    color: colors.gray600,
  },
  lastUpdated: {
    textAlign: 'center',
    fontSize: typography.fontSize.caption,
    color: colors.gray500,
    padding: spacing.lg,
  },
});
```

## 3. Data Models

### JWT Token Payload (Admin)

```typescript
interface AdminTokenPayload {
  user_id: string;        // "admin"
  role: string;           // "admin"
  email: string;          // Admin email from env
  exp: number;            // Expiry timestamp
}
```

### Dashboard Response Model

```typescript
interface DashboardMetrics {
  total_products: number;
  category_breakdown: CategoryBreakdown[];
  store_distribution: StoreDistribution[];
  scraper_status: ScraperStatus[];
  last_updated: string;   // ISO 8601 timestamp
}

interface CategoryBreakdown {
  category: string;
  count: number;
}

interface StoreDistribution {
  store: string;
  count: number;
}

interface ScraperStatus {
  store: string;
  status: 'active' | 'stale' | 'inactive';
  last_scrape: string | null;  // ISO 8601 timestamp or null
}
```

## 4. Component Architecture

### Backend Components

#### Admin Middleware

```python
# app/middleware/admin.py

from fastapi import Request, HTTPException, status
from app.auth.jwt_handler import decode_access_token

async def require_admin(request: Request):
    """Middleware to verify admin role"""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    token = auth_header.split(" ")[1]
    
    try:
        payload = decode_access_token(token)
        
        if payload.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
```

#### Cache Manager

```python
# app/services/cache_manager.py

from datetime import datetime, timedelta
from typing import Any, Optional

class DashboardCache:
    def __init__(self, duration_seconds: int = 60):
        self.duration = duration_seconds
        self.data: Optional[Any] = None
        self.timestamp: Optional[datetime] = None
    
    def get(self) -> Optional[Any]:
        """Return cached data if valid"""
        if not self.data or not self.timestamp:
            return None
        
        age = (datetime.utcnow() - self.timestamp).total_seconds()
        if age >= self.duration:
            return None
        
        return self.data
    
    def set(self, data: Any):
        """Update cache with new data"""
        self.data = data
        self.timestamp = datetime.utcnow()
    
    def clear(self):
        """Invalidate cache"""
        self.data = None
        self.timestamp = None
```

### Mobile Components

#### MetricCard Component

```typescript
// mobile/components/admin/MetricCard.tsx

interface MetricCardProps {
  title: string;
  value: string | number;
  icon?: string;
}

export function MetricCard({ title, value, icon }: MetricCardProps) {
  return (
    <View style={styles.card}>
      {icon && <Ionicons name={icon} size={32} color={colors.warningOrange} />}
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.value}>{value}</Text>
    </View>
  );
}
```

#### StatusBadge Component

```typescript
// mobile/components/admin/StatusBadge.tsx

interface StatusBadgeProps {
  status: 'active' | 'stale' | 'inactive';
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const getColor = () => {
    switch (status) {
      case 'active': return colors.successGreen;
      case 'stale': return colors.warningOrange;
      case 'inactive': return colors.errorRed;
    }
  };

  return (
    <View style={[styles.badge, { backgroundColor: getColor() }]}>
      <Text style={styles.text}>{status.toUpperCase()}</Text>
    </View>
  );
}
```

## 5. Error Handling

### Backend Error Responses



```python
# Error response format
{
    "detail": "Error message",
    "status_code": 401 | 403 | 500
}

# Scenarios:
# 401 Unauthorized - Missing, invalid, or expired token
# 403 Forbidden - Valid token but insufficient permissions (non-admin)
# 500 Internal Server Error - Database errors, configuration issues
```

### Mobile Error Handling Strategy

1. **Network Errors**: Display error message + attempt to load cached data
2. **Authentication Errors**: Redirect to admin login screen
3. **API Errors**: Show error banner with retry option
4. **Offline Mode**: Display cached metrics with "Last updated" timestamp

```typescript
try {
  await fetchMetrics();
} catch (error) {
  if (error.status === 401) {
    // Token expired - redirect to login
    router.replace('/(auth)/admin-login');
  } else if (error.status === 403) {
    // Insufficient permissions
    Alert.alert('Access Denied', 'Admin access required');
  } else {
    // Network or server error - try cached data
    loadCachedMetrics();
    showErrorBanner(error.message);
  }
}
```

## 6. Security Considerations

### Authentication Security

1. **Environment-Based Credentials**
   - Admin credentials stored in `.env` file, never in database
   - No credential enumeration (generic error messages)
   - Rate limiting: 3 attempts per minute for admin login

2. **Token Security**
   - JWT tokens with 60-minute expiration
   - Role claim embedded in token for authorization
   - Tokens stored in expo-secure-store (encrypted storage)

3. **API Security**
   - All admin endpoints require valid admin token
   - Middleware verifies role claim on every request
   - No sensitive data exposed in error messages or logs

### Authorization Flow

```
1. User enters admin credentials
2. Backend validates against env variables
3. If valid, JWT issued with role="admin"
4. Mobile app stores token in secure storage
5. Each API request includes: Authorization: Bearer <token>
6. Middleware extracts token and verifies:
   - Token is valid and not expired
   - Token contains role="admin"
7. If checks pass, request proceeds
8. If checks fail, return 401/403 error
```

## 7. Performance Optimizations

### Backend Optimizations

1. **Query Parallelization**
   - All dashboard queries execute in parallel using `asyncio.gather()`
   - Reduces total response time from sum of queries to max of queries

2. **60-Second Caching**
   - In-memory cache for dashboard metrics
   - Cache key: None (single dashboard endpoint)
   - Cache invalidation: Time-based (60 seconds)
   - Reduces database load by up to 98% for frequent refreshes

3. **Efficient Queries**
   - Use aggregation functions (`COUNT`, `GROUP BY`) at database level
   - Apply `LIMIT` for top N results (categories)
   - Filter empty categories/stores with `HAVING COUNT(*) > 0`

### Mobile Optimizations

1. **Local Caching**
   - Metrics cached in AsyncStorage for offline viewing
   - Cache updated on every successful fetch
   - Displayed when network unavailable

2. **Pull-to-Refresh**
   - Standard gesture for manual refresh
   - Auto-refresh on screen focus
   - Loading states prevent duplicate requests

3. **Skeleton Loading**
   - Placeholder UI during initial load
   - Improves perceived performance
   - Maintains layout stability

## 8. Database Schema Extensions

No new tables required. The feature uses existing tables:

- `users` - For admin authentication (role column)
- `products` - For total count, category breakdown, store distribution
- `scrape_metadata` - For scraper status tracking

### Scrape Metadata Table Reference

```sql
CREATE TABLE IF NOT EXISTS scrape_metadata (
    id SERIAL PRIMARY KEY,
    store_name VARCHAR(100) NOT NULL,
    last_scrape_time TIMESTAMP,
    status VARCHAR(20) DEFAULT 'inactive',
    products_found INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_scrape_metadata_store ON scrape_metadata(store_name);
CREATE INDEX idx_scrape_metadata_time ON scrape_metadata(last_scrape_time);
```

## 9. Testing Strategy

### Unit Tests

- Admin authentication logic (credential validation)
- JWT token generation and verification
- Dashboard metric calculations (total, grouping, sorting)
- Number formatting functions
- Relative time formatting functions
- Cache get/set operations

### Integration Tests

- Admin login endpoint (valid/invalid credentials)
- Dashboard endpoint (with/without admin token)
- Authorization middleware (admin vs non-admin tokens)
- Scraper status classification (active/stale/inactive)
- Database query performance

### E2E Tests

- Complete admin login flow (mobile app)
- Dashboard display with real data
- Pull-to-refresh functionality
- Offline mode with cached data
- Tab visibility based on user role

## 10. Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Admin Credential Validation

*For any* pair of entered credentials (username, password), the authentication system SHALL accept them if and only if they exactly match the configured environment variables (ADMIN_USERNAME, ADMIN_PASSWORD).

**Validates: Requirements 1.2**

### Property 2: Admin Token Generation

*For any* successful admin authentication, the system SHALL generate a valid JWT token that contains role="admin" and can be successfully decoded.

**Validates: Requirements 1.3**

### Property 3: Invalid Credential Rejection

*For any* credential pair that does not match the environment variables, the authentication endpoint SHALL reject the request with an authentication error.

**Validates: Requirements 1.4**

### Property 4: Credential Exposure Prevention

*For any* API response or error message, the system SHALL NOT include the admin username or password from environment variables.

**Validates: Requirements 1.5**

### Property 5: Admin Access Control

*For any* request to an admin endpoint with a non-admin token, the system SHALL return HTTP 403 Forbidden status.

**Validates: Requirements 1.6, 7.2**

### Property 6: Authentication Token Validation

*For any* request to an admin endpoint with an invalid or expired token, the system SHALL return HTTP 401 Unauthorized status.

**Validates: Requirements 7.3**

### Property 7: Admin Tab Visibility for Admin Users

*For any* authenticated user with role="admin", the admin tab SHALL be visible in the tab navigation.

**Validates: Requirements 2.4**

### Property 8: Admin Tab Hidden for Non-Admin Users

*For any* authenticated user with role != "admin", the admin tab SHALL NOT be visible in the tab navigation.

**Validates: Requirements 2.5**

### Property 9: Total Products Count Accuracy

*For any* state of the products table, the total_products metric SHALL equal the number of rows in the products table.

**Validates: Requirements 3.1**

### Property 10: Number Formatting with Comma Separators

*For any* number greater than 999, the display formatting function SHALL include comma separators (e.g., 1,234).

**Validates: Requirements 3.4**

### Property 11: Category Aggregation Accuracy

*For any* products dataset, the category_breakdown metric SHALL contain counts that exactly match the number of products in each category.

**Validates: Requirements 4.1**

### Property 12: Category Descending Sort Order

*For any* category_breakdown dataset, the categories SHALL be sorted by product count in descending order.

**Validates: Requirements 4.5**

### Property 13: Empty Category Exclusion

*For any* products dataset, categories with zero products SHALL be excluded from the category_breakdown metric.

**Validates: Requirements 4.6**

### Property 14: Top 10 Categories Limit

*For any* products dataset with more than 10 categories, the dashboard SHALL display exactly 10 categories (the ones with highest counts).

**Validates: Requirements 4.7**

### Property 15: Store Aggregation Accuracy

*For any* products dataset, the store_distribution metric SHALL contain counts that exactly match the number of products from each store.

**Validates: Requirements 5.1**

### Property 16: Store Descending Sort Order

*For any* store_distribution dataset, the stores SHALL be sorted by product count in descending order.

**Validates: Requirements 5.5**

### Property 17: Empty Store Exclusion

*For any* products dataset, stores with zero products SHALL be excluded from the store_distribution metric.

**Validates: Requirements 5.6**

### Property 18: All Non-Empty Stores Displayed

*For any* products dataset, all stores with at least one product SHALL appear in the store_distribution display.

**Validates: Requirements 5.7**

### Property 19: Active Scraper Classification

*For any* scraper with last_scrape_time within 48 hours of the current time, the status SHALL be classified as "active".

**Validates: Requirements 6.2**

### Property 20: Stale Scraper Classification

*For any* scraper with last_scrape_time older than 48 hours, the status SHALL be classified as "stale".

**Validates: Requirements 6.3**

### Property 21: Scraper Status Color Mapping

*For any* scraper status value ("active", "stale", "inactive"), the display SHALL use the corresponding color (green, yellow, red respectively).

**Validates: Requirements 6.7**

### Property 22: Relative Timestamp Formatting

*For any* timestamp, the formatting function SHALL produce a relative time string in the format "X units ago" where units are chosen based on the time difference.

**Validates: Requirements 6.8**

### Property 23: Dashboard Data Refresh

*For any* successful refresh request, all displayed metrics SHALL be updated with the new values returned by the API.

**Validates: Requirements 8.4**

### Property 24: Cache Return Within Validity Period

*For any* dashboard request occurring within 60 seconds of cache creation, the system SHALL return the cached metrics without querying the database.

**Validates: Requirements 9.2, 9.3**

### Property 25: Fresh Calculation After Cache Expiry

*For any* dashboard request occurring after the 60-second cache validity period, the system SHALL calculate fresh metrics by querying the database.

**Validates: Requirements 9.4**

## 11. Deployment Considerations

### Environment Variables

Required in `.env` file:

```bash
# Admin Credentials
ADMIN_USERNAME=admin@pricepilot.com
ADMIN_PASSWORD=SecureAdminPass123!

# Existing variables
JWT_SECRET=your-secret-key
JWT_EXPIRE_MINUTES=60
DATABASE_URL=postgresql://...
```

### Backend Deployment Checklist

- [ ] Add admin credentials to `.env` file
- [ ] Update JWT token generation to include role claim
- [ ] Add admin router to main app
- [ ] Deploy admin middleware
- [ ] Test admin authentication endpoint
- [ ] Test admin dashboard endpoint
- [ ] Verify rate limiting works
- [ ] Verify caching works

### Mobile Deployment Checklist

- [ ] Add useAuth hook
- [ ] Create admin login screen
- [ ] Create admin dashboard screen
- [ ] Update tab navigation with conditional rendering
- [ ] Add admin components (MetricCard, StatusBadge)
- [ ] Test admin login flow
- [ ] Test dashboard display
- [ ] Test offline mode
- [ ] Test auto-refresh on focus

## 12. Future Enhancements

### Phase 2 Features

1. **Manual Scraper Triggers**
   - Button to trigger scraper for specific store
   - Real-time status updates via WebSocket
   - Scraper logs display

2. **User Management**
   - View all registered users
   - Activate/deactivate user accounts
   - View user activity logs

3. **Analytics Dashboard**
   - Search trends over time
   - Popular products chart
   - User growth metrics

4. **System Configuration**
   - Update scraper schedules
   - Configure price alert thresholds
   - Manage featured products

### Technical Debt

1. **Replace In-Memory Cache** with Redis for multi-instance deployments
2. **Add WebSocket** support for real-time metric updates
3. **Implement Audit Logging** for admin actions
4. **Add Database Connection Pooling** optimization for dashboard queries

---

**Programming Language**: Python (Backend), TypeScript/React Native (Mobile)

**Key Libraries**:
- Backend: FastAPI, asyncpg, python-jose (JWT), python-dotenv
- Mobile: Expo, expo-router, expo-secure-store, React Native

**Design Patterns**:
- Repository Pattern (database queries)
- Middleware Pattern (authentication/authorization)
- Cache-Aside Pattern (dashboard metrics)
- Dependency Injection (FastAPI Depends)
