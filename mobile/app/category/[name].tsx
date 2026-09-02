import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  TouchableOpacity,
  FlatList,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { getCategoryProducts, type CategoryProductsResponse } from '../../services/categories';
import ProductCard from '../../components/ProductCard';
import FilterModal from '../../components/FilterModal';
import SortModal from '../../components/SortModal';
import { colors, typography, spacing, borderRadius } from '../../constants/theme';
import type { Product } from '../../services/api';

export default function CategoryScreen() {
  const router = useRouter();
  const { name } = useLocalSearchParams<{ name: string }>();
  
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [products, setProducts] = useState<Product[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalResults, setTotalResults] = useState(0);
  const [error, setError] = useState<string | null>(null);
  
  // Filter and sort state
  const [sortBy, setSortBy] = useState<'deal_score' | 'price_asc' | 'price_desc' | 'newest'>('deal_score');
  const [minPrice, setMinPrice] = useState<number | undefined>();
  const [maxPrice, setMaxPrice] = useState<number | undefined>();
  const [selectedStore, setSelectedStore] = useState<string | undefined>();
  const [minDiscount, setMinDiscount] = useState<number | undefined>();
  
  // Modal visibility
  const [filterModalVisible, setFilterModalVisible] = useState(false);
  const [sortModalVisible, setSortModalVisible] = useState(false);

  // Capitalize category name for display
  const categoryDisplayName = name ? name.charAt(0).toUpperCase() + name.slice(1) : 'Category';

  useEffect(() => {
    if (name) {
      loadProducts();
    }
  }, [name, page, sortBy, minPrice, maxPrice, selectedStore, minDiscount]);

  async function loadProducts() {
    try {
      setError(null);
      const response = await getCategoryProducts(name, {
        page,
        limit: 20,
        sort_by: sortBy,
        min_price: minPrice,
        max_price: maxPrice,
        store: selectedStore,
        min_discount: minDiscount,
      });
      
      setProducts(response.results);
      setTotalPages(response.total_pages);
      setTotalResults(response.total_results);
    } catch (err: any) {
      console.error('Failed to load category products:', err);
      setError(err.message || 'Unable to load products. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  async function onRefresh() {
    setRefreshing(true);
    setPage(1);
    await loadProducts();
    setRefreshing(false);
  }

  function handleBackPress() {
    router.back();
  }

  function handleProductPress(productId: string) {
    router.push(`/product/${productId}`);
  }

  function handleFilterPress() {
    setFilterModalVisible(true);
  }

  function handleSortPress() {
    setSortModalVisible(true);
  }

  function handleApplyFilters(filters: any) {
    setMinPrice(filters.minPrice);
    setMaxPrice(filters.maxPrice);
    setSelectedStore(filters.store);
    setMinDiscount(filters.minDiscount);
    setPage(1);
    setFilterModalVisible(false);
  }

  function handleApplySort(sort: string) {
    setSortBy(sort as any);
    setPage(1);
    setSortModalVisible(false);
  }

  function handleNextPage() {
    if (page < totalPages) {
      setPage(page + 1);
    }
  }

  function handlePrevPage() {
    if (page > 1) {
      setPage(page - 1);
    }
  }

  const renderProduct = ({ item, index }: { item: Product; index: number }) => (
    <View style={[styles.productCard, index % 2 === 0 ? styles.productCardLeft : styles.productCardRight]}>
      <ProductCard
        product={{
          id: item.id?.toString() || '',
          name: item.title,
          imageUrl: item.image_url,
          price: item.price,
          inWishlist: false,
          storeCount: 3,
        }}
        onPress={() => handleProductPress(item.id?.toString() || '')}
        onAddPress={() => console.log('Add to wishlist:', item.id)}
      />
    </View>
  );

  return (
    <SafeAreaView style={styles.safeArea} edges={['top']}>
      <View style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={handleBackPress} style={styles.backButton}>
            <Ionicons name="arrow-back" size={24} color={colors.gray900} />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>{categoryDisplayName}</Text>
          <View style={styles.headerRight} />
        </View>

        {/* Filter & Sort Bar */}
        <View style={styles.filterBar}>
          <TouchableOpacity style={styles.filterButton} onPress={handleSortPress}>
            <Ionicons name="swap-vertical" size={18} color={colors.gray700} />
            <Text style={styles.filterButtonText}>Sort</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.filterButton} onPress={handleFilterPress}>
            <Ionicons name="options-outline" size={18} color={colors.gray700} />
            <Text style={styles.filterButtonText}>Filter</Text>
          </TouchableOpacity>

          <View style={styles.resultCount}>
            <Text style={styles.resultCountText}>
              {loading ? '...' : `${totalResults} products`}
            </Text>
          </View>
        </View>

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
            <Ionicons name="alert-circle-outline" size={64} color={colors.gray400} />
            <Text style={styles.errorTitle}>Unable to Load Products</Text>
            <Text style={styles.errorMessage}>{error}</Text>
            <TouchableOpacity style={styles.retryButton} onPress={loadProducts}>
              <Text style={styles.retryButtonText}>Retry</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* Empty State */}
        {!loading && !error && products.length === 0 && (
          <View style={styles.emptyContainer}>
            <Ionicons name="cube-outline" size={64} color={colors.gray400} />
            <Text style={styles.emptyTitle}>No Products Found</Text>
            <Text style={styles.emptyMessage}>
              Try adjusting your filters or check back later.
            </Text>
          </View>
        )}

        {/* Products Grid */}
        {!loading && !error && products.length > 0 && (
          <FlatList
            data={products}
            renderItem={renderProduct}
            keyExtractor={(item, index) => item.id?.toString() || `product-${index}`}
            numColumns={2}
            contentContainerStyle={styles.productList}
            showsVerticalScrollIndicator={false}
            refreshControl={
              <RefreshControl
                refreshing={refreshing}
                onRefresh={onRefresh}
                tintColor={colors.primary}
                colors={[colors.primary]}
              />
            }
            ListFooterComponent={
              totalPages > 1 ? (
                <View style={styles.pagination}>
                  <TouchableOpacity
                    style={[styles.pageButton, page === 1 && styles.pageButtonDisabled]}
                    onPress={handlePrevPage}
                    disabled={page === 1}
                  >
                    <Ionicons
                      name="chevron-back"
                      size={20}
                      color={page === 1 ? colors.gray400 : colors.primary}
                    />
                  </TouchableOpacity>

                  <Text style={styles.pageInfo}>
                    Page {page} of {totalPages}
                  </Text>

                  <TouchableOpacity
                    style={[styles.pageButton, page === totalPages && styles.pageButtonDisabled]}
                    onPress={handleNextPage}
                    disabled={page === totalPages}
                  >
                    <Ionicons
                      name="chevron-forward"
                      size={20}
                      color={page === totalPages ? colors.gray400 : colors.primary}
                    />
                  </TouchableOpacity>
                </View>
              ) : null
            }
          />
        )}

        {/* Filter Modal */}
        <FilterModal
          visible={filterModalVisible}
          onClose={() => setFilterModalVisible(false)}
          onApply={(f) => {
            handleApplyFilters({
              minPrice: f.minPrice ? parseFloat(f.minPrice) : undefined,
              maxPrice: f.maxPrice ? parseFloat(f.maxPrice) : undefined,
              store: f.platforms.length > 0 ? f.platforms[0] : undefined,
              minDiscount: undefined,
            });
          }}
          initialFilters={{
            type: 'Products',
            platforms: selectedStore ? [selectedStore] : [],
            categories: [],
            minPrice: minPrice ? minPrice.toString() : '0',
            maxPrice: maxPrice ? maxPrice.toString() : '1600000',
          }}
        />

        {/* Sort Modal */}
        <SortModal
          visible={sortModalVisible}
          onClose={() => setSortModalVisible(false)}
          selectedSort={
            sortBy === 'price_asc'
              ? 'Price Low to High'
              : sortBy === 'price_desc'
              ? 'Price High to Low'
              : sortBy === 'deal_score'
              ? 'Popularity'
              : 'Newest First'
          }
          onSelectSort={(sort) => {
            const mappedSort =
              sort === 'Price Low to High'
                ? 'price_asc'
                : sort === 'Price High to Low'
                ? 'price_desc'
                : sort === 'Popularity'
                ? 'deal_score'
                : 'newest';
            handleApplySort(mappedSort);
          }}
        />
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
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.gray200,
  },
  backButton: {
    width: 40,
    height: 40,
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerTitle: {
    fontSize: typography.fontSize.h3,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
  },
  headerRight: {
    width: 40,
  },
  filterBar: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    gap: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.gray200,
  },
  filterButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.medium,
    borderWidth: 1,
    borderColor: colors.gray300,
    backgroundColor: colors.white,
  },
  filterButtonText: {
    fontSize: typography.fontSize.small,
    fontWeight: typography.fontWeight.medium,
    color: colors.gray700,
  },
  resultCount: {
    flex: 1,
    alignItems: 'flex-end',
  },
  resultCountText: {
    fontSize: typography.fontSize.small,
    color: colors.gray600,
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
    marginTop: spacing.md,
    marginBottom: spacing.sm,
    textAlign: 'center',
  },
  errorMessage: {
    fontSize: typography.fontSize.body,
    color: colors.gray600,
    textAlign: 'center',
    marginBottom: spacing.lg,
  },
  retryButton: {
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.md,
    backgroundColor: colors.primary,
    borderRadius: borderRadius.medium,
  },
  retryButtonText: {
    fontSize: typography.fontSize.body,
    fontWeight: typography.fontWeight.semibold,
    color: colors.white,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: spacing.xl,
  },
  emptyTitle: {
    fontSize: typography.fontSize.h2,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
    marginTop: spacing.md,
    marginBottom: spacing.sm,
    textAlign: 'center',
  },
  emptyMessage: {
    fontSize: typography.fontSize.body,
    color: colors.gray600,
    textAlign: 'center',
  },
  productList: {
    paddingHorizontal: spacing.sm,
    paddingTop: spacing.md,
    paddingBottom: spacing.xxl,
  },
  productCard: {
    flex: 1,
    maxWidth: '50%',
    padding: spacing.xs,
  },
  productCardLeft: {
    paddingRight: spacing.xs / 2,
  },
  productCardRight: {
    paddingLeft: spacing.xs / 2,
  },
  pagination: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.xl,
    gap: spacing.lg,
  },
  pageButton: {
    width: 40,
    height: 40,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: borderRadius.medium,
    borderWidth: 1,
    borderColor: colors.primary,
    backgroundColor: colors.white,
  },
  pageButtonDisabled: {
    borderColor: colors.gray300,
    backgroundColor: colors.gray100,
  },
  pageInfo: {
    fontSize: typography.fontSize.body,
    fontWeight: typography.fontWeight.medium,
    color: colors.gray700,
  },
});
