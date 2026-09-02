import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { authStorage } from '../lib/authStorage';
// ============================================================================
// Types
// ============================================================================

export interface FavoriteItem {
  id: string;          // unique key: `${store_name}-${product_url}`
  productId?: number;  // from DB if available
  title: string;
  price: number;
  originalPrice?: number;
  discountPercent?: number;
  imageUrl: string;
  storeName: string;
  productUrl: string;
  // quantity field removed - not needed for comparison platform
}

interface FavoritesContextType {
  items: FavoriteItem[];
  addItem: (item: FavoriteItem) => void;
  removeItem: (id: string) => void;
  clearFavorites: () => void;
  itemCount: number;
  // updateQuantity removed
  // totalPrice removed
}

// ============================================================================
// Context
// ============================================================================

const STORAGE_KEY = 'pricepilot_favorites';
const OLD_CART_KEY = 'pricepilot_cart'; // For migration

const FavoritesContext = createContext<FavoritesContextType | undefined>(undefined);

export function FavoritesProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<FavoriteItem[]>([]);
  const [loaded, setLoaded] = useState(false);

  // Migrate old cart data on first load
  const migrateFromCart = useCallback(async () => {
    try {
      console.log('Checking for cart data to migrate...');
      
      // Check if already migrated
      const favoritesData = await authStorage.getItemAsync(STORAGE_KEY);
      if (favoritesData) {
        console.log('Favorites data already exists, skipping migration');
        return null;
      }
      
      // Check for old cart data
      const cartData = await authStorage.getItemAsync(OLD_CART_KEY);
      if (!cartData) {
        console.log('No cart data to migrate');
        return null;
      }
      
      // Parse cart data
      const cartItems = JSON.parse(cartData);
      console.log(`Found ${cartItems.length} cart items to migrate`);
      
      // Transform to favorites (remove quantity field)
      const favoriteItems: FavoriteItem[] = cartItems.map((item: any) => {
        const { quantity, ...rest } = item;
        return rest as FavoriteItem;
      });
      
      // Write to favorites storage
      await authStorage.setItemAsync(STORAGE_KEY, JSON.stringify(favoriteItems));
      console.log('Successfully migrated to favorites');
      
      // Remove old cart data
      await authStorage.deleteItemAsync(OLD_CART_KEY);
      console.log('Migration completed successfully');
      
      return favoriteItems;
    } catch (error) {
      console.error('Migration failed:', error);
      // Don't throw - will retry on next launch
      return null;
    }
  }, []);

  // Load persisted favorites on mount
  useEffect(() => {
    (async () => {
      try {
        // Run migration first
        const migratedItems = await migrateFromCart();
        
        if (migratedItems) {
          setItems(migratedItems);
        } else {
          // Load existing favorites
          const raw = await authStorage.getItemAsync(STORAGE_KEY);
          if (raw) {
            setItems(JSON.parse(raw));
          }
        }
      } catch (e) {
        console.error('Failed to load favorites:', e);
      } finally {
        setLoaded(true);
      }
    })();
  }, [migrateFromCart]);

  // Persist whenever items change (skip the first load)
  useEffect(() => {
    if (!loaded) return;
    authStorage.setItemAsync(STORAGE_KEY, JSON.stringify(items)).catch(e =>
      console.error('Failed to persist favorites:', e),
    );
  }, [items, loaded]);

  const addItem = useCallback((newItem: FavoriteItem) => {
    setItems(prev => {
      const existing = prev.find(i => i.id === newItem.id);
      if (existing) {
        // Already in favorites, don't add duplicate
        console.log('Product already in favorites');
        return prev;
      }
      
      return [...prev, newItem];
    });
  }, []);

  const removeItem = useCallback((id: string) => {
    setItems(prev => {
      return prev.filter(i => i.id !== id);
    });
  }, []);

  const clearFavorites = useCallback(() => {
    setItems([]);
  }, []);

  const itemCount = items.length;

  return (
    <FavoritesContext.Provider
      value={{ items, addItem, removeItem, clearFavorites, itemCount }}
    >
      {children}
    </FavoritesContext.Provider>
  );
}

export function useFavorites() {
  const ctx = useContext(FavoritesContext);
  if (!ctx) {
    throw new Error('useFavorites must be used within a FavoritesProvider');
  }
  return ctx;
}
