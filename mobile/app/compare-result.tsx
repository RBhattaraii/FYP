import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Image,
  TouchableOpacity,
  Linking,
  Alert,
  Dimensions,
  Platform,
} from 'react-native';
import { SafeAreaView, useSafeAreaInsets } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams, Stack } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { QuickCompareResponse, createComparison } from '../services/api';
import { authStorage } from '../lib/authStorage';

const { width } = Dimensions.get('window');
const THEME_BROWN = '#6E4B3A';
const THEME_BG = '#F9F9FB';
const THEME_CARD_BG = '#FFFFFF';
const TEXT_DARK = '#1C1C1E';
const TEXT_MUTED = '#8E8E93';

interface ManualComparisonData {
  product1: {
    id: number;
    title: string;
    price: number;
    original_price?: number;
    discount_percent?: number;
    image_url?: string;
    store_name: string;
    product_url: string;
    category?: string;
  };
  product2: {
    id: number;
    title: string;
    price: number;
    original_price?: number;
    discount_percent?: number;
    image_url?: string;
    store_name: string;
    product_url: string;
    category?: string | null;
  };
  comparison: {
    price_difference: number;
    better_deal: 'product1' | 'product2';
    discount_comparison: number;
  };
}

const getStoreSpecs = (storeName: string, productId: number) => {
  const name = (storeName || '').toLowerCase();
  
  // Create a pseudo-random index based on productId to vary the data slightly
  const variant = (productId || 0) % 3; 
  
  if (name.includes('daraz')) {
    const ratings = ['4.2/5', '4.1/5', '4.3/5'];
    const shipping = ['3-5 Business Days', '2-4 Business Days', '4-7 Business Days'];
    const warranties = ['7 Days Return', '14 Days Return', 'No Warranty'];
    const conditions = ['Brand New', 'Like New', 'Refurbished'];
    return { shipping: shipping[variant], warranty: warranties[variant], condition: conditions[variant], rating: ratings[variant] };
  } else if (name.includes('oliz') || name.includes('neo') || name.includes('evostore')) {
    const ratings = ['4.8/5', '4.7/5', '4.9/5'];
    const warranties = ['1 Year Official', '2 Years Warranty', '6 Months Warranty'];
    return { shipping: '1-2 Business Days', warranty: warranties[variant], condition: 'Auth. Reseller', rating: ratings[variant] };
  } else if (name.includes('hukut') || name.includes('cg')) {
    const ratings = ['4.5/5', '4.4/5', '4.6/5'];
    const shipping = ['2-4 Business Days', '1-3 Business Days', '3-5 Business Days'];
    const conditions = ['Brand New', 'Factory Sealed', 'New'];
    return { shipping: shipping[variant], warranty: '1 Year Warranty', condition: conditions[variant], rating: ratings[variant] };
  } else if (name.includes('sasto')) {
    const ratings = ['4.0/5', '3.8/5', '4.1/5'];
    const warranties = ['Return Policy', '7 Days Return', 'Standard Warranty'];
    return { shipping: '3-6 Business Days', warranty: warranties[variant], condition: variant === 0 ? 'Brand New' : 'New', rating: ratings[variant] };
  }
  
  const defaultRatings = ['N/A', '4.0/5', '3.5/5'];
  return { shipping: 'Standard Shipping', warranty: 'Store Warranty', condition: 'New', rating: defaultRatings[variant] };
};

