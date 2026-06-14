import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import FullImageCard from './FullImageCard';
import { colors, typography, spacing } from '../constants/theme';

interface TrendingItem {
  id: string;
  title: string;
  subtitle: string;
  imageUrl: string;
}

interface TrendingSectionProps {
  items: TrendingItem[];
  onItemPress: (itemId: string) => void;
  onSeeAllPress: () => void;
}

export default function TrendingSection({
  items,
  onItemPress,
  onSeeAllPress,
}: TrendingSectionProps) {
  return (
    <View style={styles.container}>
      {/* Section Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Top Price Drops</Text>
        <TouchableOpacity
          style={styles.seeAllButton}
          onPress={onSeeAllPress}
          accessibilityLabel="See all trending"
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
            width={240}
            height={280}
          />
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
    color: colors.gray600,
  },
  scrollContent: {
    paddingHorizontal: spacing.lg,
    gap: spacing.md,
  },
});
