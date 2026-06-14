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

import { ALL_PRODUCTS } from '../../data/mockData';

// Generate mock products from centralized data to ensure ID mapping works perfectly
const MOCK_PRODUCTS = ALL_PRODUCTS.map(p => ({
  id: p.id,
  name: p.title,
  price: p.price,
  rating: p.rating,
  imageUrl: p.images[0],
  inWishlist: false,
}));

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
