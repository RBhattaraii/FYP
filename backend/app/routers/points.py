"""
Points and Rewards Router
"""
from fastapi import APIRouter, Request, Depends, HTTPException, status
import asyncpg
from datetime import datetime, timedelta
import secrets

from app.limiter import limiter
from app.models.analytics import (
    RedeemPointsRequest,
    Voucher,
    ReferralStats,
    PointsTransaction,
    AdminCreateVoucherRequest,
    ValidateVoucherRequest,
    ValidateVoucherResponse,
    RedeemCheckoutRequest
)
from app.database.postgres import get_db
from app.auth.jwt_handler import decode_access_token

router = APIRouter(
    prefix="/points",
    tags=["Points & Rewards"]
)


async def get_current_user_id(request: Request) -> str:
    """Extract and verify user ID from JWT token"""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = auth_header.split(" ")[1]
    
    try:
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        return user_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}"
        )


@router.get("/balance")
@limiter.limit("60/minute")
async def get_points_balance(
    request: Request,
    db: asyncpg.Connection = Depends(get_db)
):
    """Get current points balance"""
    try:
        user_id = await get_current_user_id(request)
        
        row = await db.fetchrow("SELECT points FROM users WHERE id = $1", user_id)
        
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"points": row['points']}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get points balance error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch points balance"
        )


@router.get("/history")
@limiter.limit("30/minute")
async def get_points_history(
    request: Request,
    db: asyncpg.Connection = Depends(get_db)
):
    """Get points transaction history"""
    try:
        user_id = await get_current_user_id(request)
        
        rows = await db.fetch("""
            SELECT id, user_id, transaction_type, points_change, description, 
                   related_user_id, created_at
            FROM points_transactions
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT 100
        """, user_id)
        
        transactions = []
        for row in rows:
            d = dict(row)
            d['user_id'] = str(d['user_id'])
            if d.get('related_user_id'):
                d['related_user_id'] = str(d['related_user_id'])
            transactions.append(PointsTransaction(**d))
        
        return {"transactions": transactions, "total": len(transactions)}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get points history error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch points history"
        )


@router.get("/vouchers")
@limiter.limit("30/minute")
async def get_vouchers(
    request: Request,
    db: asyncpg.Connection = Depends(get_db)
):
    """Get user's vouchers"""
    try:
        user_id = await get_current_user_id(request)
        
        rows = await db.fetch("""
            SELECT id, user_id, voucher_code, discount_type, discount_amount, minimum_spend, usage_limit, times_used, is_global, points_cost,
                   is_redeemed, redeemed_at, expires_at, created_at
            FROM vouchers
            WHERE user_id = $1 OR is_global = TRUE
            ORDER BY created_at DESC
        """, user_id)
        
        vouchers = []
        for row in rows:
            d = dict(row)
            if d.get('user_id'):
                d['user_id'] = str(d['user_id'])
            vouchers.append(Voucher(**d))
        
        active_vouchers = [v for v in vouchers if not v.is_redeemed and (v.expires_at is None or v.expires_at.replace(tzinfo=None) > datetime.now())]
        
        return {
            "vouchers": vouchers,
            "active_count": len(active_vouchers),
            "total_count": len(vouchers)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get vouchers error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch vouchers"
        )


