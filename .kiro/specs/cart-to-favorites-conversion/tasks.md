# Implementation Plan: Cart to Favorites Conversion

## Overview

This implementation plan converts the PricePilot shopping cart system to a Favorites/Saved Products feature. The approach follows a three-phase strategy:

1. **Backend Foundation**: Migrate database schema, create new endpoints, and maintain backward compatibility
2. **Mobile App Refactoring**: Rename components, update UI terminology, and migrate local storage
3. **Integration & Cleanup**: Wire everything together, test thoroughly, and remove deprecated code

The implementation prioritizes data preservation and zero downtime, with a 14-day deprecation period for backward compatibility.

## Tasks

- [ ] 1. Set up backend database migration and models
  - [ ] 1.1 Create database migration script
    - Write Alembic migration to rename `shopping_cart` table to `favorites` (if exists)
    - Rename `cart_items` table to `favorite_items` (if exists)
    - Drop `quantity` column from `favorite_items` table
    - Create new tables with proper schema if they don't exist
    - Add all required indexes for performance
    - Ensure migration is atomic (single transaction with rollback capability)
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 3.1_

  - [ ] 1.2 Create Python models for favorites
    - Create `backend/app/models/favorites.py` with `Favorite` and `FavoriteItem` SQLAlchemy models
    - Define relationships between favorites, favorite_items, and users
    - Remove quantity field from model definition
    - Add proper column types, constraints, and defaults
    - _Requirements: 1.3, 1.4, 1.5, 1.6, 3.1, 3.4_

  - [ ]* 1.3 Write unit tests for database models
    - Test model creation and relationships
    - Test that quantity field is not present
    - Test foreign key constraints and cascading deletes
    - _Requirements: 1.3, 3.1, NFR4.1, NFR4.2_

- [ ] 2. Implement backend API endpoints
  - [ ] 2.1 Create favorites router with new endpoints
    - Create `backend/app/routers/favorites.py` 
    - Implement `POST /favorites/add` endpoint
    - Implement `DELETE /favorites/remove` endpoint
    - Implement `GET /favorites` endpoint
    - Add JWT authentication to all endpoints
    - Implement duplicate detection (return 409 if product already exists)
    - Add proper error handling and validation using Pydantic
    - _Requirements: 2.1, 2.2, 2.3, 2.5, 2.6, 2.7, 2.8, 2.9, 3.2, 3.4_

  - [ ]* 2.2 Write property test for favorites addition idempotence
    - **Property 1: Favorites Addition Idempotence**
    - **Validates: Requirements 5.6, 7.1**
    - Generate random valid products and verify adding same product multiple times results in exactly one entry
    - Test with various product data combinations

  - [ ] 2.3 Create deprecated cart router for backward compatibility
    - Create `backend/app/routers/cart.py` (deprecated)
    - Forward `POST /cart/add` to `POST /favorites/add`
    - Forward `DELETE /cart/remove` to `DELETE /favorites/remove`
    - Forward `GET /cart` to `GET /favorites`
    - Add deprecation headers (Deprecation, Sunset, Link)
    - Return 410 Gone for checkout-related endpoints
    - _Requirements: 2.10, 4.1, 4.2, 4.3, 4.4, NFR1.1, NFR1.2, NFR1.3, NFR1.4_

  - [ ]* 2.4 Write property test for API backward compatibility
    - **Property 5: API Backward Compatibility During Deprecation**
    - **Validates: Requirements 2.10, NFR1.1-NFR1.5**
    - Generate random cart endpoint requests and verify they return same 2xx responses as favorites endpoints
    - Test all deprecated cart endpoints forward correctly

  - [ ]* 2.5 Write unit tests for favorites endpoints
    - Test successful product addition (201 Created)
    - Test duplicate addition (409 Conflict)
    - Test product removal (200 OK)
    - Test get favorites list (200 OK)
    - Test authentication failures (401 Unauthorized)
    - Test removing non-existent item (404 Not Found)
    - _Requirements: 2.5, 2.6, 2.7, 2.8, 2.9, NFR4.1_

- [ ] 3. Checkpoint - Ensure backend tests pass
  - Run all backend unit tests and property tests
  - Verify database migration works on test database
  - Test deprecated cart endpoints forward correctly
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 4. Implement mobile storage migration
  - [ ] 4.1 Create mobile storage migration logic
    - Add migration function in `mobile/context/FavoritesContext.tsx`
    - Check for existing `pricepilot_cart` key in AsyncStorage
    - Read cart items and remove quantity field from each
    - Write transformed items to `pricepilot_favorites` key
    - Delete old `pricepilot_cart` key after successful migration
    - Add retry logic for failed migrations
    - Log migration status for debugging
    - _Requirements: 5.8, 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7_

  - [ ]* 4.2 Write property test for migration completeness
    - **Property 2: Migration Completeness**
    - **Validates: Requirements 13.1-13.7, 14.1-14.7**
    - Generate random cart items with quantity fields
    - Verify all product data fields are preserved except quantity
    - Test migration produces valid FavoriteItem objects

  - [ ]* 4.3 Write unit tests for storage migration
    - Test migration with cart data present
    - Test migration with no cart data
    - Test migration failure and retry logic
    - Test quantity field removal
    - _Requirements: 14.1-14.7, NFR4.3_