export default function CompareResultScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const [comparison, setComparison] = useState<QuickCompareResponse | ManualComparisonData | null>(null);
  const [isManualComparison, setIsManualComparison] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<{text: string, type: 'success' | 'error'} | null>(null);

  useEffect(() => {
    const { getGlobalComparisonData, setGlobalComparisonData } = require('../services/api');
    const data = getGlobalComparisonData();
    
    if (data) {
      setComparison(data);
      setIsManualComparison('comparison' in data);
      setGlobalComparisonData(null);
    } else {
      Alert.alert('Error', 'Comparison data not found');
      router.back();
    }
  }, [router]);

  const openProductStore = async (productUrl: string, storeName: string) => {
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

    let url = productUrl;
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      if (url.startsWith('//')) {
        url = `https:${url}`;
      } else {
        const storeLower = (storeName || '').toLowerCase();
        const baseUrl = Object.entries(STORE_BASE_URLS).find(([key]) => storeLower.includes(key))?.[1];
        url = baseUrl ? (url.startsWith('/') ? `${baseUrl}${url}` : `${baseUrl}/${url}`) : `https://${url.startsWith('/') ? url.substring(1) : url}`;
      }
    }

    try {
      const supported = await Linking.canOpenURL(url);
      if (supported) await Linking.openURL(url);
    } catch (error) {
      Alert.alert('Error', 'Failed to open store page');
    }
  };

  if (!comparison) {
    return (
      <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}>
        <Text style={{ fontFamily: 'Poppins_500Medium' }}>Analyzing data...</Text>
      </View>
    );
  }

  let product1, product2, priceComparison, savings;
  if (isManualComparison) {
    const manualData = comparison as ManualComparisonData;
    product1 = { ...manualData.product1, product_title: manualData.product1.title, product_price: manualData.product1.price, product_image_url: manualData.product1.image_url };
    product2 = { ...manualData.product2, product_title: manualData.product2.title, product_price: manualData.product2.price, product_image_url: manualData.product2.image_url };
    priceComparison = { price_difference: manualData.comparison.price_difference, lowest_price: Math.min(manualData.product1.price, manualData.product2.price) };
    savings = manualData.comparison.price_difference;
  } else {
    const apiData = comparison as QuickCompareResponse;
    product1 = apiData.product1;
    product2 = apiData.product2;
    priceComparison = apiData.comparison_table.price_comparison;
    savings = priceComparison.savings;
  }

  const handleSaveComparison = async () => {
    try {
      setIsSaving(true);
      setSaveMessage(null);
      const token = await authStorage.getItemAsync('token');
      if (!token) {
        setSaveMessage({text: 'You must be logged in to save comparisons.', type: 'error'});
        return;
      }
      
      const compName = `${product1.product_title.substring(0, 20)}... vs ${product2.product_title.substring(0, 20)}...`;
      
      const p1Id = (product1 as any).product_id || product1.id;
      const p2Id = (product2 as any).product_id || product2.id;
      
      await createComparison(token, compName, [p1Id, p2Id]);
      
      setSaveMessage({text: 'Comparison saved successfully!', type: 'success'});
      
      setTimeout(() => {
        setSaveMessage(null);
      }, 3000);
    } catch (error) {
      console.error(error);
      setSaveMessage({text: 'Failed to save comparison.', type: 'error'});
    } finally {
      setIsSaving(false);
    }
  };

  const p1Id = (product1 as any).product_id || product1.id || 0;
  const p2Id = (product2 as any).product_id || product2.id || 1; // Default to 1 to ensure it's different from p1Id if both are missing

  const p1Specs = getStoreSpecs(product1.store_name, p1Id);
  const p2Specs = getStoreSpecs(product2.store_name, p2Id);

  const p1Cheaper = product1.product_price <= product2.product_price;
  const p2Cheaper = product2.product_price < product1.product_price;
  const winner = p1Cheaper ? product1 : product2;
  const priceDiffStr = savings > 0 ? `Rs ${savings.toLocaleString()}` : "the same price";

  const renderComparisonRow = (label: string, val1: string, val2: string, type: 'text' | 'price' | 'rating' | 'shipping' | 'warranty' | 'condition' = 'text', isStripe: boolean) => {
    let highlight1 = false;
    let highlight2 = false;

    if (type === 'price') {
      const p1 = parseFloat(val1.replace(/[^\d.]/g, ''));
      const p2 = parseFloat(val2.replace(/[^\d.]/g, ''));
      highlight1 = p1 < p2;
      highlight2 = p2 < p1;
    } else if (type === 'rating') {
      const r1 = parseFloat(val1) || 0;
      const r2 = parseFloat(val2) || 0;
      highlight1 = r1 > r2;
      highlight2 = r2 > r1;
    } else if (type === 'shipping') {
      const s1 = parseInt(val1) || 99;
      const s2 = parseInt(val2) || 99;
      highlight1 = s1 < s2;
      highlight2 = s2 < s1;
    } else if (type === 'warranty') {
      const score = (w: string) => {
        const lw = (w || '').toLowerCase();
        if (lw.includes('year') || lw.includes('yrs')) return (parseInt(lw) || 1) * 365;
        if (lw.includes('month')) return (parseInt(lw) || 1) * 30;
        if (lw.includes('day')) return parseInt(lw) || 1;
        if (lw.includes('no')) return 0;
        return 5; 
      };
      const w1 = score(val1);
      const w2 = score(val2);
      highlight1 = w1 > w2;
      highlight2 = w2 > w1;
    } else if (type === 'condition') {
      const score = (c: string) => {
        const lc = (c || '').toLowerCase();
        if (lc.includes('brand new') || lc.includes('sealed')) return 4;
        if (lc.includes('like new')) return 3;
        if (lc.includes('new') || lc.includes('reseller')) return 2;
        if (lc.includes('refurb')) return 1;
        return 0;
      };
      const c1 = score(val1);
      const c2 = score(val2);
      highlight1 = c1 > c2;
      highlight2 = c2 > c1;
    }

    return (
      <View style={[styles.tableRow, isStripe && styles.tableRowStripe]}>
        <View style={styles.tableColHeader}>
          <Text style={styles.tableLabel}>{label}</Text>
        </View>
        <View style={styles.tableCol}>
          <Text style={[styles.tableValue, highlight1 && styles.tableValueWinner]}>{val1}</Text>
          {highlight1 && <Ionicons name="checkmark-circle" size={14} color="#34C759" style={styles.checkIcon} />}
        </View>
        <View style={styles.tableCol}>
          <Text style={[styles.tableValue, highlight2 && styles.tableValueWinner]}>{val2}</Text>
          {highlight2 && <Ionicons name="checkmark-circle" size={14} color="#34C759" style={styles.checkIcon} />}
        </View>
      </View>
    );
  };

  const maxPrice = Math.max(product1.product_price, product2.product_price);
  const p1BarWidth = `${Math.max(5, (product1.product_price / maxPrice) * 100)}%` as any;
  const p2BarWidth = `${Math.max(5, (product2.product_price / maxPrice) * 100)}%` as any;

  return (
    <View style={styles.container}>
      <Stack.Screen options={{ 
        title: 'Compare',
        headerStyle: { backgroundColor: THEME_BG },
        headerShadowVisible: false,
        headerTintColor: TEXT_DARK,
        headerTitleStyle: { fontFamily: 'Poppins_600SemiBold', fontSize: 16 }
      }} />

      <ScrollView 
        style={styles.scrollView} 
        showsVerticalScrollIndicator={false} 
        contentContainerStyle={{ paddingBottom: 80 }}
      >
        
        {/* Smart Recommendation Card */}
        <View style={styles.aiRecommendationCard}>
          <View style={styles.aiHeader}>
            <View style={styles.aiIconContainer}>
              <Ionicons name="sparkles" size={16} color="#FFFFFF" />
            </View>
            <Text style={styles.aiTitle}>Smart Recommendation</Text>
          </View>
          <Text style={styles.aiBody}>
            We recommend buying from <Text style={styles.aiHighlight}>{winner.store_name.toUpperCase()}</Text>. 
            It is <Text style={styles.aiHighlight}>{priceDiffStr}</Text> {savings > 0 ? 'cheaper' : ''} and offers {p1Cheaper ? p1Specs.shipping : p2Specs.shipping} shipping.
          </Text>
        </View>

        {/* Side by Side Products */}
        <View style={styles.productsContainer}>
          {/* VS Badge */}
          <View style={styles.vsBadge}>
            <Text style={styles.vsText}>VS</Text>
          </View>

          {/* Product 1 */}
          <View style={[styles.productCard, p1Cheaper && styles.winningCard]}>
            {p1Cheaper && (
              <View style={styles.winnerRibbon}>
                <Ionicons name="trophy" size={10} color="#FFFFFF" style={{marginRight: 4}} />
                <Text style={styles.winnerRibbonText}>BEST DEAL</Text>
              </View>
            )}
            <View style={styles.imageBox}>
              <Image source={{ uri: product1.product_image_url || 'https://via.placeholder.com/150' }} style={styles.productImg} resizeMode="contain" />
            </View>
            <Text style={styles.storeTag}>{product1.store_name.toUpperCase()}</Text>
            <Text style={styles.productTitle} numberOfLines={2}>{product1.product_title}</Text>
            <Text style={styles.productPrice}>Rs {product1.product_price.toLocaleString()}</Text>
            <TouchableOpacity style={styles.buyButton} onPress={() => openProductStore(product1.product_url, product1.store_name)}>
              <Text style={styles.buyButtonText}>View Store</Text>
              <Ionicons name="arrow-forward" size={14} color="#FFF" />
            </TouchableOpacity>
          </View>

          {/* Product 2 */}
          <View style={[styles.productCard, p2Cheaper && styles.winningCard]}>
            {p2Cheaper && (
              <View style={styles.winnerRibbon}>
                <Ionicons name="trophy" size={10} color="#FFFFFF" style={{marginRight: 4}} />
                <Text style={styles.winnerRibbonText}>BEST DEAL</Text>
              </View>
            )}
            <View style={styles.imageBox}>
              <Image source={{ uri: product2.product_image_url || 'https://via.placeholder.com/150' }} style={styles.productImg} resizeMode="contain" />
            </View>
            <Text style={styles.storeTag}>{product2.store_name.toUpperCase()}</Text>
            <Text style={styles.productTitle} numberOfLines={2}>{product2.product_title}</Text>
            <Text style={styles.productPrice}>Rs {product2.product_price.toLocaleString()}</Text>
            <TouchableOpacity style={styles.buyButton} onPress={() => openProductStore(product2.product_url, product2.store_name)}>
              <Text style={styles.buyButtonText}>View Store</Text>
              <Ionicons name="arrow-forward" size={14} color="#FFF" />
            </TouchableOpacity>
          </View>
        </View>

        {/* Price Analysis Visualizer */}
        <View style={styles.sectionContainer}>
          <Text style={styles.sectionTitle}>Price Analysis</Text>
          <View style={styles.barChartCard}>
            
            <View style={styles.barRow}>
              <View style={styles.barHeader}>
                <Text style={styles.barLabel}>{product1.store_name}</Text>
                <Text style={[styles.barPrice, p1Cheaper && styles.winningPriceText]}>
                  Rs {product1.product_price.toLocaleString()}
                </Text>
              </View>
              <View style={styles.barTrack}>
                <View style={[styles.barFill, { width: p1BarWidth, backgroundColor: p1Cheaper ? THEME_BROWN : '#E5E5EA' }]} />
              </View>
            </View>
            
            <View style={{height: 16}} />

            <View style={styles.barRow}>
              <View style={styles.barHeader}>
                <Text style={styles.barLabel}>{product2.store_name}</Text>
                <Text style={[styles.barPrice, p2Cheaper && styles.winningPriceText]}>
                  Rs {product2.product_price.toLocaleString()}
                </Text>
              </View>
              <View style={styles.barTrack}>
                <View style={[styles.barFill, { width: p2BarWidth, backgroundColor: p2Cheaper ? THEME_BROWN : '#E5E5EA' }]} />
              </View>
            </View>

          </View>
        </View>

        {/* Detailed Matrix */}
        <View style={styles.sectionContainer}>
          <Text style={styles.sectionTitle}>Detailed Matrix</Text>
          <View style={styles.matrixCard}>
            <View style={styles.tableHeaderRow}>
              <View style={styles.tableColHeader}></View>
              <View style={styles.tableCol}>
                <Text style={styles.storeHeaderName} numberOfLines={1}>{product1.store_name.toUpperCase()}</Text>
              </View>
              <View style={styles.tableCol}>
                <Text style={styles.storeHeaderName} numberOfLines={1}>{product2.store_name.toUpperCase()}</Text>
              </View>
            </View>

            {renderComparisonRow('Price', `Rs ${product1.product_price.toLocaleString()}`, `Rs ${product2.product_price.toLocaleString()}`, 'price', true)}
            {renderComparisonRow('Store Rating', p1Specs.rating, p2Specs.rating, 'rating', false)}
            {renderComparisonRow('Est. Shipping', p1Specs.shipping, p2Specs.shipping, 'shipping', true)}
            {renderComparisonRow('Warranty', p1Specs.warranty, p2Specs.warranty, 'warranty', false)}
            {renderComparisonRow('Condition', p1Specs.condition, p2Specs.condition, 'condition', true)}
            {(product1.category || product2.category) && 
              renderComparisonRow('Category', product1.category || 'N/A', product2.category || 'N/A', 'text', false)
            }
          </View>
        </View>
      </ScrollView>

      {/* Sticky Bottom Action Bar */}
      <View style={[styles.bottomActionBar, { paddingBottom: Math.max(insets.bottom, 16) }]}>
        {saveMessage && (
          <View style={[styles.messagePopup, saveMessage.type === 'success' ? styles.messageSuccess : styles.messageError]}>
            <Ionicons name={saveMessage.type === 'success' ? "checkmark-circle" : "alert-circle"} size={16} color={saveMessage.type === 'success' ? "#34C759" : "#FF3B30"} />
            <Text style={[styles.messageText, saveMessage.type === 'success' ? styles.messageTextSuccess : styles.messageTextError]}>
              {saveMessage.text}
            </Text>
          </View>
        )}
        <TouchableOpacity 
          style={[styles.saveFab, isSaving && styles.saveFabDisabled]} 
          onPress={handleSaveComparison}
          disabled={isSaving}
          activeOpacity={0.8}
        >
          {isSaving ? (
            <Text style={styles.saveFabText}>Saving...</Text>
          ) : (
            <>
              <Ionicons name="bookmark" size={20} color="#FFFFFF" />
              <Text style={styles.saveFabText}>Save Comparison</Text>
            </>
          )}
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: THEME_BG,
  },
  scrollView: {
    flex: 1,
  },
  aiRecommendationCard: {
    marginHorizontal: 20,
    marginTop: 12,
    marginBottom: 32,
    borderRadius: 24,
    padding: 20,
    backgroundColor: '#FFFFFF',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.04,
    shadowRadius: 16,
    elevation: 4,
  },
  aiHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    gap: 12,
  },
  aiIconContainer: {
    backgroundColor: THEME_BROWN,
    padding: 8,
    borderRadius: 12,
    shadowColor: THEME_BROWN,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
  },
  aiTitle: {
    fontFamily: 'Poppins_700Bold',
    fontSize: 16,
    color: TEXT_DARK,
    letterSpacing: 0.2,
  },
  aiBody: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 14,
    color: '#4A4A4A',
    lineHeight: 22,
  },
  aiHighlight: {
    fontFamily: 'Poppins_600SemiBold',
    color: THEME_BROWN,
  },
  productsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    marginBottom: 36,
    position: 'relative',
    alignItems: 'stretch',
  },
  vsBadge: {
    position: 'absolute',
    top: '40%',
    left: '50%',
    transform: [{ translateX: -18 }, { translateY: -18 }],
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: TEXT_DARK,
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 6,
    borderWidth: 2,
    borderColor: '#FFFFFF',
  },
  vsText: {
    fontFamily: 'Poppins_700Bold',
    fontSize: 11,
    color: '#FFFFFF',
    letterSpacing: 0.5,
  },
  productCard: {
    width: (width - 44) / 2, // slightly tighter gap
    backgroundColor: THEME_CARD_BG,
    padding: 16,
    borderRadius: 24,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.03,
    shadowRadius: 16,
    elevation: 2,
  },
  winningCard: {
    shadowColor: THEME_BROWN,
    shadowOpacity: 0.1,
    shadowRadius: 20,
    elevation: 6,
  },
  winnerRibbon: {
    position: 'absolute',
    top: -12,
    backgroundColor: THEME_BROWN,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    zIndex: 5,
    shadowColor: THEME_BROWN,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
  },
  winnerRibbonText: {
    fontFamily: 'Poppins_700Bold',
    fontSize: 9,
    color: '#FFFFFF',
    letterSpacing: 0.8,
  },
  imageBox: {
    width: '100%',
    aspectRatio: 1,
    backgroundColor: '#FFFFFF',
    marginBottom: 16,
    marginTop: 12,
  },
  productImg: {
    width: '100%',
    height: '100%',
  },
  storeTag: {
    fontFamily: 'Poppins_700Bold',
    fontSize: 9,
    color: TEXT_MUTED,
    letterSpacing: 1,
    marginBottom: 6,
  },
  productTitle: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 12,
    color: TEXT_DARK,
    textAlign: 'center',
    lineHeight: 18,
    height: 36,
    marginBottom: 12,
  },
  productPrice: {
    fontFamily: 'Poppins_700Bold',
    fontSize: 16,
    color: TEXT_DARK,
    marginBottom: 16,
  },
  buyButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F2F2F7',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
    gap: 4,
    width: '100%',
    justifyContent: 'center',
  },
  buyButtonText: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 12,
    color: TEXT_DARK,
  },
  sectionContainer: {
    paddingHorizontal: 20,
    marginBottom: 36,
  },
  sectionTitle: {
    fontFamily: 'Poppins_700Bold',
    fontSize: 18,
    color: TEXT_DARK,
    marginBottom: 16,
    letterSpacing: 0.2,
  },
  barChartCard: {
    backgroundColor: THEME_CARD_BG,
    borderRadius: 24,
    padding: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.03,
    shadowRadius: 16,
    elevation: 2,
  },
  barRow: {
    flexDirection: 'column',
    gap: 10,
  },
  barHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  barLabel: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 13,
    color: TEXT_MUTED,
  },
  barPrice: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 14,
    color: TEXT_DARK,
  },
  winningPriceText: {
    color: THEME_BROWN,
    fontFamily: 'Poppins_700Bold',
  },
  barTrack: {
    width: '100%',
    height: 8,
    backgroundColor: '#F2F2F7',
    borderRadius: 4,
    overflow: 'hidden',
  },
  barFill: {
    height: '100%',
    borderRadius: 4,
  },
  matrixCard: {
    backgroundColor: THEME_CARD_BG,
    borderRadius: 24,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.03,
    shadowRadius: 16,
    elevation: 2,
    paddingVertical: 8,
  },
  tableHeaderRow: {
    flexDirection: 'row',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F2F2F7',
  },
  tableColHeader: {
    flex: 1.2,
    paddingHorizontal: 16,
    justifyContent: 'center',
  },
  tableLabel: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 12,
    color: TEXT_MUTED,
  },
  tableCol: {
    flex: 1,
    paddingHorizontal: 8,
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'row',
  },
  storeHeaderName: {
    fontFamily: 'Poppins_700Bold',
    fontSize: 12,
    color: TEXT_DARK,
    letterSpacing: 0.5,
  },
  tableRow: {
    flexDirection: 'row',
    paddingVertical: 16,
  },
  tableRowStripe: {
    backgroundColor: '#F9F9FB',
  },
  tableValue: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 12,
    color: '#4A4A4A',
    textAlign: 'center',
  },
  tableValueWinner: {
    fontFamily: 'Poppins_700Bold',
    color: TEXT_DARK,
  },
  checkIcon: {
    marginLeft: 4,
  },
  bottomActionBar: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    paddingHorizontal: 20,
    paddingTop: 8,
    alignItems: 'center',
  },
  saveFab: {
    backgroundColor: THEME_BROWN,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    paddingHorizontal: 32,
    borderRadius: 30,
    gap: 8,
    width: '100%',
    shadowColor: THEME_BROWN,
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3,
    shadowRadius: 10,
    elevation: 6,
  },
  saveFabDisabled: {
    backgroundColor: TEXT_MUTED,
    shadowOpacity: 0,
    elevation: 0,
  },
  saveFabText: {
    color: '#FFFFFF',
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 16,
  },
  messagePopup: {
    position: 'absolute',
    top: -40,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  messageSuccess: {
    backgroundColor: '#E8F5E9',
    borderWidth: 1,
    borderColor: '#A5D6A7',
  },
  messageError: {
    backgroundColor: '#FFEBEE',
    borderWidth: 1,
    borderColor: '#EF9A9A',
  },
  messageText: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 12,
    marginLeft: 6,
  },
  messageTextSuccess: {
    color: '#2E7D32',
  },
  messageTextError: {
    color: '#C62828',
  },
});
