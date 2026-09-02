/**
 * Categories Service
 */

import { API_BASE_URL } from '../lib/config';
import type { Product } from './api';

export interface Category {
  name: string;
  product_count: number;
}

export interface CategoryFilters {
  price_range: {
    min: number;
    max: number;
  };
  stores: string[];
  discount_ranges: Array<{
    label: string;
    value: number;
  }>;
  sort_options: Array<{
    label: string;
    value: string;
  }>;
}

export interface CategoryProductsResponse {
  request_id: string;
  query: string;
  tier: string;
  is_complete: boolean;
  results: Product[];
  results_count: number;
  tier1_platforms: string[];
  message: string;
  page: number;
  limit: number;
  total_pages: number;
  total_results: number;
}

/**
 * Get all available categories
 */
export async function getCategories(): Promise<Category[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/categories/`);

    if (!response.ok) {
      throw new Error('Failed to fetch categories');
    }

    const data = await response.json();
    return data.categories;
  } catch (error) {
    console.error('Get categories error:', error);
    throw error;
  }
}

/**
 * Get products in a category
 */
export async function getCategoryProducts(
  categoryName: string,
  options?: {
    page?: number;
    limit?: number;
    sort_by?: 'price_asc' | 'price_desc' | 'deal_score' | 'newest';
    min_price?: number;
    max_price?: number;
    store?: string;
    min_discount?: number;
  }
): Promise<CategoryProductsResponse> {
  try {
    const params = new URLSearchParams();
    
    if (options?.page) params.append('page', options.page.toString());
    if (options?.limit) params.append('limit', options.limit.toString());
    if (options?.sort_by) params.append('sort_by', options.sort_by);
    if (options?.min_price !== undefined) params.append('min_price', options.min_price.toString());
    if (options?.max_price !== undefined) params.append('max_price', options.max_price.toString());
    if (options?.store) params.append('store', options.store);
    if (options?.min_discount !== undefined) params.append('min_discount', options.min_discount.toString());

    const url = `${API_BASE_URL}/categories/${encodeURIComponent(categoryName)}${params.toString() ? '?' + params.toString() : ''}`;
    
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error('Failed to fetch category products');
    }

    return await response.json();
  } catch (error) {
    console.error('Get category products error:', error);
    throw error;
  }
}

/**
 * Get available filters for a category
 */
export async function getCategoryFilters(categoryName: string): Promise<CategoryFilters> {
  try {
    const response = await fetch(`${API_BASE_URL}/categories/${encodeURIComponent(categoryName)}/filters`);

    if (!response.ok) {
      throw new Error('Failed to fetch category filters');
    }

    return await response.json();
  } catch (error) {
    console.error('Get category filters error:', error);
    throw error;
  }
}
