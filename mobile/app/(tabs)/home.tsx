import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, Platform, ActivityIndicator, Text, RefreshControl, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import * as Haptics from 'expo-haptics';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import Header from '../../components/Header';
import SearchBar from '../../components/SearchBar';
import CategoryPills from '../../components/CategoryPills';

import TrendingSection from '../../components/TrendingSection';
import RecommendedSection from '../../components/RecommendedSection';
import { colors, spacing, typography, borderRadius, shadows } from '../../constants/theme';
import { fetchHomeScreenProducts, Product } from '../../services/api';
import { getPointsBalance } from '../../services/points';
import { authStorage } from '../../lib/authStorage';
import { Image } from 'react-native';

// Dummy data for top-level categories
const topCategories = [
  { id: 'Electronics', name: 'Electronics', imageUrl: 'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=200&h=200&fit=crop' },
  { id: 'Home_Appliances', name: 'Home', imageUrl: 'https://images.unsplash.com/photo-1556020685-e6a42ea1cd14?w=200&h=200&fit=crop' },
  { id: 'perfume', name: 'Beauty', imageUrl: 'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=200&h=200&fit=crop' },
  { id: 'smartwatch', name: 'Sports', imageUrl: 'https://images.unsplash.com/photo-1517649763962-0c623066013b?w=200&h=200&fit=crop' },
  { id: 'phone', name: 'Auto', imageUrl: 'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=200&h=200&fit=crop' },
  { id: 'bottle', name: 'Toys', imageUrl: 'https://images.unsplash.com/photo-1566576912321-d58ddd7a6088?w=200&h=200&fit=crop' },
  { id: 'shirt', name: 'Fashion', imageUrl: 'https://images.unsplash.com/photo-1445205170230-053b83016050?w=200&h=200&fit=crop' },
  { id: 'bag', name: 'Grocery', imageUrl: 'https://images.unsplash.com/photo-1542838132-92c53300491e?w=200&h=200&fit=crop' },
  { id: 'laptop', name: 'Books', imageUrl: 'https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=200&h=200&fit=crop' },
  { id: 'Computer_Accessories', name: 'Health', imageUrl: 'https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=200&h=200&fit=crop' },
];

const quickFilters = [
  { id: 'all', label: 'All' },
  { id: 'phones', label: 'Phones' },
  { id: 'laptops', label: 'Laptops' },
  { id: 'audio', label: 'Audio' },
  { id: 'home', label: 'Home' },
];

const homeCategories = [
  { id: 'tech', name: 'Tech', icon: 'laptop' },
  { id: 'audio', name: 'Audio', icon: 'headset' },
  { id: 'home', name: 'Home', icon: 'home' },
  { id: 'trending', name: 'Trending', icon: 'trending-up' },
];

