import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { authStorage } from '../lib/authStorage';

// ============================================================================
// Types
// ============================================================================

export interface CartItem {
  id: string;          // unique cart key: `${store_name}-${product_url}`
  productId?: number;  // from DB if available
  title: string;
  price: number;
  originalPrice?: number;
  discountPercent?: number;
  imageUrl: string;
  storeName: string;
  productUrl: string;
  quantity: number;
}

interface CartContextType {
  items: CartItem[];
  addItem: (item: Omit<CartItem, 'quantity'>) => void;
  removeItem: (id: string) => void;
  updateQuantity: (id: string, quantity: number) => void;
  clearCart: () => void;
  itemCount: number;
  totalPrice: number;
}

// ============================================================================
// Context
// ============================================================================

const STORAGE_KEY = 'pricepilot_cart';

const CartContext = createContext<CartContextType | undefined>(undefined);

export function CartProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<CartItem[]>([]);
  const [loaded, setLoaded] = useState(false);

  // Load persisted cart on mount
  useEffect(() => {
    (async () => {
      try {
        const raw = await authStorage.getItemAsync(STORAGE_KEY);
        if (raw) {
          setItems(JSON.parse(raw));
        }
      } catch (e) {
        console.error('Failed to load cart:', e);
      } finally {
        setLoaded(true);
      }
    })();
  }, []);

  // Persist whenever items change (skip the first load)
  useEffect(() => {
    if (!loaded) return;
    authStorage.setItemAsync(STORAGE_KEY, JSON.stringify(items)).catch(e =>
      console.error('Failed to persist cart:', e),
    );
  }, [items, loaded]);

  const addItem = useCallback((newItem: Omit<CartItem, 'quantity'>) => {
    setItems(prev => {
      const existing = prev.find(i => i.id === newItem.id);
      if (existing) {
        // Increment quantity
        return prev.map(i =>
          i.id === newItem.id ? { ...i, quantity: i.quantity + 1 } : i,
        );
      }
      return [...prev, { ...newItem, quantity: 1 }];
    });
  }, []);

  const removeItem = useCallback((id: string) => {
    setItems(prev => prev.filter(i => i.id !== id));
  }, []);

  const updateQuantity = useCallback((id: string, quantity: number) => {
    if (quantity < 1) return;
    setItems(prev => prev.map(i => (i.id === id ? { ...i, quantity } : i)));
  }, []);

  const clearCart = useCallback(() => {
    setItems([]);
  }, []);

  const itemCount = items.reduce((sum, i) => sum + i.quantity, 0);
  const totalPrice = items.reduce((sum, i) => sum + i.price * i.quantity, 0);

  return (
    <CartContext.Provider
      value={{ items, addItem, removeItem, updateQuantity, clearCart, itemCount, totalPrice }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return ctx;
}
