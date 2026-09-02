import React, { useState, useRef, useEffect } from 'react';
import { View, StyleSheet, FlatList, ScrollView, Platform, NativeSyntheticEvent, NativeScrollEvent, Text, TouchableOpacity, Image, Animated, Easing, useWindowDimensions } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import * as Haptics from 'expo-haptics';
import { Ionicons } from '@expo/vector-icons';

import Header from '../../components/Header';
import ProductCard from '../../components/ProductCard';
import FullImageCard from '../../components/FullImageCard';
import { colors, spacing, typography, borderRadius, shadows } from '../../constants/theme';
import { ALL_PRODUCTS } from '../../data/mockData';

const BRAND_OFFERS = [
  { id: 'brand1', name: 'Nike', offer: '60% OFF', logo: 'https://cdn-icons-png.flaticon.com/512/732/732229.png' },
  { id: 'brand2', name: 'Sony', offer: '40% OFF', logo: 'https://cdn-icons-png.flaticon.com/512/5969/5969282.png' },
  { id: 'brand3', name: 'Apple', offer: 'SAVE $200', logo: 'https://cdn-icons-png.flaticon.com/512/0/747.png' },
  { id: 'brand4', name: 'Samsung', offer: 'FREE BUDS', logo: 'https://cdn-icons-png.flaticon.com/512/5969/5969116.png' },
  { id: 'brand5', name: 'Adidas', offer: '50% OFF', logo: 'https://cdn-icons-png.flaticon.com/512/732/732148.png' },
  { id: 'brand6', name: 'Puma', offer: 'FLAT 30%', logo: 'https://cdn-icons-png.flaticon.com/512/732/732238.png' },
  { id: 'brand7', name: 'LG', offer: 'CASHBACK', logo: 'https://cdn-icons-png.flaticon.com/512/882/882753.png' },
];

const MOCK_BANNERS = [
  {
    id: 'b1',
    title: 'Super Summer Sale',
    subtitle: 'Up to 50% Off Everything',
    imageUrl: 'https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?w=800&h=400&fit=crop'
  },
  {
    id: 'b2',
    title: 'Tech Deals',
    subtitle: 'Extra 20% on Laptops',
    imageUrl: 'https://images.unsplash.com/photo-1550009158-9efff6c9e54a?w=800&h=400&fit=crop'
  },
  {
    id: 'b3',
    title: 'Fashion Week',
    subtitle: 'Buy 1 Get 1 Free',
    imageUrl: 'https://images.unsplash.com/photo-1445205170230-053b83016050?w=800&h=400&fit=crop'
  },
  {
    id: 'b4',
    title: 'Home Essentials',
    subtitle: 'Flat 30% Off',
    imageUrl: 'https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?w=800&h=400&fit=crop'
  }
];



import { fetchHomeScreenProducts, Product } from '../../services/api';

