#Requirements Document: PricePilot Home Screen

## Functional Requirements

### FR1: Header Display
**Priority**: High  
**Description**: The home screen must display a header with logo, personalized greeting, and notification bell.

**Acceptance Criteria**:
- AC1.1: Header displays "Hello, [First Name]" using the authenticated user's first name
- AC1.2: Notification bell icon shows a red badge dot when unread notifications exist
- AC1.3: Tapping notification bell navigates to notifications screen
- AC1.4: Header remains fixed at top during scroll
- AC1.5: Header height is 60px with proper padding

### FR2: Product Search
**Priority**: High  
**Description**: Users must be able to search for products using text or voice input.

**Acceptance Criteria**:
- AC2.1: Search bar displays with placeholder text "Search products..."
- AC2.2: Search bar has magnifying glass icon on left and microphone icon on right
- AC2.3: Tapping search bar navigates to dedicated search screen
- AC2.4: Tapping microphone icon activates voice search
- AC2.5: Search bar has 48px height with rounded corners (12px radius)
- AC2.6: Focus state shows indigo border (2px)

### FR3: Category Filtering
**Priority**: High  
**Description**: Users must be able to filter products by category using horizontal scrollable pills.

**Acceptance Criteria**:
- AC3.1: Display 6 category pills: Electronics, Fashion, Home & Kitchen, Beauty, Sports, Books
- AC3.2: Pills are horizontally scrollable with 4-5 visible on screen
- AC3.3: Active pill has indigo background with white text
- AC3.4: Inactive pills have gray background with gray text
- AC3.5: Tapping a pill filters products by that category
- AC3.6: "All" category is active by default
- AC3.7: Only one category can be active at a time

### FR4: Trending Products Display
**Priority**: High  
**Description**: Display a horizontal scrollable list of trending products.

**Acceptance Criteria**:
- AC4.1: Section header displays "Trending Now" with "See all" link
- AC4.2: Display minimum 5 trending products in horizontal scroll
- AC4.3: Each product card shows: image, name, current price, add button
- AC4.4: Product cards are 160px wide × 200px tall
- AC4.5: Show 2.2 cards on screen to hint at scrollability
- AC4.6: Tapping product card navigates to product detail screen
- AC4.7: Tapping "See all" navigates to full trending products list
- AC4.8: Products load from GET /products/trending endpoint

### FR5: Recommended Products Display
**Priority**: High  
**Description**: Display personalized product recommendations in horizontal carousel.

**Acceptance Criteria**:
- AC5.1: Section header displays "Recommended for You" with "See all" link
- AC5.2: Display minimum 5 recommended products in horizontal scroll
- AC5.3: Each card shows: image, name, store, current price, original price, discount, wishlist button
- AC5.4: Recommendation cards are 280px wide × 140px tall
- AC5.5: Show 1.3 cards on screen to hint at scrollability
- AC5.6: Tapping card navigates to product detail screen
- AC5.7: Tapping "See all" navigates to full recommendations list
- AC5.8: Products load from GET /products/recommended endpoint with user_id

### FR6: Wishlist Management
**Priority**: High  
**Description**: Users must be able to add/remove products to/from wishlist from home screen.

**Acceptance Criteria**:
- AC6.1: Trending product cards show "+" button to add to wishlist
- AC6.2: Recommended product cards show heart icon to toggle wishlist
- AC6.3: Tapping add/wishlist button adds product to wishlist
- AC6.4: Button shows visual feedback (checkmark or filled heart) when added
- AC6.5: Optimistic UI update occurs immediately
- AC6.6: If API call fails, revert UI and show error toast
- AC6.7: Wishlist state syncs across all product displays
- AC6.8: Haptic feedback occurs on successful add

### FR7: Bottom Tab Navigation
**Priority**: High  
**Description**: Display bottom tab navigation with 4 tabs: Home, Scan/Alarm, Wishlist, Profile.

**Acceptance Criteria**:
- AC7.1: Tab bar is fixed at bottom with 64px height
- AC7.2: Display 4 tabs with icons and labels
- AC7.3: Home tab is active by default (indigo color with indicator)
- AC7.4: Inactive tabs show gray icons and labels
- AC7.5: Tapping tab navigates to respective screen
- AC7.6: Active tab shows indigo indicator pill above icon
- AC7.7: Wishlist tab shows count badge if items > 0
- AC7.8: Haptic feedback on tab tap

