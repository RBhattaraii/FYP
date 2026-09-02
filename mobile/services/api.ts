/**
 * API Service Layer
 * Handles all backend API calls for PricePilot app
 */

import { API_URL, fetchWithTimeout } from '../constants/api';

// ============================================================================
// TypeScript Interfaces (matching backend Pydantic models)
// ============================================================================

export interface Product {
  id?: number;
  title: string;
  price: number;
  original_price?: number;
  discount_percent?: number;
  image_url: string;
  store_name: string;
  product_url: string;
  category?: string;
  store_count?: number;
  alternative_offers?: Array<{
    store_name: string;
    price: number;
    original_price?: number;
    discount_percent?: number;
    product_url: string;
    image_url: string;
  }>;
}

export interface HomeScreenResponse {
  best_deals: Product[];
  top_price_drops: Product[];
  tech_gadgets?: Product[];
  audio_essentials?: Product[];
  home_appliances?: Product[];
}

export interface SearchResponse {
  request_id: string;
  query: string;
  tier: number;
  is_complete: boolean;
  results: Product[];
  results_count: number;
  tier1_platforms?: string[];
  message: string;
  page?: number;
  limit?: number;
  total_pages?: number;
  total_results?: number;
}

export interface SearchStatusResponse {
  request_id: string;
  is_complete: boolean;
  new_results_count: number;
  new_results: Product[];
  message: string;
}

export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  phone?: string;
  created_at: string;
}

export interface UpdateProfileRequest {
  full_name?: string;
  phone?: string;
}

export interface UpdateProfileResponse extends UserProfile {
  message: string;
}

// Compare API Interfaces
export interface ComparisonItem {
  id: number;
  product_id: number;
  product_title: string;
  product_price: number;
  product_image_url?: string;
  product_url: string;
  store_name: string;
  category?: string;
  added_at: string;
}

export interface ProductComparison {
  id: number;
  user_id: string;
  comparison_name: string;
  created_at: string;
  updated_at: string;
  items: ComparisonItem[];
}

export interface QuickCompareResponse {
  product1: ComparisonItem;
  product2: ComparisonItem;
  comparison_table: {
    products: Array<{
      id: number;
      title: string;
      price: number;
      image_url?: string;
      store: string;
      category?: string;
      url: string;
    }>;
    price_comparison: {
      lowest_price: number;
      highest_price: number;
      price_difference: number;
      savings: number;
    };
    store_comparison: string[];
    category_comparison: string[];
  };
  message: string;
}

export interface ComparisonListResponse {
  comparisons: ProductComparison[];
  total_comparisons: number;
}

// Price History API Interfaces
export interface PriceHistoryPoint {
  price: number;
  date: string;
}

export interface PriceHistoryStatistics {
  lowest_price: number;
  highest_price: number;
  average_price: number;
  price_trend: 'up' | 'down' | 'stable' | 'insufficient_data' | 'no_history';
  data_points: number;
}

export interface PriceHistoryResponse {
  product_id: number;
  product_title: string;
  current_price: number;
  original_price?: number;
  store_name: string;
  price_history: PriceHistoryPoint[];
  statistics: PriceHistoryStatistics;
  realtime_scraping?: boolean;
  forecast?: {
    predicted_price_15_days: number;
    predicted_price_30_days: number;
    trend_direction: 'up' | 'down' | 'stable';
    confidence_score: number;
    recommendation: 'Buy Now' | 'Wait' | 'Neutral';
    explanation: string;
  };
}

// ============================================================================
// API Functions
// ============================================================================

/**
 * Fetch home screen products (curated best deals and price drops)
 * Endpoint: GET /products/home
 */
export async function fetchHomeScreenProducts(): Promise<HomeScreenResponse> {
  try {
    const response = await fetchWithTimeout(`${API_URL}/products/home`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error: any) {
    console.error('Failed to fetch home screen products:', error);
    throw new Error(error.message || 'Failed to load products. Please try again.');
  }
}

/**
 * Fetch single product detail by ID
 * Endpoint: GET /products/{id}
 */
export async function fetchProductDetail(productId: string): Promise<Product> {
  try {
    const encodedId = encodeURIComponent(productId);
    const response = await fetchWithTimeout(`${API_URL}/products/${encodedId}`);
    
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Product not found');
      }
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error: any) {
    console.error('Failed to fetch product detail:', error);
    throw new Error(error.message || 'Failed to load product details.');
  }
}

