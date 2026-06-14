import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, typography, spacing, borderRadius } from '../constants/theme';

interface CategoryItem {
  id: string;
  name: string;
  iconName: keyof typeof Ionicons.glyphMap;
  backgroundColor: string;
}

const categoriesData: CategoryItem[] = [
  { id: '1', name: 'Fashion', iconName: 'shirt-outline', backgroundColor: '#FFF5E1' }, // Light Orange/Yellow
  { id: '2', name: 'Footwear', iconName: 'footsteps-outline', backgroundColor: '#FFEBEA' }, // Light Pink/Red
  { id: '3', name: 'Gift', iconName: 'gift-outline', backgroundColor: '#FFEBEA' }, // Light Pink/Red
  { id: '4', name: 'Gadget', iconName: 'hardware-chip-outline', backgroundColor: '#F3E8FF' }, // Light Purple
  { id: '5', name: 'Comp', iconName: 'laptop-outline', backgroundColor: '#E6F4EA' }, // Light Green
];

export default function HomeCategories() {
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Categories</Text>
        <TouchableOpacity>
          <Text style={styles.seeAllText}>See All</Text>
        </TouchableOpacity>
      </View>
      
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
        decelerationRate="fast"
      >
        {categoriesData.map((category) => (
          <TouchableOpacity
            key={category.id}
            style={styles.categoryItem}
            activeOpacity={0.7}
          >
            <View style={[styles.iconContainer, { backgroundColor: category.backgroundColor }]}>
              <Ionicons name={category.iconName} size={24} color={colors.gray900} />
            </View>
            <Text style={styles.categoryName} numberOfLines={1}>
              {category.name}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginTop: spacing.sm,
    marginBottom: spacing.lg,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    marginBottom: spacing.md,
  },
  title: {
    fontSize: typography.fontSize.h3,
    fontWeight: typography.fontWeight.semibold,
    color: colors.gray900,
  },
  seeAllText: {
    fontSize: typography.fontSize.body,
    color: colors.gray600,
  },
  scrollContent: {
    paddingHorizontal: spacing.lg,
    gap: spacing.md,
  },
  categoryItem: {
    alignItems: 'center',
    width: 68,
  },
  iconContainer: {
    width: 56,
    height: 56,
    borderRadius: borderRadius.medium,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.xs,
  },
  categoryName: {
    fontSize: typography.fontSize.caption,
    fontWeight: typography.fontWeight.regular,
    color: colors.gray900,
    textAlign: 'center',
  },
});
