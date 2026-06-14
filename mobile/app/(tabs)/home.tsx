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

// Dummy data for top price drops (formerly trending products)
const trendingProducts = [
  {
    id: '1',
    title: 'Sony WH-1000XM4 Headphones',
    subtitle: 'Price dropped by $50',
    imageUrl: 'https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=800&h=1000&fit=crop',
  },
  {
    id: '2',
    title: 'Apple iPad Air (5th Gen)',
    subtitle: 'Lowest price in 30 days',
    imageUrl: 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=800&h=1000&fit=crop',
  },
  {
    id: '3',
    title: 'Samsung Galaxy S23',
    subtitle: 'Compare 5 stores',
    imageUrl: 'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=800&h=1000&fit=crop',
  },
];

// Dummy data for recommended comparisons
const recommendedProducts = [
  {
    id: '1',
    title: 'Nike Air Max 270',
    subtitle: 'Best deal found at Foot Locker',
    imageUrl: 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=1000&h=600&fit=crop',
  },
  {
    id: '2',
    title: 'Dyson V11 Vacuum',
    subtitle: 'Price matched at Target',
    imageUrl: 'https://images.unsplash.com/photo-1558317374-067fb5f30001?w=1000&h=600&fit=crop',
  },
];

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
    console.log('Item pressed:', productId);
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
