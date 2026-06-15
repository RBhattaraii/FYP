import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, Animated, Pressable } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, typography, spacing, dimensions, borderRadius, shadows } from '../constants/theme';

interface Product {
  id: string;
  name: string;
  price: number;
  rating?: number;
  imageUrl: string;
  inWishlist: boolean;
  promotionalBadge?: string;
  storeCount?: number;
}

interface ProductCardProps {
  product: Product;
  onPress: () => void;
  onAddPress: () => void;
}

export default function ProductCard({ product, onPress, onAddPress }: ProductCardProps) {
  const scaleAnim = React.useRef(new Animated.Value(1)).current;
  const buttonScaleAnim = React.useRef(new Animated.Value(1)).current;

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

  const handleAddPress = () => {
    // Spring animation for button
    Animated.sequence([
      Animated.spring(buttonScaleAnim, {
        toValue: 1.2,
        friction: 3,
        tension: 40,
        useNativeDriver: true,
      }),
      Animated.spring(buttonScaleAnim, {
        toValue: 1,
        friction: 3,
        tension: 40,
        useNativeDriver: true,
      }),
    ]).start();
    
    onAddPress();
  };

  return (
    <Animated.View style={{ transform: [{ scale: scaleAnim }] }}>
      <TouchableOpacity
        style={styles.container}
        onPress={onPress}
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        activeOpacity={1}
        accessibilityLabel={`${product.name}, $${product.price.toFixed(2)}`}
        accessibilityRole="button"
      >
        {/* Product Image */}
        <View style={styles.imageContainer}>
          <Image
            source={{ uri: product.imageUrl }}
            style={styles.image}
            resizeMode="cover"
          />
          
          {/* Wishlist Heart Top Left */}
          <Animated.View style={[styles.wishlistIconContainer, { transform: [{ scale: buttonScaleAnim }] }]}>
            <TouchableOpacity
              style={styles.wishlistButton}
              onPress={handleAddPress}
              accessibilityLabel={`Toggle ${product.name} in wishlist`}
              accessibilityRole="button"
            >
              <Ionicons
                name={product.inWishlist ? 'heart' : 'heart-outline'}
                size={20}
                color={product.inWishlist ? colors.warningOrange : colors.gray900}
              />
            </TouchableOpacity>
          </Animated.View>

          {/* Promotional Badge Top Right */}
          {product.promotionalBadge && (
            <View style={styles.badgeContainer}>
              <Text style={styles.badgeText}>{product.promotionalBadge}</Text>
            </View>
          )}
        </View>

        {/* Product Name */}
        <Text style={styles.name} numberOfLines={2}>
          {product.name}
        </Text>

        {/* Price Row */}
        <View style={styles.priceRow}>
          <View>
            <Text style={styles.storeCount}>{product.storeCount || 3}+ Stores</Text>
            <View style={styles.priceContainer}>
              <Text style={styles.priceLabel}>From </Text>
              <Text style={styles.price}>${product.price.toFixed(2)}</Text>
            </View>
          </View>

          {/* View Deals Button */}
          <Pressable
            style={({ pressed }) => [
              styles.addButton,
              pressed && styles.addButtonPressed
            ]}
            onPress={onPress}
            accessibilityLabel={`Compare deals for ${product.name}`}
            accessibilityRole="button"
          >
            {({ pressed }) => (
              <Ionicons 
                name="chevron-forward" 
                size={14} 
                color={pressed ? colors.white : colors.gray900} 
              />
            )}
          </Pressable>
        </View>
      </TouchableOpacity>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    width: dimensions.trendingCard.width,
    minHeight: 270, // Increased height to accommodate larger image
    backgroundColor: colors.white,
    borderRadius: borderRadius.medium,
    borderWidth: 1,
    borderColor: colors.gray100,
    padding: spacing.sm, // Reduced padding to reduce "border" around content
    ...shadows.card,
  },
  imageContainer: {
    position: 'relative',
    width: '100%',
  },
  image: {
    width: '100%',
    height: 180, // Taller image to emphasize the product
    borderRadius: borderRadius.small,
    backgroundColor: colors.gray50,
  },
  wishlistIconContainer: {
    position: 'absolute',
    top: spacing.xs,
    left: spacing.xs,
  },
  wishlistButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: 'rgba(255, 255, 255, 0.85)',
    justifyContent: 'center',
    alignItems: 'center',
    ...shadows.button,
  },
  badgeContainer: {
    position: 'absolute',
    top: spacing.xs,
    right: spacing.xs,
    backgroundColor: colors.warningOrange,
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: borderRadius.small,
  },
  badgeText: {
    color: colors.white,
    fontSize: 10,
    fontWeight: typography.fontWeight.bold,
  },
  name: {
    marginTop: spacing.md,
    fontSize: typography.fontSize.caption,
    fontWeight: typography.fontWeight.medium,
    color: colors.gray900,
    lineHeight: typography.lineHeight.caption,
  },
  priceRow: {
    marginTop: spacing.sm,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
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
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
  },
  storeCount: {
    fontSize: typography.fontSize.caption,
    color: colors.gray600,
    marginBottom: 2,
    fontWeight: typography.fontWeight.medium,
  },
  addButton: {
    width: 26,
    height: 26,
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: colors.gray300,
    borderRadius: borderRadius.small,
    justifyContent: 'center',
    alignItems: 'center',
  },
  addButtonPressed: {
    backgroundColor: colors.gray900,
    borderColor: colors.gray900,
  },
});