export default function OffersScreen() {
  const router = useRouter();
  const { width } = useWindowDimensions();
  const [products, setProducts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeBanner, setActiveBanner] = useState(0);
  const activeBannerRef = useRef(0);
  const scrollViewRef = useRef<ScrollView>(null);
  const bannerIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const marqueeAnim = useRef(new Animated.Value(0)).current;
  const SINGLE_ROW_WIDTH = 84 * BRAND_OFFERS.length; // 72 width + 12 margin

  useEffect(() => {
    Animated.loop(
      Animated.timing(marqueeAnim, {
        toValue: -SINGLE_ROW_WIDTH,
        duration: 15000,
        easing: Easing.linear,
        useNativeDriver: true,
      })
    ).start();
  }, [marqueeAnim, SINGLE_ROW_WIDTH]);

  const startAutoScroll = () => {
    stopAutoScroll();
    bannerIntervalRef.current = setInterval(() => {
      let nextIndex = activeBannerRef.current + 1;
      if (nextIndex >= MOCK_BANNERS.length) {
        nextIndex = 0;
      }
      scrollViewRef.current?.scrollTo({ x: nextIndex * width, animated: true });
    }, 4000);
  };

  const stopAutoScroll = () => {
    if (bannerIntervalRef.current) {
      clearInterval(bannerIntervalRef.current);
    }
  };

  useEffect(() => {
    startAutoScroll();
    loadOffers();
    return () => stopAutoScroll();
  }, []);

  const loadOffers = async () => {
    try {
      setLoading(true);
      const data = await fetchHomeScreenProducts();
      // Use best deals for the offers grid
      const formatted = data.best_deals.map((p: Product) => ({
        id: p.id ? p.id.toString() : p.title,
        name: p.title,
        price: p.price,
        imageUrl: p.image_url,
        inWishlist: false,
        promotionalBadge: p.discount_percent ? `${p.discount_percent}% OFF` : undefined,
      }));
      setProducts(formatted);
    } catch (err) {
      console.error('Failed to load offers:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleScroll = (event: NativeSyntheticEvent<NativeScrollEvent>) => {
    const offsetX = event.nativeEvent.contentOffset.x;
    const index = Math.round(offsetX / width);
    if (index !== activeBanner && index >= 0 && index < MOCK_BANNERS.length) {
      setActiveBanner(index);
      activeBannerRef.current = index;
    }
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
      <Header />
      
      {/* Offer Banner Carousel */}
      <View style={styles.bannerContainer}>
        <ScrollView
          ref={scrollViewRef}
          horizontal
          showsHorizontalScrollIndicator={false}
          pagingEnabled
          decelerationRate="fast"
          onScroll={handleScroll}
          scrollEventThrottle={16}
          onScrollBeginDrag={stopAutoScroll}
          onScrollEndDrag={startAutoScroll}
        >
          {MOCK_BANNERS.map((banner) => (
            <View key={banner.id} style={{ width: width, paddingHorizontal: spacing.lg }}>
              <FullImageCard
                title={banner.title}
                subtitle={banner.subtitle}
                imageUrl={banner.imageUrl}
                onPress={() => console.log('Banner pressed', banner.id)}
                width={width - 2 * spacing.lg}
                height={160}
              />
            </View>
          ))}
        </ScrollView>
        <View style={styles.paginationContainer}>
          {MOCK_BANNERS.map((_, index) => (
            <View
              key={index}
              style={[
                styles.dot,
                activeBanner === index && styles.activeDot
              ]}
            />
          ))}
        </View>
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
  bannerContainer: {
    marginTop: spacing.sm,
  },
  paginationContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: spacing.md,
    marginBottom: spacing.xs,
  },
  dot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: colors.gray300,
    marginHorizontal: 4,
  },
  activeDot: {
    width: 16,
    backgroundColor: colors.primaryIndigo,
  },
  brandSectionContainer: {
    marginTop: spacing.sm,
    marginBottom: spacing.lg,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    marginBottom: spacing.md,
  },
  sectionTitle: {
    fontSize: typography.fontSize.h3,
    fontWeight: typography.fontWeight.semibold,
    color: colors.gray900,
  },
  seeAllText: {
    fontSize: typography.fontSize.body,
    color: colors.primaryIndigo,
    fontWeight: typography.fontWeight.semibold,
  },
  marqueeContainer: {
    overflow: 'hidden',
    paddingBottom: spacing.sm,
  },
  marqueeInner: {
    flexDirection: 'row',
    width: 84 * 14, // 14 items (2x7)
  },
  brandItem: {
    alignItems: 'center',
    width: 72,
    marginRight: spacing.md,
  },
  brandLogoCircle: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: colors.white,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.gray100,
    ...shadows.card,
    marginBottom: spacing.xs,
  },
  brandLogoImage: {
    width: 36,
    height: 36,
    borderRadius: 18,
  },
  brandItemOffer: {
    fontSize: 11,
    fontWeight: '800',
    color: colors.primary,
    textAlign: 'center',
  },
  brandItemName: {
    fontSize: 10,
    color: colors.gray400,
    marginTop: 2,
    textAlign: 'center',
  },
  gridContent: {
    paddingBottom: 100, // Extra padding for bottom navigation
  },
  columnWrapper: {
    justifyContent: 'space-between',
    paddingHorizontal: spacing.md,
    marginBottom: spacing.lg,
  },
  cardWrapper: {
    alignItems: 'center',
  },
});
