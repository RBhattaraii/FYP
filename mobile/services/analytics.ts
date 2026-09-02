/**
 * Analytics Service
 */

import { API_BASE_URL } from '../lib/config';

export interface PurchaseStatistics {
  period: 'month' | 'year';
  product_count: number;
  total_spent: number;
  total_savings: number;
}

export interface SmartInsights {
  total_savings: number;
  missed_products_count: number;
  missed_products: Array<{
    product_id: number;
    product_title: string;
    viewed_price: number;
    lowest_price: number;
    potential_savings: number;
  }>;
  category_spending: Record<string, number>;
  monthly_spending_trend: Array<{
    month: string;
    purchase_count: number;
    total_spent: number;
  }>;
  average_discount: number;
  suggested_products: Array<{
    id: number;
    title: string;
    price: number;
    discount_percent: number;
    image_url?: string;
    store_name: string;
  }>;
}

export interface PointsTransaction {
  id: number;
  user_id: string;
  transaction_type: string;
  points_change: number;
  description: string;
  related_user_id?: string;
  created_at: string;
}

export interface AnalyticsResponse {
  current_points: number;
  monthly_stats: PurchaseStatistics;
  yearly_stats: PurchaseStatistics;
  points_history: PointsTransaction[];
  smart_insights: SmartInsights;
}

export interface RecordActivityRequest {
  activity_type: 'store_visit' | 'purchase' | 'wishlist_add' | 'alert_set';
  product_id?: number;
  product_title?: string;
  product_price?: number;
  store_name?: string;
  savings_amount?: number;
}

/**
 * Get complete analytics dashboard
 */
export async function getAnalyticsDashboard(token: string): Promise<AnalyticsResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/analytics/dashboard`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch analytics dashboard');
    }

    return await response.json();
  } catch (error) {
    console.error('Get analytics dashboard error:', error);
    throw error;
  }
}

/**
 * Record user activity
 */
export async function recordActivity(
  token: string,
  activity: RecordActivityRequest
): Promise<{ message: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/analytics/record`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(activity),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to record activity');
    }

    return await response.json();
  } catch (error) {
    console.error('Record activity error:', error);
    throw error;
  }
}

/**
 * Record a product purchase
 */
export async function recordPurchase(
  token: string,
  productId: number,
  productTitle: string,
  productPrice: number,
  storeName: string,
  savingsAmount: number
): Promise<{ message: string }> {
  return recordActivity(token, {
    activity_type: 'purchase',
    product_id: productId,
    product_title: productTitle,
    product_price: productPrice,
    store_name: storeName,
    savings_amount: savingsAmount,
  });
}

/**
 * Record a store visit
 */
export async function recordStoreVisit(
  token: string,
  productId: number,
  productTitle: string,
  productPrice: number,
  storeName: string
): Promise<{ message: string }> {
  return recordActivity(token, {
    activity_type: 'store_visit',
    product_id: productId,
    product_title: productTitle,
    product_price: productPrice,
    store_name: storeName,
  });
}
