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
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
        decelerationRate="fast"
        snapToInterval={undefined}
        snapToAlignment="start"
        bounces={true}
      >
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
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    height: 100,
    marginTop: spacing.sm,
    marginBottom: spacing.md,
  },
  scrollContent: {
    paddingHorizontal: spacing.lg,
    gap: spacing.md,
  },
  categoryItem: {
    alignItems: 'center',
    width: 64,
  },
  circle: {
    width: 60,
    height: 60,
    borderRadius: 30,
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
