import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  Image,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter, Stack, useFocusEffect } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { colors, spacing, typography, borderRadius, shadows } from '../constants/theme';
import { getUserComparisons, ProductComparison, setGlobalComparisonData } from '../services/api';
import { authStorage } from '../lib/authStorage';

export default function MyComparisonsScreen() {
  const router = useRouter();
  const [comparisons, setComparisons] = useState<ProductComparison[]>([]);
  const [loading, setLoading] = useState(true);

  useFocusEffect(
    React.useCallback(() => {
      loadComparisons();
    }, [])
  );

  const getStoreColor = (storeName: string) => {
    if (!storeName) return '#64748B';
    const name = storeName.toLowerCase();
    if (name.includes('daraz')) return '#F97316';
    if (name.includes('hukut')) return '#8B5CF6';
    if (name.includes('sasto')) return '#EAB308';
    return '#64748B';
  };

  const loadComparisons = async () => {
    try {
      const token = await authStorage.getItemAsync('token');
      if (token) {
        const response = await getUserComparisons(token);
        setComparisons(response.comparisons);
      }
    } catch (error) {
      console.error('Failed to load comparisons:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleComparisonSelect = (comparison: ProductComparison) => {
    if (!comparison.items || comparison.items.length < 2) {
      return;
    }

    const item1 = comparison.items[0];
    const item2 = comparison.items[1];

    const comparisonObj = {
      product1: {
        id: item1.product_id,
        title: item1.product_title,
        price: Number(item1.product_price),
        image_url: item1.product_image_url,
        store_name: item1.store_name,
        product_url: item1.product_url,
        category: item1.category,
      },
      product2: {
        id: item2.product_id,
        title: item2.product_title,
        price: Number(item2.product_price),
        image_url: item2.product_image_url,
        store_name: item2.store_name,
        product_url: item2.product_url,
        category: item2.category,
      },
      comparison: {
        price_difference: Math.abs(Number(item1.product_price) - Number(item2.product_price)),
        better_deal: Number(item1.product_price) <= Number(item2.product_price) ? 'product1' : 'product2',
        discount_comparison: 0,
      }
    };

    setGlobalComparisonData(comparisonObj);
    router.push('/compare-result');
  };

  const renderComparisonItem = ({ item }: { item: ProductComparison }) => {
    if (!item.items || item.items.length < 2) {
      return (
        <View style={styles.comparisonCard}>
          <View style={styles.cardHeader}>
            <Text style={styles.comparisonName}>{item.comparison_name}</Text>
            <Text style={styles.dateText}>{new Date(item.created_at).toLocaleDateString()}</Text>
          </View>
          <View style={[styles.cardBody, { padding: 16 }]}>
            <Text style={{ fontFamily: 'Poppins_400Regular', color: '#EF4444' }}>
              Invalid comparison (missing products)
            </Text>
          </View>
        </View>
      );
    }
    const item1 = item.items[0];
    const item2 = item.items[1];

    let name1 = item1.product_title || 'Product 1';
    let name2 = item2.product_title || 'Product 2';
    if (item.comparison_name && item.comparison_name.includes(' vs ')) {
       const parts = item.comparison_name.split(' vs ');
       name1 = parts[0];
       name2 = parts[1];
    }

    return (
      <TouchableOpacity
        style={styles.comparisonCard}
        onPress={() => handleComparisonSelect(item)}
        activeOpacity={0.85}
      >
        <LinearGradient
           colors={['#ffffff', '#fdfbf9']}
           style={StyleSheet.absoluteFillObject}
        />
        
        <View style={styles.cardHeader}>
          <View style={styles.titleWrapper}>
            <Text style={styles.comparisonName} numberOfLines={1}>{name1}</Text>
            <Text style={styles.comparisonSubName} numberOfLines={1}>vs {name2}</Text>
          </View>
          <Text style={styles.dateText}>
            {new Date(item.created_at).toLocaleDateString(undefined, {month: 'short', day: 'numeric'})}
          </Text>
        </View>

        <View style={styles.productsRow}>
          {/* Product 1 */}
          <View style={styles.productColumn}>
            <View style={styles.imageWrapper}>
              <Image 
                source={{ uri: item1.product_image_url || 'https://via.placeholder.com/120' }} 
                style={styles.productImage} 
                resizeMode="contain"
              />
              <View style={[styles.storeBadge, { backgroundColor: getStoreColor(item1.store_name) }]}>
                <Text style={styles.storeBadgeText}>{item1.store_name}</Text>
              </View>
            </View>
            <Text style={styles.priceText} numberOfLines={1}>Rs {Number(item1.product_price).toLocaleString()}</Text>
          </View>

          {/* VS Badge */}
          <View style={styles.vsBadgeContainer}>
            <LinearGradient 
              colors={['#FF6B6B', '#FF8E53']} 
              start={{x: 0, y: 0}} 
              end={{x: 1, y: 1}}
              style={styles.vsBadgeGradient}
            >
              <Text style={styles.vsBadgeText}>VS</Text>
            </LinearGradient>
          </View>

          {/* Product 2 */}
          <View style={styles.productColumn}>
            <View style={styles.imageWrapper}>
              <Image 
                source={{ uri: item2.product_image_url || 'https://via.placeholder.com/120' }} 
                style={styles.productImage} 
                resizeMode="contain"
              />
              <View style={[styles.storeBadge, { backgroundColor: getStoreColor(item2.store_name) }]}>
                <Text style={styles.storeBadgeText}>{item2.store_name}</Text>
              </View>
            </View>
            <Text style={styles.priceText} numberOfLines={1}>Rs {Number(item2.product_price).toLocaleString()}</Text>
          </View>
        </View>
      </TouchableOpacity>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <Stack.Screen options={{ headerShown: false }} />
      
      {/* Custom Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color={colors.gray900} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>My Comparisons</Text>
        <View style={{ width: 40 }} />
      </View>

      {loading ? (
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color="#6E4B3A" />
        </View>
      ) : comparisons.length === 0 ? (
        <View style={styles.centerContainer}>
          <Ionicons name="layers-outline" size={64} color={colors.gray300} />
          <Text style={styles.emptyTitle}>No Comparisons Yet</Text>
          <Text style={styles.emptyText}>
            Save products you want to compare side-by-side to see them here.
          </Text>
        </View>
      ) : (
        <FlatList
          data={comparisons}
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderComparisonItem}
          contentContainerStyle={styles.listContainer}
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.gray50,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.lg,
    backgroundColor: colors.white,
    borderBottomWidth: 1,
    borderBottomColor: colors.gray200,
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.gray100,
  },
  headerTitle: {
    fontSize: typography.fontSize.h3,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
  },
  centerContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing.xl,
  },
  emptyTitle: {
    fontSize: typography.fontSize.h2,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
    marginTop: spacing.lg,
    marginBottom: spacing.sm,
  },
  emptyText: {
    fontSize: typography.fontSize.body,
    color: colors.gray500,
    textAlign: 'center',
    lineHeight: 22,
  },
  listContainer: {
    padding: spacing.lg,
  },
  comparisonCard: {
    backgroundColor: '#ffffff',
    borderRadius: 24,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: 'rgba(0,0,0,0.04)',
    shadowColor: '#6E4B3A',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.08,
    shadowRadius: 16,
    elevation: 5,
    overflow: 'hidden',
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: 16,
  },
  titleWrapper: {
    flex: 1,
    paddingRight: 12,
  },
  comparisonName: {
    fontSize: 16,
    fontFamily: 'Poppins_600SemiBold',
    color: '#2d3748',
    marginBottom: 2,
  },
  comparisonSubName: {
    fontSize: 14,
    fontFamily: 'Poppins_400Regular',
    color: '#718096',
  },
  dateText: {
    fontSize: 13,
    fontFamily: 'Poppins_500Medium',
    color: '#a0aec0',
    backgroundColor: '#edf2f7',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
    overflow: 'hidden',
  },
  productsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 20,
    paddingBottom: 24,
  },
  productColumn: {
    flex: 1,
    alignItems: 'center',
  },
  imageWrapper: {
    width: 100,
    height: 100,
    borderRadius: 20,
    backgroundColor: '#ffffff',
    padding: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 3,
    borderWidth: 1,
    borderColor: '#f7fafc',
  },
  productImage: {
    width: '100%',
    height: '100%',
  },
  storeBadge: {
    position: 'absolute',
    bottom: -10,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  storeBadgeText: {
    color: '#ffffff',
    fontSize: 10,
    fontFamily: 'Poppins_700Bold',
    textTransform: 'uppercase',
  },
  priceText: {
    fontSize: 17,
    fontFamily: 'Poppins_700Bold',
    color: '#1a202c',
    marginTop: 4,
  },
  vsBadgeContainer: {
    width: 44,
    height: 44,
    marginHorizontal: 12,
    zIndex: 10,
    shadowColor: '#FF6B6B',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
  vsBadgeGradient: {
    width: '100%',
    height: '100%',
    borderRadius: 22,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 3,
    borderColor: '#ffffff',
  },
  vsBadgeText: {
    color: '#ffffff',
    fontFamily: 'Poppins_700Bold',
    fontSize: 14,
  },
  cardBody: {
    padding: 16,
  }
});
