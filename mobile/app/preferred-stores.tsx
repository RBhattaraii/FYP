/**
 * Preferred Stores Management Page
 * Allows users to manage their preferred shopping stores
 */

import { View, Text, FlatList, TouchableOpacity, StyleSheet, Switch, Image } from 'react-native';
import { useEffect, useState } from 'react';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { authStorage } from '../lib/authStorage';
import { colors, typography, spacing, borderRadius } from '../constants/theme';

interface Store {
  id: string;
  name: string;
  logo: string;
  description: string;
  isPreferred: boolean;
  rating: number;
  deliveryTime: string;
}

const ALL_STORES: Store[] = [
  {
    id: 'daraz',
    name: 'Daraz',
    logo: 'https://images.unsplash.com/photo-1542838132-92c53300491e?w=100&h=100&fit=crop',
    description: 'Largest online marketplace in Nepal with widest product assortments.',
    isPreferred: false,
    rating: 4.2,
    deliveryTime: '2-4 Days',
  },
  {
    id: 'hukut',
    name: 'Hukut',
    logo: 'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=100&h=100&fit=crop',
    description: 'Popular gadgets store in Nepal for tech and laptops.',
    isPreferred: false,
    rating: 4.5,
    deliveryTime: '1-2 Days',
  },
  {
    id: 'oliz',
    name: 'Oliz Store',
    logo: 'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=100&h=100&fit=crop',
    description: 'Authorized reseller of premium Apple products and gadgets.',
    isPreferred: false,
    rating: 4.8,
    deliveryTime: '1 Day',
  },
  {
    id: 'jeevee',
    name: 'Jeevee',
    logo: 'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=100&h=100&fit=crop',
    description: 'Premier shopping platform for health, babycare, beauty & cosmetics.',
    isPreferred: false,
    rating: 4.4,
    deliveryTime: '2-3 Days',
  },
  {
    id: 'cgdigital',
    name: 'CG Digital',
    logo: 'https://images.unsplash.com/photo-1556020685-e6a42ea1cd14?w=100&h=100&fit=crop',
    description: 'Top multi-brand electronics retail outlet chain in Nepal.',
    isPreferred: false,
    rating: 4.3,
    deliveryTime: '3-5 Days',
  },
  {
    id: 'sastodeal',
    name: 'Sastodeal',
    logo: 'https://images.unsplash.com/photo-1542838132-92c53300491e?w=100&h=100&fit=crop',
    description: 'One of the leading e-commerce companies in Nepal.',
    isPreferred: false,
    rating: 3.9,
    deliveryTime: '3-5 Days',
  },
];

