import React, { useState } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, Image, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { colors, typography, spacing, borderRadius, shadows } from '../constants/theme';
import { ALL_PRODUCTS } from '../data/mockData';
import Header from '../components/Header';

const INITIAL_WISHLIST = ALL_PRODUCTS.slice(0, 4).map(p => ({
  ...p,
  inWishlist: true,
  imageUrl: p.images[0]
}));



const EmptyState = ({ onExplore }: { onExplore: () => void }) => (
  <View style={styles.emptyContainer}>
    <Ionicons name="heart-dislike-outline" size={80} color={colors.gray300} style={styles.emptyIcon} />
    <Text style={styles.emptyTitle}>Your wishlist is empty</Text>
    <Text style={styles.emptySubtitle}>Save items you love to review them later.</Text>
    <TouchableOpacity style={styles.exploreButton} onPress={onExplore} activeOpacity={0.8}>
      <Text style={styles.exploreButtonText}>Explore Products</Text>
    </TouchableOpacity>
  </View>
);

const WishlistCard = ({
  item,
  onPress,
  onRemove,
  onCompare
}: {
  item: any;
  onPress: () => void;
  onRemove: () => void;
  onCompare: () => void;
}) => {
  return (
    <TouchableOpacity style={styles.cardContainer} onPress={onPress} activeOpacity={0.8}>
      {/* Left side: Image */}
      <View style={styles.imageContainer}>
        <Image source={{ uri: item.imageUrl }} style={styles.image} />
        {/* Rating Badge over image */}
        <View style={styles.ratingBadge}>
          <Ionicons name="star" size={12} color={colors.warningOrange} />
          <Text style={styles.ratingText}>{item.rating}</Text>
        </View>
      </View>

      {/* Right side: Content */}
      <View style={styles.contentContainer}>
        <View style={styles.titleRow}>
          <Text style={styles.title} numberOfLines={2}>{item.title}</Text>
          <TouchableOpacity onPress={onRemove} style={styles.removeButton} activeOpacity={0.7} hitSlop={{ top: 10, right: 10, bottom: 10, left: 10 }}>
            <Ionicons name="close-outline" size={22} color={colors.gray400} />
          </TouchableOpacity>
        </View>

        <Text style={styles.brandText}>{item.brand}</Text>

        {/* Badges */}
        <View style={styles.badgesRow}>
          <View style={styles.stockBadge}>
            <Text style={styles.stockBadgeText}>3+ Offers</Text>
          </View>
          {item.price > 200 && (
            <View style={styles.promoBadge}>
              <Text style={styles.promoBadgeText}>Best Deal</Text>
            </View>
          )}
        </View>

        {/* Bottom Row: Price & Action */}
        <View style={styles.bottomRow}>
          <View style={styles.priceContainer}>
            <Text style={styles.priceLabel}>From </Text>
            <Text style={styles.price}>${item.price.toFixed(2)}</Text>
          </View>
          <TouchableOpacity style={styles.cartButton} onPress={onCompare} activeOpacity={0.7}>
            <Ionicons name="pricetags-outline" size={16} color={colors.gray900} style={{ marginRight: 4 }} />
            <Text style={styles.cartButtonText}>Compare</Text>
          </TouchableOpacity>
        </View>
      </View>
    </TouchableOpacity>
  );
};

