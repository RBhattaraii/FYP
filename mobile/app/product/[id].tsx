import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, Image, TouchableOpacity, Dimensions } from 'react-native';
import { useLocalSearchParams, useRouter, Stack } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { colors, spacing, typography, borderRadius, shadows } from '../../constants/theme';

const { width } = Dimensions.get('window');

import { ALL_PRODUCTS, MOCK_OFFERS } from '../../data/mockData';

export default function ProductDetailScreen() {
  const { id } = useLocalSearchParams();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  
  // Find product from centralized mock data, or fallback if ID doesn't match
  const foundProduct = ALL_PRODUCTS.find(p => p.id === id) || ALL_PRODUCTS[0];
  
  // Combine product info with dynamic offers (faking varied prices)
  const productData = {
    ...foundProduct,
    offers: MOCK_OFFERS.map((o, idx) => ({
      ...o,
      price: foundProduct.price + (idx * 5.99), // Give slight variations to prices
    }))
  };
  
  const [activeImageIndex, setActiveImageIndex] = useState(0);

  const handleScroll = (event: any) => {
    const scrollPosition = event.nativeEvent.contentOffset.x;
    const currentIndex = Math.round(scrollPosition / width);
    setActiveImageIndex(currentIndex);
  };

  return (
    <View style={styles.container}>
      <Stack.Screen options={{ headerShown: false }} />
      <ScrollView 
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{ paddingBottom: insets.bottom + 120 }}
      >
        {/* Top Area: Navigation and Actions */}
        <View style={[styles.topArea, { marginTop: Math.max(insets.top, spacing.md) }]}>
          <TouchableOpacity 
            style={styles.iconButton} 
            onPress={() => router.back()}
          >
            <Ionicons name="close" size={24} color={colors.gray900} />
          </TouchableOpacity>
          
          <View style={styles.actionStack}>
            <TouchableOpacity style={styles.iconButton}>
              <Ionicons name="share-outline" size={22} color={colors.gray900} />
            </TouchableOpacity>
            <TouchableOpacity style={[styles.iconButton, { marginTop: spacing.md }]}>
              <Ionicons name="heart-outline" size={22} color={colors.gray900} />
            </TouchableOpacity>
          </View>
        </View>

        {/* Product Gallery Section */}
        <View style={styles.gallerySection}>
          <ScrollView 
            horizontal 
            pagingEnabled 
            showsHorizontalScrollIndicator={false}
            onScroll={handleScroll}
            scrollEventThrottle={16}
          >
            {productData.images.map((img, index) => (
              <View key={index} style={styles.imageContainer}>
                <Image 
                  source={{ uri: img }} 
                  style={styles.productImage} 
                  resizeMode="contain"
                />
              </View>
            ))}
          </ScrollView>
          
          {/* Pagination Indicators */}
          <View style={styles.paginationContainer}>
            {productData.images.map((_, index) => (
              <View 
                key={index} 
                style={[
                  styles.paginationDot, 
                  activeImageIndex === index && styles.paginationDotActive
                ]} 
              />
            ))}
          </View>
        </View>

        {/* Product Information Block */}
        <View style={styles.infoBlock}>
          {/* Header & Title Area */}
          <View style={styles.headerRow}>
            <Text style={styles.brand}>{productData.brand.toUpperCase()}</Text>
            <View style={styles.ratingContainer}>
              <Ionicons name="star" size={16} color="#FFD700" />
              <Text style={styles.ratingText}>{productData.rating}</Text>
              <Text style={styles.reviewsText}>({productData.reviewsCount})</Text>
            </View>
          </View>
          
          <Text style={styles.title}>{productData.title}</Text>
          
          <Text style={styles.descriptionText}>
            {productData.description}
          </Text>

          {/* Information Tabs */}
          <View style={styles.tabsRow}>
            <View style={styles.tabItem}>
              <Ionicons name="information-circle-outline" size={24} color={colors.gray900} />
              <Text style={styles.tabLabel}>Details</Text>
            </View>
            <View style={styles.tabSeparator} />
            <View style={styles.tabItem}>
              <Ionicons name="analytics-outline" size={24} color={colors.gray900} />
              <Text style={styles.tabLabel}>Compare</Text>
            </View>
            <View style={styles.tabSeparator} />
            <View style={styles.tabItem}>
              <Ionicons name="time-outline" size={24} color={colors.gray900} />
              <Text style={styles.tabLabel}>History</Text>
            </View>
          </View>
        </View>

        {/* Offers Section */}
        <View style={styles.offersSection}>
          {/* Header */}
          <View style={styles.offersHeader}>
            <Text style={styles.offersCount}>{productData.offers.length} Offers</Text>
            <TouchableOpacity>
              <Text style={styles.showAllLink}>Show all</Text>
            </TouchableOpacity>
          </View>

          {/* Offer Cards List */}
          <View style={styles.offersList}>
            {productData.offers.map((offer) => (
              <View key={offer.id} style={styles.offerCard}>
                {/* Top Row */}
                <View style={styles.offerCardTop}>
                  <Text style={styles.offerPrice}>${offer.price.toFixed(2)}</Text>
                  <View style={styles.storeInfoContainer}>
                    <Text style={styles.storeName}>{offer.storeName}</Text>
                  </View>
                  <TouchableOpacity style={styles.expandButton}>
                    <Ionicons name="chevron-forward" size={20} color={colors.gray400} />
                  </TouchableOpacity>
                </View>
                
                {/* Bottom Row */}
                <View style={styles.offerCardBottom}>
                  <Text style={styles.offerVariant}>{offer.variant}</Text>
                  <Text style={[
                    styles.offerStatus, 
                    offer.status === 'In Stock' ? styles.statusInStock : styles.statusOut
                  ]}>
                    {offer.status}
                  </Text>
                </View>
              </View>
            ))}
          </View>
        </View>
      </ScrollView>

      {/* Fixed Bottom Action Bar */}
      <View style={[styles.bottomBar, { paddingBottom: Math.max(insets.bottom, spacing.md) }]}>
        <View style={styles.bottomPriceContainer}>
          <Text style={styles.bottomPriceLabel}>Best Price</Text>
          <Text style={styles.bottomPriceValue}>${productData.price.toFixed(2)}</Text>
        </View>
        <TouchableOpacity style={styles.primaryButton}>
          <Text style={styles.primaryButtonText}>Buy Now</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.white,
  },
  topArea: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    paddingHorizontal: spacing.lg,
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    zIndex: 10,
  },
  iconButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.white,
    justifyContent: 'center',
    alignItems: 'center',
    ...shadows.card,
  },
  actionStack: {
    alignItems: 'center',
  },
  gallerySection: {
    paddingTop: 80, // Space for the absolute top area
    alignItems: 'center',
    backgroundColor: colors.gray50,
    paddingBottom: spacing.lg,
    borderBottomWidth: 1,
    borderBottomColor: colors.gray100,
  },
  imageContainer: {
    width: width,
    alignItems: 'center',
    justifyContent: 'center',
    // Removed paddingHorizontal so image fills the width
  },
  productImage: {
    width: '100%',
    height: width, // Square aspect ratio 1:1
  },
  paginationContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: spacing.md,
  },
  paginationDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.gray200,
    marginHorizontal: 4,
  },
  paginationDotActive: {
    width: 24,
    backgroundColor: colors.warningOrange, // using warning orange for brand matching
  },
  infoBlock: {
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.xl,
    paddingBottom: spacing.sm, // Reduced space
  },
  title: {
    fontSize: typography.fontSize.h2,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
    textAlign: 'left',
    lineHeight: typography.lineHeight.h2,
    marginTop: spacing.xs,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.xs,
  },
  brand: {
    fontSize: typography.fontSize.caption,
    color: colors.indigoPrimary,
    fontWeight: typography.fontWeight.bold,
    letterSpacing: 1,
  },
  descriptionText: {
    fontSize: typography.fontSize.body,
    color: colors.gray600,
    lineHeight: typography.lineHeight.bodyLarge,
    marginTop: spacing.md,
  },
  ratingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  ratingText: {
    fontSize: typography.fontSize.body,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
    marginLeft: 4,
  },
  reviewsText: {
    fontSize: typography.fontSize.caption,
    color: colors.gray400,
    marginLeft: 4,
  },
  bottomBar: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: colors.white,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.gray100,
    ...shadows.card,
  },
  bottomPriceContainer: {
    flex: 1,
  },
  bottomPriceLabel: {
    fontSize: typography.fontSize.caption,
    color: colors.gray500,
  },
  bottomPriceValue: {
    fontSize: typography.fontSize.h2,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
  },
  primaryButton: {
    backgroundColor: colors.indigoPrimary,
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.md,
    borderRadius: borderRadius.full,
    ...shadows.button,
  },
  primaryButtonText: {
    color: colors.white,
    fontSize: typography.fontSize.button,
    fontWeight: typography.fontWeight.semibold,
  },
  tabsRow: {
    flexDirection: 'row',
    justifyContent: 'space-evenly',
    alignItems: 'center',
    backgroundColor: colors.white,
    borderRadius: borderRadius.medium,
    paddingVertical: spacing.md,
    marginTop: spacing.lg,
    borderWidth: 1,
    borderColor: colors.gray200,
  },
  tabItem: {
    alignItems: 'center',
    flex: 1,
  },
  tabLabel: {
    fontSize: typography.fontSize.caption,
    fontWeight: typography.fontWeight.medium,
    color: colors.gray900,
    marginTop: spacing.xs,
  },
  tabSeparator: {
    width: 1,
    height: 30,
    backgroundColor: colors.gray200,
  },
  offersSection: {
    paddingHorizontal: spacing.lg,
    marginTop: spacing.xs, // Reduced space between info and offers
  },
  offersHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  offersCount: {
    fontSize: typography.fontSize.bodyLarge,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
  },
  showAllLink: {
    fontSize: typography.fontSize.body,
    fontWeight: typography.fontWeight.medium,
    color: colors.warningOrange,
  },
  offersList: {
    gap: spacing.md,
  },
  offerCard: {
    backgroundColor: colors.gray50,
    borderRadius: borderRadius.medium,
    padding: spacing.md,
  },
  offerCardTop: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  offerPrice: {
    fontSize: typography.fontSize.h3,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
    flex: 1,
  },
  storeInfoContainer: {
    flex: 2,
    alignItems: 'flex-end',
    paddingRight: spacing.sm,
  },
  storeName: {
    fontSize: typography.fontSize.body,
    fontWeight: typography.fontWeight.semibold,
    color: colors.gray900,
  },
  expandButton: {
    padding: spacing.xs,
  },
  offerCardBottom: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: spacing.sm,
    paddingTop: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.gray100,
  },
  offerVariant: {
    fontSize: typography.fontSize.caption,
    color: colors.gray600,
  },
  offerStatus: {
    fontSize: typography.fontSize.caption,
    fontWeight: typography.fontWeight.bold,
  },
  statusInStock: {
    color: colors.successGreen,
  },
  statusOut: {
    color: colors.errorRed,
  },
});
