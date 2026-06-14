import React, { useState } from 'react';
import { View, StyleSheet, FlatList, TouchableOpacity, Text, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import * as Haptics from 'expo-haptics';

import Header from '../../components/Header';
import SearchBar from '../../components/SearchBar';
import ProductCard from '../../components/ProductCard';
import { colors, spacing, typography } from '../../constants/theme';

const TABS = ['Popular', 'Latest', 'Best Sellers'];

// Mock data
const MOCK_PRODUCTS = [
  {
    id: '1',
    name: 'Sony WH-1000XM4 Headphones',
    price: 249.99,
    rating: 4.8,
    imageUrl: 'https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=400&h=400&fit=crop',
    inWishlist: false,
  },
  {
    id: '2',
    name: 'Apple iPad Air',
    price: 599.00,
    rating: 4.9,
    imageUrl: 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400&h=400&fit=crop',
    inWishlist: true,
  },
  {
    id: '3',
    name: 'Samsung Galaxy S23',
    price: 799.00,
    rating: 4.7,
    imageUrl: 'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400&h=400&fit=crop',
    inWishlist: false,
  },
  {
    id: '4',
    name: 'Nike Air Max 270',
    price: 129.99,
    rating: 4.5,
    imageUrl: 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop',
    inWishlist: false,
  },
  {
    id: '5',
    name: 'Dyson V11 Vacuum',
    price: 449.50,
    rating: 4.6,
    imageUrl: 'https://images.unsplash.com/photo-1558317374-067fb5f30001?w=400&h=400&fit=crop',
    inWishlist: false,
  },
  {
    id: '6',
    name: 'Apple Watch Series 8',
    price: 399.00,
    rating: 4.8,
    imageUrl: 'https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=400&h=400&fit=crop',
    inWishlist: true,
  },
];

export default function ExploreScreen() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState(TABS[0]);
  const [products, setProducts] = useState(MOCK_PRODUCTS);

  const handleTabPress = (tab: string) => {
    if (Platform.OS === 'ios') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    setActiveTab(tab);
  };

  const handleProductPress = (id: string) => {
    router.push(`/product/${id}`);
  };

  const handleAddPress = (id: string) => {
    setProducts(prev => 
      prev.map(p => 
        p.id === id ? { ...p, inWishlist: !p.inWishlist } : p
      )
    );
  };

  const renderHeader = () => (
    <View>
      <Header 
        title="Explore" 
        showBackBtn={false}
      />
      <SearchBar 
        onPress={() => router.push('/search')}
        onVoicePress={() => console.log('Voice search')}
      />
      
      <View style={styles.tabsContainer}>
        <FlatList
          horizontal
          showsHorizontalScrollIndicator={false}
          data={TABS}
          keyExtractor={(item) => item}
          contentContainerStyle={styles.tabsContent}
          renderItem={({ item }) => {
            const isActive = activeTab === item;
            return (
              <TouchableOpacity
                style={[styles.tab, isActive && styles.activeTab]}
                onPress={() => handleTabPress(item)}
              >
                <Text style={[styles.tabText, isActive && styles.activeTabText]}>
                  {item}
                </Text>
              </TouchableOpacity>
            );
          }}
        />
      </View>
    </View>
  );

  return (
    <SafeAreaView style={styles.safeArea} edges={['top']}>
      <FlatList
        data={products}
        keyExtractor={(item) => item.id}
        numColumns={2}
        ListHeaderComponent={renderHeader}
        contentContainerStyle={styles.gridContent}
        columnWrapperStyle={styles.columnWrapper}
        showsVerticalScrollIndicator={false}
        renderItem={({ item }) => (
          <View style={styles.cardWrapper}>
            <ProductCard 
              product={item} 
              onPress={() => handleProductPress(item.id)}
              onAddPress={() => handleAddPress(item.id)}
            />
          </View>
        )}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: colors.white,
  },
  tabsContainer: {
    marginTop: spacing.sm,
    marginBottom: spacing.md,
  },
  tabsContent: {
    paddingHorizontal: spacing.lg,
    gap: spacing.md,
  },
  tab: {
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: 20,
    backgroundColor: colors.gray100,
    marginRight: spacing.sm, // Fallback for older react-native versions without gap support
  },
  activeTab: {
    backgroundColor: colors.warningOrange, // using warningOrange to match accent highlight as requested (orange/red style)
  },
  tabText: {
    fontSize: typography.fontSize.body,
    fontWeight: typography.fontWeight.medium,
    color: colors.gray600,
  },
  activeTabText: {
    color: colors.white,
    fontWeight: typography.fontWeight.bold,
  },
  gridContent: {
    paddingBottom: 100, // Extra padding for bottom navigation
  },
  columnWrapper: {
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    marginBottom: spacing.lg,
  },
  cardWrapper: {
    alignItems: 'center',
  },
});
