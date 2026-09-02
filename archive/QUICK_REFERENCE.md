# PricePilot - Quick Reference Card

## 🚀 Start Everything

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd mobile
npx expo start
```

---

## 🗄️ Database Migration

```sql
-- Run this in Supabase SQL Editor
-- File: backend/migrations/add_missing_features.sql
```

**Verify migration:**
```sql
SELECT COUNT(*) FROM wishlist;
SELECT COUNT(*) FROM price_alerts;
SELECT COUNT(*) FROM notifications;
```

---

## 🔌 API Endpoints Quick Reference

### Base URL
```
http://localhost:8000
```

### Authentication Required
All endpoints except categories require:
```
Authorization: Bearer YOUR_JWT_TOKEN
```

### Wishlist
```
GET    /wishlist/                    - Get wishlist
POST   /wishlist/add                 - Add to wishlist
DELETE /wishlist/{product_id}        - Remove from wishlist
POST   /wishlist/toggle/{product_id} - Toggle wishlist
```

### Notifications & Alerts
```
GET    /notifications/               - Get all notifications
POST   /notifications/{id}/read      - Mark as read
POST   /notifications/read-all       - Mark all as read
GET    /notifications/alerts         - Get price alerts
POST   /notifications/alerts         - Create price alert
PUT    /notifications/alerts/{id}    - Update alert
DELETE /notifications/alerts/{id}    - Delete alert
```

### Points & Rewards
```
GET    /points/balance               - Get points balance
GET    /points/history               - Get transactions
GET    /points/vouchers              - Get vouchers
POST   /points/redeem                - Redeem points
GET    /points/referral              - Get referral stats
POST   /points/use-referral          - Apply referral code
POST   /points/complete-profile      - Claim profile bonus
```

### Analytics
```
GET    /analytics/dashboard          - Get complete analytics
POST   /analytics/record             - Record activity
```

### Categories
```
GET    /categories/                  - List all categories
GET    /categories/{name}            - Get products in category
GET    /categories/{name}/filters    - Get filter options
```

### Price History
```
GET    /price-history/{product_id}   - Get price history
```

### Admin (requires admin role)
```
GET    /admin/dashboard              - System metrics
GET    /admin/users                  - User statistics
POST   /admin/trigger-scraper        - Manual scrape
```

---

## 💎 Points System

### Earning Points
| Action | Points | Condition |
|--------|--------|-----------|
| Registration | +100 | Welcome bonus |
| Complete Profile | +50 | Add full_name & phone |
| First Wishlist | +5 | First item only |
| Set Price Alert | +5 | Per alert |
| Purchase | +10 | Per purchase |
| Referral (Referrer) | +50 | When referred user registers |
| Referral (New User) | +25 | Welcome bonus |

### Redeeming Points
- Minimum: 100 points
- Conversion: 1 point = Rs 1 discount
- Validity: 30 days

---

## 📱 Frontend Services

### Import Statements
```typescript
// Wishlist
import { 
  getWishlist, 
  addToWishlist, 
  toggleWishlist 
} from '../services/wishlist';

// Notifications
import { 
  getNotifications, 
  createPriceAlert 
} from '../services/notifications';

// Points
import { 
  getPointsBalance, 
  redeemPoints, 
  getReferralStats 
} from '../services/points';

// Analytics
import { 
  getAnalyticsDashboard, 
  recordPurchase 
} from '../services/analytics';

// Categories
import { 
  getCategories, 
  getCategoryProducts 
} from '../services/categories';
```

### Get Auth Token
```typescript
import AsyncStorage from '@react-native-async-storage/async-storage';

const token = await AsyncStorage.getItem('authToken');
```

---

## 🎨 Code Snippets

### Add to Wishlist
```typescript
import { addToWishlist } from '../services/wishlist';
import AsyncStorage from '@react-native-async-storage/async-storage';

const handleAddToWishlist = async () => {
  const token = await AsyncStorage.getItem('authToken');
  
  await addToWishlist(token, {
    product_id: product.id,
    product_title: product.title,
    product_price: product.price,
    product_image_url: product.image_url,
    product_url: product.product_url,
    store_name: product.store_name
  });
  
  Alert.alert('Success', 'Added to wishlist!');
};
```

### Set Price Alert
```typescript
import { createPriceAlert } from '../services/notifications';

const handleSetAlert = async (targetPrice) => {
  const token = await AsyncStorage.getItem('authToken');
  
  await createPriceAlert(token, {
    product_id: product.id,
    product_title: product.title,
    product_url: product.product_url,
    store_name: product.store_name,
    target_price: targetPrice,
    current_price: product.price
  });
  
  Alert.alert('Success', 'Price alert set!');
};
```

### Record Purchase
```typescript
import { recordPurchase } from '../services/analytics';

const handlePurchase = async () => {
  const token = await AsyncStorage.getItem('authToken');
  const savings = product.original_price - product.price;
  
  await recordPurchase(
    token,
    product.id,
    product.title,
    product.price,
    product.store_name,
    savings
  );
  
  // Opens store URL
  Linking.openURL(product.product_url);
};
```

### Get Points Balance
```typescript
import { getPointsBalance } from '../services/points';