/**
 * Fetch user profile (requires authentication token)
 * Endpoint: GET /auth/me
 */
export async function fetchUserProfile(token?: string): Promise<UserProfile> {
  try {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    // Add token if provided, otherwise will be handled by auth middleware
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetchWithTimeout(`${API_URL}/auth/me`, {
      headers,
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error: any) {
    console.error('Failed to fetch user profile:', error);
    throw new Error(error.message || 'Failed to load user profile.');
  }
}

/**
 * Update user profile (requires authentication token)
 * Endpoint: PUT /auth/me
 */
export async function updateUserProfile(
  token: string,
  profileData: UpdateProfileRequest
): Promise<UpdateProfileResponse> {
  try {
    const response = await fetchWithTimeout(`${API_URL}/auth/me`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(profileData),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Failed to update profile' }));
      throw new Error(errorData.detail || 'Failed to update profile');
    }
    
    const data = await response.json();
    return data;
  } catch (error: any) {
    console.error('Failed to update user profile:', error);
    throw error;
  }
}

/**
 * Search products with tiered scraping strategy
 * Endpoint: GET /products/search?q={query}
 * Returns Tier 1 results immediately (~2s), continues scraping in background
 */
export async function searchProducts(
  query: string, 
  page: number = 1, 
  limit: number = 50,
  sortBy: string = 'relevance',
  isCategory: boolean = false
): Promise<SearchResponse> {
  try {
    const encodedQuery = encodeURIComponent(query);
    const categoryParam = isCategory ? '&is_category=true' : '';
    const response = await fetchWithTimeout(
      `${API_URL}/products/search/db?q=${encodedQuery}&page=${page}&limit=${limit}&sort_by=${sortBy}${categoryParam}`,
      {},
      60000 // 60 second timeout for search to accommodate slow live scraper responses
    );
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error: any) {
    console.error('Failed to search products:', error);
    throw new Error(error.message || 'Search failed. Please try again.');
  }
}

/**
 * Poll for Tier 2 search results (background scraping completion)
 * Endpoint: GET /products/search/status?request_id={requestId}
 */
export async function pollSearchStatus(requestId: string, query: string): Promise<SearchStatusResponse> {
  try {
    const encodedQuery = encodeURIComponent(query);
    const response = await fetchWithTimeout(
      `${API_URL}/products/search/status?request_id=${requestId}&query=${encodedQuery}`
    );
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error: any) {
    console.error('Failed to poll search status:', error);
    throw new Error(error.message || 'Failed to check search status.');
  }
}

/**
 * Login user and get authentication token
 * Endpoint: POST /auth/login
 */
export async function login(email: string, password: string): Promise<{ access_token: string; token_type: string }> {
  try {
    const response = await fetchWithTimeout(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(errorData.detail || 'Invalid credentials');
    }
    
    const data = await response.json();
    return data;
  } catch (error: any) {
    console.error('Login failed:', error);
    throw error;
  }
}

/**
 * Register new user
 * Endpoint: POST /auth/register
 */
export async function register(email: string, password: string, fullName: string): Promise<{ message: string }> {
  try {
    const response = await fetchWithTimeout(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email,
        password,
        full_name: fullName,
      }),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Registration failed' }));
      throw new Error(errorData.detail || 'Failed to register');
    }
    
    const data = await response.json();
    return data;
  } catch (error: any) {
    console.error('Registration failed:', error);
    throw error;
  }
}

/**
 * Change user password
 * Endpoint: POST /auth/change-password
 */
export async function changePassword(token: string, currentPassword: string, newPassword: string): Promise<{ message: string }> {
  try {
    const response = await fetchWithTimeout(`${API_URL}/auth/change-password`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Failed to change password' }));
      throw new Error(errorData.detail || 'Failed to change password');
    }
    
    return await response.json();
  } catch (error: any) {
    console.error('Change password failed:', error);
    throw error;
  }
}

/**
 * Delete user account
 * Endpoint: POST /auth/delete-account
 */
