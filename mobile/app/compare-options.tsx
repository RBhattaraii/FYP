import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView, Platform, ScrollView, Image } from 'react-native';
import { useLocalSearchParams, useRouter, Stack } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Product, setGlobalSelectedProduct } from '../services/api';

const THEME_BROWN = '#6E4B3A';

export default function CompareOptionsScreen() {
  const { productData } = useLocalSearchParams();
  const router = useRouter();
  const [product, setProduct] = useState<Product | null>(null);

  useEffect(() => {
    if (productData && typeof productData === 'string') {
      try {
        setProduct(JSON.parse(productData));
      } catch (e) {
        console.error('Failed to parse product data', e);
      }
    }
  }, [productData]);

  const handleCompareWithSaved = () => {
    if (product) {
      setTimeout(() => {
        setGlobalSelectedProduct(product);
        router.push('/compare-saved');
      }, 100);
    }
  };

  const handleSearchToCompare = () => {
    if (product) {
      setTimeout(() => {
        setGlobalSelectedProduct(product);
        router.push('/compare-search');
      }, 100);
    }
  };

  const navigateToMyComparisons = () => {
    router.push('/my-comparisons');
  };

  if (!product) return null;

  return (
    <SafeAreaView style={styles.safeArea}>
      <Stack.Screen options={{ headerShown: false }} />
      <View style={styles.header}>
        <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={24} color="#111111" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Compare Options</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: 60 }} showsVerticalScrollIndicator={false}>
        {/* Hero Product Highlight */}
        <View style={styles.heroCard}>
          <Text style={styles.heroLabel}>CURRENTLY COMPARING</Text>
          {product.image_url ? (
            <Image 
              source={{ uri: product.image_url }} 
              style={[
                styles.heroImage,
                // @ts-ignore
                Platform.OS === 'web' ? { mixBlendMode: 'multiply' } : {}
              ]} 
              resizeMode="contain" 
            />
          ) : (
            <View style={[styles.heroImage, { backgroundColor: '#F5F5F5', justifyContent: 'center', alignItems: 'center' }]}>
              <Ionicons name="image-outline" size={40} color="#BDBDBD" />
            </View>
          )}
          <Text style={styles.heroTitle} numberOfLines={2}>{product.title}</Text>
          <View style={styles.priceRow}>
            <Text style={styles.heroPrice}>Rs {product.price.toLocaleString()}</Text>
            <View style={styles.storeBadge}>
              <Text style={styles.storeBadgeText}>{product.store_name}</Text>
            </View>
          </View>
        </View>

        <Text style={styles.sectionTitle}>Choose an Option</Text>

        <View style={styles.optionsContainer}>
          {/* Option 1: Saved */}
          <TouchableOpacity style={styles.optionCard} onPress={handleCompareWithSaved} activeOpacity={0.7}>
            <View style={[styles.iconContainer, { backgroundColor: '#F4ECE7' }]}>
              <Ionicons name="heart" size={24} color={THEME_BROWN} />
            </View>
            <View style={styles.optionContent}>
              <Text style={styles.optionTitle}>Saved Products</Text>
              <Text style={styles.optionDescription}>Compare with your favorites and saved items</Text>
            </View>
            <Ionicons name="chevron-forward" size={24} color="#BDBDBD" />
          </TouchableOpacity>

          {/* Option 2: Search */}
          <TouchableOpacity style={styles.optionCard} onPress={handleSearchToCompare} activeOpacity={0.7}>
            <View style={[styles.iconContainer, { backgroundColor: '#F3E5F5' }]}>
              <Ionicons name="search" size={24} color="#8E24AA" />
            </View>
            <View style={styles.optionContent}>
              <Text style={styles.optionTitle}>Search Product</Text>
              <Text style={styles.optionDescription}>Find any new product to compare instantly</Text>
            </View>
            <Ionicons name="chevron-forward" size={24} color="#BDBDBD" />
          </TouchableOpacity>

          {/* Option 3: History */}
          <TouchableOpacity style={styles.optionCard} onPress={navigateToMyComparisons} activeOpacity={0.7}>
            <View style={[styles.iconContainer, { backgroundColor: '#E3F2FD' }]}>
              <Ionicons name="layers" size={24} color="#1976D2" />
            </View>
            <View style={styles.optionContent}>
              <Text style={styles.optionTitle}>My Comparisons</Text>
              <Text style={styles.optionDescription}>View your saved product comparisons history</Text>
            </View>
            <Ionicons name="chevron-forward" size={24} color="#BDBDBD" />
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#F7F7F7',
    paddingTop: Platform.OS === 'android' ? 24 : 0,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 24,
    paddingBottom: 16,
    paddingTop: 8,
    backgroundColor: '#F7F7F7',
  },
  backButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  headerTitle: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 18,
    color: '#111111',
  },
  container: {
    flex: 1,
    paddingHorizontal: 24,
  },
  heroCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 28,
    padding: 24,
    marginTop: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.04,
    shadowRadius: 16,
    elevation: 4,
    alignItems: 'center',
  },
  heroLabel: {
    fontFamily: 'Poppins_700Bold',
    fontSize: 11,
    color: THEME_BROWN,
    letterSpacing: 1,
    marginBottom: 24,
  },
  heroImage: {
    width: 160,
    height: 160,
    borderRadius: 16,
    marginBottom: 24,
  },
  heroTitle: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 16,
    color: '#111111',
    textAlign: 'center',
    marginBottom: 16,
    lineHeight: 24,
  },
  priceRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  heroPrice: {
    fontFamily: 'Poppins_700Bold',
    fontSize: 24,
    color: THEME_BROWN,
  },
  storeBadge: {
    backgroundColor: '#F5F5F5',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 9999,
  },
  storeBadgeText: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 12,
    color: '#757575',
  },
  sectionTitle: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 16,
    color: '#111111',
    marginTop: 36,
    marginBottom: 16,
  },
  optionsContainer: {
    gap: 16,
  },
  optionCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    padding: 20,
    borderRadius: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.03,
    shadowRadius: 12,
    elevation: 2,
  },
  iconContainer: {
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  optionContent: {
    flex: 1,
  },
  optionTitle: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 15,
    color: '#111111',
    marginBottom: 4,
  },
  optionDescription: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 13,
    color: '#757575',
    lineHeight: 18,
  },
});
