import React, { useState, useMemo } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, ScrollView, Image, SafeAreaView, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { colors, typography, spacing, borderRadius, shadows } from '../constants/theme';
import FilterModal, { FilterState } from '../components/FilterModal';
import SortModal from '../components/SortModal';

const searchHistory = ['Electronics', 'Pants', 'Long Shirt', 'Long Shirt'];

const verticalProducts = [
  {
    id: 'v1',
    title: 'BMW i8 2023',
    subtitle: 'Lisbon, Portugal',
    price: 200,
    unit: 'Week',
    rating: 4.5,
    available: true,
    image: 'https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800&h=400&fit=crop',
    avatar: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100&h=100&fit=crop',
    brand: 'BMW',
    condition: 'New'
  },
  {
    id: 'v2',
    title: 'Toyota Camry',
    subtitle: 'Porto, Portugal',
    price: 80,
    unit: 'Week',
    rating: 4.8,
    available: true,
    image: 'https://images.unsplash.com/photo-1560958089-b8a1929cea89?w=800&h=400&fit=crop',
    avatar: 'https://images.unsplash.com/photo-1599566150163-29194dcaad36?w=100&h=100&fit=crop',
    brand: 'Toyota',
    condition: 'Used'
  },
  {
    id: 'v3',
    title: 'Ferrari F8',
    subtitle: 'Faro, Portugal',
    price: 800,
    unit: 'Week',
    rating: 5.0,
    available: false,
    image: 'https://images.unsplash.com/photo-1592198084033-aade902d1aae?w=800&h=400&fit=crop',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop',
    brand: 'Ferrari',
    condition: 'New'
  }
];

const initialFilterState: FilterState = {
  type: 'Products',
  platforms: [],
  categories: [],
  minPrice: '0',
  maxPrice: '16000',
};