export async function deleteAccount(token: string, password: string): Promise<{ message: string }> {
  try {
    const response = await fetchWithTimeout(`${API_URL}/auth/delete-account`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ password }),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Failed to delete account' }));
      throw new Error(errorData.detail || 'Failed to delete account');
    }
    
    return await response.json();
  } catch (error: any) {
    console.error('Delete account failed:', error);
    throw error;
  }
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Progressive search with polling
 * Returns Tier 1 results immediately, then polls for Tier 2 results
 * 
 * @param query - Search query string
 * @param onTier1Results - Callback when Tier 1 results are ready
 * @param onTier2Update - Callback when Tier 2 results arrive (may be called multiple times)
 * @param onComplete - Callback when all scraping is complete
 * @param maxPolls - Maximum number of polls (default: 6 = 12 seconds)
 */
export async function progressiveSearch(
  query: string,
  onTier1Results: (results: SearchResponse) => void,
  onTier2Update: (newResults: Product[], allResults: Product[]) => void,
  onComplete: () => void,
  maxPolls: number = 6,
  page: number = 1,
  limit: number = 50,
  sortBy: string = 'relevance'
): Promise<void> {
  try {
    // Step 1: Get Tier 1 results
    const tier1Response = await searchProducts(query, page, limit, sortBy);
    onTier1Results(tier1Response);
    
    if (tier1Response.is_complete) {
      // All results already available (likely from cache)
      onComplete();
      return;
    }
    
    // Step 2: Poll for Tier 2 results
    const requestId = tier1Response.request_id;
    let pollCount = 0;
    let allResults = [...tier1Response.results];
    
    const pollInterval = setInterval(async () => {
      try {
        pollCount++;
        const statusResponse = await pollSearchStatus(requestId, query);
        
        if (statusResponse.new_results_count > 0) {
          // New results available
          allResults = [...allResults, ...statusResponse.new_results];
          onTier2Update(statusResponse.new_results, allResults);
        }
        
        if (statusResponse.is_complete || pollCount >= maxPolls) {
          clearInterval(pollInterval);
          onComplete();
        }
      } catch (error) {
        console.error('Polling error:', error);
        clearInterval(pollInterval);
        onComplete();
      }
    }, 2000); // Poll every 2 seconds
    
  } catch (error) {
    console.error('Progressive search failed:', error);
    throw error;
  }
}

// ============================================================================
// EXPLANATION FOR VIVA
// ============================================================================

/*
Q: Why use TypeScript interfaces that match backend Pydantic models?
A: This ensures type safety across the entire stack. The frontend knows
   exactly what data structure to expect from the backend. If the backend
   changes, TypeScript will catch type mismatches at compile time.

Q: What is the purpose of fetchWithTimeout?
A: It prevents requests from hanging indefinitely if the backend is slow
   or unresponsive. After 10 seconds (or custom timeout), it aborts the
   request and throws an error, allowing the app to show error UI.

Q: How does the progressive search function work?
A: It implements the tiered search UX:
   1. Calls searchProducts() to get Tier 1 results (~2s, 3 platforms)
   2. Shows these results immediately via onTier1Results callback
   3. If not complete, polls every 2 seconds for Tier 2 results
   4. Updates UI with new results via onTier2Update callback
   5. Stops after 6 polls (12s) or when complete
   This gives users fast feedback while loading more results in background.

Q: Why separate API calls from component logic?
A: Separation of concerns:
   - API service handles HTTP communication, error handling, data fetching
   - Components handle UI rendering and user interactions
   - Makes code more maintainable and testable
   - API functions can be reused across multiple components

Q: What happens if the backend is not running?
A: fetchWithTimeout will throw a timeout error after 10 seconds.
   Components catch this error and display user-friendly error messages
   like "Unable to connect. Make sure backend is running."
*/

// ============================================================================
// Compare API Functions
// ============================================================================

/**
 * Quick comparison between two products
 * Endpoint: POST /compare/quick
 */
export async function quickCompareProducts(
  token: string, 
  product1Id: number, 
  product2Id: number
): Promise<QuickCompareResponse> {
  try {
    const response = await fetchWithTimeout(`${API_URL}/compare/quick`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        product1_id: product1Id,
        product2_id: product2Id,
      }),
    });
    
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      try {
        const errorData = await response.json();
        if (errorData.detail) errorMessage = errorData.detail;
      } catch (e) {}
      throw new Error(errorMessage);
    }
    
    const data = await response.json();
    return data;
  } catch (error: any) {
    console.error('Failed to compare products:', error);
    throw new Error(error.message || 'Failed to compare products.');
  }
}

