import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, Animated } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, typography, spacing, dimensions, borderRadius, shadows } from '../constants/theme';

interface RecommendedProduct {
  id: string;
  name: string;
  store: string;
  price: number;
  originalPrice?: number;
  discount?: number;
  imageUrl: string;
  inWishlist: boolean;
}

interface RecommendationCardProps {
  product: RecommendedProduct;
  onPress: () => void;
  onWishlistPress: () => void;
}

export default function RecommendationCard({ 
  product, 
  onPress, 
  onWishlistPress 
}: RecommendationCardProps) {
  const scaleAnim = React.useRef(new Animated.Value(1)).current;
  const heartScaleAnim = React.useRef(new Animated.Value(1)).current;

  const handlePressIn = () => {
    Animated.timing(scaleAnim, {
      toValue: 0.98,
      duration: 150,
      useNativeDriver: true,
    }).start();
  };

  const handlePressOut = () => {
    Animated.timing(scaleAnim, {
      toValue: 1,
      duration: 150,
      useNativeDriver: true,
    }).start();
  };

  const handleWishlistPress = () => {
    // Spring animation for heart
    Animated.sequence([
      Animated.spring(heartScaleAnim, {
        toValue: 1.3,
        friction: 3,
        tension: 40,
        useNativeDriver: true,
      }),
      Animated.spring(heartScaleAnim, {
        toValue: 1,
        friction: 3,
        tension: 40,
        useNativeDriver: true,
      }),
    ]).start();
    
    onWishlistPress();
  };

  return (
    <Animated.View style={{ transform: [{ scale: scaleAnim }] }}>
      <TouchableOpacity
        style={styles.container}
        onPress={onPress}
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        activeOpacity={1}
        accessibilityLabel={`${product.name}, ${product.store}, $${product.price.toFixed(2)}`}
        accessibilityRole="button"
      >
        {/* Product Image */}
        <Image
          source={{ uri: product.imageUrl }}
          style={styles.image}
          resizeMode="cover"
        />

        {/* Content Area */}
        <View style={styles.content}>
          {/* Product Name */}
          <Text style={styles.name} numberOfLines={2}>
            {product.name}
          </Text>

          {/* Store Name */}
          <Text style={styles.store}>{product.store}</Text>

          {/* Price Row */}
          <View style={styles.priceRow}>
            <View style={styles.priceInfo}>
              <Text style={styles.price}>${product.price.toFixed(2)}</Text>
              {product.originalPrice && (
                <Text style={styles.originalPrice}>
                  ${product.originalPrice.toFixed(2)}
                </Text>
              )}
              {product.discount && (
                <Text style={styles.discount}>{product.discount}% OFF</Text>
              )}
            </View>

            {/* Wishlist Button */}
            <Animated.View style={{ transform: [{ scale: heartScaleAnim }] }}>
              <TouchableOpacity
                style={styles.wishlistButton}
                onPress={handleWishlistPress}
                accessibilityLabel={`${product.inWishlist ? 'Remove from' : 'Add to'} wishlist`}
                accessibilityRole="button"
              >
                <Ionicons
                  name={product.inWishlist ? 'heart' : 'heart-outline'}
                  size={20}
                  color={product.inWishlist ? colors.primary : colors.gray600}
                />
              </TouchableOpacity>
            </Animated.View>
          </View>
        </View>
      </TouchableOpacity>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    width: dimensions.recommendedCard.width,
    height: dimensions.recommendedCard.height,
    backgroundColor: colors.white,
    borderRadius: borderRadius.large,
    borderWidth: 1,
    borderColor: colors.gray100,
    padding: spacing.base,
    flexDirection: 'row',
    ...shadows.featuredCard,
  },
  image: {
    width: 100,
    height: dimensions.recommendedCard.height - spacing.base * 2,
    borderRadius: borderRadius.medium,
    backgroundColor: colors.gray50,
  },
  content: {
    flex: 1,
    marginLeft: spacing.md,
    justifyContent: 'space-between',
  },
  name: {
    fontSize: typography.fontSize.h3,
    fontWeight: typography.fontWeight.semibold,
    color: colors.gray900,
    lineHeight: typography.lineHeight.h3,
  },
  store: {
    fontSize: typography.fontSize.caption,
    fontWeight: typography.fontWeight.regular,
    color: colors.gray400,
    marginTop: spacing.xs,
  },
  priceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  priceInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  price: {
    fontSize: typography.fontSize.bodyLarge,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
  },
  originalPrice: {
    fontSize: typography.fontSize.caption,
    fontWeight: typography.fontWeight.regular,
    color: colors.gray400,
    textDecorationLine: 'line-through',
  },
  discount: {
    fontSize: typography.fontSize.caption,
    fontWeight: typography.fontWeight.semibold,
    color: colors.successGreen,
  },
  wishlistButton: {
    width: 32,
    height: 32,
    backgroundColor: colors.gray50,
    borderRadius: borderRadius.small,
    justifyContent: 'center',
    alignItems: 'center',
  },
});
