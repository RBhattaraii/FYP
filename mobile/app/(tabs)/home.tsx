import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import * as Haptics from 'expo-haptics';
import { useRouter } from 'expo-router';
import Header from '../../components/Header';
import SearchBar from '../../components/SearchBar';
import CategoryPills from '../../components/CategoryPills';
import HomeCategories from '../../components/HomeCategories';
import TrendingSection from '../../components/TrendingSection';
import RecommendedSection from '../../components/RecommendedSection';
import { colors, spacing } from '../../constants/theme';

// Dummy data for top-level categories
const topCategories = [
  { id: 'electronics', name: 'Electronics', imageUrl: 'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=200&h=200&fit=crop' },
  { id: 'home', name: 'Home', imageUrl: 'https://images.unsplash.com/photo-1556020685-e6a42ea1cd14?w=200&h=200&fit=crop' },
  { id: 'beauty', name: 'Beauty', imageUrl: 'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=200&h=200&fit=crop' },
  { id: 'sports', name: 'Sports', imageUrl: 'https://images.unsplash.com/photo-1517649763962-0c623066013b?w=200&h=200&fit=crop' },
  { id: 'auto', name: 'Auto', imageUrl: 'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=200&h=200&fit=crop' },
];

import { ALL_PRODUCTS } from '../../data/mockData';

// Map trending products directly from our centralized data source to preserve matching IDs
const trendingProducts = ALL_PRODUCTS.slice(0, 3).map((p, index) => ({
  id: p.id,
  title: p.title,
  subtitle: index === 0 ? 'Price dropped by $50' : index === 1 ? 'Lowest price in 30 days' : 'Compare 5 stores',
  imageUrl: p.images[0],
}));

// Map recommended products directly from our centralized data source to preserve matching IDs
const recommendedProducts = ALL_PRODUCTS.slice(3, 5).map((p, index) => ({
  id: p.id,
  title: p.title,
  subtitle: index === 0 ? 'Best deal found at Foot Locker' : 'Price matched at Target',
  imageUrl: p.images[0],
}));

export default function HomeScreen() {
  const router = useRouter();
  const [activeCategory, setActiveCategory] = useState('electronics');

  const handleCategoryPress = (categoryId: string) => {
    if (Platform.OS === 'ios') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    setActiveCategory(categoryId);
  };

  const handleSearchPress = () => {
    router.push('/search');
  };

  const handleVoicePress = () => {
    console.log('Voice search pressed');
  };

  const handleNotificationPress = () => {
    console.log('Notifications pressed');
  };

  const handleProductPress = (productId: string) => {
    router.push(`/product/${productId}`);
  };

  const handleSeeAllTrending = () => {
    console.log('See all trending');
  };

  const handleSeeAllRecommended = () => {
    console.log('See all recommended');
  };

  return (
    <SafeAreaView style={styles.safeArea} edges={['top']}>
      <View style={styles.container}>
        {/* Header */}
        <Header
          firstName="john"
          hasUnreadNotifications={true}
          onNotificationPress={handleNotificationPress}
        />

        {/* Scrollable Content */}
        <ScrollView
          style={styles.scrollView}
          contentContainerStyle={{ paddingBottom: 150 }}
          showsVerticalScrollIndicator={false}
          bounces={true}
          alwaysBounceVertical={true}
          decelerationRate="normal"
          scrollEventThrottle={16}
          contentInsetAdjustmentBehavior="automatic"
        >
          {/* Search Bar */}
          <SearchBar
            onPress={handleSearchPress}
            onVoicePress={handleVoicePress}
          />

          {/* Top Categories (Circular) */}
          <CategoryPills
            categories={topCategories}
            activeCategory={activeCategory}
            onCategoryPress={handleCategoryPress}
          />

          {/* Categories (Grid) */}
          <HomeCategories />

          {/* Trending Now Section */}
          <TrendingSection
            items={trendingProducts}
            onItemPress={handleProductPress}
            onSeeAllPress={handleSeeAllTrending}
          />

          {/* Recommended for You Section */}
          <RecommendedSection
            items={recommendedProducts}
            onItemPress={handleProductPress}
            onSeeAllPress={handleSeeAllRecommended}
          />
          
        </ScrollView>
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
});
