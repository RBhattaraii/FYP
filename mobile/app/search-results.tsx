import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { View, Text, StyleSheet, FlatList, Image, TouchableOpacity, SafeAreaView, Platform, Pressable, ActivityIndicator, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { colors, typography, spacing, borderRadius } from '../constants/theme';
import FilterModal, { FilterState } from '../components/FilterModal';
import SortModal from '../components/SortModal';
import { searchProducts, pollSearchStatus, Product } from '../services/api';
import { useFavorites } from '../context/FavoritesContext';

type SearchResultProduct = Product & {
  name: string;
  brand: string;
  image: string;
  rating: number;
  isFavorite: boolean;
};

const initialFilterState: FilterState = {
  type: 'Products',
  platforms: [],
  categories: [],
  minPrice: '0',
  maxPrice: '1600000',
};

export default function SearchResultsScreen() {
  const router = useRouter();
  const params = useLocalSearchParams();
  const initialQuery = Array.isArray(params.query) ? params.query[0] : params.query || '';

  const [searchQuery] = useState(initialQuery);
  const [isFilterVisible, setIsFilterVisible] = useState(false);
  const [isSortVisible, setIsSortVisible] = useState(false);
  const initialSort = useMemo(() => {
    const rawSort = Array.isArray(params.sort) ? params.sort[0] : params.sort;
    return rawSort || 'Relevance';
  }, [params.sort]);

  const initialFilters = useMemo(() => {
    const rawFilters = Array.isArray(params.filters) ? params.filters[0] : params.filters;
    if (rawFilters) {
      try {
        return JSON.parse(rawFilters);
      } catch (e) {
        console.error('Failed to parse filters from query params', e);
      }
    }
    return initialFilterState;
  }, [params.filters]);

  const [selectedSort, setSelectedSort] = useState(initialSort);
  const [filters, setFilters] = useState<FilterState>(initialFilters);
  const [loading, setLoading] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [searchResults, setSearchResults] = useState<SearchResultProduct[]>([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const { items: favoriteItems, addItem, removeItem } = useFavorites();
  const [isLiveScraping, setIsLiveScraping] = useState(false);
  const [liveScrapeMessage, setLiveScrapeMessage] = useState('');

  const pollForLiveResults = (requestId: string, query: string) => {
    let attempts = 0;
    const maxAttempts = 15;

    const poll = async () => {
      if (attempts >= maxAttempts) {
        setIsLiveScraping(false);
        setLiveScrapeMessage('');
        return;
      }

      try {
        const statusRes = await pollSearchStatus(requestId, query);

        if (statusRes.is_complete) {
          setIsLiveScraping(false);
          setLiveScrapeMessage('Found new live products!');
          
          // Silently refresh page 1 from the database to get properly sorted results (offline + new Daraz products)
          try {
            let apiSort = 'relevance';
            if (selectedSort === 'Price Low to High') apiSort = 'price_asc';
            if (selectedSort === 'Price High to Low') apiSort = 'price_desc';
            if (selectedSort === 'Discount') apiSort = 'discount';
            
            const isCategory = params.query && params.isCategory === 'true';
            const res = await searchProducts(query, 1, 50, apiSort, !!isCategory);
            
            const mappedResults = res.results.map((product: any, index: number) => ({
              ...product,
              name: product.title,
              brand: product.store_name,
              image: product.image_url,
              rating: product.discount_percent ? Math.min(5, Math.max(3, product.discount_percent / 20)) : 4,
              isFavorite: false,
            }));
            
            setSearchResults(prev => {
              if (prev.length <= 50) return mappedResults;
              
              // If user has already scrolled past page 1, keep their page 2+ items, just replace page 1
              const combined = [...mappedResults];
              const existingUrls = new Set(mappedResults.map((p: any) => p.product_url));
              
              for (let i = 50; i < prev.length; i++) {
                if (!existingUrls.has(prev[i].product_url)) {
                  combined.push(prev[i]);
                }
              }
              return combined;
            });
          } catch (e) {
            console.error('Silent refresh failed:', e);
          }
          
          setTimeout(() => setLiveScrapeMessage(''), 3000);
          return;
        }

        attempts++;
        setTimeout(poll, 2000);
      } catch (error) {
        console.error('Polling error', error);
        setIsLiveScraping(false);
        setLiveScrapeMessage('');
      }
    };

    setTimeout(poll, 2000);
  };

  useEffect(() => {
    let isActive = true;

    async function runSearch() {
      const query = searchQuery.trim();
      if (!query) {
        setSearchResults([]);
        setSearchError(null);
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setSearchError(null);
        setPage(1);
        setHasMore(true);

        let apiSort = 'relevance';
        if (selectedSort === 'Price Low to High') apiSort = 'price_asc';
        if (selectedSort === 'Price High to Low') apiSort = 'price_desc';
        if (selectedSort === 'Discount') apiSort = 'discount';

        const isCategory = params.isCategory === 'true';
        const res = await searchProducts(query, 1, 50, apiSort, !!isCategory);
        if (!isActive) return;

        const mappedResults = res.results.map((product: any, index: number) => ({
          ...product,
          name: product.title,
          brand: product.store_name,
          image: product.image_url,
          rating: product.discount_percent ? Math.min(5, Math.max(3, product.discount_percent / 20)) : 4,
        }));

        setSearchResults(mappedResults);
        if (res.total_pages && 1 >= res.total_pages) {
          setHasMore(false);
        }

        if (res.is_complete === false && res.request_id) {
          setIsLiveScraping(true);
          setLiveScrapeMessage('Live scraping websites for fresh results...');
          pollForLiveResults(res.request_id, query);
        }
      } catch (error: any) {
        if (!isActive) return;
        setSearchError(error.message || 'Unable to load search results');
        setSearchResults([]);
      } finally {
        if (isActive) setLoading(false);
      }
    }

    runSearch();
    return () => { isActive = false; };
  }, [searchQuery, selectedSort]);

  const loadMore = useCallback(async () => {
    if (loadingMore || !hasMore || loading) return;

    try {
      setLoadingMore(true);
      const nextPage = page + 1;
      
      let apiSort = 'relevance';
      if (selectedSort === 'Price Low to High') apiSort = 'price_asc';
      if (selectedSort === 'Price High to Low') apiSort = 'price_desc';
      if (selectedSort === 'Discount') apiSort = 'discount';

      const isCategory = params.isCategory === 'true';
      const res = await searchProducts(searchQuery, nextPage, 50, apiSort, !!isCategory);

      const mappedResults = res.results.map((product: any, index: number) => ({
        ...product,
        name: product.title,
        brand: product.store_name,
        image: product.image_url,
        rating: product.discount_percent ? Math.min(5, Math.max(3, product.discount_percent / 20)) : 4,
      }));

      setSearchResults(prev => [...prev, ...mappedResults]);
      setPage(nextPage);

      if (res.total_pages && nextPage >= res.total_pages) {
        setHasMore(false);
      }
    } catch (error) {
      console.error('Failed to load more products:', error);
    } finally {
      setLoadingMore(false);
    }
  }, [loadingMore, hasMore, loading, page, searchQuery, selectedSort]);

  const handleApplyFilters = (newFilters: FilterState) => {
    setFilters(newFilters);
    setIsFilterVisible(false);
  };

  const filteredGridProducts = useMemo(() => {
    let list = [...searchResults];

    // Apply price filter
    if (filters.minPrice || filters.maxPrice) {
      const min = parseFloat(filters.minPrice) || 0;
      const max = parseFloat(filters.maxPrice) || Infinity;
      list = list.filter(p => p.price >= min && p.price <= max);
    }

    // Apply platform filter
    if (filters.platforms && filters.platforms.length > 0) {
      list = list.filter(p =>
        filters.platforms.some(platform =>
          (p.store_name || '').toLowerCase().includes(platform.toLowerCase())
        )
      );
    }

    // Apply category filter
    if (filters.categories && filters.categories.length > 0) {
      list = list.filter(p =>
        filters.categories.some(cat =>
          (p.category || '').toLowerCase().includes(cat.toLowerCase())
        )
      );
    }

    // Note: We no longer sort locally here because sorting is now correctly
    // handled by the PostgreSQL database across all paginated pages!
    // This prevents the bug where scrolling down ruins the sort order.

    return list;
  }, [filters, searchResults]);

  // Memoize render function
  const renderProduct = useCallback(({ item: product, index }: { item: SearchResultProduct; index: number }) => {
    const favId = `${product.store_name}-${product.product_url}`;
    const isFav = favoriteItems.some(f => f.id === favId);
    
    return (
    <TouchableOpacity 
      style={styles.productCard}
      onPress={() => {
        const { setGlobalSelectedProduct } = require('../services/api');
        setGlobalSelectedProduct(product);
        router.push({
          pathname: `/product/${encodeURIComponent(favId)}`
        });
      }}
      activeOpacity={0.9}
    >
      <View style={styles.imageContainer}>
        <Image source={{ uri: product.image }} style={styles.productImage} resizeMode="cover" />
        <TouchableOpacity 
          style={styles.heartButton} 
          onPress={() => {
            if (isFav) {
              removeItem(favId);
            } else {
              addItem({
                id: favId,
                productId: product.id,
                title: product.name,
                price: product.price,
                originalPrice: product.original_price,
                discountPercent: product.discount_percent,
                imageUrl: product.image,
                storeName: product.store_name,
                productUrl: product.product_url
              });
            }
          }}
        >
          <Ionicons name={isFav ? 'heart' : 'heart-outline'} size={20} color={isFav ? '#FF4757' : '#6E4B3A'} />
        </TouchableOpacity>
      </View>
      
      <View style={styles.infoRow}>
        <Text style={styles.productName} numberOfLines={1}>{product.name}</Text>
        <View style={styles.ratingBox}>
          <Ionicons name="star" size={14} color="#FBBF24" />
          <Text style={styles.ratingText}>{product.rating.toFixed(1)}</Text>
        </View>
      </View>
      
      <Text style={styles.productPrice}>Rs {product.price.toLocaleString()}</Text>
    </TouchableOpacity>
  )}, [router, favoriteItems, addItem, removeItem]);

  const renderHeader = () => (
    <>
      {isLiveScraping && (
        <View style={styles.liveScrapeBanner}>
          <Ionicons name="globe-outline" size={14} color={colors.primaryDark} />
          <Text style={styles.liveScrapeText}> {liveScrapeMessage}</Text>
        </View>
      )}
    </>
  );

  const renderFooter = () => {
    if (loadingMore) {
      return (
        <View style={styles.footerLoader}>
          <ActivityIndicator size="small" color={colors.primary} />
          <Text style={styles.footerText}>Loading more...</Text>
        </View>
      );
    }
    if (!hasMore && filteredGridProducts.length > 0) {
      return <Text style={styles.emptyText}>All {filteredGridProducts.length} results shown</Text>;
    }
    return null;
  };

  const renderEmpty = () => {
    if (loading) {
      return (
        <View style={styles.emptyContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={styles.emptyText}>Searching database...</Text>
        </View>
      );
    }
    if (searchError) {
      return <Text style={styles.emptyText}>{searchError}</Text>;
    }
    return <Text style={styles.emptyText}>No products found for "{searchQuery}".</Text>;
  };

  const keyExtractor = useCallback((item: SearchResultProduct, index: number) => 
    `${item.id || item.product_url}-${index}`, []
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity
            onPress={() => {
              if (router.canGoBack()) router.back();
              else router.replace('/');
            }}
            style={styles.headerIcon}
          >
            <Ionicons name="arrow-back" size={20} color="#111111" />
          </TouchableOpacity>
          <Text style={styles.headerTitle} numberOfLines={1}>
            {searchQuery ? searchQuery : 'Search Results'}
          </Text>
          <TouchableOpacity style={styles.headerIcon} onPress={() => router.push('/search')}>
            <Ionicons name="search-outline" size={20} color="#111111" />
          </TouchableOpacity>
        </View>

        <FlatList
          data={filteredGridProducts}
          renderItem={renderProduct}
          keyExtractor={keyExtractor}
          numColumns={2}
          columnWrapperStyle={styles.row}
          contentContainerStyle={styles.scrollContent}
          ListHeaderComponent={renderHeader}
          ListFooterComponent={renderFooter}
          ListEmptyComponent={renderEmpty}
          onEndReached={loadMore}
          onEndReachedThreshold={0.5}
          initialNumToRender={10}
          maxToRenderPerBatch={10}
          windowSize={5}
          removeClippedSubviews={true}
          showsVerticalScrollIndicator={false}
        />

        {/* Floating Sort/Filter Pill */}
        <View style={styles.floatingPill}>
          <TouchableOpacity style={styles.pillButton} onPress={() => setIsSortVisible(true)}>
            <Ionicons name="swap-vertical" size={18} color="#FFFFFF" />
            <Text style={styles.pillText}>Sort</Text>
          </TouchableOpacity>
          <View style={styles.pillDivider} />
          <TouchableOpacity style={styles.pillButton} onPress={() => setIsFilterVisible(true)}>
            <Ionicons name="options-outline" size={18} color="#FFFFFF" />
            <Text style={styles.pillText}>Filter</Text>
          </TouchableOpacity>
        </View>

        <FilterModal
          visible={isFilterVisible}
          onClose={() => setIsFilterVisible(false)}
          onApply={handleApplyFilters}
          initialFilters={filters}
        />
        <SortModal
          visible={isSortVisible}
          onClose={() => setIsSortVisible(false)}
          selectedSort={selectedSort}
          onSelectSort={setSelectedSort}
        />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#FAFAFA',
    paddingTop: Platform.OS === 'android' ? 25 : 0,
  },
  container: {
    flex: 1,
    backgroundColor: '#FAFAFA',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 24,
    paddingBottom: 16,
    paddingTop: 8,
  },
  headerIcon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    borderWidth: 1,
    borderColor: '#EEEEEE',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
  },
  headerTitle: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 16,
    color: '#111111',
    flex: 1,
    textAlign: 'center',
  },
  headerPlaceholder: {
    width: 44,
  },
  scrollContent: {
    paddingHorizontal: 24,
    paddingBottom: 100,
    paddingTop: 16,
  },
  row: {
    justifyContent: 'space-between',
  },
  productCard: {
    width: '47%',
    marginBottom: 24,
  },
  imageContainer: {
    width: '100%',
    aspectRatio: 0.9,
    borderRadius: 16,
    overflow: 'hidden',
    backgroundColor: '#F5F5F5',
    marginBottom: 12,
  },
  productImage: {
    width: '100%',
    height: '100%',
  },
  heartButton: {
    position: 'absolute',
    top: 12,
    right: 12,
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#F0E5D8',
    justifyContent: 'center',
    alignItems: 'center',
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  productName: {
    flex: 1,
    fontFamily: 'Poppins_400Regular',
    fontSize: 14,
    color: '#111111',
    marginRight: 8,
  },
  ratingBox: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  ratingText: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 12,
    color: '#757575',
  },
  productPrice: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 14,
    color: '#111111',
  },
  emptyText: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 14,
    color: '#757575',
    textAlign: 'center',
    marginTop: 32,
    paddingHorizontal: 24,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 64,
  },
  footerLoader: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 24,
  },
  footerText: {
    marginLeft: 8,
    fontFamily: 'Poppins_400Regular',
    fontSize: 14,
    color: '#757575',
  },
  liveScrapeBanner: {
    flexDirection: 'row',
    backgroundColor: '#F5F5F5',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: '#EEEEEE',
  },
  liveScrapeText: {
    color: '#6E4B3A',
    fontFamily: 'Poppins_500Medium',
    fontSize: 12,
    marginLeft: 8,
  },
  floatingPill: {
    position: 'absolute',
    bottom: 32,
    alignSelf: 'center',
    flexDirection: 'row',
    backgroundColor: '#111111',
    borderRadius: 30,
    paddingVertical: 12,
    paddingHorizontal: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  pillButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
  },
  pillText: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 14,
    color: '#FFFFFF',
    marginLeft: 8,
  },
  pillDivider: {
    width: 1,
    height: 18,
    backgroundColor: '#333333',
    marginHorizontal: 8,
  }
});
