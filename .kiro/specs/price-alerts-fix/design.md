# Price Alerts Feature Fix - Design

## Architecture Overview
The price alerts system consists of:
1. **Frontend**: React Native mobile app
2. **Backend API**: FastAPI endpoints
3. **Database**: PostgreSQL with price_alerts table
4. **State Management**: Local storage + API sync

## Component Design

### 1. Backend API Layer
**File**: `backend/app/routers/notifications.py`

**Endpoints**:
```
GET    /notifications/alerts       - List all user alerts
POST   /notifications/alerts       - Create new alert
PUT    /notifications/alerts/{id}  - Update alert
DELETE /notifications/alerts/{id}  - Delete alert
```

**Error Handling Strategy**:
- Catch database connection errors → Return 503 Service Unavailable
- Catch duplicate alert errors → Return 400 Bad Request with clear message
- Catch auth errors → Return 401 Unauthorized
- Catch not found errors → Return 404 Not Found
- Log all errors for debugging

### 2. Frontend API Service
**File**: `mobile/services/notifications.ts`

**Functions**:
```typescript
createPriceAlert(token, alertData): Promise<PriceAlert>
getPriceAlerts(token): Promise<PriceAlertsResponse>
deletePriceAlert(token, alertId): Promise<void>
```

**Error Parsing Strategy**:
- Parse JSON error responses properly
- Extract 'detail' field from error responses
- Provide fallback error messages
- Attach error details to Error object

### 3. Product Detail Page
**File**: `mobile/app/product/[id].tsx`

**Set Alert Flow**:
```
1. User clicks "Set Alert" button
2. Show loading spinner on button
3. Create optimistic alert in local storage
4. Call createPriceAlert API
5a. On success:
    - Remove optimistic alert
    - Show success alert with "View Alerts" button
5b. On duplicate error:
    - Show "Alert Already Exists" message
    - Provide "View Alerts" option
5c. On other error:
    - Show specific error message
    - Remove optimistic alert
```

### 4. Price Alerts Page
**File**: `mobile/app/price-alerts.tsx`

**Display Flow**:
```
1. On mount: Fetch alerts from API
2. Merge with optimistic alerts from local storage
3. Display in FlatList
4. Handle loading/error/empty states
5. Allow toggle active/inactive
6. Allow delete with confirmation
```

## Data Models

### PriceAlert (Backend)
```python
id: int
user_id: UUID
product_id: int
product_title: str
product_url: str
store_name: str
target_price: Decimal
current_price: Decimal
is_active: bool
triggered_at: datetime | None
created_at: datetime
```

### PriceAlert (Frontend)
```typescript
id: string
productName: string
currentPrice: number
targetPrice: number
isActive: boolean
createdAt: string
lastChecked: string
storeName?: string
```

## Error Scenarios & Handling

| Scenario | HTTP Status | User Message | Action |
|----------|-------------|--------------|--------|
| Database connection failed | 503 | "Service temporarily unavailable. Please try again later." | Show retry button |
| Alert already exists | 400 | "Alert Already Exists - You already have an active price alert for this product." | Show "View Alerts" button |
| Unauthorized | 401 | "Session expired. Please log in again." | Redirect to login |
| Product not found | 404 | "Product not found." | Go back |
| Network error | N/A | "Network error. Please check your connection." | Show retry button |
| Unknown error | 500 | "Something went wrong. Please try again." | Show retry button |

## Testing Strategy

### Unit Tests
- Test error parsing in API service
- Test optimistic alert creation/removal
- Test alert list merging logic

### Integration Tests
- Test end-to-end alert creation flow
- Test duplicate alert handling
- Test alert deletion flow

### Manual Testing
1. Create alert on product page → Verify success message
2. Try creating duplicate alert → Verify duplicate message
3. View alerts in Price Alerts page → Verify all alerts shown
4. Delete alert → Verify confirmation and removal
5. Test with network offline → Verify error handling
