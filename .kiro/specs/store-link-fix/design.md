# Store Link Fix Bugfix Design

## Overview

The mobile app's "View on Store" functionality fails for Jeevee and Oliz products due to incorrect URL construction in the scrapers. Jeevee links return 404 Not Found errors because the URL format is missing the product template ID in the slug, and Oliz links return 403 Forbidden errors because the URL construction is untested and may be using incorrect URL patterns. This fix will correct the URL construction logic in both scrapers to generate valid, accessible product URLs while ensuring that all other store integrations (Daraz, Hukut, Neostore, Hardwarepasal) continue to work correctly.

The fix targets the URL generation logic in `jeevee_scraper.py` and `oliz_scraper.py`, implementing proper slug normalization and URL validation to ensure users can successfully navigate to product pages on these stores.

## Glossary

- **Bug_Condition (C)**: The condition that triggers the bug - when store links for Jeevee or Oliz products are clicked, they return HTTP error codes (404 for Jeevee, 403 for Oliz) instead of successfully loading the product page
- **Property (P)**: The desired behavior when store links are clicked - the device browser should successfully load the product page with HTTP 200 or 3xx status codes
- **Preservation**: Existing store link functionality for Daraz, Hukut, Neostore, and Hardwarepasal that must remain unchanged by the fix
- **slug**: The SEO-friendly URL identifier derived from the product name or seo_details, normalized to lowercase with non-alphanumeric characters replaced by hyphens
- **product_template_id**: The Jeevee-specific identifier that must be appended to the slug to form a valid product URL
- **product_url**: The complete HTTPS URL stored in the database that links to the product on the store's website
- **URL normalization**: The process of converting a product name or identifier into a valid URL slug by lowercasing and replacing special characters with hyphens

## Bug Details

### Bug Condition

The bug manifests when a user clicks "View on Store" for products from Jeevee or Oliz stores. For Jeevee products, the constructed URL follows an incorrect format that omits critical identifiers, causing the Jeevee server to return HTTP 404 Not Found. For Oliz products, the URL construction may be using an incorrect pattern or the constructed URLs are not validated before storage, leading to HTTP 403 Forbidden responses when accessed.

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input of type UserClickEvent with properties {product_url: string, platform: string}
  OUTPUT: boolean
  
  RETURN (input.platform == "jeevee" 
         AND input.product_url matches pattern "https://www.jeevee.com/products/{slug}-{template_id}"
         AND HTTP_GET(input.product_url).status_code == 404)
         OR
         (input.platform == "oliz_store"
         AND input.product_url matches pattern "https://www.olizstore.com/product/{slug}"
         AND HTTP_GET(input.product_url).status_code == 403)
END FUNCTION
```

### Examples

**Jeevee Examples:**
- **Current (Incorrect)**: A product with `label="Apple iPhone 15 Pro Max"` and `product_template_id=12345` generates URL `https://www.jeevee.com/products/apple-iphone-15-pro-max-12345` → Returns 404 Not Found
- **Expected (Correct)**: Same product should generate URL using actual `seo_details.slug` value if present, e.g., `https://www.jeevee.com/products/iphone-15-pro-max-12345` → Returns 200 OK

**Oliz Examples:**
- **Current (Incorrect)**: A product with `slug="samsung-galaxy-s24"` generates URL `https://www.olizstore.com/product/samsung-galaxy-s24` → Returns 403 Forbidden
- **Expected (Correct)**: Same product should use the exact slug from API response and validate the URL returns 200 before storage → Returns 200 OK

**Edge Cases:**
- **Missing seo_details**: A Jeevee product with no `seo_details.slug` should fallback to generating slug from `label` field → Should return 200 OK
- **Special characters in slug**: A product name with special characters like "Laptop (15.6\") - 16GB RAM!" should normalize to valid URL slug → Should return 200 OK
- **URL validation timeout**: If Oliz URL validation takes >5 seconds, the system should timeout and mark URL as unavailable rather than storing an invalid URL

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Mouse/touch clicks on "View on Store" buttons for Daraz, Hukut, Neostore, and Hardwarepasal products must continue to work exactly as before
- URL storage and retrieval must preserve the exact character sequence for all working store URLs
- The mobile app's URL resolution logic (handling relative vs absolute URLs, protocol-relative URLs) must remain unchanged
- Error handling for network failures, timeouts, and invalid URLs must continue to work as before

**Scope:**
All inputs that do NOT involve Jeevee or Oliz product URLs should be completely unaffected by this fix. This includes:
- Clicks on Daraz, Hukut, Neostore, and Hardwarepasal product URLs
- Product URL storage and retrieval from the database
- The mobile app's browser opening logic in `[id].tsx`
- Error messages displayed for network failures or timeouts

## Hypothesized Root Cause

Based on the bug description and code analysis, the most likely issues are:

