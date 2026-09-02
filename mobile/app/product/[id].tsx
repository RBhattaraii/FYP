import React, { useState, useCallback, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, Image, TouchableOpacity, Dimensions, ActivityIndicator, Linking, Alert, useWindowDimensions, Platform, Modal, TextInput, Share } from 'react-native';
import { useLocalSearchParams, useRouter, Stack } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useFocusEffect } from '@react-navigation/native';
import { colors, spacing, typography, borderRadius, shadows } from '../../constants/theme';
import { fetchProductDetail, Product } from '../../services/api';
import { useFavorites } from '../../context/FavoritesContext';
import { authStorage } from '../../lib/authStorage';
import { createPriceAlert } from '../../services/notifications';
import { useAuth } from '../../hooks/useAuth';



export default function ProductDetailScreen() {
  const { width: windowWidth } = useWindowDimensions();
  const isTabletOrWeb = windowWidth > 768;
  const contentMaxWidth = 680;
  const imageSize = isTabletOrWeb ? 450 : windowWidth;
  const { id, productData } = useLocalSearchParams();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { addItem, removeItem, items } = useFavorites();

  // State for API data
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [product, setProduct] = useState<Product | null>(null);
  const [activeImageIndex, setActiveImageIndex] = useState(0);
  const [imageVersion, setImageVersion] = useState(0);
  const [isAlertModalVisible, setIsAlertModalVisible] = useState(false);
  const [targetPriceInput, setTargetPriceInput] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [alertSuccess, setAlertSuccess] = useState(false);
  const [similarProducts, setSimilarProducts] = useState<Product[]>([]);

  // Check if current product is in favorites
  const isInFavorites = product ? items.some(item => 
    item.id === `${product.store_name}-${product.product_url}`
  ) : false;

  useEffect(() => {
    let isActive = true;

    async function loadProduct() {
      if (!id || Array.isArray(id)) {
        setError('Invalid product ID');
        setLoading(false);
        return;
      }

      // If product is already loaded and we just returned to this screen, do not reset it
      if (product) {
        return;
      }

      try {
        setLoading(true);
        setError(null);
        setActiveImageIndex(0);
        const { globalSelectedProduct } = require('../../services/api');
        
        if (globalSelectedProduct) {
          const parsedProduct = { ...globalSelectedProduct }; // clone it
          if (!parsedProduct.title && parsedProduct.name) {
            parsedProduct.title = parsedProduct.name;
          }
          setProduct(parsedProduct);
          
          // Clear it so it doesn't bleed into future deep links that only provide an ID
          const { setGlobalSelectedProduct } = require('../../services/api');
          setGlobalSelectedProduct(null);
        } else if (productData && typeof productData === 'string') {
          try {
            const parsedProduct = JSON.parse(productData);
            // Map search result fields to Product type if needed
            if (!parsedProduct.title && parsedProduct.name) {
              parsedProduct.title = parsedProduct.name;
            }
            setProduct(parsedProduct);
          } catch (e) {
            console.error("Failed to parse product data", e);
            setError("Failed to parse product data");
          }
        } else {
          // Fallback to fetching from API if data isn't in memory or params
          const data = await fetchProductDetail(String(id));
          setProduct(data);
        }

        if (!isActive) return;

        // Fetch similar products based on the first word of the title
        try {
          const { searchProducts } = require('../../services/api');
          const p = product || (productData && typeof productData === 'string' ? JSON.parse(productData) : null);
          if (p && p.title) {
            const keyword = p.title.split(' ')[0];
            const similarData = await searchProducts(keyword, 1, 6);
            if (isActive) {
              setSimilarProducts(similarData.results.filter((item: Product) => item.id?.toString() !== id?.toString()));
            }
          }
        } catch (e) {
          console.error("Failed to fetch similar products", e);
        }

        setImageVersion((current) => current + 1);
      } catch (err: any) {
        if (!isActive) {
          return;
        }

        console.error('Failed to load product:', err);
        setError(err.message || 'Unable to load product details');
      } finally {
        if (isActive) {
          setLoading(false);
        }
      }
    }

    loadProduct();

    return () => {
      isActive = false;
    };
  }, [id]);

  const appendCacheVersion = (url: string) => {
    const separator = url.includes('?') ? '&' : '?';
    return `${url}${separator}v=${imageVersion}`;
  };
  
  const handleScroll = (event: any) => {
    const scrollPosition = event.nativeEvent.contentOffset.x;
    const currentIndex = Math.round(scrollPosition / windowWidth);
    setActiveImageIndex(currentIndex);
  };

  // Map of store names to their base URLs for resolving relative paths
  const STORE_BASE_URLS: Record<string, string> = {
    daraz: 'https://www.daraz.com.np',
    oliz: 'https://www.olizstore.com',
    jeevee: 'https://www.jeevee.com',
    hukut: 'https://hukut.com',
    cgdigital: 'https://cgdigital.com.np',
    better: 'https://www.thebetterappliances.com',
    hardwarepasal: 'https://hardwarepasal.com',
    neostore: 'https://www.neostore.com.np',
    ufonepal: 'https://www.ufonepal.com',
    sastodeal: 'https://www.sastodeal.com',
  };

  const handleOpenStore = async () => {
    if (!product?.product_url) {
      return;
    }

    let url = product.product_url;

    // If already a full URL, use it directly
    if (url.startsWith('http://') || url.startsWith('https://')) {
      // Already absolute — good to go
    } else if (url.startsWith('//')) {
      // Protocol-relative URL
      url = `https:${url}`;
    } else {
      // Relative URL — need to prepend the store's base URL
      const storeLower = (product.store_name || '').toLowerCase();
      const baseUrl = Object.entries(STORE_BASE_URLS).find(
        ([key]) => storeLower.includes(key)
      )?.[1];
      
      if (baseUrl) {
        url = url.startsWith('/') ? `${baseUrl}${url}` : `${baseUrl}/${url}`;
      } else {
        console.warn(`Unknown store "${product.store_name}" for relative URL: ${url}`);
        // Fallback
        url = url.startsWith('/') ? `https://${url.substring(1)}` : `https://${url}`;
      }
    }

    try {
      const supported = await Linking.canOpenURL(url);
      if (supported) {
        await Linking.openURL(url);
      } else {
        console.error('Cannot open URL:', url);
      }
    } catch (openError) {
      console.error('Failed to open store URL:', openError);
    }
  };

  const handleShare = async () => {
    if (!product) return;
    try {
      await Share.share({
        message: `Check out this deal on ${product.store_name}: ${product.title} for Rs ${product.price?.toLocaleString()}!`,
        url: product.product_url,
        title: product.title
      });
    } catch (error: any) {
      console.error(error.message);
    }
  };

  const handleSetPriceAlert = () => {
    if (!product) {
      Alert.alert('Error', 'No product to create an alert for.');
      return;
    }
    const defaultTarget = Math.round((product.price || 0) * 0.9);
    setTargetPriceInput(defaultTarget.toString());
    setIsAlertModalVisible(true);
  };

  const submitPriceAlert = async () => {
    if (!product) return;
    try {
      setIsCreating(true);
      const targetNumber = parseFloat(targetPriceInput.replace(/,/g, ''));
      if (isNaN(targetNumber) || targetNumber <= 0) {
        Alert.alert('Invalid Price', 'Please enter a valid target price.');
        setIsCreating(false);
        return;
      }
      
      const payload = {
        product_id: Number(product.id) || 0,
        target_price: targetNumber,
        product_title: product.title || '',
        store_name: product.store_name || '',
        product_url: product.product_url || '',
        current_price: product.price || 0
      };
      
      const token = (await authStorage.getItemAsync('token')) || '';
      await createPriceAlert(token, payload);
      setIsCreating(false);
      setAlertSuccess(true);
      
    } catch (err: any) {
      console.error('Failed to create price alert', err);
      Alert.alert('Error', err.message || 'Could not create price alert.');
      setIsCreating(false);
    }
  };

  const handleAddToFavorites = async () => {
    if (product) {
      const favId = `${product.store_name}-${product.product_url}`;
      if (isInFavorites) {
        removeItem(favId);
      } else {
        await addItem({
          id: favId,
          productId: product.id,
          title: product.title || '',
          price: product.price || 0,
          originalPrice: product.original_price,
          discountPercent: product.discount_percent,
          imageUrl: product.image_url || '',
          storeName: product.store_name || '',
          productUrl: product.product_url || '',
        });
        Alert.alert('Success', 'Added to favorites');
      }
    }
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#6E4B3A" />
        <Text style={styles.loadingText}>Loading product details...</Text>
      </View>
    );
  }

  if (error || !product) {
    return (
      <View style={styles.centerContainer}>
        <Ionicons name="alert-circle-outline" size={64} color="#D32F2F" />
        <Text style={styles.errorTitle}>Oops!</Text>
        <Text style={styles.errorMessage}>{error || 'Product not found'}</Text>
        <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
          <Text style={styles.backButtonText}>Go Back</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Stack.Screen options={{ headerShown: false }} />
      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={{ paddingBottom: insets.bottom + 140 }}>
        {/* Image Section */}
        <View style={styles.imageSection}>
          <Image 
            source={{ uri: appendCacheVersion(product.image_url) }} 
            style={styles.mainImage} 
            resizeMode="cover" 
          />
          
          <View style={[styles.header, { marginTop: Math.max(insets.top, 16) }]}>
            <TouchableOpacity style={styles.headerIcon} onPress={() => router.back()}>
              <Ionicons name="arrow-back" size={24} color="#111111" />
            </TouchableOpacity>
            
            <Text style={styles.headerTitle}>Product Details</Text>
            
            <View style={{ flexDirection: 'row', gap: 12 }}>
              <TouchableOpacity style={styles.headerIcon} onPress={handleShare}>
                <Ionicons name="share-social-outline" size={24} color="#111111" />
              </TouchableOpacity>
              <TouchableOpacity style={styles.headerIcon} onPress={handleAddToFavorites}>
                <Ionicons 
                  name={isInFavorites ? "heart" : "heart-outline"} 
                  size={24} 
                  color={isInFavorites ? "#FF4757" : "#111111"} 
                />
              </TouchableOpacity>
            </View>
          </View>
          
          {/* Store Badge */}
          <View style={styles.storeBadgeWrapper}>
            <View style={styles.storeBadge}>
              <Text style={styles.storeBadgeInitial}>{product.store_name?.charAt(0).toUpperCase() || 'S'}</Text>
              <Text style={styles.storeBadgeName}>{product.store_name || 'Store'}</Text>
            </View>
          </View>
        </View>

        {/* Content Section */}
        <View style={styles.contentSection}>
          <View style={styles.titleRow}>
            <Text style={styles.categoryText}>{product.store_name || 'Store'}</Text>
          </View>
          
          <Text style={styles.title}>{product.title}</Text>
          
          <View style={styles.divider} />
          
          <Text style={styles.sectionHeading}>Actions</Text>
          <View style={styles.actionButtonsRow}>
             <TouchableOpacity style={styles.actionButton} onPress={handleSetPriceAlert}>
                <Ionicons name="notifications-outline" size={24} color="#6E4B3A" />
                <Text style={styles.actionButtonText}>Price Alert</Text>
             </TouchableOpacity>
             <TouchableOpacity style={styles.actionButton} onPress={() => {
                router.push({ 
                  pathname: '/compare-options', 
                  params: { productData: JSON.stringify(product) } 
                });
             }}>
                <Ionicons name="git-compare-outline" size={24} color="#6E4B3A" />
                <Text style={styles.actionButtonText}>Compare</Text>
             </TouchableOpacity>
             <TouchableOpacity style={styles.actionButton} onPress={() => {
                if (product?.id) {
                  router.push({
                    pathname: '/price-history/[id]',
                    params: { 
                      id: product.id, 
                      title: product.title, 
                      currentPrice: product.price 
                    }
                  });
                }
             }}>
                <Ionicons name="stats-chart-outline" size={24} color="#6E4B3A" />
                <Text style={styles.actionButtonText}>History</Text>
             </TouchableOpacity>
          </View>
        </View>
      </ScrollView>

      {/* Bottom Bar */}
      <View style={[styles.bottomBar, { paddingBottom: Math.max(insets.bottom, 16) }]}>
        <View style={styles.priceContainer}>
          <Text style={styles.priceLabel}>Total Price</Text>
          <Text style={styles.priceValue}>Rs {product.price?.toLocaleString() || 'N/A'}</Text>
        </View>
        <TouchableOpacity style={styles.cartButton} onPress={handleOpenStore}>
          <Ionicons name="bag-outline" size={18} color="#FFFFFF" style={{ marginRight: 8 }} />
          <Text style={styles.cartButtonText}>View Store</Text>
        </TouchableOpacity>
      </View>

      {/* Target Price Modal */}
      <Modal
        visible={isAlertModalVisible}
        transparent
        animationType="fade"
        onRequestClose={() => setIsAlertModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            {alertSuccess ? (
              <View style={{ alignItems: 'center', width: '100%' }}>
                <Ionicons name="checkmark-circle" size={80} color="#4CAF50" style={{ marginBottom: 16 }} />
                <Text style={styles.modalTitle}>Success!</Text>
                <Text style={styles.modalSubtitle}>Price alert created successfully. You will be notified when the price drops.</Text>
                <View style={styles.modalButtons}>
                  <TouchableOpacity style={styles.modalCancelBtn} onPress={() => { setAlertSuccess(false); setIsAlertModalVisible(false); }}>
                    <Text style={styles.modalCancelText}>Close</Text>
                  </TouchableOpacity>
                  <TouchableOpacity style={styles.modalSaveBtn} onPress={() => { setAlertSuccess(false); setIsAlertModalVisible(false); router.push('/price-alerts'); }}>
                    <Text style={styles.modalSaveText}>View Alerts</Text>
                  </TouchableOpacity>
                </View>
              </View>
            ) : (
              <>
                <Text style={styles.modalTitle}>Set Price Alert</Text>
                <Text style={styles.modalSubtitle}>Notify me when price drops below:</Text>
                
                <View style={styles.inputContainer}>
                  <Text style={styles.currencyPrefix}>Rs.</Text>
                  <TextInput
                    style={styles.priceInput}
                    value={targetPriceInput}
                    onChangeText={setTargetPriceInput}
                    keyboardType="numeric"
                    placeholder="Enter target price"
                    placeholderTextColor="#A0A0A0"
                    editable={!isCreating}
                  />
                </View>

                <View style={styles.modalButtons}>
                  <TouchableOpacity 
                    style={styles.modalCancelBtn}
                    onPress={() => setIsAlertModalVisible(false)}
                    disabled={isCreating}
                  >
                    <Text style={styles.modalCancelText}>Cancel</Text>
                  </TouchableOpacity>
                  <TouchableOpacity 
                    style={styles.modalSaveBtn}
                    onPress={submitPriceAlert}
                    disabled={isCreating}
                  >
                    {isCreating ? (
                      <ActivityIndicator color="#FFFFFF" size="small" />
                    ) : (
                      <Text style={styles.modalSaveText}>Set Alert</Text>
                    )}
                  </TouchableOpacity>
                </View>
              </>
            )}
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
paddingHorizontal: 24,
  },
  loadingText: {
    marginTop: 16,
    fontFamily: 'Poppins_500Medium',
    fontSize: 14,
    color: '#757575',
  },
  errorTitle: {
    fontFamily: 'Poppins_700Bold',
    fontSize: 20,
    color: '#111111',
    marginTop: 24,
    marginBottom: 8,
    textAlign: 'center',
  },
  errorMessage: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 14,
    color: '#757575',
    textAlign: 'center',
    marginBottom: 24,
  },
  backButton: {
    backgroundColor: '#111111',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 9999,
  },
  backButtonText: {
    color: '#FFFFFF',
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 14,
  },
  imageSection: {
    width: '100%',
    height: 460, // Taller image matching the screenshot
    backgroundColor: '#FFFFFF',
  },
  header: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 24,
    zIndex: 10,
  },
  headerIcon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  headerTitle: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 16,
    color: '#111111',
  },
  mainImage: {
    width: '100%',
    height: '100%',
  },
  storeBadgeWrapper: {
    position: 'absolute',
    bottom: -30,
    left: '50%',
    transform: [{ translateX: -30 }], // Perfectly centers the 60px badge
    zIndex: 20,
  },
  storeBadge: {
    width: 60,
    height: 60,
    borderRadius: 12,
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#EEEEEE',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  storeBadgeInitial: {
    fontFamily: 'Poppins_700Bold',
    fontSize: 20,
    color: '#6E4B3A',
  },
  storeBadgeName: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 9,
    color: '#757575',
    marginTop: 2,
    textAlign: 'center',
  },
  contentSection: {
    paddingHorizontal: 24,
    paddingTop: 45, // Space for the overlapping badge
  },
  titleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  categoryText: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 14,
    color: '#A0A0A0',
  },
  ratingBox: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  ratingText: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 14,
    color: '#757575',
  },
  title: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 18,
    color: '#111111',
    marginBottom: 24,
    lineHeight: 26,
  },
  sectionHeading: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 16,
    color: '#111111',
    marginBottom: 8,
  },
  descriptionText: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 14,
    color: '#757575',
    lineHeight: 20,
    marginBottom: 16,
  },
  readMoreText: {
    fontFamily: 'Poppins_600SemiBold',
    color: '#6E4B3A', // Subtle brown
    textDecorationLine: 'underline',
  },
  divider: {
    height: 1,
    backgroundColor: '#EEEEEE',
    marginVertical: 16,
  },
  sizeRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 24,
    flexWrap: 'wrap',
  },
  sizeButton: {
    minWidth: 44,
    height: 44,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#EEEEEE',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 8,
  },
  sizeButtonActive: {
    backgroundColor: '#6E4B3A',
    borderColor: '#6E4B3A',
  },
  sizeText: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 14,
    color: '#111111',
  },
  sizeTextActive: {
    color: '#FFFFFF',
  },
  colorSelectedText: {
    fontFamily: 'Poppins_400Regular',
    color: '#757575',
  },
  bottomBar: {
    position: 'absolute',
    bottom: 24,
    left: 24,
    right: 24,
    backgroundColor: '#FFFFFF',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderRadius: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 8,
  },
  priceContainer: {
    flex: 1,
    marginLeft: 8,
  },
  priceLabel: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 12,
    color: '#757575',
  },
  priceValue: {
    fontFamily: 'Poppins_700Bold',
    fontSize: 18,
    color: '#111111',
  },
  cartButton: {
    backgroundColor: '#6E4B3A',
    flexDirection: 'row',
    paddingHorizontal: 24,
    paddingVertical: 14,
    borderRadius: 9999,
    alignItems: 'center',
  },
  cartButtonText: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 14,
    color: '#FFFFFF',
  },
  actionButtonsRow: {
    flexDirection: 'row',
    justifyContent: 'space-evenly',
    alignItems: 'center',
    backgroundColor: '#F9F9F9',
    borderRadius: 16,
    paddingVertical: 12,
    marginTop: 16,
  },
  actionButton: {
    alignItems: 'center',
    flex: 1,
    borderRightWidth: 1,
    borderRightColor: '#EEEEEE',
  },
  actionButtonText: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 10,
    color: '#757575',
    marginTop: 4,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    width: '100%',
    borderRadius: 24,
    padding: 24,
    alignItems: 'center',
  },
  modalTitle: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 20,
    color: '#111111',
    marginBottom: 8,
  },
  modalSubtitle: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 14,
    color: '#757575',
    textAlign: 'center',
    marginBottom: 24,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F5F5F5',
    borderRadius: 12,
    paddingHorizontal: 16,
    width: '100%',
    height: 56,
    marginBottom: 24,
  },
  currencyPrefix: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 18,
    color: '#111111',
    marginRight: 8,
  },
  priceInput: {
    flex: 1,
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 18,
    color: '#111111',
    height: '100%',
  },
  modalButtons: {
    flexDirection: 'row',
    width: '100%',
    gap: 12,
  },
  modalCancelBtn: {
    flex: 1,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#F5F5F5',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalCancelText: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 15,
    color: '#111111',
  },
  modalSaveBtn: {
    flex: 1,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#6E4B3A',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalSaveText: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 14,
    color: '#FFFFFF',
  },
  similarCard: {
    width: 140,
    backgroundColor: '#F9F9F9',
    borderRadius: 12,
    padding: 12,
  },
  similarImage: {
    width: '100%',
    height: 100,
    resizeMode: 'contain',
    marginBottom: 8,
  },
  similarTitle: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 12,
    color: '#111111',
    lineHeight: 18,
  },
  similarPrice: {
    fontFamily: 'Poppins_700Bold',
    fontSize: 14,
    color: '#E53935',
    marginTop: 4,
  }
});