@router.post("/redeem", response_model=Voucher)
@limiter.limit("10/minute")
async def redeem_points(
    request: Request,
    redemption: RedeemPointsRequest,
    db: asyncpg.Connection = Depends(get_db)
):
    """Redeem points for a discount voucher"""
    try:
        user_id = await get_current_user_id(request)
        
        # Check if user has enough points
        user_row = await db.fetchrow("SELECT points FROM users WHERE id = $1", user_id)
        
        if not user_row or user_row['points'] < redemption.points_to_redeem:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient points"
            )
            
        voucher_code = f"PRICE{secrets.token_hex(4).upper()}"
        description = f"Redeemed for {redemption.discount_amount} Rs voucher"
        
        if redemption.global_voucher_id:
            global_voucher = await db.fetchrow("SELECT * FROM vouchers WHERE id = $1 AND is_global = TRUE", redemption.global_voucher_id)
            if not global_voucher:
                raise HTTPException(status_code=404, detail="Voucher tier not found")
                
            # Check if user already redeemed this exact global voucher by looking at transactions
            # Or simpler: check if they have a voucher that starts with this code
            existing = await db.fetchval("""
                SELECT 1 FROM points_transactions 
                WHERE user_id = $1 AND transaction_type = 'redeemed_voucher' 
                AND description LIKE $2
            """, user_id, f"%({global_voucher['voucher_code']})%")
            
            if existing:
                raise HTTPException(status_code=400, detail="You have already redeemed this reward tier")
                
            voucher_code = f"{global_voucher['voucher_code']}-{secrets.token_hex(3).upper()}"
            description = f"Redeemed for {redemption.discount_amount} Rs voucher ({global_voucher['voucher_code']})"
        
        # Create voucher
        voucher_row = await db.fetchrow("""
            INSERT INTO vouchers (user_id, voucher_code, discount_amount, points_cost, expires_at)
            VALUES ($1, $2, $3, $4, NOW() + INTERVAL '30 days')
            RETURNING id, user_id, voucher_code, discount_type, discount_amount, minimum_spend, usage_limit, times_used, is_global, points_cost, 
                      is_redeemed, redeemed_at, expires_at, created_at
        """, user_id, voucher_code, redemption.discount_amount, redemption.points_to_redeem)
        
        # Deduct points
        await db.execute("""
            UPDATE users SET points = points - $1 WHERE id = $2
        """, redemption.points_to_redeem, user_id)
        
        # Record transaction
        await db.execute("""
            INSERT INTO points_transactions (user_id, transaction_type, points_change, description)
            VALUES ($1, 'redeemed_voucher', $2, $3)
        """, user_id, -redemption.points_to_redeem, description)
        
        d = dict(voucher_row)
        if d.get('user_id'):
            d['user_id'] = str(d['user_id'])
        return Voucher(**d)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Redeem points error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to redeem points"
        )


@router.get("/referral", response_model=ReferralStats)
@limiter.limit("30/minute")
async def get_referral_stats(
    request: Request,
    db: asyncpg.Connection = Depends(get_db)
):
    """Get referral statistics"""
    try:
        user_id = await get_current_user_id(request)
        
        # Get referral code
        user_row = await db.fetchrow("""
            SELECT email, referral_code FROM users WHERE id = $1
        """, user_id)
        
        if not user_row:
            raise HTTPException(status_code=404, detail="User not found")
            
        referral_code = user_row['referral_code']
        
        if not referral_code:
            # Generate a new referral code
            import secrets
            import string
            
            # Simple fallback base
            base = user_row['email'].split('@')[0][:4].upper()
            
            # Generate 6 random alphanumeric characters
            alphabet = string.ascii_uppercase + string.digits
            random_part = ''.join(secrets.choice(alphabet) for _ in range(6))
            
            referral_code = f"{base}{random_part}"
            
            await db.execute("""
                UPDATE users SET referral_code = $1 WHERE id = $2
            """, referral_code, user_id)
        
        # Count total referrals
        total_referrals = await db.fetchval("""
            SELECT COUNT(*) FROM users WHERE referred_by = $1
        """, user_id)
        
        # Count pending referrals (referred users who haven't made first purchase)
        pending_referrals = await db.fetchval("""
            SELECT COUNT(*)
            FROM users u
            WHERE u.referred_by = $1
            AND NOT EXISTS (
                SELECT 1 FROM user_activity ua
                WHERE ua.user_id = u.id AND ua.activity_type = 'purchase'
            )
        """, user_id)
        
        # Calculate points earned from referrals
        points_earned = await db.fetchval("""
            SELECT COALESCE(SUM(points_change), 0)
            FROM points_transactions
            WHERE user_id = $1 AND transaction_type = 'earned_referral'
        """, user_id)
        
        return ReferralStats(
            referral_code=referral_code,
            total_referrals=total_referrals or 0,
            pending_referrals=pending_referrals or 0,
            points_earned_from_referrals=points_earned or 0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get referral stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch referral stats"
        )