1. **Jeevee: Incorrect Slug Construction**: The scraper builds the slug by combining the normalized label with the template_id, but this may not match Jeevee's actual URL pattern
   - The code currently does: `slug = f"{base_slug}-{template_id}"` where base_slug is derived from the label
   - Jeevee may require using the actual `seo_details.slug` value without modification
   - The template_id may need to be formatted differently or positioned differently in the URL

2. **Jeevee: Missing or Incorrect seo_details.slug Usage**: The fallback logic when `seo_details.slug` is empty may not match Jeevee's expected format
   - The code normalizes the label to create a slug, but Jeevee's actual slugs may follow different conventions
   - Multiple consecutive hyphens or specific character handling may differ from the current implementation

3. **Oliz: Unvalidated URL Construction**: The Oliz scraper constructs URLs using the `slug` field from the API response but does not validate these URLs
   - The URLs are stored in the database without checking if they actually return 200 OK
   - Oliz may have changed their URL pattern or the slug format may be incorrect
   - The slug from the API response may need additional processing or transformation

4. **Oliz: Incorrect URL Pattern**: The URL construction may be using the wrong base path or domain
   - Current pattern: `https://www.olizstore.com/product/{slug}`
   - Oliz may require a different base path (e.g., `/products/`, `/item/`, `/p/`)
   - The domain may have changed or require different subdomain handling

## Correctness Properties

Property 1: Bug Condition - Store Links Load Successfully

_For any_ product URL where the platform is "jeevee" or "oliz_store", the fixed scraper SHALL construct a URL that returns HTTP status code 200 or 3xx (redirects) when accessed, enabling users to successfully view the product on the store website.

**Validates: Requirements 2.1, 2.2, 2.3, 2.6, 2.7, 2.9, 2.12**

Property 2: Preservation - Non-Affected Store Links Continue Working

_For any_ product URL where the platform is NOT "jeevee" or "oliz_store" (specifically Daraz, Hukut, Neostore, Hardwarepasal), the fixed code SHALL produce exactly the same URL construction and storage behavior as the original code, preserving all existing functionality for these store integrations.

**Validates: Requirements 3.1, 3.5, 3.8, 3.11, 3.14, 3.15, 3.16**

## Fix Implementation

### Changes Required

Assuming our root cause analysis is correct:

**File 1**: `c:\Users\NITOR 5\Desktop\FYP\scrapers\jeevee\jeevee_scraper.py`

**Function**: `async_scrape_jeevee`

**Specific Changes**:
1. **Correct Slug Construction Logic**: Modify the slug generation to properly use `seo_details.slug` when available
   - Extract `seo_details.slug` from the API response
   - If `seo_details.slug` exists and is non-empty, use it directly after normalization
   - Only fallback to label-based slug generation if `seo_details.slug` is missing or empty
   - Ensure the template_id is appended in the correct format: `{slug}-{template_id}`

2. **Improve Slug Normalization**: Enhance the slug normalization to match Jeevee's expected format
   - Convert to lowercase
   - Replace all non-alphanumeric characters (except hyphens) with single hyphens
   - Remove consecutive hyphens (e.g., `---` becomes `-`)
   - Strip leading and trailing hyphens

3. **Add URL Validation**: Implement validation to verify constructed URLs are accessible
   - After constructing the product_url, perform an HTTP HEAD request to validate it returns 200 or 3xx
   - If validation fails, log a warning with the product name and URL
   - Optionally retry with alternative slug formats if the primary format fails
   - Only store URLs that pass validation

4. **Handle Edge Cases**: Add proper handling for missing or malformed data
   - Check if `product_template_id` exists before using it
   - Validate that normalized slugs are not empty after processing
   - Handle cases where API response structure differs from expected format

**File 2**: `c:\Users\NITOR 5\Desktop\FYP\scrapers\oliz\oliz_scraper.py`

**Function**: `async_scrape_oliz`

**Specific Changes**:
1. **Verify URL Pattern**: Confirm the correct Oliz URL pattern through testing
   - Test if `https://www.olizstore.com/product/{slug}` is correct or if alternative patterns work
   - Check if Oliz uses different base paths like `/products/`, `/item/`, or `/p/`
   - Document the verified correct pattern in code comments

2. **Add URL Validation**: Implement pre-storage URL validation for Oliz products
   - After constructing product_url from the slug, perform HTTP HEAD request with 5-second timeout
   - Only store URLs that return 200 or 3xx status codes
   - If validation fails with 403 or 404, log the failure and mark URL as unavailable
   - Handle timeout gracefully by marking URL as unavailable

3. **Improve Error Handling**: Add robust error handling for HTTP requests
   - Catch request exceptions (timeout, connection errors, SSL errors)
   - Log detailed error information for debugging
   - Continue processing other products even if one URL validation fails

4. **Add Retry Logic**: Implement fallback URL patterns if primary validation fails
   - If `https://www.olizstore.com/product/{slug}` returns 403, try alternative patterns
   - Document which URL patterns are attempted and their success rates
   - Store the first successfully validated URL pattern

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bug on unfixed code, then verify the fix works correctly and preserves existing behavior.

