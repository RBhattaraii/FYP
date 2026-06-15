import React, { useState, useMemo } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Image } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { colors, typography, spacing, borderRadius, shadows } from '../../constants/theme';
import { ALL_PRODUCTS } from '../../data/mockData';
import Header from '../../components/Header';

const MOCK_CART = [
  {
    sellerId: 's1',
    sellerName: 'Apple Official Store',
    items: [
      {
        id: 'c1',
        productId: '2',
        name: 'Apple iPad Air (5th Gen)',
        variant: 'Space Gray, 256GB',
        price: 599.00,
        imageUrl: ALL_PRODUCTS[1].images[0],
        stockStatus: 'In Stock',
        quantity: 1,
      }
    ]
  },
  {
    sellerId: 's2',
    sellerName: 'Sony Authorized Dealer',
    items: [
      {
        id: 'c2',
        productId: '1',
        name: 'Sony WH-1000XM4 Headphones',
        variant: 'Black',
        price: 249.99,
        imageUrl: ALL_PRODUCTS[0].images[0],
        stockStatus: 'Only 2 left',
        promoBadge: '5% OFF',
        quantity: 1,
      }
    ]
  },
  {
    sellerId: 's3',
    sellerName: 'Nike Official Store',
    items: [
      {
        id: 'c3',
        productId: '4',
        name: 'Nike Air Max 270',
        variant: 'White/Black, US 10',
        price: 129.99,
        imageUrl: ALL_PRODUCTS[3].images[0],
        stockStatus: 'In Stock',
        quantity: 2,
      }
    ]
  }
];