@router.post("/use-referral")
@limiter.limit("5/minute")
async def use_referral_code(
    request: Request,
    referral_code: str,
    db: asyncpg.Connection = Depends(get_db)
):
    """Apply a referral code (for new users during registration)"""
    try:
        user_id = await get_current_user_id(request)
        
        # Check if user already used a referral code
        user_row = await db.fetchrow("SELECT referred_by FROM users WHERE id = $1", user_id)
        
        if user_row['referred_by']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already used a referral code"
            )
        
        # Find referrer
        referrer_row = await db.fetchrow("""
            SELECT id FROM users WHERE referral_code = $1
        """, referral_code)
        
        if not referrer_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid referral code"
            )
        
        referrer_id = referrer_row['id']
        
        # Check not using own referral code
        if referrer_id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot use your own referral code"
            )
        
        # Update user's referred_by
        await db.execute("""
            UPDATE users SET referred_by = $1 WHERE id = $2
        """, referrer_id, user_id)
        
        # Award points to referrer
        await db.execute("""
            SELECT award_points($1, 50, 'earned_referral', 'Referral bonus')
        """, referrer_id)
        
        # Award bonus points to new user
        await db.execute("""
            SELECT award_points($1, 25, 'earned_referral', 'Referral signup bonus')
        """, user_id)
        
        return {"message": "Referral code applied successfully", "bonus_points": 25}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Use referral code error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to apply referral code"
        )


@router.post("/complete-profile")
@limiter.limit("5/minute")
async def complete_profile_bonus(
    request: Request,
    db: asyncpg.Connection = Depends(get_db)
):
    """Award points for completing profile (called after user updates full_name and phone)"""
    try:
        user_id = await get_current_user_id(request)
        
        # Check if profile is already marked as completed
        user_row = await db.fetchrow("""
            SELECT profile_completed, full_name, phone FROM users WHERE id = $1
        """, user_id)
        
        if user_row['profile_completed']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Profile completion bonus already claimed"
            )
        
        # Check if profile is actually complete
        if not user_row['full_name'] or not user_row['phone']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please complete your profile (full name and phone required)"
            )
        
        # Mark profile as completed
        await db.execute("""
            UPDATE users SET profile_completed = TRUE WHERE id = $1
        """, user_id)
        
        # Award points
        await db.execute("""
            SELECT award_points($1, 50, 'earned_profile', 'Profile completion bonus')
        """, user_id)
        
        return {"message": "Profile completion bonus awarded", "bonus_points": 50}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Complete profile bonus error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to award profile completion bonus"
        )

# ============================================================================
# NEW VOUCHER SYSTEM ENDPOINTS
# ============================================================================

@router.post("/vouchers/admin/create")
async def admin_create_voucher(
    request: AdminCreateVoucherRequest,
    db: asyncpg.Connection = Depends(get_db)
):
    """Admin endpoint to generate complex vouchers"""
    try:
        # Check if code already exists
        exists = await db.fetchval("SELECT id FROM vouchers WHERE voucher_code = $1", request.voucher_code)
        if exists:
            raise HTTPException(status_code=400, detail="Voucher code already exists")
        
        if request.expires_in_days > 0:
            expires_expr = f"NOW() + (INTERVAL '1 day' * {request.expires_in_days})"
        else:
            # Set to 100 years from now instead of NULL to satisfy DB NOT NULL constraint
            expires_expr = "NOW() + INTERVAL '100 years'"

        query = f"""
            INSERT INTO vouchers (
                voucher_code, discount_type, discount_amount, minimum_spend, 
                usage_limit, times_used, is_global, points_cost, expires_at
            )
            VALUES ($1, $2, $3, $4, $5, 0, TRUE, $6, {expires_expr})
            RETURNING id, user_id, voucher_code, discount_type, discount_amount, minimum_spend, usage_limit, times_used, is_global, points_cost, 
                      is_redeemed, redeemed_at, expires_at, created_at
        """
        
        voucher_row = await db.fetchrow(
            query, 
            request.voucher_code, 
            request.discount_type, 
            request.discount_amount, 
            request.minimum_spend, 
            request.usage_limit, 
            request.points_cost
        )
             
        d = dict(voucher_row)
        if d.get('user_id'):
            d['user_id'] = str(d['user_id'])
        return Voucher(**d)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Admin create voucher error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create global voucher")