export default function WishlistScreen() {
  const router = useRouter();
  const [wishlistItems, setWishlistItems] = useState(INITIAL_WISHLIST);

  const handleRemoveWishlist = (id: string) => {
    setWishlistItems(prev => prev.filter(item => item.id !== id));
  };

  const handleCompare = (id: string) => {
    // In a real app, this might navigate specifically to a comparison tab inside the product details
    router.push(`/product/${id}`);
  };

  const handleProductPress = (id: string) => {
    router.push(`/product/${id}`);
  };

  const renderItem = ({ item }: { item: any }) => (
    <WishlistCard
      item={item}
      onPress={() => handleProductPress(item.id)}
      onRemove={() => handleRemoveWishlist(item.id)}
      onCompare={() => handleCompare(item.id)}
    />
  );

  return (
    <SafeAreaView style={styles.safeArea} edges={['top']}>
      <Header
        title="Wishlist"
        showBackBtn={true}
        onBackPress={() => router.back()}
      />

      {wishlistItems.length === 0 ? (
        <EmptyState onExplore={() => router.navigate('/(tabs)/explore')} />
      ) : (
        <FlatList
          data={wishlistItems}
          keyExtractor={(item) => item.id}
          renderItem={renderItem}
          contentContainerStyle={styles.listContent}
          showsVerticalScrollIndicator={false}
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: colors.gray50,
  },
  listContent: {
    padding: spacing.md,
    paddingBottom: spacing['4xl'],
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: spacing.xl,
  },
  emptyIcon: {
    marginBottom: spacing.lg,
  },
  emptyTitle: {
    fontSize: typography.fontSize.h2,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
    marginBottom: spacing.sm,
    textAlign: 'center',
  },
  emptySubtitle: {
    fontSize: typography.fontSize.body,
    color: colors.gray600,
    textAlign: 'center',
    marginBottom: spacing.xl,
    lineHeight: 22,
  },
  exploreButton: {
    backgroundColor: colors.primary,
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.md,
    borderRadius: borderRadius.full,
  },
  exploreButtonText: {
    color: colors.white,
    fontSize: typography.fontSize.bodyLarge,
    fontWeight: typography.fontWeight.bold,
  },
  cardContainer: {
    flexDirection: 'row',
    backgroundColor: colors.white,
    borderRadius: borderRadius.medium,
    marginBottom: spacing.md,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: colors.gray100,
  },
  imageContainer: {
    width: 110,
    height: 130,
    backgroundColor: colors.gray100,
  },
  image: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  ratingBadge: {
    position: 'absolute',
    top: spacing.sm,
    left: spacing.sm,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: borderRadius.small,
  },
  ratingText: {
    fontSize: 10,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
    marginLeft: 2,
  },
  contentContainer: {
    flex: 1,
    padding: spacing.md,
    justifyContent: 'space-between',
  },
  titleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  title: {
    flex: 1,
    fontSize: typography.fontSize.body,
    fontWeight: typography.fontWeight.medium,
    color: colors.gray900,
    marginRight: spacing.sm,
  },
  removeButton: {
    padding: 2,
  },
  brandText: {
    fontSize: typography.fontSize.caption,
    color: colors.gray600,
    marginTop: 2,
  },
  badgesRow: {
    flexDirection: 'row',
    marginTop: spacing.sm,
    marginBottom: spacing.xs,
  },
  stockBadge: {
    borderWidth: 1,
    borderColor: colors.successGreen,
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: borderRadius.small,
    marginRight: spacing.xs,
  },
  stockBadgeText: {
    color: colors.successGreen,
    fontSize: 10,
    fontWeight: typography.fontWeight.medium,
  },
  promoBadge: {
    borderWidth: 1,
    borderColor: colors.warningOrange,
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: borderRadius.small,
  },
  promoBadgeText: {
    color: colors.warningOrange,
    fontSize: 10,
    fontWeight: typography.fontWeight.medium,
  },
  bottomRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: spacing.sm,
  },
  priceContainer: {
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  priceLabel: {
    fontSize: typography.fontSize.caption,
    color: colors.gray700,
    fontWeight: typography.fontWeight.medium,
  },
  price: {
    fontSize: typography.fontSize.body,
    fontWeight: typography.fontWeight.semibold,
    color: colors.gray900,
  },
  cartButton: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.gray200,
    backgroundColor: colors.white,
    paddingHorizontal: spacing.md,
    paddingVertical: 6,
    borderRadius: borderRadius.full,
  },
  cartButtonText: {
    color: colors.gray900,
    fontSize: typography.fontSize.caption,
    fontWeight: typography.fontWeight.medium,
  },
});