- [ ] 5. Refactor mobile context and state management
  - [ ] 5.1 Rename CartContext to FavoritesContext
    - Rename `mobile/context/CartContext.tsx` to `mobile/context/FavoritesContext.tsx`
    - Rename `CartProvider` to `FavoritesProvider`
    - Rename `useCart` hook to `useFavorites`
    - Rename `CartItem` interface to `FavoriteItem`
    - Remove `quantity` property from `FavoriteItem` interface
    - Remove `updateQuantity` function
    - Remove `totalPrice` computed property
    - Update STORAGE_KEY from 'pricepilot_cart' to 'pricepilot_favorites'
    - Update all import statements throughout the mobile app
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.9, 5.10_

  - [ ]* 5.2 Write unit tests for FavoritesContext
    - Test addItem adds product without quantity field
    - Test addItem prevents duplicate products (idempotence)
    - Test removeItem removes product correctly
    - Test clearFavorites empties the list
    - Test itemCount computation
    - Test migrateFromCart removes quantity field
    - _Requirements: 5.1-5.10, NFR4.3_

- [ ] 6. Update mobile API service layer
  - [ ] 6.1 Rename API service functions
    - Rename `addToCart` to `addToFavorites` in API service
    - Rename `removeFromCart` to `removeFromFavorites`
    - Rename `getCart` to `getFavorites`
    - Update endpoint URLs from `/cart/*` to `/favorites/*`
    - Remove quantity parameter from request payloads
    - Add handling for 410 Gone responses from deprecated endpoints
    - Update response type definitions
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

  - [ ]* 6.2 Write unit tests for API service
    - Test addToFavorites calls correct endpoint
    - Test removeFromFavorites calls correct endpoint
    - Test getFavorites returns favorites without quantity
    - Test error handling for network failures
    - _Requirements: 9.1-9.6, NFR4.3_

- [ ] 7. Checkpoint - Ensure mobile data layer tests pass
  - Run all mobile context and API service tests
  - Verify migration logic works correctly
  - Test that quantity fields are removed everywhere
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Update mobile screens and navigation
  - [ ] 8.1 Rename cart screen to favorites screen
    - Rename `mobile/app/(tabs)/cart.tsx` to `mobile/app/(tabs)/favorites.tsx`
    - Update tab navigation label from "Cart" to "Favorites"
    - Update tab navigation icon from "cart" to "heart" or "bookmark"
    - Update screen header from "Shopping Cart" to "Favorites"
    - Update route references throughout the app
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

  - [ ] 8.2 Update empty state UI
    - Change empty state icon from "cart-outline" to "heart-outline"
    - Update empty state message to "Your favorites list is empty"
    - Add subtitle "Save products to compare prices later"
    - Update styling and layout as needed
    - _Requirements: 6.5, 6.6, 6.7_

- [ ] 9. Update mobile UI components and terminology
  - [ ] 9.1 Update product card and detail page buttons
    - Change "Add to Cart" buttons to "Save" or "Add to Favorites"
    - Update button icons from "cart-outline" to "heart-outline" or "bookmark-outline"
    - Update DealCard component button text
    - Update product detail page button text
    - Show filled heart icon when product is in favorites
    - Update toast messages to "Saved!" or "Added to Favorites!"
    - _Requirements: 7.1, 7.2, 7.5, 7.6, 7.7, 7.8_

  - [ ] 9.2 Remove quantity controls and checkout UI
    - Remove quantity increment/decrement controls (+/-) from favorite items
    - Remove quantity display from favorite items
    - Remove "Check Out" button from favorites screen
    - Remove subtotal and total price displays
    - Remove item selection checkboxes
    - Remove "Select All" checkbox
    - Update display to show "X items saved" instead of total price
    - _Requirements: 7.3, 7.4, 8.1, 8.2, 8.3, 8.4, 8.5, 8.7_

  - [ ] 9.3 Implement store grouping display
    - Group favorite items by storeName
    - Display store name as section header for each group
    - Show store logo or icon next to store name (if available)
    - Maintain alphabetical ordering of stores
    - Display product count for each store "(3 items)"
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_

  - [ ]* 9.4 Write property test for store grouping consistency
    - **Property 3: Store Grouping Consistency**
    - **Validates: Requirements 10.1-10.6**
    - Generate random sets of favorite items with various store names
    - Verify grouping produces correct partitions (no duplicates, no missing items)
    - Verify all items in a group have identical storeName

  - [ ] 9.5 Add "Compare Prices" button
    - Add "Compare Prices" button at bottom of favorites screen
    - Enable button only when 2 or more products exist
    - Style with indigo background, white text, 48px height
    - Wire button to navigate to comparison screen (pass favorite items)
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6_

  - [ ]* 9.6 Write property test for empty state invariant
    - **Property 4: Empty State Invariant**
    - **Validates: Requirements 6.7, 11.2**
    - Generate favorites lists with 0 items
    - Verify empty state view is displayed
    - Verify "Compare Prices" button is disabled

  - [ ]* 9.7 Write integration tests for favorites screen
    - Test adding product to favorites from product detail page
    - Test removing product from favorites
    - Test empty state display
    - Test store grouping display
    - Test "Compare Prices" button enable/disable
    - _Requirements: 6.1-6.7, 7.1-7.8, 8.1-8.7, 10.1-10.6, 11.1-11.6, NFR4.4_

