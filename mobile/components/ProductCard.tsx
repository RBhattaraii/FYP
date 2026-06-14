import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, Animated } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, typography, spacing, dimensions, borderRadius, shadows } from '../constants/theme';

interface Product {
  id: string;
  name: string;
  price: number;
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
        <Image
          source={{ uri: product.imageUrl }}
          style={styles.image}
          resizeMode="cover"
        />

        {/* Product Name */}
        <Text style={styles.name} numberOfLines={2}>
          {product.name}
        </Text>

        {/* Price Row */}
        <View style={styles.priceRow}>
          <Text style={styles.price}>${product.price.toFixed(2)}</Text>

          {/* Add Button */}
          <Animated.View style={{ transform: [{ scale: buttonScaleAnim }] }}>
            <TouchableOpacity
              style={styles.addButton}
              onPress={handleAddPress}
              accessibilityLabel={`Add ${product.name} to wishlist`}
              accessibilityRole="button"
            >
              <Ionicons
                name={product.inWishlist ? 'checkmark' : 'add'}
                size={16}
                color={colors.white}
              />
            </TouchableOpacity>
          </Animated.View>
        </View>
      </TouchableOpacity>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    width: dimensions.trendingCard.width,
    height: dimensions.trendingCard.height,
    backgroundColor: colors.white,
    borderRadius: borderRadius.medium,
    borderWidth: 1,
    borderColor: colors.gray100,
    padding: spacing.md,
    ...shadows.card,
  },
  image: {
    width: dimensions.trendingCard.width - spacing.md * 2,
    height: 100,
    borderRadius: borderRadius.small,
    backgroundColor: colors.gray50,
  },
  name: {
    marginTop: spacing.sm,
    fontSize: typography.fontSize.body,
    fontWeight: typography.fontWeight.semibold,
    color: colors.gray900,
    lineHeight: typography.lineHeight.body,
  },
  priceRow: {
    marginTop: spacing.xs,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  price: {
    fontSize: typography.fontSize.bodyLarge,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
  },
  addButton: {
    width: 28,
    height: 28,
    backgroundColor: colors.indigoPrimary,
    borderRadius: borderRadius.small,
    justifyContent: 'center',
    alignItems: 'center',
    ...shadows.button,
  },
});
