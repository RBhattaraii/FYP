import React from 'react';
import { View, Text, StyleSheet, Pressable, Image, Animated, TouchableWithoutFeedback, Dimensions } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';

const { width } = Dimensions.get('window');
// Calculate card width based on screen size to allow 2 columns with padding
const cardWidth = (width - 48 - 16) / 2; 

interface Product {
  id: string;
  name: string;
  price: number;
  rating?: number;
  imageUrl: string;
  inWishlist: boolean;
  promotionalBadge?: string;
  storeCount?: number;
}

interface ProductCardProps {
  product: Product;
  onPress: () => void;
  onAddPress: () => void;
}

export default function ProductCard({ product, onPress, onAddPress }: ProductCardProps) {
  const scaleAnim = React.useRef(new Animated.Value(1)).current;

  const handlePressIn = () => {
    Animated.spring(scaleAnim, {
      toValue: 0.95,
      useNativeDriver: true,
      damping: 12,
      mass: 0.6,
      stiffness: 180,
    }).start();
  };

  const handlePressOut = () => {
    Animated.spring(scaleAnim, {
      toValue: 1,
      useNativeDriver: true,
      damping: 12,
      mass: 0.6,
      stiffness: 180,
    }).start();
  };

  return (
    <Animated.View style={{ transform: [{ scale: scaleAnim }] }}>
      <Pressable
        style={styles.productCard}
        onPress={onPress}
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
      >
        <View style={styles.imageContainer}>
          <Image
            source={{ uri: product.imageUrl || 'https://via.placeholder.com/150?text=No+Image' }}
            style={styles.productImage}
            resizeMode="cover"
          />
          <LinearGradient 
            colors={['rgba(0,0,0,0.3)', 'transparent']} 
            style={StyleSheet.absoluteFillObject} 
            start={{x: 0, y: 0}} end={{x: 0, y: 0.4}}
          />
          <TouchableWithoutFeedback onPress={onAddPress}>
            <View style={styles.heartButton}>
              <Ionicons
                name={product.inWishlist ? 'heart' : 'heart-outline'}
                size={18}
                color={product.inWishlist ? '#FF4757' : '#2D3436'}
              />
            </View>
          </TouchableWithoutFeedback>
        </View>

        <View style={styles.cardDetails}>
          <Text style={styles.productName} numberOfLines={2}>
            {product.name}
          </Text>

          <View style={styles.priceRow}>
            <Text style={styles.productPrice}>Rs {product.price.toLocaleString()}</Text>
            <View style={styles.ratingBadge}>
              <Ionicons name="star" size={12} color="#FFA502" />
              <Text style={styles.ratingText}>{product.rating || '4.9'}</Text>
            </View>
          </View>
          
          <Text style={styles.storeCount}>{product.storeCount || 3}+ Stores Available</Text>
        </View>
      </Pressable>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  productCard: {
    width: cardWidth,
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.06,
    shadowRadius: 16,
    elevation: 4,
    marginBottom: 20,
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
    marginBottom: 8,
  },
  priceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
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
  storeCount: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 11,
    color: '#B2BEC3',
  }
});
