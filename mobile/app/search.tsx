import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, ScrollView, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { authStorage } from '../lib/authStorage';
import { colors, typography, spacing, borderRadius, shadows } from '../constants/theme';
import FilterModal, { FilterState } from '../components/FilterModal';
import SortModal from '../components/SortModal';

const RECENT_SEARCHES_KEY = 'pricepilot_recent_searches';

const POPULAR_SEARCHES = ['Gaming Laptop', 'Wireless Earbuds', 'Smartphone', 'Mechanical Keyboard'];

const initialFilterState: FilterState = {
  type: 'Products',
  platforms: [],
  categories: [],
  minPrice: '0',
  maxPrice: '1600000',
};

export default function SearchScreen() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [isFilterVisible, setIsFilterVisible] = useState(false);
  const [isSortVisible, setIsSortVisible] = useState(false);
  const [selectedSort, setSelectedSort] = useState('Relevance');
  const [filters, setFilters] = useState<FilterState>(initialFilterState);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);

  useEffect(() => {
    loadRecentSearches();
  }, []);

  const loadRecentSearches = async () => {
    try {
      const stored = await authStorage.getItemAsync(RECENT_SEARCHES_KEY);
      if (stored) {
        setRecentSearches(JSON.parse(stored));
      }
    } catch (e) {
      console.error('Failed to load recent searches', e);
    }
  };

  const saveRecentSearch = async (query: string) => {
    if (!query.trim()) return;
    try {
      const updatedSearches = [query, ...recentSearches.filter(s => s !== query)].slice(0, 10);
      setRecentSearches(updatedSearches);
      await authStorage.setItemAsync(RECENT_SEARCHES_KEY, JSON.stringify(updatedSearches));
    } catch (e) {
      console.error('Failed to save recent search', e);
    }
  };

  const clearRecentSearches = async () => {
    try {
      await authStorage.deleteItemAsync(RECENT_SEARCHES_KEY);
      setRecentSearches([]);
    } catch (e) {
      console.error('Failed to clear recent searches', e);
    }
  };

  const removeRecentSearch = async (query: string) => {
    try {
      const updated = recentSearches.filter(s => s !== query);
      setRecentSearches(updated);
      await authStorage.setItemAsync(RECENT_SEARCHES_KEY, JSON.stringify(updated));
    } catch (e) {
      console.error('Failed to remove recent search', e);
    }
  };

  const executeSearch = (query: string) => {
    if (query.trim().length > 0) {
      saveRecentSearch(query.trim());
      router.push({ 
        pathname: '/search-results', 
        params: { 
          query: query.trim(),
          filters: JSON.stringify(filters),
          sort: selectedSort
        } 
      });
    }
  };

  const handleSearch = () => {
    executeSearch(searchQuery);
  };

  const handleApplyFilters = (newFilters: FilterState) => {
    setFilters(newFilters);
    setIsFilterVisible(false);
  };



  return (
    <SafeAreaView style={styles.safeArea} edges={['top']}>
      <View style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity 
            onPress={() => {
              if (router.canGoBack()) {
                router.back();
              } else {
                router.replace('/');
              }
            }} 
            style={styles.headerIcon}
          >
            <Ionicons name="arrow-back" size={20} color={'#111111'} />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Search</Text>
          <View style={styles.headerPlaceholder} />
        </View>

        <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollContent} keyboardShouldPersistTaps="handled">
          {/* Search Input */}
          <View style={styles.searchBarContainer}>
            <Ionicons name="search-outline" size={20} color={'#757575'} style={styles.searchIcon} />
            <TextInput
              style={styles.searchInput}
              placeholder="Search"
              placeholderTextColor={'#BDBDBD'}
              value={searchQuery}
              onChangeText={setSearchQuery}
              onSubmitEditing={handleSearch}
              returnKeyType="search"
              autoFocus
            />
          </View>

          {!searchQuery.trim() && (
            <>
              {/* Popular Searches */}
              <View style={styles.sectionHeader}>
                <Text style={styles.sectionTitle}>Popular Searches</Text>
              </View>
              <View style={styles.popularTagsContainer}>
                {POPULAR_SEARCHES.map((item, index) => (
                  <TouchableOpacity 
                    key={index} 
                    style={styles.popularTag}
                    onPress={() => {
                      setSearchQuery(item);
                      executeSearch(item);
                    }}
                  >
                    <Text style={styles.popularTagText}>{item}</Text>
                  </TouchableOpacity>
                ))}
              </View>

              <View style={styles.divider} />

              {/* Recent Searches */}
              {recentSearches.length > 0 && (
                <>
                  <View style={styles.sectionHeader}>
                    <Text style={styles.sectionTitle}>Recent Searches</Text>
                    <TouchableOpacity onPress={clearRecentSearches}>
                      <Text style={styles.clearText}>Clear</Text>
                    </TouchableOpacity>
                  </View>
                  <View style={styles.historyList}>
                    {recentSearches.map((item, index) => (
                      <View key={index} style={styles.historyItem}>
                        <TouchableOpacity 
                          style={{ flex: 1, flexDirection: 'row', alignItems: 'center' }}
                          onPress={() => {
                            setSearchQuery(item);
                            executeSearch(item);
                          }}
                        >
                          <Ionicons name="time-outline" size={18} color={'#BDBDBD'} style={{ marginRight: 12 }} />
                          <Text style={styles.historyText}>{item}</Text>
                        </TouchableOpacity>
                        <TouchableOpacity 
                          style={styles.closeIconCircle}
                          onPress={() => removeRecentSearch(item)}
                        >
                          <Ionicons name="close" size={14} color="#757575" />
                        </TouchableOpacity>
                      </View>
                    ))}
                  </View>
                </>
              )}
            </>
          )}

        </ScrollView>
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
    paddingHorizontal: 24,
    paddingBottom: 16,
    paddingTop: 8,
  },
  headerTitle: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 16,
    color: '#111111',
  },
  headerIcon: {
    width: 40, // Slightly smaller to match screenshot
    height: 40,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#EEEEEE',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
  },
  headerPlaceholder: {
    width: 40, // Matches headerIcon to perfectly center the title
  },
  scrollContent: {
    paddingBottom: 40,
  },
  searchBarContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    marginHorizontal: 24,
    borderRadius: 9999,
    borderWidth: 1,
    borderColor: '#EEEEEE',
    height: 48, // Slightly shorter, like the screenshot
    paddingHorizontal: 16,
    marginTop: 12, // Tighter margin
    marginBottom: 24, // Tighter margin
  },
  searchIcon: {
    marginRight: 10,
  },
  searchInput: {
    flex: 1,
    fontFamily: 'Poppins_400Regular',
    fontSize: 14,
    color: '#111111',
    height: '100%',
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 24,
    marginBottom: 12,
  },
  sectionTitle: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 16,
    color: '#111111',
  },
  clearText: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 14,
    color: '#111111', // Changed to black to match the monochromatic theme
  },
  divider: {
    height: 1,
    backgroundColor: '#EEEEEE',
    marginHorizontal: 24,
    marginBottom: 12,
  },
  historyList: {
    paddingHorizontal: 24,
  },
  historyItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 12, // Tighter vertical spacing
  },
  historyText: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 14,
    color: '#757575',
  },
  closeIconCircle: {
    padding: spacing.xs,
  },
  popularTagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 24,
    marginBottom: 20,
    gap: 8,
  },
  popularTag: {
    backgroundColor: '#F5EBE1', // Theme light brown
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  popularTagText: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 12,
    color: '#704F38', // Theme dark brown
  },
  productsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: spacing.lg,
    justifyContent: 'space-between',
  },
  productCard: {
    width: '48%',
    backgroundColor: colors.white,
    borderRadius: borderRadius.medium,
    marginBottom: spacing.md,
    ...shadows.card,
    borderWidth: 1,
    borderColor: colors.gray50,
    overflow: 'hidden',
  },
  productImage: {
    width: '100%',
    height: 120,
    backgroundColor: colors.gray50,
  },
  productInfo: {
    padding: spacing.sm,
  },
  productName: {
    fontSize: typography.fontSize.body,
    color: colors.gray900,
    marginBottom: 4,
  },
  productPrice: {
    fontSize: typography.fontSize.body,
    fontWeight: typography.fontWeight.bold,
    color: colors.errorRed,
    marginBottom: 4,
  },
  ratingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  ratingText: {
    fontSize: typography.fontSize.caption,
    color: colors.gray600,
    marginLeft: 4,
  },
  reviewsText: {
    fontSize: typography.fontSize.caption,
    color: colors.gray400,
    marginLeft: 4,
  },
  verticalListContainer: {
    paddingHorizontal: spacing.lg,
  },
  verticalCard: {
    backgroundColor: '#F8F9FA',
    borderRadius: borderRadius.large,
    padding: spacing.md,
    marginBottom: spacing.lg,
  },
  topSection: {
    position: 'relative',
    height: 180,
    backgroundColor: '#F8F9FA',
    borderRadius: borderRadius.medium,
    overflow: 'hidden',
  },
  carImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'contain',
  },
  ratingPill: {
    position: 'absolute',
    top: spacing.sm,
    left: spacing.sm,
    backgroundColor: colors.white,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: borderRadius.full,
    ...shadows.card,
  },
  avatar: {
    width: 20,
    height: 20,
    borderRadius: 10,
    marginRight: 6,
  },
  ratingPillText: {
    fontSize: typography.fontSize.caption,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
    marginRight: 4,
  },
  heartButton: {
    position: 'absolute',
    top: spacing.sm,
    right: spacing.sm,
    backgroundColor: colors.white,
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    ...shadows.card,
  },
  paginationDots: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    position: 'absolute',
    bottom: spacing.sm,
    width: '100%',
  },
  dot: {
    width: 4,
    height: 4,
    borderRadius: 2,
    backgroundColor: colors.gray400,
    marginHorizontal: 2,
  },
  activeDot: {
    backgroundColor: colors.gray900,
  },
  separator: {
    height: 1,
    backgroundColor: colors.gray200,
    marginVertical: spacing.md,
  },
  bottomSection: {
    paddingHorizontal: spacing.xs,
  },
  titleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  verticalTitle: {
    fontSize: typography.fontSize.bodyLarge,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
  },
  availabilityContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  availabilityText: {
    fontSize: typography.fontSize.caption,
    color: colors.gray600,
    marginRight: 4,
  },
  availabilityDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: colors.successGreen,
  },
  subtitleRow: {
    marginBottom: spacing.md,
  },
  verticalSubtitle: {
    fontSize: typography.fontSize.caption,
    color: colors.gray400,
  },
  priceRow: {
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  verticalPrice: {
    fontSize: typography.fontSize.h3,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
    marginRight: 4,
  },
  verticalUnit: {
    fontSize: typography.fontSize.caption,
    color: colors.gray600,
  },
  emptyText: {
    fontSize: typography.fontSize.body,
    color: colors.gray600,
    textAlign: 'center',
    marginTop: spacing.xl,
    paddingHorizontal: spacing.lg,
  },
});
