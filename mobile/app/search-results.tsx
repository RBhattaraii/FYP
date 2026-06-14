import React, { useState, useMemo } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Image, SafeAreaView, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { colors, typography, spacing, borderRadius } from '../constants/theme';
import FilterModal, { FilterState } from '../components/FilterModal';
import SortModal from '../components/SortModal';

// Mock data reflecting a variety of categories for search testing
const recentProducts = [
  { id: '1', name: 'Extreme Gloss', brand: 'Shampoo Dark', price: 1300, rating: 3.9, image: 'https://images.unsplash.com/photo-1620054707624-9b5edccdf4d8?w=400&h=400&fit=crop', isFavorite: false },
  { id: '2', name: 'Extreme Gloss', brand: 'Silver Hard Wax', price: 1500, rating: 4.1, image: 'https://images.unsplash.com/photo-1607525381615-566bc90757db?w=400&h=400&fit=crop', isFavorite: false },
  { id: '3', name: 'Oil Filter', brand: 'TO-1212M', price: 1300, rating: 3.9, image: 'https://images.unsplash.com/photo-1635336049257-2e1d70a3111f?w=400&h=400&fit=crop', isFavorite: false },
  { id: '4', name: 'AC Filter', brand: 'CMI-4005B', price: 1900, rating: 3.9, image: 'https://images.unsplash.com/photo-1635336049257-2e1d70a3111f?w=400&h=400&fit=crop', isFavorite: true },
  
  // Electronics
  { id: '5', name: 'iPhone 15 Pro', brand: 'Apple', price: 99900, rating: 4.8, image: 'https://images.unsplash.com/photo-1696446701796-da61225697cc?w=400&h=400&fit=crop', isFavorite: true },
  { id: '6', name: 'MacBook Air M2', brand: 'Apple', price: 120000, rating: 4.9, image: 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&h=400&fit=crop', isFavorite: false },
  { id: '7', name: 'Galaxy S24 Ultra', brand: 'Samsung', price: 110000, rating: 4.7, image: 'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400&h=400&fit=crop', isFavorite: true },
  { id: '8', name: 'Sony WH-1000XM5', brand: 'Sony', price: 35000, rating: 4.6, image: 'https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=400&h=400&fit=crop', isFavorite: false },
  
  // Clothing
  { id: '9', name: 'Classic T-Shirt', brand: 'Nike', price: 2500, rating: 4.3, image: 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=400&fit=crop', isFavorite: false },
  { id: '10', name: 'Running Shoes', brand: 'Adidas', price: 8500, rating: 4.5, image: 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop', isFavorite: true },
  { id: '11', name: 'Denim Jacket', brand: 'Levi\'s', price: 6500, rating: 4.2, image: 'https://images.unsplash.com/photo-1576871337622-98d48d1cf531?w=400&h=400&fit=crop', isFavorite: false },
  { id: '12', name: 'Cargo Pants', brand: 'Zara', price: 4500, rating: 4.0, image: 'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=400&h=400&fit=crop', isFavorite: true },
  
  // Home & Lifestyle
  { id: '13', name: 'Ceramic Coffee Mug', brand: 'HomeGoods', price: 800, rating: 4.7, image: 'https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?w=400&h=400&fit=crop', isFavorite: false },
  { id: '14', name: 'Office Chair', brand: 'IKEA', price: 15000, rating: 4.4, image: 'https://images.unsplash.com/photo-1505843490538-5133c6c7d0e1?w=400&h=400&fit=crop', isFavorite: false },
  { id: '15', name: 'Desk Lamp', brand: 'Philips', price: 3200, rating: 4.1, image: 'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=400&h=400&fit=crop', isFavorite: true },
];

const initialFilterState: FilterState = {
  type: 'Products',
  platforms: [],
  categories: [],
  minPrice: '0',
  maxPrice: '16000',
};

export default function SearchResultsScreen() {
  const router = useRouter();
  const params = useLocalSearchParams();
  const initialQuery = Array.isArray(params.query) ? params.query[0] : params.query || '';
  
  const [searchQuery, setSearchQuery] = useState(initialQuery);
  const [isFilterVisible, setIsFilterVisible] = useState(false);
  const [isSortVisible, setIsSortVisible] = useState(false);
  const [selectedSort, setSelectedSort] = useState('Relevance');
  const [filters, setFilters] = useState<FilterState>(initialFilterState);

  const handleApplyFilters = (newFilters: FilterState) => {
    setFilters(newFilters);
    setIsFilterVisible(false);
  };

  // Filter Logic
  const filterList = (list: any[]) => {
    return list.filter(item => {
      // Filter by Search Query
      const itemName = item.name || item.brand;
      if (searchQuery && !itemName.toLowerCase().includes(searchQuery.toLowerCase())) {
        return false;
      }
      return true;
    });
  };

  const filteredGridProducts = useMemo(() => filterList(recentProducts), [filters, searchQuery]);

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.headerIcon}>
            <Ionicons name="chevron-back" size={24} color={colors.gray900} />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Feature Product</Text>
          <TouchableOpacity style={styles.headerIcon} onPress={() => router.push('/search')}>
            <Ionicons name="search-outline" size={24} color={colors.gray900} />
          </TouchableOpacity>
        </View>

        {/* Sub Header: Sort & Filter */}
        <View style={styles.subHeaderRow}>
          <TouchableOpacity style={styles.sortByContainer} onPress={() => setIsSortVisible(true)}>
            <Text style={styles.sortByText}>Sort by</Text>
            <Ionicons name="chevron-down" size={16} color={colors.gray900} />
          </TouchableOpacity>

          <View style={styles.filterContainer}>
            <TouchableOpacity>
              <Ionicons name="grid-outline" size={20} color={colors.gray900} />
            </TouchableOpacity>
            <View style={styles.divider} />
            <TouchableOpacity style={styles.filterContainer} onPress={() => setIsFilterVisible(true)}>
              <Ionicons name="funnel-outline" size={20} color={colors.gray900} />
              <Text style={styles.filterText}>Filter</Text>
            </TouchableOpacity>
          </View>
        </View>

        <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollContent}>
          <View style={styles.productsGrid}>
            {filteredGridProducts.length === 0 && <Text style={styles.emptyText}>No items found matching your filters.</Text>}
            {filteredGridProducts.map((product) => (
              <TouchableOpacity key={product.id} style={styles.productCard}>
                <TouchableOpacity style={styles.heartIcon}>
                  <Ionicons 
                    name="heart" 
                    size={20} 
                    color={product.isFavorite ? colors.errorRed : '#5B636A'} 
                  />
                </TouchableOpacity>

                <Image source={{ uri: product.image }} style={styles.productImage} resizeMode="contain" />

                <View style={styles.productInfo}>
                  <View style={styles.priceRow}>
                    <Text style={styles.productPrice}>{product.price.toLocaleString()}৳</Text>
                    <View style={styles.ratingContainer}>
                      <Ionicons name="star" size={12} color="#FBBF24" />
                      <Text style={styles.ratingText}>({product.rating})</Text>
                    </View>
                  </View>

                  <Text style={styles.productName} numberOfLines={2}>{product.name}{'\n'}{product.brand}</Text>

                  <TouchableOpacity style={styles.addButton}>
                    <Ionicons name="add" size={20} color={colors.white} />
                  </TouchableOpacity>
                </View>
              </TouchableOpacity>
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
    backgroundColor: '#E6E9ED',
    paddingTop: Platform.OS === 'android' ? 25 : 0,
  },
  container: {
    flex: 1,
    backgroundColor: '#E6E9ED',
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
  subHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    marginBottom: spacing.lg,
    marginTop: spacing.sm,
  },
  sortByContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  sortByText: {
    fontSize: typography.fontSize.body,
    color: colors.gray900,
    fontWeight: typography.fontWeight.semibold,
    marginRight: 4,
  },
  filterContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  filterText: {
    fontSize: typography.fontSize.body,
    color: colors.gray900,
    marginLeft: 6,
  },
  divider: {
    width: 1,
    height: 16,
    backgroundColor: colors.gray400,
    marginHorizontal: 10,
  },
  scrollContent: {
    paddingBottom: spacing.xl,
  },
  productsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: spacing.lg,
    justifyContent: 'space-between',
  },
  productCard: {
    width: '48%',
    backgroundColor: '#D1D8E0', // Matching the card color from image
    borderRadius: borderRadius.large,
    marginBottom: spacing.md,
    padding: spacing.md,
    position: 'relative',
  },
  heartIcon: {
    position: 'absolute',
    top: spacing.md,
    right: spacing.md,
    zIndex: 1,
  },
  productImage: {
    width: '100%',
    height: 100,
    marginTop: spacing.lg,
    marginBottom: spacing.md,
  },
  productInfo: {
    flex: 1,
  },
  priceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  productPrice: {
    fontSize: typography.fontSize.bodyLarge,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
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
  productName: {
    fontSize: typography.fontSize.caption,
    color: colors.gray700,
    lineHeight: 18,
    paddingRight: 24, 
  },
  addButton: {
    position: 'absolute',
    bottom: -4,
    right: -4,
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: '#4B5563',
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyText: {
    fontSize: typography.fontSize.body,
    color: colors.gray600,
    textAlign: 'center',
    marginTop: spacing.xl,
    paddingHorizontal: spacing.lg,
  },
});
