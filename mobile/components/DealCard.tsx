import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image } from 'react-native';
import { colors, typography, borderRadius, shadows, spacing } from '../constants/theme';

interface DealCardProps {
  title: string;
  imageUrl: string;
  price: number;
  originalPrice?: number;
  discountPercent?: number;
  storeName?: string;
  badgeLabel?: string;
  width?: number | string;
  onPress: () => void;
  onAddPress?: () => void; // Kept for interface compatibility but not rendered
}

export default function DealCard({
  title,
  imageUrl,
  price,
  originalPrice,
  discountPercent,
  storeName,
  badgeLabel,
  width = '100%',
  onPress,
}: DealCardProps) {
  const formattedPrice = `Rs ${price.toLocaleString()}`;

  return (
    <TouchableOpacity
      style={[styles.productCard, { width: width as any }]}
      activeOpacity={0.8}
      onPress={onPress}
    >
      <View style={styles.imageContainer}>
        <Image
          source={{ uri: imageUrl }}
          style={styles.productImage}
          resizeMode="cover"
        />
        {discountPercent ? (
          <View style={styles.discountBadge}>
            <Text style={styles.discountText}>-{Math.round(discountPercent)}%</Text>
          </View>
        ) : badgeLabel ? (
          <View style={styles.discountBadge}>
            <Text style={styles.discountText}>{badgeLabel}</Text>
          </View>
        ) : null}
      </View>
      
      <View style={styles.productInfo}>
        <Text style={styles.productName} numberOfLines={2}>
          {title}
        </Text>
        
        {storeName && (
          <Text style={styles.storeName}>{storeName}</Text>
        )}
        
        <View style={styles.priceRow}>
          <Text style={styles.productPrice}>
            {formattedPrice}
          </Text>
          {originalPrice && (
            <Text style={styles.originalPrice}>
              Rs {originalPrice.toLocaleString()}
            </Text>
          )}
        </View>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  productCard: {
    borderRadius: borderRadius.large,
    backgroundColor: colors.white,
    ...shadows.card,
    borderWidth: 1,
    borderColor: colors.gray100,
  },
  imageContainer: {
    width: '100%',
    aspectRatio: 1,
    borderTopLeftRadius: borderRadius.large,
    borderTopRightRadius: borderRadius.large,
    overflow: 'hidden',
    backgroundColor: colors.gray50,
  },
  productImage: {
    width: '100%',
    height: '100%',
  },
  discountBadge: {
    position: 'absolute',
    top: spacing.sm,
    right: spacing.sm,
    backgroundColor: '#704F38',
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
    borderRadius: borderRadius.medium,
  },
  discountText: {
    color: colors.white,
    fontSize: typography.fontSize.caption,
    fontWeight: typography.fontWeight.bold,
  },
  productInfo: {
    padding: spacing.md,
  },
  productName: {
    fontFamily: typography.fontFamily.primary,
    fontSize: typography.fontSize.small,
    fontWeight: typography.fontWeight.medium,
    color: colors.gray900,
    marginBottom: spacing.xs,
    height: 36, // Fixed height for 2 lines
  },
  storeName: {
    fontFamily: typography.fontFamily.primary,
    fontSize: typography.fontSize.caption,
    color: colors.gray500,
    marginBottom: spacing.xs,
  },
  priceRow: {
    flexDirection: 'row',
    alignItems: 'baseline',
    flexWrap: 'wrap',
    gap: spacing.xs,
  },
  productPrice: {
    fontFamily: typography.fontFamily.primary,
    fontSize: typography.fontSize.body,
    fontWeight: typography.fontWeight.bold,
    color: '#6E4B3A', // THEME_BROWN
  },
  originalPrice: {
    fontFamily: typography.fontFamily.primary,
    fontSize: typography.fontSize.caption,
    color: colors.gray400,
    textDecorationLine: 'line-through',
  },
});