/**
 * Search products for comparison
 * Endpoint: POST /compare/search
 */
export async function searchForComparison(
  token: string,
  query: string,
  excludeProductIds: number[] = [],
  limit: number = 20
): Promise<{ query: string; results: Product[]; count: number }> {
  try {
    const response = await fetchWithTimeout(`${API_URL}/compare/search`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,

        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        exclude_product_ids: excludeProductIds,
        limit,
      }),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error: any) {
    console.error('Failed to search for comparison:', error);
    throw new Error(error.message || 'Failed to search products.');
  }
}

/**
 * Create and save comparison
 * Endpoint: POST /compare/create
 */
export async function createComparison(
  token: string,
  name: string,
  productIds: number[] = []
): Promise<any> {
  try {
    const response = await fetchWithTimeout(`${API_URL}/compare/create`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,

        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        comparison_name: name,
        product_ids: productIds,
      }),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error: any) {
    console.error('Failed to create comparison:', error);
    throw new Error(error.message || 'Failed to save comparison.');
  }
}

/**
 * Get user's saved comparisons
 * Endpoint: GET /compare/
 */
export async function getUserComparisons(token: string): Promise<ComparisonListResponse> {
  try {
    const timestamp = new Date().getTime();
    const response = await fetchWithTimeout(`${API_URL}/compare/?t=${timestamp}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error: any) {
    console.error('Failed to fetch user comparisons:', error);
    throw new Error(error.message || 'Failed to load comparisons.');
  }
}

// ============================================================================
// Price History API Functions
// ============================================================================

/**
 * Get price history for a product
 * Endpoint: GET /price-history/{product_id}
 */
export async function getProductPriceHistory(
  productId: number,
  days: number = 60
): Promise<PriceHistoryResponse> {
  try {
    const response = await fetchWithTimeout(`${API_URL}/price-history/${productId}?days=${days}`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error: any) {
    console.error('Failed to fetch price history:', error);
    throw new Error(error.message || 'Failed to load price history.');
  }
}

/**
 * Trigger real-time scraping for a product
 * Endpoint: POST /price-history/scrape/{product_id}
 */
export async function triggerRealtimeScrape(productId: number): Promise<{
  status: string;
  message: string;
  price_changed: boolean;
  old_price?: number;
  new_price?: number;
  current_price?: number;
  scraped_at: string;
}> {
  try {
    const response = await fetchWithTimeout(`${API_URL}/price-history/scrape/${productId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    const data = await response.json();
    return data;
  } catch (error: any) {
    console.error('Failed to trigger real-time scrape:', error);
    throw new Error(error.message || 'Failed to check current price.');
  }
}

// ============================================================================
// Voucher API Functions
// ============================================================================

export async function adminCreateVoucher(token: string, data: any): Promise<any> {
  try {
    const response = await fetchWithTimeout(`${API_URL}/points/vouchers/admin/create`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${response.status}`);
    }
    return await response.json();
  } catch (error: any) {
    throw new Error(error.message || 'Failed to create voucher.');
  }
}

export async function validateVoucher(token: string, data: { voucher_code: string, order_total: number }): Promise<any> {
  try {
    const response = await fetchWithTimeout(`${API_URL}/points/vouchers/validate`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${response.status}`);
    }
    return await response.json();
  } catch (error: any) {
    throw new Error(error.message || 'Failed to validate voucher.');
  }
}

export async function redeemCheckoutVoucher(token: string, data: { voucher_code: string, order_total: number }): Promise<any> {
  try {
    const response = await fetchWithTimeout(`${API_URL}/points/vouchers/redeem_checkout`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${response.status}`);
    }
    return await response.json();
  } catch (error: any) {
    throw new Error(error.message || 'Failed to redeem voucher.');
  }
}

// Global variable to hold the selected product for navigation, bypassing URL parameter truncation limits
export let globalSelectedProduct: Product | null = null;

export const setGlobalSelectedProduct = (product: Product | null) => {
  globalSelectedProduct = product;
};

let globalComparisonData: any = null;

export const setGlobalComparisonData = (data: any) => {
  globalComparisonData = data;
};

export const getGlobalComparisonData = () => {
  return globalComparisonData;
};
