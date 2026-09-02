import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface Category {
  id: string;
  name: string;
}

interface CategoryPillsProps {
  categories: Category[];
  activeCategory: string;
  onCategoryPress: (categoryId: string) => void;
}

// Map tech categories to Ionicons
const getCategoryIcon = (id: string): keyof typeof Ionicons.glyphMap => {
  const map: Record<string, keyof typeof Ionicons.glyphMap> = {
    'Electronics': 'hardware-chip-outline',
    'phone': 'phone-portrait-outline',
    'laptop': 'laptop-outline',
    'smartwatch': 'watch-outline',
    'audio': 'headset-outline',
    'Home_Appliances': 'home-outline',
    'Computer_Accessories': 'desktop-outline',
  };
  return map[id] || 'apps-outline';
};

export default function CategoryPills({ 
  categories, 
  activeCategory, 
  onCategoryPress 
}: CategoryPillsProps) {
  // Take top 4 for the row layout like the screenshot
  const displayCategories = categories.slice(0, 4);

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Category</Text>
        <TouchableOpacity activeOpacity={0.7}>
          <Text style={styles.seeAllText}>See All</Text>
        </TouchableOpacity>
      </View>
      
      <View style={styles.gridContainer}>
        {displayCategories.map((category) => {
          const isActive = category.id === activeCategory;
          return (
            <TouchableOpacity
              key={category.id}
              activeOpacity={0.7}
              style={styles.categoryItem}
              onPress={() => onCategoryPress(category.id)}
            >
              <View style={styles.circle}>
                <Ionicons 
                  name={getCategoryIcon(category.id)} 
                  size={24} 
                  color={'#111111'} 
                />
              </View>
              <Text
                style={styles.categoryText}
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
    paddingHorizontal: 24,
    marginBottom: 24,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  title: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 18,
    color: '#111111',
  },
  seeAllText: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 13,
    color: '#9E9E9E',
  },
  gridContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  categoryItem: {
    alignItems: 'center',
    width: '22%',
  },
  circle: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#F5F5F5',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  circleActive: {
    backgroundColor: '#111111',
  },
  categoryText: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 12,
    color: '#111111',
    textAlign: 'center',
  },
});
