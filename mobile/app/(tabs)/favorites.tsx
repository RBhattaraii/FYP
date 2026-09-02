import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Image, Platform, Dimensions } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { useFavorites } from '../../context/FavoritesContext';

const { width } = Dimensions.get('window');
const cardWidth = (width - 48 - 16) / 2; // 24px padding on sides, 16px gap between cards

export default function FavoritesScreen() {
  const router = useRouter();
  const { items: favoriteItems, removeItem } = useFavorites();


  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.header}>
        <TouchableOpacity style={styles.headerIcon} onPress={() => router.canGoBack() ? router.back() : router.replace('/')}>
          <Ionicons name="arrow-back" size={20} color="#111111" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>My Wishlist</Text>
        <View style={styles.headerPlaceholder} />
      </View>

      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollContent}>
        {favoriteItems.length === 0 ? (
          <View style={styles.emptyState}>
            <Ionicons name="heart-outline" size={80} color="#E0E0E0" />
            <Text style={styles.emptyTitle}>Your wishlist is empty</Text>
          </View>
        ) : (
          <View style={styles.gridContainer}>
            {favoriteItems.map((item) => (
              <TouchableOpacity 
                key={item.id} 
                style={styles.productCard} 
                activeOpacity={0.9} 
                onPress={() => {
                  const productData = {
                    id: item.productId || item.id,
                    title: item.title,
                    price: item.price,
                    image_url: item.imageUrl,
                    store_name: item.storeName,
                    product_url: item.productUrl,
                    original_price: item.originalPrice,
                    discount_percent: item.discountPercent
                  };
                  router.push({
                    pathname: `/product/${encodeURIComponent(item.id)}`,
                    params: { productData: JSON.stringify(productData) }
                  });
                }}
              >
                <View style={styles.imageContainer}>
                  <Image source={{ uri: item.imageUrl }} style={styles.productImage} resizeMode="cover" />
                  <LinearGradient 
                    colors={['rgba(0,0,0,0.4)', 'transparent']} 
                    style={StyleSheet.absoluteFillObject} 
                    start={{x: 0, y: 0}} end={{x: 0, y: 0.4}}
                  />
                  <TouchableOpacity style={styles.heartButton} onPress={() => removeItem(item.id)} activeOpacity={0.7}>
                    <Ionicons name="heart" size={18} color="#FF4757" />
                  </TouchableOpacity>
                </View>
                
                <View style={styles.cardDetails}>
                  <Text style={styles.productName} numberOfLines={2}>{item.title}</Text>
                  
                  <View style={styles.priceRow}>
                    <Text style={styles.productPrice}>Rs {item.price.toLocaleString()}</Text>
                    <View style={styles.ratingBadge}>
                      <Ionicons name="star" size={12} color="#FFA502" />
                      <Text style={styles.ratingText}>4.9</Text>
                    </View>
                  </View>
                </View>
              </TouchableOpacity>
            ))}
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#FAFAFA',
    paddingTop: Platform.OS === 'android' ? 25 : 0,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 24,
    paddingBottom: 16,
    paddingTop: 8,
  },
  headerIcon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    borderWidth: 1,
    borderColor: '#EEEEEE',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
  },
  headerTitle: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 16,
    color: '#111111',
  },
  headerPlaceholder: {
    width: 44,
  },
  scrollContent: {
    paddingHorizontal: 24,
    paddingBottom: 100,
  },
  gridContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    paddingTop: 8,
  },
  productCard: {
    width: cardWidth,
    marginBottom: 24,
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.06,
    shadowRadius: 16,
    elevation: 4,
  },
  imageContainer: {
    width: '100%',
    height: cardWidth * 1.15,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    overflow: 'hidden',
    backgroundColor: '#F7F7F7',
  },
  productImage: {
    width: '100%',
    height: '100%',
  },
  heartButton: {
    position: 'absolute',
    top: 12,
    right: 12,
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 5,
  },
  cardDetails: {
    padding: 12,
    paddingTop: 14,
  },
  productName: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 13,
    color: '#2D3436',
    lineHeight: 18,
    height: 36, // Force two lines
    marginBottom: 10,
  },
  priceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  productPrice: {
    fontFamily: 'Poppins_700Bold',
    fontSize: 15,
    color: '#FF6B6B',
  },
  ratingBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF8E1',
    paddingHorizontal: 6,
    paddingVertical: 3,
    borderRadius: 8,
    gap: 4,
  },
  ratingText: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 11,
    color: '#FFA502',
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 80,
  },
  emptyTitle: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 16,
    color: '#B2BEC3',
    marginTop: 16,
  }
});