### FR8: Loading States
**Priority**: Medium  
**Description**: Display appropriate loading states while data is being fetched.

**Acceptance Criteria**:
- AC8.1: Show skeleton screens for product cards during initial load
- AC8.2: Skeleton has animated shimmer effect (gray gradient)
- AC8.3: Header and search bar load immediately
- AC8.4: Categories load after 200ms
- AC8.5: Product sections load progressively
- AC8.6: Skeleton cards match dimensions of actual product cards

### FR9: Empty States
**Priority**: Medium  
**Description**: Display appropriate empty states when no data is available.

**Acceptance Criteria**:
- AC9.1: If no trending products, show icon, title "No trending products yet", subtitle
- AC9.2: If no recommendations, show icon, title "Building your recommendations", subtitle, CTA button
- AC9.3: Empty state CTA button navigates to explore/browse screen
- AC9.4: Empty states use gray color scheme (not alarming)

### FR10: Error Handling
**Priority**: Medium  
**Description**: Display appropriate error states and provide recovery options.

**Acceptance Criteria**:
- AC10.1: Network error shows wifi icon, title, subtitle, "Retry" button
- AC10.2: Server error shows alert icon, title, subtitle, "Retry" button
- AC10.3: Retry button re-fetches data for affected section
- AC10.4: Other sections remain functional if one section fails
- AC10.5: Image load errors show placeholder with product icon
- AC10.6: Wishlist errors show toast with retry option

### FR11: Pull to Refresh
**Priority**: Low  
**Description**: Users can pull down to refresh all content on home screen.

**Acceptance Criteria**:
- AC11.1: Pulling down from top triggers refresh
- AC11.2: Show indigo loading spinner during refresh
- AC11.3: Refresh all sections (trending, recommended, categories)
- AC11.4: Haptic feedback on refresh trigger
- AC11.5: Scroll position resets to top after refresh

### FR12: Scroll Behavior
**Priority**: Low  
**Description**: Implement smooth scrolling with proper nested scroll handling.

**Acceptance Criteria**:
- AC12.1: Vertical scroll for main content with momentum
- AC12.2: Horizontal scroll for category pills with momentum
- AC12.3: Horizontal scroll for product sections with momentum
- AC12.4: Nested scrolls don't interfere with each other
- AC12.5: Header shows subtle shadow when scrolled
- AC12.6: Scroll maintains 60fps performance

## Non-Functional Requirements

### NFR1: Performance
**Priority**: High  
**Description**: Home screen must load and perform smoothly.

**Acceptance Criteria**:
- AC1.1: Initial screen load completes within 2 seconds
- AC1.2: Product images load within 1 second
- AC1.3: Scroll maintains ≥55 FPS
- AC1.4: Memory usage stays below 150MB
- AC1.5: API responses cached for 5-15 minutes

### NFR2: Accessibility
**Priority**: High  
**Description**: Home screen must be accessible to users with disabilities.

**Acceptance Criteria**:
- AC2.1: All interactive elements have minimum 44px × 44px touch targets
- AC2.2: All elements have proper screen reader labels
- AC2.3: Color contrast meets WCAG AA standards (≥4.5:1)
- AC2.4: Focus order is logical (top to bottom, left to right)
- AC2.5: Screen reader announces section changes
- AC2.6: All actions can be performed without gestures (tap only)

### NFR3: Visual Design
**Priority**: High  
**Description**: Home screen must follow PricePilot design system.

