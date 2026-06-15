import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Image } from 'react-native';
import { colors, typography, spacing, dimensions } from '../constants/theme';

interface Category {
  id: string;
  name: string;
  imageUrl?: string;
}

interface CategoryPillsProps {
  categories: Category[];
  activeCategory: string;
  onCategoryPress: (categoryId: string) => void;
}

export default function CategoryPills({ 
  categories, 
  activeCategory, 
  onCategoryPress 
}: CategoryPillsProps) {
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Categories</Text>
        <TouchableOpacity>
          <Text style={styles.seeAllText}>See All</Text>
        </TouchableOpacity>
      </View>
      <View style={styles.gridContainer}>
        {categories.map((category) => {
          const isActive = category.id === activeCategory;
          return (
            <TouchableOpacity
              key={category.id}
              style={styles.categoryItem}
              onPress={() => onCategoryPress(category.id)}
              activeOpacity={0.7}
              accessibilityLabel={`${category.name} category`}
              accessibilityState={{ selected: isActive }}
              accessibilityRole="button"
            >
              <View style={[styles.circle, isActive && styles.circleActive]}>
                <Image 
                  source={{ uri: category.imageUrl || `https://via.placeholder.com/80?text=${category.name.charAt(0)}` }} 
                  style={styles.image} 
                />
              </View>
              <Text
                style={[
                  styles.categoryText,
                  isActive && styles.categoryTextActive,
                ]}
                numberOfLines={1}
              >
                {category.name}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>
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
  gridContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
  },
  categoryItem: {
    alignItems: 'center',
    width: '18%', // Fits 5 items per row with space-between
    marginBottom: spacing.md,
  },
  circle: {
    width: 56,
    height: 56,
    borderRadius: 28,
    overflow: 'hidden',
    backgroundColor: colors.gray100,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: 'transparent',
    marginBottom: spacing.xs,
  },
  circleActive: {
    borderColor: colors.warningOrange,
  },
  image: {
    width: '100%',
    height: '100%',
  },
  categoryText: {
    fontSize: typography.fontSize.caption,
    fontWeight: typography.fontWeight.regular,
    color: colors.gray600,
    textAlign: 'center',
  },
  categoryTextActive: {
    fontWeight: typography.fontWeight.semibold,
    color: colors.gray900,
  },
});
