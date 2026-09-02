import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, useWindowDimensions, ScrollView } from 'react-native';
import DealCard from './DealCard';
import { colors, typography, spacing } from '../constants/theme';

interface RecommendedItem {
  id: string;
  title: string;
  imageUrl: string;
  price: number;
  originalPrice?: number;
  discountPercent?: number;
  storeName?: string;
}

interface RecommendedSectionProps {
  title?: string;
  items: RecommendedItem[];
  onItemPress: (itemId: string) => void;
  onSeeAllPress: () => void;
}

export default function RecommendedSection({
  title = "Top Price Drops",
  items,
  onItemPress,
  onSeeAllPress,
}: RecommendedSectionProps) {
  const { width } = useWindowDimensions();
  const visibleCardsCount = width > 768 ? 3.5 : 2.15;
  const cardWidth = (width - spacing.lg * 2 - spacing.md * (Math.ceil(visibleCardsCount) - 1)) / visibleCardsCount;

  return (
    <View style={styles.container}>
      {/* Section Header */}
      <View style={styles.header}>
        <Text style={styles.title}>{title}</Text>
        <TouchableOpacity
          style={styles.seeAllButton}
          onPress={onSeeAllPress}
          accessibilityLabel="See all recommended"
          accessibilityRole="button"
        >
          <Text style={styles.seeAllText}>See all</Text>
        </TouchableOpacity>
      </View>

      <ScrollView 
        horizontal 
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
        snapToInterval={cardWidth + spacing.md}
        decelerationRate="fast"
      >
        {items.map((item) => (
          <View key={item.id} style={{ width: cardWidth }}>
            <DealCard
              title={item.title}
              imageUrl={item.imageUrl}
              price={item.price}
              originalPrice={item.originalPrice}
              discountPercent={item.discountPercent}
              storeName={item.storeName}
              badgeLabel={item.discountPercent ? `${item.discountPercent}% OFF` : undefined}
              width={cardWidth}
              onPress={() => onItemPress(item.id)}
              onAddPress={() => onItemPress(item.id)}
            />
          </View>
        ))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginTop: spacing.xl,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    marginBottom: spacing.md,
  },
  title: {
    fontSize: typography.fontSize.h2,
    fontWeight: typography.fontWeight.semibold,
    color: colors.gray900,
  },
  seeAllButton: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  seeAllText: {
    fontSize: typography.fontSize.body,
    fontWeight: typography.fontWeight.regular,
    color: '#704F38',
  },
  scrollContent: {
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.sm,
    flexDirection: 'row',
    gap: spacing.md,
  },
});
