/**
 * Points & Rewards Service
 */

import { API_URL } from '../constants/api';

export interface PointsTransaction {
  id: number;
  user_id: string;
  transaction_type: string;
  points_change: number;
  description: string;
  related_user_id?: string;
  created_at: string;
}

export interface Voucher {
  id: number;
  user_id: string;
  voucher_code: string;
  discount_amount: number;
  points_cost: number;
  is_global: boolean;
  is_redeemed: boolean;
  redeemed_at?: string;
  expires_at: string | null;
  created_at: string;
}

export interface ReferralStats {
  referral_code: string;
  total_referrals: number;
  pending_referrals: number;
  points_earned_from_referrals: number;
}

/**
 * Get current points balance
 */
export async function getPointsBalance(token: string): Promise<number> {
  try {
    const response = await fetch(`${API_URL}/points/balance`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch points balance');
    }

    const data = await response.json();
    return data.points;
  } catch (error) {
    console.error('Get points balance error:', error);
    throw error;
  }
}

/**
 * Get points transaction history
 */
export async function getPointsHistory(token: string): Promise<PointsTransaction[]> {
  try {
    const response = await fetch(`${API_URL}/points/history`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch points history');
    }

    const data = await response.json();
    return data.transactions;
  } catch (error) {
    console.error('Get points history error:', error);
    throw error;
  }
}

/**
 * Get user's vouchers
 */
export async function getVouchers(token: string): Promise<{
  vouchers: Voucher[];
  active_count: number;
  total_count: number;
}> {
  try {
    const response = await fetch(`${API_URL}/points/vouchers`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch vouchers');
    }

    return await response.json();
  } catch (error) {
    console.error('Get vouchers error:', error);
    throw error;
  }
}

/**
 * Redeem points for a discount voucher
 */
export async function redeemPoints(
  token: string,
  pointsToRedeem: number,
  discountAmount: number,
  globalVoucherId?: number
): Promise<Voucher> {
  try {
    const payload = {
      points_to_redeem: Number(pointsToRedeem),
      discount_amount: Number(discountAmount),
      global_voucher_id: globalVoucherId,
    };
    console.log('Sending redeem payload:', payload);

    const response = await fetch(`${API_URL}/points/redeem`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const error = await response.json();
      let errorMessage = 'Failed to redeem points';
      if (error.detail) {
        errorMessage = typeof error.detail === 'string' ? error.detail : JSON.stringify(error.detail);
      }
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    console.error('Redeem points error:', error);
    throw error;
  }
}

/**
 * Get referral statistics
 */
export async function getReferralStats(token: string): Promise<ReferralStats> {
  try {
    const response = await fetch(`${API_URL}/points/referral`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch referral stats');
    }

    return await response.json();
  } catch (error) {
    console.error('Get referral stats error:', error);
    throw error;
  }
}

/**
 * Apply a referral code
 */
export async function useReferralCode(
  token: string,
  referralCode: string
): Promise<{ message: string; bonus_points: number }> {
  try {
    const response = await fetch(`${API_URL}/points/use-referral?referral_code=${referralCode}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to apply referral code');
    }

    return await response.json();
  } catch (error) {
    console.error('Use referral code error:', error);
    throw error;
  }
}

/**
 * Claim profile completion bonus
 */
export async function claimProfileBonus(token: string): Promise<{
  message: string;
  bonus_points: number;
}> {
  try {
    const response = await fetch(`${API_URL}/points/complete-profile`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to claim profile bonus');
    }

    return await response.json();
  } catch (error) {
    console.error('Claim profile bonus error:', error);
    throw error;
  }
}