export default function SearchScreen() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [isFilterVisible, setIsFilterVisible] = useState(false);
  const [isSortVisible, setIsSortVisible] = useState(false);
  const [selectedSort, setSelectedSort] = useState('Relevance');
  const [filters, setFilters] = useState<FilterState>(initialFilterState);

  const handleSearch = () => {
    if (searchQuery.trim().length > 0) {
      router.push({ pathname: '/search-results', params: { query: searchQuery } });
    }
  };

  const handleApplyFilters = (newFilters: FilterState) => {
    setFilters(newFilters);
    setIsFilterVisible(false);
  };



  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.headerIcon}>
            <Ionicons name="chevron-back" size={24} color={colors.gray900} />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Search</Text>
          <TouchableOpacity style={styles.headerIcon}>
            <Ionicons name="notifications-outline" size={24} color={colors.gray900} />
          </TouchableOpacity>
        </View>

        <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollContent}>
          {/* Search Input */}
          <View style={styles.searchBarContainer}>
            <TouchableOpacity style={styles.sortActionIcon} onPress={() => setIsSortVisible(true)}>
              <Ionicons name="options-outline" size={20} color={colors.gray900} />
            </TouchableOpacity>
            
            <TextInput
              style={styles.searchInput}
              placeholder="Search your item"
              placeholderTextColor={colors.gray400}
              value={searchQuery}
              onChangeText={setSearchQuery}
              onSubmitEditing={handleSearch}
              returnKeyType="search"
              autoFocus
            />
            <TouchableOpacity style={styles.actionIcon} onPress={() => setIsFilterVisible(true)}>
              <Ionicons name="funnel-outline" size={20} color={'#E53935'} />
            </TouchableOpacity>
            <TouchableOpacity style={styles.actionIcon} onPress={handleSearch}>
              <Ionicons name="search-outline" size={20} color={colors.gray900} />
            </TouchableOpacity>
          </View>

          {/* Recent Comparisons */}
              <View style={styles.sectionHeader}>
                <Text style={styles.sectionTitle}>Recent Comparisons</Text>
                <TouchableOpacity>
                  <Text style={styles.clearText}>All Clear</Text>
                </TouchableOpacity>
              </View>

              <View style={styles.historyContainer}>
                {searchHistory.map((item, index) => (
                  <TouchableOpacity key={index} style={styles.historyPill}>
                    <Text style={styles.historyText}>{item}</Text>
                    <Ionicons name="close" size={16} color={colors.gray400} style={styles.closeIcon} />
                  </TouchableOpacity>
                ))}
              </View>

              {/* Trending Comparisons (New Vertical Design) */}
              <View style={[styles.sectionHeader, styles.recentlySearchHeader]}>
                <Text style={styles.sectionTitle}>Trending Comparisons</Text>
                <TouchableOpacity>
                  <Text style={styles.viewAllText}>View all</Text>
                </TouchableOpacity>
              </View>

              <View style={styles.verticalListContainer}>
                {verticalProducts.length === 0 && <Text style={styles.emptyText}>No items found.</Text>}
                {verticalProducts.map((product) => (
                  <View key={product.id} style={styles.verticalCard}>
                    {/* Top Section */}
                    <View style={styles.topSection}>
                      <Image source={{ uri: product.image }} style={styles.carImage} />
                      
                      {/* Rating Pill */}
                      <View style={styles.ratingPill}>
                        <Image source={{ uri: product.avatar }} style={styles.avatar} />
                        <Text style={styles.ratingPillText}>{product.rating}</Text>
                        <Ionicons name="star" size={12} color={colors.gray900} />
                      </View>

                      {/* Heart Icon */}
                      <TouchableOpacity style={styles.heartButton}>
                        <Ionicons name="heart-outline" size={18} color={colors.gray900} />
                      </TouchableOpacity>

                      {/* Pagination Dots */}
                      <View style={styles.paginationDots}>
                        {[1, 2, 3, 4, 5, 6].map((dot, index) => (
                          <View key={index} style={[styles.dot, index === 1 && styles.activeDot]} />
                        ))}
                      </View>
                    </View>

                    <View style={styles.separator} />

                    {/* Bottom Section */}
                    <View style={styles.bottomSection}>
                      <View style={styles.titleRow}>
                        <Text style={styles.verticalTitle}>{product.title}</Text>
                        <View style={styles.availabilityContainer}>
                          <Text style={styles.availabilityText}>{product.available ? 'Available' : 'Unavailable'}</Text>
                          {product.available && <View style={styles.availabilityDot} />}
                        </View>
                      </View>

                      <View style={styles.subtitleRow}>
                        <Text style={styles.verticalSubtitle}>{product.subtitle} • {product.condition}</Text>
                      </View>

                      <View style={styles.priceRow}>
                        <Text style={styles.verticalPrice}>€ {product.price}</Text>
                        <Text style={styles.verticalUnit}>{product.unit}</Text>
                      </View>
                    </View>
                  </View>
                ))}
              </View>

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
    paddingTop: Platform.OS === 'android' ? 25 : 0,
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
  },
  headerTitle: {
    fontSize: typography.fontSize.h2,
    fontWeight: typography.fontWeight.semibold,
    color: colors.gray900,
  },
  headerIcon: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  scrollContent: {
    paddingBottom: spacing.xl,
  },
  searchBarContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.gray50,
    marginHorizontal: spacing.lg,
    borderRadius: borderRadius.medium,
    height: 50,
    paddingHorizontal: spacing.md,
    marginTop: spacing.sm,
    marginBottom: spacing.xl,
  },
  searchIcon: {
    marginRight: spacing.sm,
  },
  searchInput: {
    flex: 1,
    fontSize: typography.fontSize.body,
    color: colors.gray900,
    height: '100%',
  },
  actionIcon: {
    padding: spacing.xs,
    marginLeft: spacing.xs,
  },
  sortActionIcon: {
    padding: spacing.xs,
    marginRight: spacing.sm,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    marginBottom: spacing.md,
  },
  recentlySearchHeader: {
    marginTop: spacing.xl,
  },
  sectionTitle: {
    fontSize: typography.fontSize.bodyLarge,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
  },
  clearText: {
    fontSize: typography.fontSize.body,
    color: colors.gray600,
  },
  viewAllText: {
    fontSize: typography.fontSize.body,
    color: colors.primary,
  },
  historyContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: spacing.lg,
    gap: spacing.sm,
  },
  historyPill: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderWidth: 1,
    borderColor: colors.gray100,
    borderRadius: borderRadius.medium,
    backgroundColor: colors.white,
  },
  historyText: {
    fontSize: typography.fontSize.body,
    color: colors.gray600,
    marginRight: spacing.sm,
  },
  closeIcon: {
    opacity: 0.5,
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
