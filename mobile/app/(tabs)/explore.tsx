import React, { useState, useEffect } from 'react';
import { View, StyleSheet, FlatList, TouchableOpacity, Text, Platform, useWindowDimensions, Image, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import * as Haptics from 'expo-haptics';
import { Ionicons } from '@expo/vector-icons';

import Header from '../../components/Header';
import ProductCard from '../../components/ProductCard';
import { colors, spacing, typography } from '../../constants/theme';

import { searchProducts, Product } from '../../services/api';
import { useFavorites } from '../../context/FavoritesContext';

const BRANDS = [
  { id: 'hukut', name: 'Hukut', label: 'H', color: '#FF4757' },
  { id: 'koreanbp', name: 'KoreanBP', label: 'KB', color: '#2ED573' },
  { id: 'oliz', name: 'Oliz', label: 'O', color: '#FFA502' },
  { id: 'cgdigital', name: 'CG Digital', label: 'CG', color: '#FF6348' },
];

export default function BrandsScreen() {
  const router = useRouter();
  const { width } = useWindowDimensions();
  const numColumns = width > 768 ? 4 : (width > 480 ? 3 : 2);
  
  const { items: favoriteItems, addItem, removeItem } = useFavorites();

  const [activeBrand, setActiveBrand] = useState(BRANDS[0]);
  const [products, setProducts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [totalResults, setTotalResults] = useState(0);
  const [page, setPage] = useState(1);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);

  useEffect(() => {
    loadBrandProducts(activeBrand.name, 1);
  }, [activeBrand]);

  const loadBrandProducts = async (brandName: string, pageNum = 1) => {
    try {
      if (pageNum === 1) setLoading(true);
      else setLoadingMore(true);
      
      const data = await searchProducts(brandName, pageNum, 20); // Changed to 20 per page for better infinite scroll feel
      
      const formatted = data.results.map((p: Product) => ({
        id: p.id ? p.id.toString() : p.title,
        name: p.title,
        price: p.price,
        imageUrl: p.image_url,
        inWishlist: false,
        promotionalBadge: p.discount_percent ? `${p.discount_percent}% OFF` : undefined,
        _original: p, 
      }));

      if (pageNum === 1) {
        setProducts(formatted);
      } else {
        setProducts(prev => [...prev, ...formatted]);
      }

      setTotalResults(data.total_results || data.results_count || formatted.length);
      setHasMore(formatted.length === 20);
      setPage(pageNum);
    } catch (err) {
      console.error('Failed to load brand products:', err);
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  const handleBrandPress = (brand: typeof BRANDS[0]) => {
    if (Platform.OS === 'ios') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    setActiveBrand(brand);
  };

  const handleProductPress = (id: string) => {
    const p = products.find(prod => prod.id === id);
    if (p?._original) {
      const { setGlobalSelectedProduct } = require('../../services/api');
      setGlobalSelectedProduct(p._original);
      router.push(`/product/${encodeURIComponent(`${p._original.store_name}-${p._original.product_url}`)}`);
    } else {
      router.push(`/product/${id}`);
    }
  };

  const handleAddPress = (id: string) => {
    const p = products.find(prod => prod.id === id);
    if (!p) return;
    
    const favId = p._original ? `${p._original.store_name}-${p._original.product_url}` : p.id;
    const isFav = favoriteItems.some(f => f.id === favId);
    
    if (isFav) {
      removeItem(favId);
    } else {
      addItem({
        id: favId,
        productId: p._original?.id,
        title: p.name,
        price: p.price,
        originalPrice: p._original?.original_price,
        discountPercent: p._original?.discount_percent,
        imageUrl: p.imageUrl,
        storeName: p._original?.store_name || activeBrand.name,
        productUrl: p._original?.product_url || ''
      });
    }
  };

  const renderHeader = () => (
    <View>
      <View style={styles.headerRow}>
        <TouchableOpacity 
          style={styles.headerIcon}
          onPress={() => router.push('/home')}
        >
          <Ionicons name="arrow-back" size={20} color={'#111111'} />
        </TouchableOpacity>
        <Text style={styles.pageTitle}>Top Brands & Stores</Text>
      </View>

      <View style={styles.titleContainer}>
        <Text style={styles.pageSubtitle}>Discover products directly from your favorite local retailers.</Text>
      </View>
      
      <View style={styles.brandsContainer}>
        <FlatList
          horizontal
          showsHorizontalScrollIndicator={false}
          data={BRANDS}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.brandsContent}
          renderItem={({ item }) => {
            const isActive = activeBrand.id === item.id;
            return (
              <TouchableOpacity
                style={styles.brandPillContainer}
                onPress={() => handleBrandPress(item)}
                activeOpacity={0.7}
              >
                <View style={[
                  styles.brandCircle, 
                  isActive ? styles.brandCircleActive : { backgroundColor: item.color + '20' }
                ]}>
                  <Text style={[
                    styles.brandInitials, 
                    isActive ? { color: '#FFFFFF' } : { color: item.color }
                  ]}>
                    {item.label}
                  </Text>
                </View>
                <Text style={[styles.brandName, isActive && styles.brandNameActive]}>
                  {item.name}
                </Text>
              </TouchableOpacity>
            );
          }}
        />
      </View>
      
      <View style={styles.resultsHeader}>
        <Text style={styles.resultsTitle}>Latest from {activeBrand.name}</Text>
        <Text style={styles.resultsCount}>{totalResults} products</Text>
      </View>
    </View>
  );

  return (
    <SafeAreaView style={styles.safeArea} edges={['top']}>
      {loading ? (
        <View style={styles.loadingContainer}>
          {renderHeader()}
          <View style={styles.loaderWrapper}>
            <ActivityIndicator size="large" color="#111111" />
          </View>
        </View>
      ) : (
        <FlatList
          key={numColumns}
          data={products}
          keyExtractor={(item) => item.id}
          numColumns={numColumns}
          ListHeaderComponent={renderHeader}
          contentContainerStyle={styles.gridContent}
          columnWrapperStyle={[
            styles.columnWrapper,
            numColumns > 2 && { justifyContent: 'flex-start', gap: spacing.md }
          ]}
          showsVerticalScrollIndicator={false}
          onEndReached={() => {
            if (hasMore && !loadingMore) {
              loadBrandProducts(activeBrand.name, page + 1);
            }
          }}
          onEndReachedThreshold={0.5}
          ListFooterComponent={
            loadingMore ? (
              <View style={styles.footerLoader}>
                <ActivityIndicator size="small" color="#111111" />
              </View>
            ) : null
          }
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text style={styles.emptyTitle}>No Products Found</Text>
              <Text style={styles.emptyMessage}>We couldn't find any products for {activeBrand.name}.</Text>
            </View>
          }
          renderItem={({ item }) => {
            const favId = item._original ? `${item._original.store_name}-${item._original.product_url}` : item.id;
            const isFav = favoriteItems.some(f => f.id === favId);
            return (
              <View style={styles.cardWrapper}>
                <ProductCard 
                  product={{...item, inWishlist: isFav}} 
                  onPress={() => handleProductPress(item.id)}
                  onAddPress={() => handleAddPress(item.id)}
                />
              </View>
            );
          }}
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: colors.white,
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.sm,
    marginTop: spacing.sm,
  },
  headerIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#EEEEEE',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    marginRight: spacing.md,
  },
  titleContainer: {
    paddingHorizontal: spacing.lg,
    marginTop: spacing.sm,
    marginBottom: spacing.md,
  },
  pageTitle: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 18,
    color: '#111111',
  },
  pageSubtitle: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 14,
    color: '#757575',
    marginTop: 4,
  },
  brandsContainer: {
    marginBottom: spacing.lg,
  },
  brandsContent: {
    paddingHorizontal: spacing.lg,
    gap: spacing.md,
  },
  brandPillContainer: {
    alignItems: 'center',
    marginRight: spacing.sm,
    width: 72,
  },
  brandCircle: {
    width: 64,
    height: 64,
    borderRadius: 32,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  brandCircleActive: {
    backgroundColor: '#111111',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 4,
  },
  brandInitials: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 20,
  },
  brandName: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 12,
    color: '#757575',
    textAlign: 'center',
  },
  brandNameActive: {
    color: '#111111',
    fontFamily: 'Poppins_600SemiBold',
  },
  resultsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    marginBottom: spacing.md,
  },
  resultsTitle: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 18,
    color: '#111111',
  },
  resultsCount: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 13,
    color: '#9E9E9E',
  },
  gridContent: {
    paddingBottom: 100, // Extra padding for bottom navigation
  },
  columnWrapper: {
    justifyContent: 'space-between',
    paddingHorizontal: spacing.md,
    marginBottom: spacing.lg,
  },
  cardWrapper: {
    alignItems: 'center',
  },
  loadingContainer: {
    flex: 1,
  },
  loaderWrapper: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 60,
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingTop: 60,
  },
  emptyTitle: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 18,
    color: '#111111',
    marginBottom: 8,
  },
  emptyMessage: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 14,
    color: '#757575',
    textAlign: 'center',
  },
  footerLoader: {
    paddingVertical: 20,
    alignItems: 'center',
  }
});