**Acceptance Criteria**:
- AC3.1: Use pure white background (#FFFFFF)
- AC3.2: Use indigo primary color (#6366F1) for accents
- AC3.3: Use Inter or SF Pro Display font family
- AC3.4: Use 4px base spacing unit
- AC3.5: Use 12-16px border radius for cards
- AC3.6: Use subtle shadows for depth (elevation 1-2)
- AC3.7: Maintain consistent spacing (16px horizontal, 24px section gaps)

### NFR4: Responsiveness
**Priority**: Medium  
**Description**: Home screen must adapt to different screen sizes.

**Acceptance Criteria**:
- AC4.1: Support screen widths from 320px to 428px
- AC4.2: Product cards scale proportionally
- AC4.3: Text remains readable at all sizes
- AC4.4: Touch targets remain ≥44px at all sizes
- AC4.5: Layout doesn't break on small screens (iPhone SE)
- AC4.6: Layout utilizes space on large screens (iPhone Pro Max)

### NFR5: Offline Support
**Priority**: Low  
**Description**: Home screen should handle offline scenarios gracefully.

**Acceptance Criteria**:
- AC5.1: Show cached data if available when offline
- AC5.2: Display offline indicator in header
- AC5.3: Disable actions that require network
- AC5.4: Queue wishlist actions for sync when online
- AC5.5: Show appropriate message when no cached data

### NFR6: Analytics
**Priority**: Low  
**Description**: Track user interactions for product improvement.

**Acceptance Criteria**:
- AC6.1: Log screen view event on mount
- AC6.2: Log product card taps with product ID
- AC6.3: Log category filter selections
- AC6.4: Log wishlist add/remove actions
- AC6.5: Log "See all" link taps
- AC6.6: Log search bar taps
- AC6.7: Log error occurrences with error type

## Data Requirements

### DR1: User Data
**Source**: Authentication context  
**Fields**:
- `user_id`: string (UUID)
- `first_name`: string
- `email`: string
- `has_unread_notifications`: boolean

### DR2: Product Data
**Source**: GET /products/trending, GET /products/recommended  
**Fields**:
- `id`: string (UUID)
- `name`: string (max 100 chars)
- `price`: number (positive float)
- `original_price`: number | null
- `discount`: number | null (0-100)
- `image_url`: string (valid URL)
- `store`: string
- `category`: string
- `in_wishlist`: boolean
- `trending_rank`: number | null

### DR3: Category Data
**Source**: GET /categories  
**Fields**:
- `id`: string
- `name`: string
- `icon`: string | null
- `product_count`: number

### DR4: Wishlist Data
**Source**: POST /wishlist/add, DELETE /wishlist/remove  
**Fields**:
- `product_id`: string (UUID)
- `user_id`: string (UUID)
- `added_at`: timestamp

## API Requirements

### API1: Get Trending Products
**Endpoint**: GET /products/trending  
**Query Params**:
- `limit`: number (default: 10, max: 50)

**Response**: 200 OK
```json
{
  "products": [
    {
      "id": "uuid",
      "name": "string",
      "price": 99.99,
      "original_price": 129.99,
      "discount": 23,
      "image_url": "https://...",
      "store": "Amazon",
      "category": "Electronics",
      "in_wishlist": false,
      "trending_rank": 1
    }
  ],
  "total": 50
}
```

**Error Responses**:
- 500: Server error
- 503: Service unavailable

### API2: Get Recommended Products
**Endpoint**: GET /products/recommended  
**Query Params**:
- `user_id`: string (UUID, required)
- `limit`: number (default: 10, max: 50)

**Response**: 200 OK
```json
{
  "products": [
    {
      "id": "uuid",
      "name": "string",
      "price": 99.99,
      "original_price": 129.99,
      "discount": 23,
      "image_url": "https://...",
      "store": "Amazon",
      "category": "Electronics",
      "in_wishlist": false,
      "recommendation_score": 0.95
    }
  ],
  "total": 100
}
```

**Error Responses**:
- 401: Unauthorized
- 500: Server error

### API3: Get Categories
**Endpoint**: GET /categories  
**Query Params**: None

**Response**: 200 OK
```json
{
  "categories": [
    {
      "id": "electronics",
      "name": "Electronics",
      "icon": "cpu",
      "product_count": 1234
    }
  ]
}
```

**Error Responses**:
- 500: Server error

### API4: Add to Wishlist
**Endpoint**: POST /wishlist/add  
**Headers**: Authorization: Bearer {token}  
**Body**:
```json
{
  "product_id": "uuid"
}
```

**Response**: 201 Created
```json
{
  "success": true,
  "message": "Product added to wishlist"
}
```

**Error Responses**:
- 400: Invalid product ID
- 401: Unauthorized
- 409: Already in wishlist
- 500: Server error

### API5: Remove from Wishlist
**Endpoint**: DELETE /wishlist/remove  
**Headers**: Authorization: Bearer {token}  
**Body**:
```json
{
  "product_id": "uuid"
}
```

**Response**: 200 OK
```json
{
  "success": true,
  "message": "Product removed from wishlist"
}
```

**Error Responses**:
- 400: Invalid product ID
- 401: Unauthorized
- 404: Not in wishlist
- 500: Server error

## Dependencies

### External Libraries
- `expo-router`: ^2.0.0 - File-based routing
- `react-native-reanimated`: ^3.0.0 - Animations
- `react-native-gesture-handler`: ^2.0.0 - Gestures
- `@react-native-async-storage/async-storage`: ^1.0.0 - Local storage
- `react-query`: ^3.0.0 - Server state management
- `zod`: ^3.0.0 - Schema validation

### Internal Dependencies
- Authentication context (user data)
- API client (fetch wrapper)
- Design system components
- Navigation configuration

## Constraints

### Technical Constraints
- Must work on iOS 13+ and Android 8+
- Must support React Native 0.72+
- Must use Expo SDK 54
- Must use TypeScript
- Must use fetch (no axios)

### Business Constraints
- Must load within 2 seconds on 4G connection
- Must support minimum 100 products per section
- Must cache data to reduce API calls
- Must track analytics for product decisions

### Design Constraints
- Must follow existing auth screen design language
- Must use indigo color scheme (#6366F1)
- Must use whitish theme (white background)
- Must maintain WCAG AA accessibility standards

## Success Metrics

### User Engagement
- **Target**: 80% of users interact with trending section
- **Target**: 60% of users interact with recommended section
- **Target**: 40% of users add products to wishlist from home screen
- **Target**: Average session time ≥2 minutes

### Performance
- **Target**: 95% of loads complete within 2 seconds
- **Target**: 99% uptime for API endpoints
- **Target**: <1% error rate for wishlist actions
- **Target**: 60 FPS scroll performance on 90% of devices

### Accessibility
- **Target**: 100% of interactive elements have proper labels
- **Target**: 100% of color contrasts meet WCAG AA
- **Target**: 100% of touch targets ≥44px

## Out of Scope

The following features are explicitly out of scope for this iteration:

1. **Search Implementation**: Search screen and functionality (separate feature)
2. **Voice Search**: Voice input processing (future enhancement)
3. **Product Detail Screen**: Full product information view (separate feature)
4. **Notifications Screen**: Notification list and management (separate feature)
5. **Category Filter Backend**: Server-side category filtering (use client-side for now)
6. **Price Alerts**: Price drop notifications (future enhancement)
7. **Social Features**: Sharing, reviews, ratings (future enhancement)
8. **AR Preview**: Augmented reality product view (future enhancement)
9. **Personalization Algorithm**: ML-based recommendations (use simple algorithm for now)
10. **Offline Mode**: Full offline functionality (only basic caching)

## Assumptions

1. **Backend APIs**: All required endpoints are available and functional
2. **Product Data**: Sufficient product data exists for trending and recommendations
3. **Image CDN**: Product images are hosted on reliable CDN
4. **Authentication**: User is authenticated before accessing home screen
5. **Network**: Users have stable internet connection (4G or better)
6. **Device**: Users have modern devices (iOS 13+, Android 8+)
7. **Permissions**: App has necessary permissions (network, storage)
8. **Categories**: Category list is static (doesn't change frequently)

## Risks & Mitigations

### Risk 1: Slow API Response
**Impact**: High - Poor user experience  
**Probability**: Medium  
**Mitigation**:
- Implement aggressive caching (5-15 minutes)
- Show skeleton screens immediately
- Load sections progressively
- Implement timeout and retry logic

### Risk 2: Large Image Sizes
**Impact**: Medium - Slow load times, high data usage  
**Probability**: High  
**Mitigation**:
- Use WebP format with JPEG fallback
- Implement image resizing on backend
- Use lazy loading for off-screen images
- Set memory and disk cache limits

### Risk 3: Inconsistent Product Data
**Impact**: Medium - UI breaks or displays incorrectly  
**Probability**: Medium  
**Mitigation**:
- Validate all API responses with Zod schemas
- Provide fallback values for missing fields
- Log validation errors to analytics
- Show placeholder for missing images

### Risk 4: Wishlist Sync Issues
**Impact**: Low - User confusion about wishlist state  
**Probability**: Low  
**Mitigation**:
- Implement optimistic updates
- Revert on error with clear feedback
- Queue actions for retry
- Sync wishlist state on app resume

### Risk 5: Performance on Low-End Devices
**Impact**: Medium - Poor experience for some users  
**Probability**: Medium  
**Mitigation**:
- Optimize FlatList configuration
- Use removeClippedSubviews on Android
- Limit number of rendered items
- Profile performance on low-end devices
- Consider reducing animations on slow devices