export default function PreferredStoresScreen() {
  const router = useRouter();
  const params = useLocalSearchParams();
  const [stores, setStores] = useState<Store[]>(ALL_STORES);
  const [loading, setLoading] = useState(false);
  const [selectedStoreName, setSelectedStoreName] = useState<string | null>(null);

  useEffect(() => {
    checkAuthAndLoad();

    const storeId = Array.isArray(params.selectedStoreId)
      ? params.selectedStoreId[0]
      : params.selectedStoreId;
    const storeName = Array.isArray(params.selectedStoreName)
      ? params.selectedStoreName[0]
      : params.selectedStoreName;

    if (storeName) {
      setSelectedStoreName(storeName);
    }

    if (storeId) {
      setStores(prev =>
        prev.map(store =>
          store.id === storeId ? { ...store, isPreferred: true } : store
        )
      );
    } else if (storeName) {
      setStores(prev => {
        const matched = prev.find(store => store.name.toLowerCase() === storeName.toLowerCase());
        if (!matched) return prev;
        return prev.map(store =>
          store.id === matched.id ? { ...store, isPreferred: true } : store
        );
      });
    }
  }, [params]);

  const checkAuthAndLoad = async () => {
    try {
      const token = await authStorage.getItemAsync('token');
      if (!token) {
        router.replace('/(auth)/login');
        return;
      }
      
      // In real app, load store preferences from API here
      setStores(ALL_STORES); // Using mock data for now
    } catch (error) {
      console.error('Auth check failed:', error);
      router.replace('/(auth)/login');
    }
  };

  const toggleStorePreference = (storeId: string) => {
    setStores(prev => 
      prev.map(store => 
        store.id === storeId 
          ? { ...store, isPreferred: !store.isPreferred }
          : store
      )
    );
  };

  const preferredStores = stores.filter(store => store.isPreferred);
  const otherStores = stores.filter(store => !store.isPreferred);

  const renderStore = ({ item }: { item: Store }) => (
    <View style={styles.storeCard}>
      <View style={styles.storeHeader}>
        <View style={styles.storeLogoContainer}>
          <Image 
            source={{ uri: item.logo }} 
            style={styles.storeLogo}
            resizeMode="contain"
          />
        </View>
        
        <View style={styles.storeInfo}>
          <Text style={styles.storeName}>{item.name}</Text>
          <Text style={styles.storeDescription} numberOfLines={2}>
            {item.description}
          </Text>
          
          <View style={styles.storeMetrics}>
            <View style={styles.ratingContainer}>
              <Ionicons name="star" size={14} color={colors.warningOrange} />
              <Text style={styles.ratingText}>{item.rating}</Text>
            </View>
            
            <View style={styles.deliveryContainer}>
              <Ionicons name="time-outline" size={14} color={colors.gray500} />
              <Text style={styles.deliveryText}>{item.deliveryTime}</Text>
            </View>
          </View>
        </View>
        
        <Switch
          value={item.isPreferred}
          onValueChange={() => toggleStorePreference(item.id)}
          trackColor={{ false: colors.gray300, true: colors.primary + '40' }}
          thumbColor={item.isPreferred ? colors.primary : colors.gray400}
        />
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={24} color="#000" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Preferred Stores</Text>
        <View style={{ width: 24 }} />
      </View>

      {/* Info Card */}
      <View style={styles.infoCard}>
        <Ionicons name="information-circle" size={20} color={colors.primary} />
        <Text style={styles.infoText}>
          Select your preferred stores to prioritize them in search results and price comparisons.
        </Text>
      </View>
      {selectedStoreName && (
        <View style={styles.selectedSummaryCard}>
          <Text style={styles.selectedSummaryTitle}>Selected store</Text>
          <Text style={styles.selectedSummaryText}>{selectedStoreName}</Text>
        </View>
      )}

      {/* Summary */}
      <View style={styles.summaryCard}>
        <Text style={styles.summaryText}>
          {preferredStores.length} of {stores.length} stores selected
        </Text>
      </View>

      <FlatList
        data={[
          ...preferredStores,
          ...(otherStores.length > 0 ? [{ id: 'divider' } as any] : []),
          ...otherStores
        ]}
        renderItem={({ item }) => {
          if (item.id === 'divider') {
            return (
              <View style={styles.sectionDivider}>
                <Text style={styles.sectionTitle}>Other Stores</Text>
              </View>
            );
          }
          return renderStore({ item });
        }}
        keyExtractor={item => item.id}
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={false}
        ListHeaderComponent={
          preferredStores.length > 0 ? (
            <View style={styles.sectionHeader}>
              <Text style={styles.sectionTitle}>Preferred Stores</Text>
            </View>
          ) : null
        }
      />
    </View>
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
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: colors.white,
    borderBottomWidth: 1,
    borderBottomColor: colors.gray100,
    paddingTop: 50,
  },
  headerTitle: {
    fontSize: typography.fontSize.h3,
    fontWeight: typography.fontWeight.bold,
  },
  infoCard: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: colors.primary + '10',
    margin: spacing.lg,
    padding: spacing.md,
    borderRadius: borderRadius.medium,
    gap: spacing.sm,
  },
  infoText: {
    flex: 1,
    fontSize: typography.fontSize.body,
    color: colors.primary,
    lineHeight: 20,
  },
  summaryCard: {
    backgroundColor: colors.white,
    marginHorizontal: spacing.lg,
    marginBottom: spacing.lg,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    borderRadius: borderRadius.medium,
    borderWidth: 1,
    borderColor: colors.gray100,
  },
  selectedSummaryCard: {
    backgroundColor: colors.primary + '10',
    marginHorizontal: spacing.lg,
    marginBottom: spacing.sm,
    padding: spacing.md,
    borderRadius: borderRadius.medium,
    borderWidth: 1,
    borderColor: colors.primary + '20',
  },
  selectedSummaryTitle: {
    fontSize: typography.fontSize.bodyLarge,
    fontWeight: typography.fontWeight.semibold,
    color: colors.primary,
    marginBottom: spacing.xs,
  },
  selectedSummaryText: {
    fontSize: typography.fontSize.body,
    color: colors.gray900,
  },
  summaryText: {
    fontSize: typography.fontSize.body,
    color: colors.gray600,
    textAlign: 'center',
    fontWeight: typography.fontWeight.medium,
  },
  listContent: {
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.xl,
  },
  sectionHeader: {
    marginBottom: spacing.md,
  },
  sectionDivider: {
    marginVertical: spacing.lg,
  },
  sectionTitle: {
    fontSize: typography.fontSize.bodyLarge,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
    marginBottom: spacing.sm,
  },
  storeCard: {
    backgroundColor: colors.white,
    borderRadius: borderRadius.medium,
    marginBottom: spacing.md,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: colors.gray100,
  },
  storeHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  storeLogoContainer: {
    width: 48,
    height: 48,
    borderRadius: borderRadius.small,
    backgroundColor: colors.gray50,
    marginRight: spacing.md,
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
  },
  storeLogo: {
    width: 40,
    height: 40,
  },
  storeInfo: {
    flex: 1,
    marginRight: spacing.md,
  },
  storeName: {
    fontSize: typography.fontSize.bodyLarge,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
    marginBottom: spacing.xs,
  },
  storeDescription: {
    fontSize: typography.fontSize.body,
    color: colors.gray600,
    marginBottom: spacing.sm,
    lineHeight: 20,
  },
  storeMetrics: {
    flexDirection: 'row',
    gap: spacing.md,
  },
  ratingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
  },
  ratingText: {
    fontSize: typography.fontSize.caption,
    color: colors.gray700,
    fontWeight: typography.fontWeight.medium,
  },
  deliveryContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
  },
  deliveryText: {
    fontSize: typography.fontSize.caption,
    color: colors.gray700,
  },
});