export default function CartScreen() {
  const [cartData, setCartData] = useState(MOCK_CART);
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());

  const toggleItemSelection = (itemId: string) => {
    setSelectedItems(prev => {
      const next = new Set(prev);
      if (next.has(itemId)) next.delete(itemId);
      else next.add(itemId);
      return next;
    });
  };

  const toggleAllSelection = () => {
    const allItemIds = cartData.flatMap(s => s.items.map(i => i.id));
    const allSelected = allItemIds.every(id => selectedItems.has(id));
    
    if (allSelected) {
      setSelectedItems(new Set());
    } else {
      setSelectedItems(new Set(allItemIds));
    }
  };

  const updateQuantity = (sellerId: string, itemId: string, delta: number) => {
    setCartData(prev => prev.map(seller => {
      if (seller.sellerId !== sellerId) return seller;
      return {
        ...seller,
        items: seller.items.map(item => {
          if (item.id !== itemId) return item;
          const newQuantity = Math.max(1, item.quantity + delta);
          return { ...item, quantity: newQuantity };
        })
      };
    }));
  };

  const totalItems = useMemo(() => cartData.flatMap(s => s.items).length, [cartData]);
  const isAllSelected = totalItems > 0 && selectedItems.size === totalItems;
  
  const subtotal = useMemo(() => {
    let sum = 0;
    cartData.forEach(seller => {
      seller.items.forEach(item => {
        if (selectedItems.has(item.id)) {
          sum += item.price * item.quantity;
        }
      });
    });
    return sum;
  }, [cartData, selectedItems]);
  
  const Checkbox = ({ selected, onPress }: { selected: boolean, onPress: () => void }) => (
    <TouchableOpacity onPress={onPress} style={styles.checkboxContainer} activeOpacity={0.7}>
      <Ionicons 
        name={selected ? "checkmark-circle" : "ellipse-outline"} 
        size={24} 
        color={selected ? colors.primary : colors.gray300} 
      />
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.safeArea} edges={['top']}>
      <Header title="Shopping Cart" />

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {cartData.map(seller => {
          return (
            <View key={seller.sellerId} style={styles.sellerGroup}>
              {/* Seller Header */}
              <View style={styles.sellerHeader}>
                <Ionicons name="storefront-outline" size={18} color={colors.gray900} style={styles.storeIcon} />
                <Text style={styles.sellerName}>{seller.sellerName}</Text>
                <Ionicons name="chevron-forward" size={16} color={colors.gray400} style={styles.chevron} />
              </View>

              {/* Items */}
              {seller.items.map((item, index) => (
                <View key={item.id} style={[styles.itemRow, index === seller.items.length - 1 && styles.lastItemRow]}>
                  <Checkbox selected={selectedItems.has(item.id)} onPress={() => toggleItemSelection(item.id)} />
                  
                  <Image source={{ uri: item.imageUrl }} style={styles.itemImage} />
                  
                  <View style={styles.itemInfo}>
                    <Text style={styles.itemName} numberOfLines={2}>{item.name}</Text>
                    <View style={styles.itemVariantBox}>
                      <Text style={styles.itemVariantText}>{item.variant}</Text>
                      <Ionicons name="chevron-down" size={12} color={colors.gray600} />
                    </View>
                    
                    {item.promoBadge && (
                      <View style={styles.promoBadge}>
                        <Text style={styles.promoBadgeText}>{item.promoBadge}</Text>
                      </View>
                    )}
                    
                    <Text style={[styles.stockText, item.stockStatus.includes('left') && styles.lowStockText]}>
                      {item.stockStatus}
                    </Text>

                    <View style={styles.priceRow}>
                      <Text style={styles.itemPrice}>${item.price.toFixed(2)}</Text>
                      
                      {/* Quantity Controls */}
                      <View style={styles.quantityControls}>
                        <TouchableOpacity onPress={() => updateQuantity(seller.sellerId, item.id, -1)} style={styles.quantityBtn}>
                          <Ionicons name="remove" size={16} color={item.quantity > 1 ? colors.gray900 : colors.gray400} />
                        </TouchableOpacity>
                        <Text style={styles.quantityText}>{item.quantity}</Text>
                        <TouchableOpacity onPress={() => updateQuantity(seller.sellerId, item.id, 1)} style={styles.quantityBtn}>
                          <Ionicons name="add" size={16} color={colors.gray900} />
                        </TouchableOpacity>
                      </View>
                    </View>
                  </View>
                </View>
              ))}
            </View>
          );
        })}
      </ScrollView>

      {/* Sticky Bottom Summary */}
      <View style={styles.bottomSummary}>
        <View style={styles.summaryLeft}>
           <Checkbox selected={isAllSelected} onPress={toggleAllSelection} />
           <Text style={styles.selectAllText}>All</Text>
        </View>
        <View style={styles.summaryRight}>
           <View style={styles.totalsContainer}>
             <Text style={styles.totalLabel}>Total</Text>
             <Text style={styles.totalPrice}>${subtotal.toFixed(2)}</Text>
           </View>
           <TouchableOpacity 
             style={[styles.checkoutBtn, selectedItems.size === 0 && styles.checkoutBtnDisabled]}
             activeOpacity={0.8}
             disabled={selectedItems.size === 0}
           >
              <Text style={styles.checkoutBtnText}>Check Out ({selectedItems.size})</Text>
           </TouchableOpacity>
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: colors.gray50,
  },
  scrollContent: {
    paddingVertical: spacing.md,
    paddingBottom: 100, // Extra space for the fixed bottom summary
  },
  sellerGroup: {
    backgroundColor: colors.white,
    marginBottom: spacing.md,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: colors.gray100,
  },
  sellerHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
    paddingBottom: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.gray50,
  },
  checkboxContainer: {
    marginRight: spacing.sm,
    padding: spacing.xs,
  },
  storeIcon: {
    marginRight: spacing.xs,
  },
  sellerName: {
    fontSize: typography.fontSize.bodyLarge,
    fontWeight: typography.fontWeight.semibold,
    color: colors.gray900,
  },
  chevron: {
    marginLeft: 'auto',
  },
  itemRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: spacing.lg,
  },
  lastItemRow: {
    marginBottom: 0,
  },
  itemImage: {
    width: 80,
    height: 80,
    borderRadius: borderRadius.small,
    backgroundColor: colors.gray100,
    marginRight: spacing.md,
  },
  itemInfo: {
    flex: 1,
  },
  itemName: {
    fontSize: typography.fontSize.body,
    fontWeight: typography.fontWeight.medium,
    color: colors.gray900,
    marginBottom: spacing.xs,
  },
  itemVariantBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.gray50,
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: borderRadius.small,
    alignSelf: 'flex-start',
    marginBottom: spacing.xs,
  },
  itemVariantText: {
    fontSize: typography.fontSize.caption,
    color: colors.gray600,
    marginRight: 4,
  },
  promoBadge: {
    backgroundColor: colors.warningOrange + '1A',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
    alignSelf: 'flex-start',
    marginBottom: 4,
  },
  promoBadgeText: {
    fontSize: 10,
    fontWeight: typography.fontWeight.bold,
    color: colors.warningOrange,
  },
  stockText: {
    fontSize: typography.fontSize.caption,
    color: colors.gray600,
    marginBottom: spacing.xs,
  },
  lowStockText: {
    color: colors.errorRed,
    fontWeight: typography.fontWeight.medium,
  },
  priceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: spacing.xs,
  },
  itemPrice: {
    fontSize: typography.fontSize.h3,
    fontWeight: typography.fontWeight.bold,
    color: colors.indigoPrimary,
  },
  quantityControls: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.gray200,
    borderRadius: borderRadius.small,
  },
  quantityBtn: {
    padding: 6,
  },
  quantityText: {
    fontSize: typography.fontSize.body,
    fontWeight: typography.fontWeight.medium,
    color: colors.gray900,
    width: 24,
    textAlign: 'center',
  },
  bottomSummary: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: colors.white,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.gray100,
    ...shadows.featuredCard,
  },
  summaryLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  selectAllText: {
    fontSize: typography.fontSize.body,
    fontWeight: typography.fontWeight.medium,
    color: colors.gray600,
  },
  summaryRight: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  totalsContainer: {
    alignItems: 'flex-end',
    marginRight: spacing.md,
  },
  totalLabel: {
    fontSize: typography.fontSize.caption,
    color: colors.gray600,
  },
  totalPrice: {
    fontSize: typography.fontSize.h2,
    fontWeight: typography.fontWeight.bold,
    color: colors.indigoPrimary,
  },
  checkoutBtn: {
    backgroundColor: colors.gray900,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderRadius: borderRadius.full,
  },
  checkoutBtnDisabled: {
    backgroundColor: colors.gray300,
  },
  checkoutBtnText: {
    color: colors.white,
    fontSize: typography.fontSize.body,
    fontWeight: typography.fontWeight.bold,
  },
});