@router.post("/vouchers/validate", response_model=ValidateVoucherResponse)
async def validate_voucher(
    request: ValidateVoucherRequest,
    db: asyncpg.Connection = Depends(get_db)
):
    """Validate a voucher against an order total"""
    try:
        voucher = await db.fetchrow("""
            SELECT id, discount_type, discount_amount, minimum_spend, usage_limit, times_used, expires_at, is_redeemed, is_global
            FROM vouchers WHERE voucher_code = $1
        """, request.voucher_code.strip())
        
        if not voucher:
            return ValidateVoucherResponse(is_valid=False, message="Invalid voucher code", discount_amount=0, new_total=request.order_total)
            
        if voucher['is_redeemed'] and not voucher['is_global']:
            return ValidateVoucherResponse(is_valid=False, message="Voucher already redeemed", discount_amount=0, new_total=request.order_total)
            
        if voucher['is_global'] and voucher['times_used'] >= voucher['usage_limit']:
            return ValidateVoucherResponse(is_valid=False, message="Voucher usage limit reached", discount_amount=0, new_total=request.order_total)
            
        if voucher['expires_at'] < datetime.now():
            return ValidateVoucherResponse(is_valid=False, message="Voucher has expired", discount_amount=0, new_total=request.order_total)
            
        if request.order_total < voucher['minimum_spend']:
            return ValidateVoucherResponse(is_valid=False, message=f"Minimum spend of Rs {voucher['minimum_spend']} required", discount_amount=0, new_total=request.order_total)
            
        # Calculate discount
        if voucher['discount_type'] == 'percentage':
            discount = request.order_total * (voucher['discount_amount'] / 100)
        else:
            discount = voucher['discount_amount']
            
        new_total = max(0, request.order_total - discount)
        
        return ValidateVoucherResponse(
            is_valid=True, 
            message="Voucher applied successfully!", 
            discount_amount=discount, 
            new_total=new_total,
            voucher_id=voucher['id']
        )
    except Exception as e:
        print(f"Validate voucher error: {e}")
        raise HTTPException(status_code=500, detail="Failed to validate voucher")


@router.post("/vouchers/redeem_checkout")
async def redeem_checkout_voucher(
    request: RedeemCheckoutRequest,
    db: asyncpg.Connection = Depends(get_db)
):
    """Permanently consume the voucher for an order"""
    try:
        # Validate first
        validation = await validate_voucher(request, db)
        if not validation.is_valid:
            raise HTTPException(status_code=400, detail=validation.message)
            
        voucher_id = validation.voucher_id
        
        # Mark as used
        await db.execute("""
            UPDATE vouchers 
            SET times_used = times_used + 1, 
                is_redeemed = CASE WHEN is_global = FALSE THEN TRUE ELSE is_redeemed END,
                redeemed_at = CASE WHEN is_global = FALSE THEN NOW() ELSE redeemed_at END
            WHERE id = $1
        """, voucher_id)
        
        return {"message": "Voucher redeemed successfully", "discount_applied": validation.discount_amount}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Redeem checkout error: {e}")
        raise HTTPException(status_code=500, detail="Failed to redeem voucher")