- [ ] 10. Checkpoint - Ensure mobile UI tests pass
  - Run all mobile screen and component tests
  - Verify empty state displays correctly
  - Verify store grouping works properly
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 11. Run database migration in staging environment
  - [ ] 11.1 Execute database migration script
    - Create backup of production database in staging
    - Run Alembic migration script
    - Verify tables are renamed correctly
    - Verify all data is preserved (check row counts)
    - Verify indexes are created properly
    - Test rollback procedure
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7, NFR2.1, NFR2.2, NFR2.3, NFR2.4_

  - [ ]* 11.2 Write integration tests for database migration
    - Test migration renames tables correctly
    - Test migration preserves all data
    - Test migration rolls back on error
    - Test quantity column is dropped
    - _Requirements: 13.1-13.7, NFR2.1-NFR2.4, NFR4.2_

- [ ] 12. Update documentation and comments
  - [ ] 12.1 Update code comments and documentation
    - Update all code comments referencing "cart" to "favorites" in mobile app
    - Update all code comments referencing "cart" to "favorites" in backend
    - Update API documentation (OpenAPI/Swagger spec)
    - Update README files with new endpoint names
    - Update component JSDoc comments
    - Add migration guide for developers
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_

- [ ] 13. End-to-end testing and validation
  - [ ]* 13.1 Write E2E tests for complete favorites flow
    - Test complete user flow: add to favorites → view favorites → remove
    - Test migration flow on first launch after update
    - Test deprecated endpoints work during deprecation period
    - Test favorites sync between local storage and backend
    - _Requirements: All, NFR4.5_

  - [ ] 13.2 Manual testing and validation
    - Test on iOS device
    - Test on Android device
    - Verify UI changes look correct
    - Test backward compatibility with old app versions
    - Verify performance meets NFR3 targets
    - Test accessibility features (screen readers, touch targets)
    - _Requirements: All, NFR3.1-NFR3.5, NFR5.1-NFR5.5, NFR6.1-NFR6.5_

- [ ] 14. Final checkpoint and deployment preparation
  - Run complete test suite (unit, property, integration, E2E)
  - Verify all acceptance criteria are met
  - Review code changes with team
  - Prepare deployment plan and rollback procedure
  - Update app store release notes
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional test tasks and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties from the design document
- Unit tests and integration tests validate specific behaviors and edge cases
- The implementation maintains backward compatibility during a 14-day deprecation period
- Data migration is atomic and reversible to ensure zero data loss
- The mobile app performs automatic local storage migration on first launch after update
- All database operations should use transactions with proper error handling
- UI changes maintain the existing indigo color scheme and familiar layout
- Backend endpoints require JWT authentication for all operations
- The "Compare Prices" button is only enabled when 2+ products are saved
- Store grouping maintains alphabetical order and displays product counts

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2"] },
    { "id": 1, "tasks": ["1.3", "2.1"] },
    { "id": 2, "tasks": ["2.2", "2.3", "4.1"] },
    { "id": 3, "tasks": ["2.4", "2.5", "4.2", "4.3", "5.1"] },
    { "id": 4, "tasks": ["5.2", "6.1"] },
    { "id": 5, "tasks": ["6.2", "8.1", "8.2"] },
    { "id": 6, "tasks": ["9.1", "9.2", "9.3"] },
    { "id": 7, "tasks": ["9.4", "9.5", "9.6", "9.7", "11.1"] },
    { "id": 8, "tasks": ["11.2", "12.1"] },
    { "id": 9, "tasks": ["13.1", "13.2"] }
  ]
}
```