export default function HomeScreen() {
  const router = useRouter();
  const [activeCategory, setActiveCategory] = useState('Electronics');
  const [pointsBalance, setPointsBalance] = useState<number | undefined>(undefined);
  
  // State for API data
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [bestDeals, setBestDeals] = useState<Product[]>([]);
  const [topPriceDrops, setTopPriceDrops] = useState<Product[]>([]);
  const [techGadgets, setTechGadgets] = useState<Product[]>([]);
  const [audioEssentials, setAudioEssentials] = useState<Product[]>([]);
  const [homeAppliances, setHomeAppliances] = useState<Product[]>([]);

  // Load products on mount
  useEffect(() => {
    loadProducts();
  }, []);

  /**
   * Load home screen products from backend API
   */
  async function loadProducts() {
    try {
      setError(null);
      
      const token = await authStorage.getItemAsync('token');
      if (token) {
        getPointsBalance(token).then(bal => setPointsBalance(bal)).catch(() => setPointsBalance(1250));
      } else {
        setPointsBalance(1250);
      }

      const data = await fetchHomeScreenProducts();
      
      // Update state with real data
      setBestDeals(data.best_deals);
      setTopPriceDrops(data.top_price_drops);
      setTechGadgets(data.tech_gadgets || []);
      setAudioEssentials(data.audio_essentials || []);
      setHomeAppliances(data.home_appliances || []);
    } catch (err: any) {
      console.error('Failed to load home products:', err);
      setError(err.message || 'Unable to load products. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  /**
   * Pull-to-refresh handler
   */
  async function onRefresh() {
    setRefreshing(true);
    await loadProducts();
    setRefreshing(false);
  }

  /**
   * Convert backend Product to UI format for TrendingSection
   */
  const trendingProducts = bestDeals.slice(0, 7).map((p, index) => ({
    id: p.id?.toString() || `trending-${index}`,
    title: p.title,
    imageUrl: p.image_url,
    price: p.price,
    originalPrice: p.original_price,
    discountPercent: p.discount_percent,
    storeName: p.store_name,
  }));

  /**
   * Convert backend Product to UI format for RecommendedSection
   */
  const recommendedProducts = topPriceDrops.slice(0, 7).map((p, index) => ({
    id: p.id?.toString() || `recommended-${index}`,
    title: p.title,
    imageUrl: p.image_url,
    price: p.price,
    originalPrice: p.original_price,
    discountPercent: p.discount_percent,
    storeName: p.store_name,
  }));

  const techProducts = techGadgets.slice(0, 7).map((p, index) => ({
    id: p.id?.toString() || `tech-${index}`,
    title: p.title,
    imageUrl: p.image_url,
    price: p.price,
    originalPrice: p.original_price,
    discountPercent: p.discount_percent,
    storeName: p.store_name,
  }));

  const audioProducts = audioEssentials.slice(0, 7).map((p, index) => ({
    id: p.id?.toString() || `audio-${index}`,
    title: p.title,
    imageUrl: p.image_url,
    price: p.price,
    originalPrice: p.original_price,
    discountPercent: p.discount_percent,
    storeName: p.store_name,
  }));

  const homeProducts = homeAppliances.slice(0, 7).map((p, index) => ({
    id: p.id?.toString() || `home-${index}`,
    title: p.title,
    imageUrl: p.image_url,
    price: p.price,
    originalPrice: p.original_price,
    discountPercent: p.discount_percent,
    storeName: p.store_name,
  }));

  const handleCategoryPress = (categoryId: string) => {
    if (Platform.OS === 'ios') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    setActiveCategory(categoryId);
    
    // Find category name to use as search query
    const category = topCategories.find(c => c.id === categoryId);
    const searchQuery = category ? category.name : categoryId;
    
    // Navigate to search-results to leverage existing DB + Daraz scraping logic
    router.push({
      pathname: '/search-results',
      params: { query: searchQuery, isCategory: 'true' }
    });
  };

  const handleSearchPress = () => {
    router.push('/search');
  };

  const handleVoicePress = () => {
    console.log('Voice search pressed');
  };

  const handleNotificationPress = () => {
    router.push('/notifications');
  };

  const handleQuickFilterPress = (filterId: string) => {
    setActiveCategory(filterId);
    router.push('/search');
  };

  const handleProductPress = (productId: string) => {
    // Find the full product object across all sections
    const allProducts = [
      ...bestDeals,
      ...topPriceDrops,
      ...techGadgets,
      ...audioEssentials,
      ...homeAppliances
    ];
    
    const product = allProducts.find(p => p.id?.toString() === productId);
    
    if (product) {
      const { setGlobalSelectedProduct } = require('../../services/api');
      setGlobalSelectedProduct(product);
      router.push(`/product/${encodeURIComponent(`${product.store_name}-${product.product_url}`)}`);
    } else {
      router.push(`/product/${productId}`);
    }
  };

  const handleSeeAllTrending = () => {
    router.push('/(tabs)/explore');
  };

  const handleSeeAllRecommended = () => {
    router.push('/(tabs)/explore');
  };

  return (
    <SafeAreaView style={styles.safeArea} edges={['top']}>
      <View style={styles.container}>
        {/* Header */}
        <Header
          hasUnreadNotifications={true}
          onNotificationPress={handleNotificationPress}
          balance={pointsBalance}
        />

        {/* Loading State */}
        {loading && (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={colors.primary} />
            <Text style={styles.loadingText}>Loading products...</Text>
          </View>
        )}

        {/* Error State */}
        {!loading && error && (
          <View style={styles.errorContainer}>
            <Text style={styles.errorTitle}>Unable to Load Products</Text>
            <Text style={styles.errorMessage}>{error}</Text>
            <Text style={styles.errorHint}>
              Make sure the backend server is running on http://localhost:8000
            </Text>
          </View>
        )}

        {/* Content - Only show when not loading */}
        {!loading && !error && (
          <ScrollView
            style={styles.scrollView}
            contentContainerStyle={styles.scrollContent}
            showsVerticalScrollIndicator={false}
            bounces={true}
            alwaysBounceVertical={true}
            decelerationRate="normal"
            scrollEventThrottle={16}
            contentInsetAdjustmentBehavior="automatic"
            refreshControl={
              <RefreshControl
                refreshing={refreshing}
                onRefresh={onRefresh}
                tintColor={colors.primary}
                colors={[colors.primary]}
              />
            }
          >
            {/* Search Bar */}
            <SearchBar
              onPress={handleSearchPress}
              onFilterPress={() => console.log('Filter pressed')}
            />

            {/* Categories Section */}
            <View style={styles.sectionHeader}>
              <Text style={styles.sectionTitle}>Category</Text>
              <TouchableOpacity onPress={() => router.push('/(tabs)/explore')}>
                <Text style={styles.seeAllText}>See All</Text>
              </TouchableOpacity>
            </View>
            <View style={styles.categoryScroll}>
              {homeCategories.map((cat) => (
                <TouchableOpacity key={cat.id} style={styles.categoryItem} onPress={() => handleCategoryPress(cat.id)}>
                  <View style={styles.categoryIconCircle}>
                    <Ionicons name={cat.icon as any} size={28} color="#704F38" />
                  </View>
                  <Text style={styles.categoryName}>{cat.name}</Text>
                </TouchableOpacity>
              ))}
            </View>


            {/* Empty State */}
            {bestDeals.length === 0 && topPriceDrops.length === 0 ? (
              <View style={styles.emptyContainer}>
                <Text style={styles.emptyTitle}>No Products Yet</Text>
                <Text style={styles.emptyMessage}>
                  Run the scraper to populate the database with products.
                </Text>
              </View>
            ) : (
              <View style={styles.flashSaleContainer}>
                {/* Deal of the Day (Original first section) */}
                {trendingProducts.length > 0 && (
                  <TrendingSection
                    title="Deal of the Day"
                    items={trendingProducts}
                    onItemPress={handleProductPress}
                    onSeeAllPress={handleSeeAllTrending}
                  />
                )}

                {/* Restored additional categories with sleek horizontal scrolling */}
                {recommendedProducts.length > 0 && (
                  <RecommendedSection
                    title="Trending Today"
                    items={recommendedProducts}
                    onItemPress={handleProductPress}
                    onSeeAllPress={handleSeeAllRecommended}
                  />
                )}
                
                {techProducts.length > 0 && (
                  <TrendingSection
                    title="Tech & Laptops"
                    items={techProducts}
                    onItemPress={handleProductPress}
                    onSeeAllPress={handleSeeAllTrending}
                  />
                )}

                {audioProducts.length > 0 && (
                  <RecommendedSection
                    title="Audio Essentials"
                    items={audioProducts}
                    onItemPress={handleProductPress}
                    onSeeAllPress={handleSeeAllRecommended}
                  />
                )}

                {homeProducts.length > 0 && (
                  <TrendingSection
                    title="Home & Appliances"
                    items={homeProducts}
                    onItemPress={handleProductPress}
                    onSeeAllPress={handleSeeAllTrending}
                  />
                )}
              </View>
            )}
          </ScrollView>
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: colors.white,
  },
  container: {
    flex: 1,
    backgroundColor: colors.white,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 100, // Extra padding to avoid cutting off at bottom tabs
  },
  quickFilterRow: {
    paddingHorizontal: spacing.lg,
    gap: spacing.sm,
    paddingBottom: spacing.sm,
  },
  quickFilterPill: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    backgroundColor: colors.gray100,
    borderRadius: 9999,
  },
  quickFilterPillActive: {
    backgroundColor: colors.gray900,
  },
  quickFilterText: {
    color: colors.gray600,
    fontSize: typography.fontSize.caption,
    fontWeight: typography.fontWeight.semibold,
  },
  quickFilterTextActive: {
    color: colors.white,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: spacing.xl,
  },
  loadingText: {
    marginTop: spacing.md,
    fontSize: typography.fontSize.body,
    color: colors.gray600,
    fontWeight: typography.fontWeight.medium,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: spacing.xl,
  },
  errorTitle: {
    fontSize: typography.fontSize.h2,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
    marginBottom: spacing.sm,
    textAlign: 'center',
  },
  errorMessage: {
    fontSize: typography.fontSize.body,
    color: colors.gray600,
    textAlign: 'center',
    marginBottom: spacing.md,
  },
  errorHint: {
    fontSize: typography.fontSize.small,
    color: colors.gray400,
    textAlign: 'center',
    fontStyle: 'italic',
  },
  emptyContainer: {
    paddingVertical: spacing.xxl * 2,
    paddingHorizontal: spacing.xl,
    alignItems: 'center',
  },
  emptyTitle: {
    fontSize: typography.fontSize.h2,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
    marginBottom: spacing.sm,
    textAlign: 'center',
  },
  emptyMessage: {
    fontSize: typography.fontSize.body,
    color: colors.gray600,
    textAlign: 'center',
    marginBottom: spacing.md,
  },
  emptyHint: {
    fontSize: typography.fontSize.small,
    color: colors.gray400,
    textAlign: 'center',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    marginTop: spacing.sm,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 24,
    marginBottom: 16,
  },
  sectionTitle: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 18,
    color: '#111111',
  },
  seeAllText: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 14,
    color: '#704F38',
  },
  categoryScroll: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 24,
    marginBottom: 32,
  },
  categoryItem: {
    alignItems: 'center',
    gap: 8,
  },
  categoryIconCircle: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#F5EBE1',
    justifyContent: 'center',
    alignItems: 'center',
  },
  categoryName: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 12,
    color: '#111111',
  },
  flashSaleContainer: {
    paddingBottom: 24,
  },
  flashSaleHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 24,
    marginBottom: 16,
  },
  flashSaleTitle: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 18,
    color: '#111111',
  },
  timerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  timerLabel: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 12,
    color: '#757575',
    marginRight: 6,
  },
  timeBox: {
    backgroundColor: '#F5F5F5',
    paddingHorizontal: 6,
    paddingVertical: 4,
    borderRadius: 4,
  },
  timeText: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 12,
    color: '#111111',
  },
  timeColon: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 12,
    color: '#111111',
    marginHorizontal: 4,
  },
  productGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 24,
    justifyContent: 'space-between',
    paddingBottom: 40,
  },
  productCard: {
    width: '48%',
    marginBottom: 16,
    borderRadius: 16,
    backgroundColor: '#FFFFFF',
    overflow: 'hidden',
  },
  productImage: {
    width: '100%',
    aspectRatio: 1, // Square image
    borderRadius: 16,
    backgroundColor: '#F5F5F5',
  },
  productInfo: {
    paddingVertical: 12,
    paddingHorizontal: 4,
  },
  productName: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 14,
    color: '#111111',
    marginBottom: 4,
  },
  productPrice: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 16,
    color: '#111111',
  },
});
