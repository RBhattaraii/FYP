import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Image,
  ActivityIndicator,
  Alert,
  TextInput,
  ScrollView,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams, Stack } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { colors, spacing, typography, borderRadius, shadows } from '../constants/theme';
import { searchForComparison, quickCompareProducts, Product } from '../services/api';
import { authStorage } from '../lib/authStorage';
import DealCard from '../components/DealCard';

export default function CompareSearchScreen() {
  const router = useRouter();
  const { productData } = useLocalSearchParams();
  const [currentProduct, setCurrentProduct] = useState<Product | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [comparing, setComparing] = useState(false);
  const [searched, setSearched] = useState(false);
  
  const [recommendations, setRecommendations] = useState<Product[]>([]);
  const [loadingRecs, setLoadingRecs] = useState(false);

  useEffect(() => {
    const { globalSelectedProduct, setGlobalSelectedProduct } = require('../services/api');
    
    if (globalSelectedProduct) {
      setCurrentProduct({ ...globalSelectedProduct });
      // clear it to avoid leaking
      setGlobalSelectedProduct(null);
    } else if (productData && typeof productData === 'string') {
      try {
        const product = JSON.parse(productData);
        setCurrentProduct(product);
      } catch (e) {
        console.error('Failed to parse product data:', e);
        Alert.alert('Error', 'Invalid product data');
        router.back();
      }
    }
  }, [productData, router]);

  useEffect(() => {
    if (currentProduct?.id && !searched && recommendations.length === 0) {
      const fetchRecs = async () => {
        setLoadingRecs(true);
        try {
          const token = (await authStorage.getItemAsync('token')) || '';
          let keywords = currentProduct.category;
          if (!keywords || keywords === 'Uncategorized') {
            keywords = currentProduct.title.split(' ').slice(0, 2).join(' ');
          }
          const response = await searchForComparison(token, keywords, [currentProduct.id], 8);
          setRecommendations(response.results);
        } catch (error) {
          console.warn('Failed to fetch recommendations:', error);
        } finally {
          setLoadingRecs(false);
        }
      };
      fetchRecs();
    }
  }, [currentProduct, searched]);

  const searchProducts = async () => {
    if (!searchQuery.trim()) {
      Alert.alert('Error', 'Please enter a search query');
      return;
    }

    if (!currentProduct?.id) {
      Alert.alert('Error', 'Current product information is missing');
      return;
    }

    setLoading(true);
    setSearched(true);
    try {
      const token = (await authStorage.getItemAsync('token')) || '';

      const response = await searchForComparison(
        token,
        searchQuery.trim(),
        [currentProduct.id], // Exclude current product
        20
      );

      setSearchResults(response.results);
    } catch (error: any) {
      console.error('Search failed:', error);
      Alert.alert('Error', error.message || 'Search failed');
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleProductSelect = async (selectedProduct: Product) => {
    if (!currentProduct) {
      Alert.alert('Error', 'Current product information is missing');
      return;
    }

    setComparing(true);
    try {
      const token = (await authStorage.getItemAsync('token')) || '';
      let comparisonObj: any = null;

      // Only attempt API compare if BOTH have valid database IDs
      if (currentProduct.id && selectedProduct.id && currentProduct.id > 0 && selectedProduct.id > 0) {
        try {
          comparisonObj = await quickCompareProducts(
            token,
            currentProduct.id,
            selectedProduct.id
          );
        } catch (apiError: any) {
          console.warn('API quick compare failed, falling back to manual:', apiError);
        }
      }

      // Fallback to manual comparison if API failed or skipped
      if (!comparisonObj) {
        const p1Price = currentProduct.price || 0;
        const p2Price = selectedProduct.price || 0;
        comparisonObj = {
          product1: currentProduct,
          product2: selectedProduct,
          comparison: {
            price_difference: Math.abs(p1Price - p2Price),
            better_deal: p1Price <= p2Price ? 'product1' : 'product2',
            discount_comparison: (currentProduct.discount_percent || 0) - (selectedProduct.discount_percent || 0)
          }
        };
      }

      // Set global variable to avoid URL truncation on Web
      const { setGlobalComparisonData } = require('../services/api');
      setGlobalComparisonData(comparisonObj);

      // Navigate to comparison result
      router.push('/compare-result');
    } catch (error: any) {
      console.error('Comparison failed:', error);
      Alert.alert('Error', error.message || 'Failed to compare products');
    } finally {
      setComparing(false);
    }
  };

  const renderSearchResult = ({ item }: { item: Product }) => (
    <View style={styles.gridItem}>
      <DealCard
        title={item.title}
        imageUrl={item.image_url || 'https://via.placeholder.com/150'}
        price={item.price}
        originalPrice={item.original_price}
        discountPercent={item.discount_percent}
        storeName={item.store_name}
        width="100%"
        onPress={() => handleProductSelect(item)}
      />
    </View>
  );

  if (!currentProduct) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <Stack.Screen options={{ headerShown: false }} />
      
      <View style={styles.topSection}>
        {/* Current Product Header */}
        <View style={styles.currentProduct}>
          <TouchableOpacity style={styles.headerIcon} onPress={() => router.back()}>
            <Ionicons name="arrow-back" size={24} color={colors.gray900} />
          </TouchableOpacity>
          
          <View style={styles.currentProductTextContainer}>
            <Text style={styles.currentProductLabel}>Comparing with:</Text>
            <Text style={styles.currentProductTitle} numberOfLines={1}>
              {currentProduct.title}
            </Text>
            <Text style={styles.currentProductPrice}>
              Rs {currentProduct.price.toLocaleString()} • {currentProduct.store_name}
            </Text>
          </View>
        </View>

        {/* Search Bar */}
        <View style={styles.searchContainer}>
          <View style={styles.searchBar}>
            <Ionicons name="search-outline" size={20} color={colors.gray400} />
            <TextInput
              style={styles.searchInput}
              placeholder="Search for products to compare..."
              placeholderTextColor={colors.gray400}
              value={searchQuery}
              onChangeText={setSearchQuery}
              onSubmitEditing={searchProducts}
              returnKeyType="search"
              autoCapitalize="none"
              autoCorrect={false}
            />
            {searchQuery.length > 0 && (
              <TouchableOpacity onPress={() => setSearchQuery('')}>
                <Ionicons name="close-circle" size={20} color={colors.gray400} />
              </TouchableOpacity>
            )}
          </View>
          <TouchableOpacity 
            style={[styles.searchButton, loading && styles.searchButtonDisabled]}
            onPress={searchProducts}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator size="small" color={colors.white} />
            ) : (
              <Text style={styles.searchButtonText}>Search</Text>
            )}
          </TouchableOpacity>
        </View>
      </View>

      {/* Results */}
      {loading && !searched ? (
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={styles.loadingText}>Searching products...</Text>
        </View>
      ) : searched && searchResults.length === 0 ? (
        <View style={styles.centerContainer}>
          <Ionicons name="search-outline" size={64} color={colors.gray400} />
          <Text style={styles.emptyTitle}>No Products Found</Text>
          <Text style={styles.emptyMessage}>
            Try searching with different keywords or product names.
          </Text>
        </View>
      ) : searched ? (
        <FlatList
          data={searchResults}
          renderItem={renderSearchResult}
          keyExtractor={(item) => item.id?.toString() || item.product_url}
          contentContainerStyle={styles.listContainer}
          showsVerticalScrollIndicator={false}
          numColumns={2}
          columnWrapperStyle={styles.columnWrapper}
          ListHeaderComponent={
            searchResults.length > 0 ? (
              <View style={styles.resultsHeader}>
                <Ionicons name="checkmark-circle-outline" size={20} color="#6E4B3A" />
                <Text style={styles.resultsText}>
                  Found {searchResults.length} products to compare
                </Text>
              </View>
            ) : null
          }
        />
      ) : (
        <ScrollView style={styles.recommendationsContainer} showsVerticalScrollIndicator={false}>
          <View style={styles.recommendationsHeader}>
            <Ionicons name="sparkles" size={18} color="#D4AF37" />
            <Text style={styles.recommendationsTitle}>Recommended for Comparison</Text>
          </View>
          
          {loadingRecs ? (
            <ActivityIndicator style={{ marginTop: spacing.xl }} color="#6E4B3A" />
          ) : recommendations.length > 0 ? (
            <View style={styles.recommendationsGrid}>
              {recommendations.map((item) => (
                <View key={item.id?.toString() || item.product_url} style={styles.gridItem}>
                  <DealCard
                    title={item.title}
                    imageUrl={item.image_url || 'https://via.placeholder.com/150'}
                    price={item.price}
                    originalPrice={item.original_price}
                    discountPercent={item.discount_percent}
                    storeName={item.store_name}
                    width="100%"
                    onPress={() => handleProductSelect(item)}
                  />
                </View>
              ))}
            </View>
          ) : (
            <View style={styles.noRecommendationsContainer}>
              <Text style={styles.noRecommendationsText}>Search above to find products to compare</Text>
            </View>
          )}
        </ScrollView>
      )}

      {/* Loading Overlay for Comparison */}
      {comparing && (
        <View style={styles.loadingOverlay}>
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={colors.primary} />
            <Text style={styles.loadingText}>Comparing products...</Text>
          </View>
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.gray50,
  },
  topSection: {
    backgroundColor: '#F9F6F0',
    borderBottomWidth: 1,
    borderBottomColor: colors.gray200,
    paddingBottom: spacing.lg,
  },
  currentProduct: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.lg,
    gap: spacing.md,
  },
  headerIcon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.white,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.gray200,
  },
  currentProductTextContainer: {
    flex: 1,
  },
  centerContainer: {
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
  emptyTitle: {
    fontSize: typography.fontSize.h2,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
    marginTop: spacing.lg,
    marginBottom: spacing.sm,
    textAlign: 'center',
  },
  emptyMessage: {
    fontSize: typography.fontSize.body,
    color: colors.gray600,
    textAlign: 'center',
    marginBottom: spacing.lg,
    paddingHorizontal: spacing.lg,
  },

  currentProductLabel: {
    fontSize: typography.fontSize.caption,
    color: colors.gray600,
    fontWeight: typography.fontWeight.semibold,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: spacing.xs,
  },
  currentProductTitle: {
    fontSize: typography.fontSize.body,
    fontWeight: typography.fontWeight.semibold,
    color: colors.gray900,
    marginBottom: spacing.xs,
  },
  currentProductPrice: {
    fontSize: typography.fontSize.bodyLarge,
    fontWeight: typography.fontWeight.bold,
    color: '#6E4B3A',
  },
  searchContainer: {
    flexDirection: 'row',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: colors.white,
    borderBottomWidth: 1,
    borderBottomColor: colors.gray200,
    alignItems: 'center',
  },
  searchBar: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.gray50,
    borderRadius: borderRadius.full,
    paddingHorizontal: spacing.md,
    height: 48,
    marginRight: spacing.md,
  },
  searchInput: {
    flex: 1,
    fontSize: typography.fontSize.body,
    color: colors.gray900,
    marginLeft: spacing.sm,
  },
  productUrl: {
    fontSize: typography.fontSize.small,
    color: colors.primary,
    marginTop: spacing.xs,
  },
  recommendationsContainer: {
    flex: 1,
    paddingTop: spacing.lg,
    backgroundColor: colors.white,
  },
  recommendationsHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.xl,
    marginBottom: spacing.md,
  },
  recommendationsTitle: {
    fontSize: typography.fontSize.h3,
    fontWeight: typography.fontWeight.semibold,
    color: colors.gray900,
    marginLeft: spacing.sm,
  },
  recommendationsList: {
    paddingHorizontal: spacing.xl,
    paddingBottom: spacing.xxl,
  },
  recommendationsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: spacing.lg,
    justifyContent: 'space-between',
    paddingBottom: spacing.xxl,
  },
  gridItem: {
    width: '48%',
    marginBottom: spacing.lg,
  },
  noRecommendationsContainer: {
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.xxl,
    alignItems: 'center',
  },
  noRecommendationsText: {
    fontSize: typography.fontSize.body,
    color: colors.gray500,
    fontStyle: 'italic',
  },
  searchButton: {
    backgroundColor: '#6E4B3A',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.full,
    minWidth: 80,
    alignItems: 'center',
    justifyContent: 'center',
  },
  searchButtonDisabled: {
    backgroundColor: colors.gray400,
  },
  searchButtonText: {
    color: colors.white,
    fontSize: typography.fontSize.button,
    fontWeight: typography.fontWeight.semibold,
  },
  resultsHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.md,
    marginBottom: spacing.sm,
  },
  resultsText: {
    fontSize: typography.fontSize.body,
    color: '#6E4B3A',
    marginLeft: spacing.sm,
    fontWeight: typography.fontWeight.medium,
  },
  listContainer: {
    padding: spacing.lg,
  },
  columnWrapper: {
    justifyContent: 'space-between',
  },
  productCard: {
    flexDirection: 'row',
    backgroundColor: colors.white,
    borderRadius: borderRadius.large,
    padding: spacing.md,
    marginBottom: spacing.md,
    ...shadows.card,
    borderWidth: 1,
    borderColor: colors.gray100,
    alignItems: 'center',
  },
  imageContainer: {
    width: 80,
    height: 80,
    borderRadius: borderRadius.small,
    overflow: 'hidden',
    backgroundColor: colors.gray50,
    borderWidth: 1,
    borderColor: colors.gray100,
  },
  productImage: {
    width: '100%',
    height: '100%',
  },
  discountBadge: {
    position: 'absolute',
    top: 0,
    right: 0,
    backgroundColor: colors.errorRed,
    paddingHorizontal: 4,
    paddingVertical: 2,
    borderBottomLeftRadius: borderRadius.small,
  },
  discountText: {
    color: colors.white,
    fontSize: 10,
    fontWeight: typography.fontWeight.bold,
  },
  productInfo: {
    flex: 1,
    marginLeft: spacing.md,
  },
  productTitle: {
    fontSize: typography.fontSize.small,
    fontWeight: typography.fontWeight.medium,
    color: colors.gray900,
    marginBottom: 2,
  },
  storeName: {
    fontSize: typography.fontSize.caption,
    color: colors.gray500,
    marginBottom: spacing.xs,
  },
  priceRow: {
    flexDirection: 'row',
    alignItems: 'baseline',
    flexWrap: 'wrap',
    gap: spacing.xs,
  },
  productPrice: {
    fontSize: typography.fontSize.body,
    fontWeight: typography.fontWeight.bold,
    color: '#6E4B3A',
  },
  originalPrice: {
    fontSize: typography.fontSize.caption,
    color: colors.gray400,
    textDecorationLine: 'line-through',
  },
  compareButtonAction: {
    backgroundColor: '#6E4B3A',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.medium,
    marginLeft: spacing.sm,
  },
  compareButtonActionText: {
    fontSize: typography.fontSize.caption,
    color: colors.white,
    fontWeight: typography.fontWeight.bold,
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingContainer: {
    backgroundColor: colors.white,
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.lg,
    borderRadius: borderRadius.medium,
    alignItems: 'center',
    ...shadows.card,
  },
});