### Exploratory Bug Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix. Confirm or refute the root cause analysis. If we refute, we will need to re-hypothesize.

**Test Plan**: Write tests that construct Jeevee and Oliz URLs using the current scraper logic, then make actual HTTP requests to those URLs to observe the 404 and 403 errors. Run these tests on the UNFIXED code to observe failures and understand the root cause.

**Test Cases**:
1. **Jeevee URL Construction Test**: Extract a sample product from Jeevee's search API and construct the URL using current logic → Should demonstrate 404 error on unfixed code
2. **Jeevee Slug Normalization Test**: Test slug generation for products with special characters, multiple spaces, and Unicode characters → Should show incorrect slug format on unfixed code
3. **Oliz URL Construction Test**: Extract a sample product from Oliz's search page and construct the URL using current logic → Should demonstrate 403 error on unfixed code
4. **Oliz URL Pattern Test**: Try multiple URL pattern variations for the same Oliz product to identify the correct pattern → Should reveal which pattern works

**Expected Counterexamples**:
- Jeevee URLs constructed as `https://www.jeevee.com/products/{normalized_label}-{template_id}` return 404
- Possible causes: incorrect slug source (should use seo_details.slug), incorrect normalization, incorrect URL pattern
- Oliz URLs constructed as `https://www.olizstore.com/product/{slug}` return 403
- Possible causes: incorrect base path, incorrect slug format, missing URL validation, changed Oliz API

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds (Jeevee and Oliz products), the fixed function produces the expected behavior (valid URLs that return 200 or 3xx).

**Pseudocode:**
```
FOR ALL product WHERE product.platform IN ["jeevee", "oliz_store"] DO
  url := constructProductUrl_fixed(product)
  http_status := HTTP_GET(url).status_code
  ASSERT http_status == 200 OR (300 <= http_status < 400)
END FOR
```

**Testing Approach**: Use property-based testing to generate diverse product data and verify URL construction and validation works for all cases.

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold (Daraz, Hukut, Neostore, Hardwarepasal products), the fixed function produces the same result as the original function.

**Pseudocode:**
```
FOR ALL product WHERE product.platform NOT IN ["jeevee", "oliz_store"] DO
  url_original := constructProductUrl_original(product)
  url_fixed := constructProductUrl_fixed(product)
  ASSERT url_original == url_fixed
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across the input domain
- It catches edge cases that manual unit tests might miss
- It provides strong guarantees that behavior is unchanged for all non-buggy inputs

**Test Plan**: Observe behavior on UNFIXED code first for Daraz, Hukut, Neostore, and Hardwarepasal products, then write property-based tests capturing that behavior.

**Test Cases**:
1. **Daraz URL Preservation**: Verify Daraz product URL construction produces identical results before and after fix
2. **Hukut URL Preservation**: Verify Hukut product URL construction produces identical results before and after fix
3. **Neostore URL Preservation**: Verify Neostore product URL construction produces identical results before and after fix
4. **Hardwarepasal URL Preservation**: Verify Hardwarepasal product URL construction produces identical results before and after fix
5. **Database Storage Preservation**: Verify URLs are stored character-for-character identically for non-affected stores
6. **Mobile App URL Opening Preservation**: Verify the mobile app's `openStore` function behavior is unchanged for non-affected stores

### Unit Tests

- Test Jeevee slug normalization with various input strings (special characters, Unicode, multiple spaces, consecutive hyphens)
- Test Jeevee URL construction with present vs. missing `seo_details.slug`
- Test Jeevee URL construction with present vs. missing `product_template_id`
- Test Oliz URL construction with different slug formats
- Test URL validation logic with mocked HTTP responses (200, 3xx, 403, 404, 5xx, timeout)
- Test error handling for missing fields, malformed data, network errors
- Test slug normalization edge cases (empty strings, only special characters, very long strings)

### Property-Based Tests

- Generate random product data for Jeevee and verify all constructed URLs pass validation (return 200 or 3xx)
- Generate random product data for Oliz and verify all constructed URLs pass validation (return 200 or 3xx)
- Generate random product data for non-affected stores (Daraz, Hukut, etc.) and verify URL construction is identical to original
- Generate random strings for slug normalization and verify output is always a valid URL slug (lowercase, hyphen-separated, no leading/trailing hyphens)
- Test that URL validation properly handles network failures, timeouts, and various HTTP status codes across many scenarios

### Integration Tests

- Test full scraping workflow for Jeevee: search → parse → construct URLs → validate URLs → store in database → retrieve from database → open in mobile app
- Test full scraping workflow for Oliz: search → parse → construct URLs → validate URLs → store in database → retrieve from database → open in mobile app
- Test that clicking "View on Store" for Jeevee products successfully opens the product page in the device browser
- Test that clicking "View on Store" for Oliz products successfully opens the product page in the device browser
- Test that clicking "View on Store" for non-affected stores continues to work as before
- Test error messages display correctly when URLs fail to load (network errors, timeouts, 403/404 responses)
