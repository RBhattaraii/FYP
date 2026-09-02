import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, Animated, Pressable, Platform } from 'react-native';
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
    Animated.spring(scaleAnim, {
      toValue: 0.96,
      useNativeDriver: true,
      damping: 12,
      mass: 0.6,
      stiffness: 180,
    }).start();
  };

  const handlePressOut = () => {
    Animated.spring(scaleAnim, {
      toValue: 1,
      useNativeDriver: true,
      damping: 12,
      mass: 0.6,
      stiffness: 180,
    }).start();
  };

  const handleWishlistPress = () => {
    // Spring animation for heart
    Animated.sequence([
      Animated.spring(heartScaleAnim, {
        toValue: 1.25,
        damping: 8,
        mass: 0.4,
        stiffness: 200,
        useNativeDriver: true,
      }),
      Animated.spring(heartScaleAnim, {
        toValue: 1,
        damping: 8,
        mass: 0.4,
        stiffness: 200,
        useNativeDriver: true,
      }),
    ]).start();
    
    onWishlistPress();
  };

  return (
    <Animated.View style={{ transform: [{ scale: scaleAnim }] }}>
      <Pressable
        style={({ hovered }: any) => [
          styles.container,
          hovered && styles.containerHovered
        ]}
        onPress={onPress}
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        accessibilityLabel={`${product.name}, ${product.store}, Rs ${product.price.toFixed(2)}`}
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
              <Text style={styles.price}>Rs {product.price.toFixed(2)}</Text>
              {product.originalPrice && (
                <Text style={styles.originalPrice}>
                  Rs {product.originalPrice.toFixed(2)}
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
                activeOpacity={0.7}
              >
                <Ionicons
                  name={product.inWishlist ? 'heart' : 'heart-outline'}
                  size={18}
                  color={product.inWishlist ? colors.primary : colors.gray900}
                />
              </TouchableOpacity>
            </Animated.View>
          </View>
        </View>
      </Pressable>
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
    ...Platform.select({
      web: {
        transition: 'all 0.2s ease-in-out',
      },
      default: {},
    }),
  },
  containerHovered: {
    borderColor: colors.primaryIndigoLight,
    ...Platform.select({
      web: {
        transform: 'translateY(-4px)',
        boxShadow: '0px 15px 35px rgba(79, 70, 229, 0.08), 0px 4px 12px rgba(0, 0, 0, 0.02)',
      },
      default: {},
    }),
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
    fontSize: 14,
    fontWeight: typography.fontWeight.semibold,
    color: colors.gray900,
    lineHeight: 18,
  },
  store: {
    fontSize: typography.fontSize.caption,
    fontWeight: typography.fontWeight.medium,
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
    fontSize: 14,
    fontWeight: typography.fontWeight.bold,
    color: colors.primaryIndigo,
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
    backgroundColor: colors.gray100,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.gray200,
  },
});
