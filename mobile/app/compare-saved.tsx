import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Image,
  ActivityIndicator,
  Alert,
  Platform,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams, Stack } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useFavorites, FavoriteItem } from '../context/FavoritesContext';
import { quickCompareProducts, Product } from '../services/api';
import { authStorage } from '../lib/authStorage';

const THEME_BROWN = '#6E4B3A';
const THEME_BEIGE = '#F9F6F0';
const { width } = Dimensions.get('window');
const COLUMN_WIDTH = (width - 48 - 16) / 2; // 24px padding sides, 16px gap

export default function CompareSavedScreen() {
  const router = useRouter();
  const { productData } = useLocalSearchParams();
  const { items: savedProducts } = useFavorites();
  const [currentProduct, setCurrentProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const { globalSelectedProduct, setGlobalSelectedProduct } = require('../services/api');
    
    if (globalSelectedProduct) {
      setCurrentProduct({ ...globalSelectedProduct });
      setGlobalSelectedProduct(null);
    } else if (productData && typeof productData === 'string') {
      try {
        const product = JSON.parse(productData);
        setCurrentProduct(product);
      } catch (e) {
        console.error('Failed to parse product data:', e);
        Alert.alert('Error', 'Invalid product data');
        router.back();
      }
    } else {
      Alert.alert('Error', 'Product information is missing');
      router.back();
    }
  }, [productData, router]);

  const handleProductSelect = async (selectedItem: FavoriteItem) => {
    if (!currentProduct || !selectedItem) {
      Alert.alert('Error', 'Product information is incomplete');
      return;
    }

    setLoading(true);
    try {
      const token = (await authStorage.getItemAsync('token')) || '';
      let comparisonObj: any = null;

      // Only attempt API compare if BOTH have valid database IDs
      if (currentProduct.id && selectedItem.productId && currentProduct.id > 0 && selectedItem.productId > 0) {
        try {
          comparisonObj = await quickCompareProducts(
            token,
            currentProduct.id,
            selectedItem.productId
          );
        } catch (apiError: any) {
          console.warn('API quick compare failed, falling back to manual:', apiError);
        }
      }

      // Fallback to manual comparison if API failed or skipped
      if (!comparisonObj) {
        comparisonObj = {
          product1: currentProduct,
          product2: {
            id: selectedItem.productId,
            title: selectedItem.title,
            price: selectedItem.price,
            original_price: selectedItem.originalPrice,
            discount_percent: selectedItem.discountPercent,
            image_url: selectedItem.imageUrl,
            store_name: selectedItem.storeName,
            product_url: selectedItem.productUrl || '',
            category: null,
          },
          comparison: {
            price_difference: Math.abs(currentProduct.price - selectedItem.price),
            better_deal: currentProduct.price <= selectedItem.price ? 'product1' : 'product2',
            discount_comparison: (currentProduct.discount_percent || 0) - (selectedItem.discountPercent || 0),
          }
        };
      }

      // Set global variable to avoid URL truncation on Web
      const { setGlobalComparisonData } = require('../services/api');
      setGlobalComparisonData(comparisonObj);

      router.push('/compare-result');
    } catch (error: any) {
      console.error('Comparison error:', error);
      if (error.response?.status === 401) {
        Alert.alert('Session Expired', 'Please log in again to use comparison features.', [
          { text: 'Cancel', style: 'cancel' },
          { text: 'Log In', onPress: () => router.push('/(auth)/login') }
        ]);
      } else {
        Alert.alert('Error', error.message || 'Failed to compare products');
      }
    } finally {
      setLoading(false);
    }
  };

  const renderSavedProduct = ({ item }: { item: FavoriteItem }) => (
    <View style={styles.gridCard}>
      <View style={styles.imageWrapper}>
        <Image 
          source={{ uri: item.imageUrl || 'https://via.placeholder.com/150' }}
          style={styles.gridImage}
          resizeMode="cover"
        />
        {item.discountPercent && item.discountPercent > 0 ? (
          <View style={styles.discountBadge}>
            <Text style={styles.discountText}>-{item.discountPercent}%</Text>
          </View>
        ) : null}
      </View>
      
      <View style={styles.gridContent}>
        <Text style={styles.storeName}>{item.storeName.toUpperCase()}</Text>
        <Text style={styles.gridTitle} numberOfLines={2}>{item.title}</Text>
        <Text style={styles.gridPrice}>Rs {item.price.toLocaleString()}</Text>

        <TouchableOpacity 
          style={styles.compareButton} 
          onPress={() => handleProductSelect(item)}
          activeOpacity={0.8}
          disabled={loading}
        >
          <Ionicons name="git-compare-outline" size={16} color="#FFFFFF" />
          <Text style={styles.compareButtonText}>Compare</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  if (!currentProduct) {
    return (
      <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}>
        <ActivityIndicator size="large" color={THEME_BROWN} />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <Stack.Screen options={{ headerShown: false }} />
      
      {/* Custom Premium Header */}
      <View style={styles.header}>
        <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={24} color="#111111" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Select to Compare</Text>
        <View style={{ width: 44 }} />
      </View>

      {/* Sleek Context Banner */}
      <View style={styles.contextBanner}>
        <Text style={styles.contextLabel}>CURRENTLY COMPARING</Text>
        <View style={styles.contextProductRow}>
          {currentProduct.image_url ? (
            <Image 
              source={{ uri: currentProduct.image_url }} 
              style={[
                styles.contextImage,
                // @ts-ignore
                Platform.OS === 'web' ? { mixBlendMode: 'multiply' } : {}
              ]} 
              resizeMode="contain" 
            />
          ) : (
            <View style={[styles.contextImage, { backgroundColor: '#EEEEEE' }]} />
          )}
          <Text style={styles.contextTitle} numberOfLines={1}>
            {currentProduct.title}
          </Text>
        </View>
      </View>

      {savedProducts.length === 0 ? (
        <View style={styles.centerContainer}>
          <View style={styles.emptyIconCircle}>
            <Ionicons name="heart-outline" size={48} color={THEME_BROWN} />
          </View>
          <Text style={styles.emptyTitle}>No Saved Products</Text>
          <Text style={styles.emptyMessage}>
            You haven't saved any products yet. Save items first to compare them against others!
          </Text>
          <TouchableOpacity 
            style={styles.browseButton}
            onPress={() => router.replace('/(tabs)/home')}
          >
            <Text style={styles.browseButtonText}>Browse Products</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <FlatList
          data={savedProducts}
          renderItem={renderSavedProduct}
          keyExtractor={(item) => item.id}
          numColumns={2}
          columnWrapperStyle={styles.rowWrapper}
          contentContainerStyle={styles.listContainer}
          showsVerticalScrollIndicator={false}
        />
      )}

      {/* Loading Overlay */}
      {loading && (
        <View style={styles.loadingOverlay}>
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={THEME_BROWN} />
            <Text style={styles.loadingText}>Analyzing...</Text>
          </View>
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: THEME_BEIGE,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 24,
    paddingVertical: 12,
    backgroundColor: THEME_BEIGE,
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
    borderWidth: 1,
    borderColor: '#EEEEEE',
  },
  headerTitle: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 16,
    color: '#111111',
  },
  contextBanner: {
    backgroundColor: '#FFFFFF',
    marginHorizontal: 24,
    marginBottom: 20,
    marginTop: 8,
    borderRadius: 16,
    padding: 16,
    shadowColor: '#6E4B3A',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.04,
    shadowRadius: 8,
    elevation: 2,
  },
  contextLabel: {
    fontFamily: 'Poppins_700Bold',
    fontSize: 10,
    color: THEME_BROWN,
    letterSpacing: 1,
    marginBottom: 8,
  },
  contextProductRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  contextImage: {
    width: 32,
    height: 32,
    borderRadius: 6,
    marginRight: 12,
  },
  contextTitle: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 14,
    color: '#111111',
    flex: 1,
  },
  listContainer: {
    paddingHorizontal: 24,
    paddingBottom: 40,
  },
  rowWrapper: {
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  gridCard: {
    width: COLUMN_WIDTH,
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.04,
    shadowRadius: 12,
    elevation: 3,
    borderWidth: 1,
    borderColor: 'rgba(0,0,0,0.02)',
  },
  imageWrapper: {
    width: '100%',
    height: COLUMN_WIDTH,
    backgroundColor: '#F5F5F5',
    position: 'relative',
  },
  gridImage: {
    width: '100%',
    height: '100%',
  },
  discountBadge: {
    position: 'absolute',
    top: 10,
    right: 10,
    backgroundColor: '#E53935',
    paddingHorizontal: 6,
    paddingVertical: 4,
    borderRadius: 8,
  },
  discountText: {
    fontFamily: 'Poppins_700Bold',
    fontSize: 10,
    color: '#FFFFFF',
  },
  gridContent: {
    padding: 14,
  },
  storeName: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 10,
    color: THEME_BROWN,
    letterSpacing: 0.5,
    marginBottom: 4,
  },
  gridTitle: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 13,
    color: '#111111',
    lineHeight: 18,
    marginBottom: 8,
    height: 36,
  },
  gridPrice: {
    fontFamily: 'Poppins_700Bold',
    fontSize: 15,
    color: '#111111',
    marginBottom: 12,
  },
  compareButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: THEME_BROWN,
    paddingVertical: 10,
    borderRadius: 12,
    gap: 6,
  },
  compareButtonText: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 13,
    color: '#FFFFFF',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 32,
  },
  emptyIconCircle: {
    width: 96,
    height: 96,
    borderRadius: 48,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.05,
    shadowRadius: 12,
    elevation: 2,
  },
  emptyTitle: {
    fontFamily: 'Poppins_700Bold',
    fontSize: 22,
    color: '#111111',
    marginBottom: 12,
    textAlign: 'center',
  },
  emptyMessage: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 14,
    color: '#757575',
    textAlign: 'center',
    marginBottom: 32,
    lineHeight: 22,
  },
  browseButton: {
    backgroundColor: THEME_BROWN,
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 9999,
  },
  browseButtonText: {
    color: '#FFFFFF',
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 16,
  },
  loadingOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0, 0, 0, 0.4)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingContainer: {
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 32,
    paddingVertical: 24,
    borderRadius: 24,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.1,
    shadowRadius: 24,
    elevation: 10,
  },
  loadingText: {
    marginTop: 16,
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 15,
    color: THEME_BROWN,
  },
});