import { View, Text, FlatList, TouchableOpacity, StyleSheet, Alert, Switch, ActivityIndicator, Platform, Image, Modal } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useEffect, useState, useRef } from 'react';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Swipeable } from 'react-native-gesture-handler';
import { authStorage } from '../lib/authStorage';
import { getPriceAlerts, deletePriceAlert, PriceAlert as RemotePriceAlert } from '../services/notifications';
import { useFocusEffect } from '@react-navigation/native';
import { getRateLimitUntil } from '../lib/telemetry';

const THEME_BROWN = '#6E4B3A';
const THEME_BG = '#FFFFFF';
const CARD_BG = '#FFFFFF';

type PriceAlert = {
  id: string;
  productName: string;
  productImage?: string;
  currentPrice: number;
  targetPrice: number;
  isActive: boolean;
  createdAt: string;
  lastChecked: string;
};

const normalizeAlert = (alert: RemotePriceAlert): PriceAlert => ({
  id: String(alert.id),
  productName: alert.product_title,
  productImage: alert.product_image_url,
  currentPrice: alert.current_price,
  targetPrice: alert.target_price,
  isActive: alert.is_active,
  createdAt: alert.created_at,
  lastChecked: alert.triggered_at ?? alert.created_at,
});

export default function PriceAlertsScreen() {
  const router = useRouter();
  const params = useLocalSearchParams();
  const [alerts, setAlerts] = useState<PriceAlert[]>([]);
  const [loading, setLoading] = useState(false);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [isCreatingOptimistic, setIsCreatingOptimistic] = useState(false);
  const [selectedProductName, setSelectedProductName] = useState<string | null>(null);
  const [selectedProductPrice, setSelectedProductPrice] = useState<number | null>(null);
  const [selectedStoreName, setSelectedStoreName] = useState<string | null>(null);
  
  // Custom Delete Modal State
  const [deleteModalVisible, setDeleteModalVisible] = useState(false);
  const [alertToDelete, setAlertToDelete] = useState<PriceAlert | null>(null);
  
  const rowRefs = useRef(new Map());

  useEffect(() => {
    const productName = Array.isArray(params.selectedProductName) ? params.selectedProductName[0] : params.selectedProductName;
    const productPrice = Array.isArray(params.selectedProductPrice) ? Number(params.selectedProductPrice[0]) : params.selectedProductPrice;
    const storeName = Array.isArray(params.selectedStoreName) ? params.selectedStoreName[0] : params.selectedStoreName;
    const optimisticFlag = Array.isArray(params.optimistic) ? params.optimistic[0] : params.optimistic;

    if (productName) setSelectedProductName(productName);
    if (productPrice) setSelectedProductPrice(Number(productPrice));
    if (storeName) setSelectedStoreName(storeName);
    setIsCreatingOptimistic(Boolean(optimisticFlag));
  }, [params]);

  useEffect(() => {
    let cancelled = false;
    let retryCount = 0;
    const maxRetries = 3;

    const loadAlerts = async () => {
      try {
        setLoading(true);
        setFetchError(null);
        const token = await authStorage.getItemAsync('token');
        if (!token) {
          if (!cancelled) router.replace('/(auth)/login');
          return;
        }

        const data = await getPriceAlerts(token);
        if (!cancelled) {
          setAlerts((data.alerts || []).map(normalizeAlert));
          setLoading(false);
          setFetchError(null);
        }
      } catch (apiError: any) {
        if (cancelled) return;

        const status = apiError?.status ?? apiError?.response?.status;
        const isRateLimit = status === 429 || apiError?.message?.includes('429');
        console.error('Get price alerts error:', apiError);
        if (isRateLimit && retryCount < maxRetries) {
          retryCount += 1;
          const delay = 1000 * Math.pow(2, retryCount);
          setTimeout(loadAlerts, delay);
        } else {
          setAlerts([]);
          setLoading(false);
          setFetchError(
            isRateLimit
              ? 'Too many requests. Please wait a moment and try again.'
              : 'Unable to load price alerts right now. Please try again later.'
          );
        }
      }
    };

    loadAlerts();
    return () => { cancelled = true; };
  }, []);

  const loadOptimistic = async () => {
    try {
      const raw = await authStorage.getItemAsync('optimistic_alerts');
      const list = raw ? JSON.parse(raw) : [];
      if (list && list.length) {
        setAlerts(prev => {
          const existingNames = new Set(prev.map(p => p.productName));
          const toAdd = list.filter((o: any) => !existingNames.has(o.productName)).map((o: any) => ({
            id: o.id,
            productName: o.productName,
            currentPrice: o.currentPrice,
            targetPrice: o.targetPrice,
            isActive: o.isActive,
            createdAt: o.createdAt,
            lastChecked: o.lastChecked,
          }));
          return [...toAdd, ...prev];
        });
      }

      const until = await getRateLimitUntil('notifications_alerts');
      if (until && until > Date.now()) {
        setFetchError('Server is rate limiting requests; please try again later.');
      }
    } catch (e) {
      console.warn('Failed to load optimistic alerts', e);
    }
  };

  useFocusEffect((() => { loadOptimistic(); return () => {}; }) as any);

  const toggleAlert = (alertId: string) => {
    setAlerts(prev => prev.map(alert => alert.id === alertId ? { ...alert, isActive: !alert.isActive } : alert));
  };

  const removeOptimisticAlertFromStorage = async (alertId: string) => {
    try {
      const raw = await authStorage.getItemAsync('optimistic_alerts');
      const list = raw ? JSON.parse(raw) : [];
      const filtered = list.filter((alert: any) => alert.id !== alertId);
      await authStorage.setItemAsync('optimistic_alerts', JSON.stringify(filtered));
    } catch (e) {
      console.warn('Failed to remove optimistic alert from storage', e);
    }
  };

  const triggerDelete = (alert: PriceAlert) => {
    setAlertToDelete(alert);
    setDeleteModalVisible(true);
    
    // Close the swipeable row
    const ref = rowRefs.current.get(alert.id);
    if (ref) {
      ref.close();
    }
  };

  const confirmDelete = async () => {
    if (!alertToDelete) return;
    const alertId = alertToDelete.id;
    const numericAlertId = Number(alertId);
    const isOptimistic = isNaN(numericAlertId);
    
    setDeleteModalVisible(false);

    if (isOptimistic) {
      setAlerts(prev => prev.filter(alert => alert.id !== alertId));
      await removeOptimisticAlertFromStorage(alertId);
      setAlertToDelete(null);
      return;
    }

    try {
      const token = await authStorage.getItemAsync('token');
      if (!token) throw new Error('Not authenticated');
      await deletePriceAlert(token, numericAlertId);
      setAlerts(prev => prev.filter(alert => alert.id !== alertId));
      await removeOptimisticAlertFromStorage(alertId);
    } catch (error: any) {
      console.error('Failed to delete price alert:', error);
      const message = error?.message || 'Unable to delete price alert. Please try again.';
      Alert.alert('Delete Failed', message);
    } finally {
      setAlertToDelete(null);
    }
  };

  const getPriceStatus = (current: number, target: number) => {
    if (current <= target) return { status: 'achieved', color: '#10B981', icon: 'checkmark-circle' };
    const percentage = ((current - target) / target * 100);
    if (percentage <= 10) return { status: 'close', color: THEME_BROWN, icon: 'time' };
    return { status: 'waiting', color: '#757575', icon: 'trending-down' };
  };

  const renderRightActions = (alert: PriceAlert) => {
    return (
      <TouchableOpacity
        style={styles.deleteSwipeAction}
        onPress={() => triggerDelete(alert)}
        activeOpacity={0.8}
      >
        <Ionicons name="trash-outline" size={24} color="#DF3B48" />
      </TouchableOpacity>
    );
  };

  const renderAlert = ({ item }: { item: PriceAlert }) => {
    return (
      <Swipeable 
        ref={(ref) => {
          if (ref) {
            rowRefs.current.set(item.id, ref);
          } else {
            rowRefs.current.delete(item.id);
          }
        }}
        renderRightActions={() => renderRightActions(item)}
        overshootRight={false}
      >
        <View style={styles.alertCard}>
          {/* Left: Image Placeholder */}
          <View style={styles.imagePlaceholder}>
            {item.productImage ? (
              <Image source={{ uri: item.productImage }} style={styles.productImage} />
            ) : (
              <Ionicons name="pricetag-outline" size={32} color="#111111" />
            )}
          </View>

          {/* Right: Content */}
          <View style={styles.cardContent}>
            <Text style={styles.productName} numberOfLines={1}>
              {item.productName}
            </Text>
            
            <Text style={styles.alertDate}>Target : Rs {item.targetPrice}</Text>
            
            <View style={styles.cardBottomRow}>
              <Text style={styles.currentPrice}>Rs {item.currentPrice}</Text>
              
              <View style={styles.rightControls}>
                <Switch
                  style={{ transform: [{ scale: 0.8 }] }}
                  value={item.isActive}
                  onValueChange={() => toggleAlert(item.id)}
                  trackColor={{ false: '#EEEEEE', true: '#9A7B66' }}
                  thumbColor={'#FFFFFF'}
                  ios_backgroundColor="#EEEEEE"
                />
              </View>
            </View>
          </View>
        </View>
      </Swipeable>
    );
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <TouchableOpacity style={styles.headerIcon} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={22} color="#111111" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Price Alerts</Text>
        <View style={styles.headerPlaceholder} />
      </View>

      {selectedProductName && (
        <View style={styles.selectedSummaryCard}>
          <Text style={styles.selectedSummaryTitle}>Selected product</Text>
          <Text style={styles.selectedSummaryText}>{selectedProductName}</Text>
          {selectedStoreName ? <Text style={styles.selectedSummaryText}>Store: {selectedStoreName}</Text> : null}
        </View>
      )}
      
      {isCreatingOptimistic && (
        <View style={styles.creatingBanner}>
          <ActivityIndicator size="small" color={THEME_BROWN} />
          <Text style={styles.creatingText}>Creating alert...</Text>
        </View>
      )}

      {fetchError ? (
        <View style={styles.errorContainer}>
          <Ionicons name="alert-circle-outline" size={50} color="#EF4444" />
          <Text style={styles.errorTitle}>Unable to load alerts</Text>
          <Text style={styles.errorText}>{fetchError}</Text>
          <TouchableOpacity
            style={styles.reloadButton}
            onPress={() => {
              setFetchError(null);
              setLoading(true);
              const retry = async () => {
                const token = await authStorage.getItemAsync('token');
                if (!token) return router.replace('/(auth)/login');
                try {
                  const data = await getPriceAlerts(token);
                  setAlerts((data.alerts || []).map(normalizeAlert));
                } catch (error) {
                  console.error('Retry get price alerts error:', error);
                } finally {
                  setLoading(false);
                }
              };
              retry();
            }}
          >
            <Text style={styles.reloadButtonText}>Try Again</Text>
          </TouchableOpacity>
        </View>
      ) : alerts.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Ionicons name="notifications-off-outline" size={64} color="#CFCBC8" />
          <Text style={styles.emptyTitle}>No Price Alerts</Text>
          <Text style={styles.emptySubtitle}>
            Set price alerts on products you're interested in to get notified when prices drop.
          </Text>
        </View>
      ) : (
        <>
          <View style={styles.summaryContainer}>
            <Text style={styles.summaryText}>
              {alerts.filter(a => a.isActive).length} active alerts
            </Text>
          </View>
          
          <FlatList
            data={alerts}
            renderItem={renderAlert}
            keyExtractor={item => item.id}
            contentContainerStyle={styles.listContent}
            showsVerticalScrollIndicator={false}
          />
        </>
      )}

      {/* Delete Confirmation Modal */}
      <Modal
        visible={deleteModalVisible}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setDeleteModalVisible(false)}
      >
        <TouchableOpacity 
          style={styles.modalOverlay} 
          activeOpacity={1} 
          onPress={() => setDeleteModalVisible(false)}
        >
          <TouchableOpacity activeOpacity={1} style={styles.bottomSheet}>
            <View style={styles.bottomSheetHandle} />
            <Text style={styles.modalTitle}>Remove from Alerts?</Text>
            <View style={styles.modalDivider} />
            
            {alertToDelete && (
              <View style={styles.modalProductCard}>
                <View style={[styles.imagePlaceholder, { width: 70, height: 70, marginRight: 12 }]}>
                  {alertToDelete.productImage ? (
                    <Image source={{ uri: alertToDelete.productImage }} style={styles.productImage} />
                  ) : (
                    <Ionicons name="pricetag-outline" size={24} color="#111111" />
                  )}
                </View>
                <View style={{ flex: 1, justifyContent: 'center' }}>
                  <Text style={styles.productName} numberOfLines={2}>{alertToDelete.productName}</Text>
                  <Text style={styles.currentPrice}>Rs {alertToDelete.currentPrice}</Text>
                </View>
              </View>
            )}
            
            <View style={styles.modalActionRow}>
              <TouchableOpacity style={styles.cancelBtn} onPress={() => setDeleteModalVisible(false)}>
                <Text style={styles.cancelBtnText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.confirmBtn} onPress={confirmDelete}>
                <Text style={styles.confirmBtnText}>Yes, Remove</Text>
              </TouchableOpacity>
            </View>
          </TouchableOpacity>
        </TouchableOpacity>
      </Modal>

    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: THEME_BG,
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
  summaryContainer: {
    paddingHorizontal: 24,
    paddingBottom: 16,
  },
  summaryText: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 14,
    color: '#555555',
  },
  listContent: {
    paddingHorizontal: 0,
    paddingBottom: 40,
  },
  alertCard: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#F5F5F5',
    paddingHorizontal: 20,
    paddingVertical: 20,
    alignItems: 'center',
  },
  deleteSwipeAction: {
    width: 80,
    backgroundColor: '#F3D5D7',
    justifyContent: 'center',
    alignItems: 'center',
  },
  imagePlaceholder: {
    width: 90,
    height: 90,
    borderRadius: 12,
    backgroundColor: '#F5F5F5',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
    overflow: 'hidden',
  },
  productImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  cardContent: {
    flex: 1,
    justifyContent: 'center',
  },
  productName: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 16,
    color: '#111111',
    marginBottom: 4,
  },
  alertDate: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 13,
    color: '#7A7A7A',
    marginBottom: 8,
  },
  cardBottomRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  currentPrice: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 16,
    color: '#111111',
  },
  rightControls: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  selectedSummaryCard: {
    backgroundColor: CARD_BG,
    marginHorizontal: 24,
    marginTop: 8,
    marginBottom: 16,
    padding: 16,
    borderRadius: 16,
  },
  selectedSummaryTitle: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 14,
    color: '#111111',
    marginBottom: 4,
  },
  selectedSummaryText: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 14,
    color: '#757575',
  },
  creatingBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    marginHorizontal: 24,
    marginBottom: 16,
    backgroundColor: CARD_BG,
    borderRadius: 8,
  },
  creatingText: {
    marginLeft: 12,
    color: THEME_BROWN,
    fontFamily: 'Poppins_500Medium',
    fontSize: 14,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 24,
  },
  errorTitle: {
    marginTop: 24,
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 18,
    color: '#111111',
    textAlign: 'center',
  },
  errorText: {
    marginTop: 8,
    fontFamily: 'Poppins_400Regular',
    fontSize: 14,
    color: '#757575',
    textAlign: 'center',
    marginBottom: 24,
  },
  reloadButton: {
    backgroundColor: THEME_BROWN,
    paddingHorizontal: 32,
    paddingVertical: 14,
    borderRadius: 9999,
  },
  reloadButtonText: {
    fontFamily: 'Poppins_600SemiBold',
    color: '#FFFFFF',
    fontSize: 14,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 32,
  },
  emptyTitle: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 20,
    color: '#111111',
    marginTop: 24,
    marginBottom: 8,
  },
  emptySubtitle: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 14,
    color: '#7A7A7A',
    textAlign: 'center',
    lineHeight: 22,
  },
  
  // Modal Styles
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.4)',
    justifyContent: 'flex-end',
  },
  bottomSheet: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 24,
    paddingBottom: Platform.OS === 'ios' ? 40 : 24,
    alignItems: 'center',
  },
  bottomSheetHandle: {
    width: 40,
    height: 4,
    backgroundColor: '#E0E0E0',
    borderRadius: 2,
    marginBottom: 20,
  },
  modalTitle: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 18,
    color: '#111111',
    marginBottom: 16,
  },
  modalDivider: {
    width: '100%',
    height: 1,
    backgroundColor: '#F0F0F0',
    marginBottom: 20,
  },
  modalProductCard: {
    flexDirection: 'row',
    width: '100%',
    backgroundColor: '#FFFFFF',
    marginBottom: 32,
  },
  modalActionRow: {
    flexDirection: 'row',
    gap: 16,
    width: '100%',
  },
  cancelBtn: {
    flex: 1,
    paddingVertical: 16,
    borderRadius: 9999,
    backgroundColor: '#F5F5F5',
    alignItems: 'center',
    justifyContent: 'center',
  },
  cancelBtnText: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 16,
    color: '#6E4B3A',
  },
  confirmBtn: {
    flex: 1,
    paddingVertical: 16,
    borderRadius: 9999,
    backgroundColor: '#6E4B3A',
    alignItems: 'center',
    justifyContent: 'center',
  },
  confirmBtnText: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 16,
    color: '#FFFFFF',
  }
});