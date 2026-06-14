import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import FullImageCard from './FullImageCard';
import { colors, typography, spacing } from '../constants/theme';

interface RecommendedItem {
  id: string;
  title: string;
  subtitle: string;
  imageUrl: string;
}

interface RecommendedSectionProps {
  items: RecommendedItem[];
  onItemPress: (itemId: string) => void;
  onSeeAllPress: () => void;
}

export default function RecommendedSection({
  items,
  onItemPress,
  onSeeAllPress,
}: RecommendedSectionProps) {
  return (
    <View style={styles.container}>
      {/* Section Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Compare These Deals</Text>
        <TouchableOpacity
          style={styles.seeAllButton}
          onPress={onSeeAllPress}
          accessibilityLabel="See all recommended"
          accessibilityRole="button"
        >
          <Text style={styles.seeAllText}>See all</Text>
        </TouchableOpacity>
      </View>

      {/* Cards */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
        decelerationRate="fast"
      >
        {items.map((item) => (
          <FullImageCard
            key={item.id}
            title={item.title}
            subtitle={item.subtitle}
            imageUrl={item.imageUrl}
            onPress={() => onItemPress(item.id)}
            width={300}
            height={200}
          />
        ))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginTop: spacing.xl,
    marginBottom: 80, // Extra margin to ensure bottom tabs don't overlap content
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
    color: colors.gray600,
  },
  scrollContent: {
    paddingHorizontal: spacing.lg,
    gap: spacing.md,
  },
});