const [points, setPoints] = useState(0);

useEffect(() => {
  const loadPoints = async () => {
    const token = await AsyncStorage.getItem('authToken');
    const balance = await getPointsBalance(token);
    setPoints(balance);
  };
  
  loadPoints();
}, []);
```

### Redeem Points
```typescript
import { redeemPoints } from '../services/points';

const handleRedeem = async () => {
  const token = await AsyncStorage.getItem('authToken');
  const pointsToRedeem = 100;
  const discount = 100; // Rs 100
  
  const voucher = await redeemPoints(token, pointsToRedeem, discount);
  
  Alert.alert(
    'Success!',
    `Voucher Code: ${voucher.voucher_code}\nDiscount: Rs ${voucher.discount_amount}`
  );
};
```

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port is in use
netstat -ano | findstr :8000

# Kill the process
taskkill /PID <PID> /F

# Restart
python -m uvicorn main:app --reload
```

### Database connection error
```bash
# Check .env file
cat backend/.env

# Verify DATABASE_URL is correct
```

### 401 Unauthorized
```typescript
// Token might be expired or invalid
await AsyncStorage.removeItem('authToken');
router.replace('/login');
```

### Import errors
```bash
# Make sure __init__.py exists
touch backend/app/routers/__init__.py
touch backend/app/models/__init__.py
```

---

## 📊 Testing Commands

### Test Backend
```bash
# Test categories (no auth needed)
curl http://localhost:8000/categories/

# Test with auth
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/points/balance

# Test POST
curl -X POST http://localhost:8000/wishlist/add \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "product_title": "Test", "product_price": 1000, "product_url": "http://test.com", "store_name": "Test"}'
```

### Get JWT Token
1. Login through mobile app
2. Open browser dev tools
3. Check AsyncStorage or network requests
4. Copy token value

---

## 🎯 Common Tasks

### Make User Admin
```sql
UPDATE users 
SET role = 'admin' 
WHERE email = 'your@email.com';
```

### Check User Points
```sql
SELECT email, points 
FROM users 
WHERE email = 'your@email.com';
```

### View All Notifications
```sql
SELECT * FROM notifications 
WHERE user_id = 'YOUR_USER_ID' 
ORDER BY created_at DESC;
```

### Check Price Alerts
```sql
SELECT * FROM price_alerts 
WHERE user_id = 'YOUR_USER_ID';
```

---

## 📁 Important Files

```
backend/
├── main.py                          # Main app entry
├── .env                             # Environment variables
├── migrations/
│   └── add_missing_features.sql    # Database migration
└── app/
    ├── routers/
    │   ├── wishlist.py             # Wishlist API
    │   ├── notifications.py        # Notifications API
    │   ├── points.py               # Points API
    │   ├── analytics.py            # Analytics API
    │   ├── categories.py           # Categories API
    │   └── admin.py                # Admin API
    └── models/
        ├── wishlist.py             # Wishlist models
        ├── notifications.py        # Notification models
        └── analytics.py            # Analytics models

mobile/
├── services/
│   ├── wishlist.ts                 # Wishlist service
│   ├── notifications.ts            # Notifications service
│   ├── points.ts                   # Points service
│   ├── analytics.ts                # Analytics service
│   └── categories.ts               # Categories service
└── app/
    ├── notifications.tsx           # Notifications page ✅
    ├── points.tsx                  # Points page ✅
    ├── price-alerts.tsx            # Price alerts page (TODO)
    ├── analytics.tsx               # Analytics page (TODO)
    └── product/
        └── [id].tsx                # Product detail (needs enhancement)
```

---

## 🎓 For Demo

### Show This Flow:
1. **Register** → Get 100 points
2. **Complete Profile** → Get 50 points (150 total)
3. **Add to Wishlist** → Get 5 points (155 total)
4. **Set Price Alert** → Get 5 points (160 total)
5. **Redeem 100 points** → Get voucher
6. **Show Referral Code** → Can invite friends
7. **View Analytics** → Show insights

### Key Features to Highlight:
- ✅ 50+ API endpoints
- ✅ 11 database tables
- ✅ Points & rewards system
- ✅ Referral program
- ✅ Price alerts with notifications
- ✅ Smart analytics
- ✅ Admin dashboard
- ✅ Category browsing
- ✅ Price history tracking

---

## 📞 Quick Help

**Backend not responding?**
→ Check if it's running on port 8000

**Frontend can't connect?**
→ Check API_BASE_URL in config

**401 errors?**
→ Token expired, login again

**Database errors?**
→ Run migration first

**Import errors?**
→ Check __init__.py files exist

---

## ✅ Pre-Demo Checklist

- [ ] Database migration ran successfully
- [ ] Backend server running (port 8000)
- [ ] Frontend app running
- [ ] Test user registered with 100 points
- [ ] Notifications page works
- [ ] Points page works
- [ ] Can add to wishlist
- [ ] Can set price alert
- [ ] Can redeem points
- [ ] Referral code displays

---

**You're ready to go! 🚀**
