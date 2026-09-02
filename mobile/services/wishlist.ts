/**
 * Wishlist Service
 * Handles wishlist operations with PricePilot backend
 */

import { API_BASE_URL } from '../lib/config';

export interface WishlistItem {
  id: number;
  user_id: string;
  product_id: number;
  product_title: string;
  product_price: number;
  product_image_url?: string;
  product_url: string;
  store_name: string;
  added_at: string;
}

export interface AddToWishlistRequest {
  product_id: number;
  product_title: string;
  product_price: number;
  product_image_url?: string;
  product_url: string;
  store_name: string;
}

/**
 * Get user's wishlist
 */
export async function getWishlist(token: string): Promise<WishlistItem[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/wishlist/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch wishlist');
    }

    const data = await response.json();
    return data.items;
  } catch (error) {
    console.error('Get wishlist error:', error);
    throw error;
  }
}

/**
 * Add product to wishlist
 */
export async function addToWishlist(
  token: string,
  item: AddToWishlistRequest
): Promise<{ message: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/wishlist/add`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(item),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to add to wishlist');
    }

    return await response.json();
  } catch (error) {
    console.error('Add to wishlist error:', error);
    throw error;
  }
}

/**
 * Remove product from wishlist
 */
export async function removeFromWishlist(
  token: string,
  productId: number
): Promise<{ message: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/wishlist/${productId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to remove from wishlist');
    }

    return await response.json();
  } catch (error) {
    console.error('Remove from wishlist error:', error);
    throw error;
  }
}

/**
 * Toggle product in wishlist (add if not exists, remove if exists)
 */
export async function toggleWishlist(
  token: string,
  productId: number,
  item: AddToWishlistRequest
): Promise<{ message: string; in_wishlist: boolean }> {
  try {
    const response = await fetch(`${API_BASE_URL}/wishlist/toggle/${productId}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(item),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to toggle wishlist');
    }

    return await response.json();
  } catch (error) {
    console.error('Toggle wishlist error:', error);
    throw error;
  }
}

/**
 * Check if product is in wishlist
 */
export async function isInWishlist(
  token: string,
  productId: number
): Promise<boolean> {
  try {
    const wishlist = await getWishlist(token);
    return wishlist.some(item => item.product_id === productId);
  } catch (error) {
    console.error('Check wishlist error:', error);
    return false;
  }
}
