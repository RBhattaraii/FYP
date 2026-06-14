import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, Animated } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, typography, spacing, dimensions, borderRadius, shadows } from '../constants/theme';

interface Product {
  id: string;
  name: string;
  price: number;
  rating?: number;
  imageUrl: string;
  inWishlist: boolean;
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
        </View>

        {/* Product Name */}
        <Text style={styles.name} numberOfLines={2}>
          {product.name}
        </Text>

        {/* Price Row */}
        <View style={styles.priceRow}>
          <View>
            <Text style={styles.price}>${product.price.toFixed(2)}</Text>
            {/* Rating below price */}
            {product.rating && (
              <View style={styles.ratingContainer}>
                <Ionicons name="star" size={12} color="#FFD700" />
                <Text style={styles.ratingText}>{product.rating}</Text>
              </View>
            )}
          </View>

          {/* Optional: Add to Cart Button (since wishlist moved) */}
          <TouchableOpacity
            style={styles.addButton}
            onPress={() => console.log('Add to cart')}
            accessibilityLabel={`Add ${product.name} to cart`}
            accessibilityRole="button"
          >
            <Ionicons name="add" size={16} color={colors.white} />
          </TouchableOpacity>
        </View>
      </TouchableOpacity>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    width: dimensions.trendingCard.width,
    minHeight: 250, // Increased height for better visibility
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
    height: 160, // Taller image to occupy more space
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
  name: {
    marginTop: spacing.md,
    fontSize: typography.fontSize.body,
    fontWeight: typography.fontWeight.semibold,
    color: colors.gray900,
    lineHeight: typography.lineHeight.body,
  },
  priceRow: {
    marginTop: spacing.sm,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
  },
  price: {
    fontSize: typography.fontSize.bodyLarge,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
  },
  ratingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
  },
  ratingText: {
    fontSize: 12,
    color: colors.gray600,
    marginLeft: 4,
    fontWeight: typography.fontWeight.medium,
  },
  addButton: {
    width: 32,
    height: 32,
    backgroundColor: colors.indigoPrimary,
    borderRadius: borderRadius.small,
    justifyContent: 'center',
    alignItems: 'center',
    ...shadows.button,
  },
});
