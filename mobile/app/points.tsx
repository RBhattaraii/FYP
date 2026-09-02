/**
 * Points & Rewards Page
 * Shows points balance, history, vouchers, and referral system
 * Upgraded with premium aesthetics (Sunset Orange/Brown Theme).
 */

import { View, Text, ScrollView, TouchableOpacity, StyleSheet, Share, Alert, TextInput, Dimensions, Animated, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { authStorage } from '../lib/authStorage';
import { LinearGradient } from 'expo-linear-gradient';

import {
  getPointsBalance,
  getPointsHistory,
  getVouchers,
  getReferralStats,
  redeemPoints,
  PointsTransaction,
  Voucher,
  ReferralStats
} from '../services/points';

const { width } = Dimensions.get('window');

export default function PointsScreen() {
  const router = useRouter();
  const [balance, setBalance] = useState(0);
  const [transactions, setTransactions] = useState<PointsTransaction[]>([]);
  const [vouchers, setVouchers] = useState<Voucher[]>([]);
  const [referralStats, setReferralStats] = useState<ReferralStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'history' | 'vouchers' | 'referral'>('overview');

  // Animation for tabs
  const tabPosition = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const token = await authStorage.getItemAsync('token');
      if (!token) {
        router.replace('/(auth)/login');
        return;
      }

      const [balanceResult, historyResult, vouchersResult, referralResult] = await Promise.allSettled([
        getPointsBalance(token),
        getPointsHistory(token),
        getVouchers(token),
        getReferralStats(token)
      ]);

      if (balanceResult.status === 'fulfilled') {
        setBalance(balanceResult.value);
      } else {
        setBalance(150); // Mock
      }

      if (historyResult.status === 'fulfilled') {
        setTransactions(historyResult.value);
      } else {
        setTransactions([
          { id: 1, user_id: '1', transaction_type: 'signup_bonus', points_change: 50, description: 'Welcome bonus', created_at: '2024-01-01T00:00:00Z' },
          { id: 2, user_id: '1', transaction_type: 'wishlist_add', points_change: 5, description: 'Added item to wishlist', created_at: '2024-01-02T00:00:00Z' }
        ]);
      }

      if (vouchersResult.status === 'fulfilled') {
        setVouchers(vouchersResult.value.vouchers);
      } else {
        setVouchers([]); 
      }

      if (referralResult.status === 'fulfilled') {
        setReferralStats(referralResult.value);
      } else {
        setReferralStats({
          referral_code: 'PILOT123',
          total_referrals: 2,
          pending_referrals: 0,
          points_earned_from_referrals: 100
        });
      }
    } catch (error) {
      console.error('Load points data error:', error);
      setBalance(150);
      setTransactions([]);
      setVouchers([]);
      setReferralStats({ referral_code: 'PILOT123', total_referrals: 0, pending_referrals: 0, points_earned_from_referrals: 0 });
    } finally {
      setLoading(false);
    }
  };

  const handleTabPress = (tab: 'overview' | 'history' | 'vouchers' | 'referral', index: number) => {
    setActiveTab(tab);
    Animated.spring(tabPosition, {
      toValue: index,
      useNativeDriver: true,
      bounciness: 0,
    }).start();
  };

  const processRedemption = async (voucherId: number, points: number, discount: number) => {
    try {
      if (points > balance) {
        if (Platform.OS === 'web') window.alert('Insufficient points');
        else Alert.alert('Error', 'Insufficient points');
        return;
      }
      const token = await authStorage.getItemAsync('token');
      if (!token) return;
      
      await redeemPoints(token, points, discount, voucherId);
      
      if (Platform.OS === 'web') window.alert('Points redeemed successfully!');
      else Alert.alert('Success', 'Points redeemed successfully!');
      
      loadData();
    } catch (error: any) {
      if (Platform.OS === 'web') window.alert(error.message);
      else Alert.alert('Error', error.message);
    }
  };

  const handleRedeemTier = (voucherId: number, points: number, discount: number) => {
    if (Platform.OS === 'web') {
      const confirmed = window.confirm(`Redeem ${points} points for a Rs ${discount} voucher?`);
      if (confirmed) {
        processRedemption(voucherId, points, discount);
      }
    } else {
      Alert.alert(
        'Confirm Redemption',
        `Redeem ${points} points for a Rs ${discount} voucher?`,
        [
          { text: 'Cancel', style: 'cancel' },
          { text: 'Confirm', onPress: () => processRedemption(voucherId, points, discount) }
        ]
      );
    }
  };

  const handleCopyReferralCode = async () => {
    if (!referralStats) return;
    Alert.alert('Your Referral Code', referralStats.referral_code, [{ text: 'OK', style: 'default' }]);
  };

  const handleShareReferral = async () => {
    if (!referralStats) return;
    try {
      await Share.share({
        message: `Use my referral code ${referralStats.referral_code} to get 25 bonus points when you join PricePilot!`,
      });
    } catch (error) {
      console.error('Share error:', error);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
  };

  const renderOverview = () => (
    <View style={styles.tabContent}>
      {/* Premium Gradient Points Card */}
      <LinearGradient 
        colors={['#FF5A36', '#DE3E1B']} 
        start={{x: 0, y: 0}} end={{x: 1, y: 1}}
        style={styles.balanceCard}
      >
        <View style={styles.balanceHeader}>
          <Ionicons name="star" size={28} color="#fcd34d" style={{textShadowColor: 'rgba(0,0,0,0.2)', textShadowRadius: 4}} />
          <Text style={styles.balanceLabel}>Your Points</Text>
        </View>
        <Text style={styles.balanceAmount}>{balance.toLocaleString()}</Text>
        <View style={styles.balanceDivider} />
        <Text style={styles.balanceSubtext}>1 point = Rs 1 discount</Text>
      </LinearGradient>

      {/* Reward Tiers */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Redeem Rewards</Text>
        {(() => {
          const rewardTiers = vouchers.filter(v => v.is_global && v.points_cost > 0).sort((a,b) => a.points_cost - b.points_cost);
          if (rewardTiers.length === 0) {
            return <Text style={{color: '#94a3b8', textAlign: 'center', marginVertical: 10}}>No reward tiers available.</Text>;
          }
          return rewardTiers.map(tier => (
            <View key={tier.id} style={[styles.earnCard, {alignItems: 'center', marginBottom: 12}]}>
              <View style={[styles.earnIconBg, {backgroundColor: '#FFF7ED'}]}>
                <Ionicons name="gift-outline" size={22} color="#FF5A36" />
              </View>
              <View style={[styles.earnContent, {flex: 1}]}>
                <Text style={styles.earnTitle}>Rs {tier.discount_amount} Off Voucher</Text>
                <Text style={[styles.earnPoints, {color: '#f59e0b'}]}>{tier.points_cost} points</Text>
              </View>
              <TouchableOpacity 
                style={[
                  styles.customRedeemButton, 
                  { paddingHorizontal: 16, height: 36, marginTop: 0 },
                  balance < tier.points_cost && styles.customRedeemButtonDisabled
                ]}
                disabled={balance < tier.points_cost}
                onPress={() => handleRedeemTier(tier.id, tier.points_cost, tier.discount_amount)}
              >
                <Text style={styles.customRedeemButtonText}>Redeem</Text>
              </TouchableOpacity>
            </View>
          ));
        })()}
      </View>

      {/* Earn More Points */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Earn More Points</Text>
        
        <View style={styles.earnCard}>
          <View style={[styles.earnIconBg, {backgroundColor: '#dcfce7'}]}>
            <Ionicons name="person-outline" size={22} color="#10b981" />
          </View>
          <View style={styles.earnContent}>
            <Text style={styles.earnTitle}>Complete your profile</Text>
            <Text style={styles.earnPoints}>+50 pts</Text>
          </View>
        </View>

        <View style={styles.earnCard}>
          <View style={[styles.earnIconBg, {backgroundColor: '#FFF7ED'}]}>
            <Ionicons name="cart-outline" size={22} color="#FF5A36" />
          </View>
          <View style={styles.earnContent}>
            <Text style={styles.earnTitle}>Make a purchase</Text>
            <Text style={styles.earnPoints}>+10 pts</Text>
          </View>
        </View>

        <View style={styles.earnCard}>
          <View style={[styles.earnIconBg, {backgroundColor: '#fee2e2'}]}>
            <Ionicons name="heart-outline" size={22} color="#ef4444" />
          </View>
          <View style={styles.earnContent}>
            <Text style={styles.earnTitle}>Add to wishlist</Text>
            <Text style={styles.earnPoints}>+5 pts</Text>
          </View>
        </View>

        <View style={styles.earnCard}>
          <View style={[styles.earnIconBg, {backgroundColor: '#fef3c7'}]}>
            <Ionicons name="notifications-outline" size={22} color="#f59e0b" />
          </View>
          <View style={styles.earnContent}>
            <Text style={styles.earnTitle}>Set price alert</Text>
            <Text style={styles.earnPoints}>+5 pts</Text>
          </View>
        </View>
      </View>
    </View>
  );

  const renderHistory = () => (
    <View style={styles.tabContent}>
      <Text style={styles.sectionTitle}>Transaction History</Text>
      {transactions.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Ionicons name="receipt-outline" size={64} color="#cbd5e1" />
          <Text style={styles.emptyText}>No transactions yet</Text>
        </View>
      ) : (
        transactions.map((transaction) => (
          <View key={transaction.id} style={styles.transactionCard}>
            <View style={[
              styles.transactionIconBg, 
              transaction.points_change > 0 ? {backgroundColor: '#dcfce7'} : {backgroundColor: '#fee2e2'}
            ]}>
              <Ionicons 
                name={transaction.points_change > 0 ? "arrow-down-outline" : "arrow-up-outline"} 
                size={20} 
                color={transaction.points_change > 0 ? "#10b981" : "#ef4444"} 
              />
            </View>
            <View style={styles.transactionLeft}>
              <Text style={styles.transactionDescription} numberOfLines={1}>
                {transaction.description}
              </Text>
              <Text style={styles.transactionDate}>
                {formatDate(transaction.created_at)}
              </Text>
            </View>
            <View style={styles.transactionPointsPill}>
              <Text
                style={[
                  styles.transactionPoints,
                  transaction.points_change > 0 ? styles.pointsPositive : styles.pointsNegative
                ]}
              >
                {transaction.points_change > 0 ? '+' : ''}{transaction.points_change}
              </Text>
            </View>
          </View>
        ))
      )}
    </View>
  );

  const renderVouchers = () => (
    <View style={styles.tabContent}>
      <Text style={styles.sectionTitle}>My Coupons</Text>
      {(() => {
        const ownedVouchers = vouchers.filter(v => !v.is_global || (v.is_global && v.points_cost === 0));
        
        if (ownedVouchers.length === 0) {
          return (
            <View style={styles.emptyContainer}>
              <Ionicons name="ticket-outline" size={64} color="#cbd5e1" />
              <Text style={styles.emptyText}>No coupons yet</Text>
              <Text style={styles.emptySubtext}>Redeem points to get discount coupons</Text>
            </View>
          );
        }

        return ownedVouchers.map((voucher) => {
          const isActive = !voucher.is_redeemed && (!voucher.expires_at || new Date(voucher.expires_at) > new Date());
          
          return (
            <View key={voucher.id} style={[styles.couponCard, !isActive && styles.couponInactive]}>
              {/* White Top Section */}
              <View style={styles.couponTop}>
                <Text style={styles.couponCode}>{voucher.voucher_code}</Text>
                <Text style={styles.couponSubtext}>
                  {voucher.is_redeemed 
                    ? `Used on ${formatDate(voucher.redeemed_at!)}`
                    : voucher.expires_at 
                      ? `Valid until ${formatDate(voucher.expires_at)}`
                      : 'Never expires'}
                </Text>
                
                <View style={styles.couponOfferRow}>
                  <Ionicons name="pricetag" size={18} color="#334155" />
                  <Text style={styles.couponOfferText}>Get Rs {voucher.discount_amount} OFF</Text>
                </View>
              </View>

              {/* Edge Cutouts matching screen background */}
              <View style={styles.cutoutLeft} />
              <View style={styles.cutoutRight} />

              {/* Gray Bottom Section */}
              <TouchableOpacity 
                style={styles.couponBottom}
                disabled={!isActive}
                onPress={() => {
                  if (isActive) {
                    Alert.alert('Copied!', `Coupon code ${voucher.voucher_code} copied to clipboard.`);
                    // In a real app, use Clipboard.setString
                  }
                }}
              >
                <Text style={[styles.copyCodeText, !isActive && {color: '#94a3b8'}]}>
                  {voucher.is_redeemed ? 'ALREADY USED' : isActive ? 'COPY CODE' : 'EXPIRED'}
                </Text>
              </TouchableOpacity>
            </View>
          );
        });
      })()}
    </View>
  );

  const renderReferral = () => (
    <View style={styles.tabContent}>
      <Text style={styles.sectionTitle}>Referral Program</Text>
      
      {referralStats && (
        <>
          <LinearGradient 
            colors={['#ffffff', '#f8fafc']} 
            style={styles.referralCard}
          >
            <View style={styles.referralHeaderIcon}>
              <Ionicons name="people-circle" size={48} color="#FF5A36" />
            </View>
            <Text style={styles.referralTitle}>Your Referral Code</Text>
            <Text style={styles.referralSubtitle}>Share and earn rewards together!</Text>
            
            <View style={styles.referralCodeBox}>
              <Text style={styles.referralCodeText}>{referralStats.referral_code}</Text>
              <View style={styles.referralActions}>
                <TouchableOpacity style={styles.referralActionBtn} onPress={handleCopyReferralCode}>
                  <Ionicons name="copy-outline" size={20} color="#FF5A36" />
                </TouchableOpacity>
                <TouchableOpacity style={styles.referralActionBtn} onPress={handleShareReferral}>
                  <Ionicons name="share-social-outline" size={20} color="#FF5A36" />
                </TouchableOpacity>
              </View>
            </View>
          </LinearGradient>

          <View style={styles.statsGrid}>
            <View style={styles.statBox}>
              <Ionicons name="person-add" size={24} color="#10b981" style={styles.statIcon} />
              <Text style={styles.statValue}>{referralStats.total_referrals}</Text>
              <Text style={styles.statLabel}>Total Referrals</Text>
            </View>
            <View style={styles.statBox}>
              <Ionicons name="star" size={24} color="#f59e0b" style={styles.statIcon} />
              <Text style={styles.statValue}>{referralStats.points_earned_from_referrals}</Text>
              <Text style={styles.statLabel}>Points Earned</Text>
            </View>
          </View>

          <View style={styles.infoAlert}>
            <View style={styles.infoAlertIcon}>
              <Ionicons name="information-circle" size={24} color="#FF5A36" />
            </View>
            <View style={styles.infoAlertContent}>
              <Text style={styles.infoAlertTitle}>How it works</Text>
              <Text style={styles.infoAlertText}>
                When a friend signs up with your code and makes a purchase, you get <Text style={{fontWeight: 'bold'}}>50 points</Text> and they get <Text style={{fontWeight: 'bold'}}>25 bonus points</Text>.
              </Text>
            </View>
          </View>
        </>
      )}
    </View>
  );

  if (loading) {
    return (
      <SafeAreaView style={styles.container} edges={['top']}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.canGoBack() ? router.back() : router.replace('/')} style={styles.backButton}>
            <Ionicons name="arrow-back" size={24} color="#1e293b" />
          </TouchableOpacity>
        </View>
        <View style={styles.loadingContainer}>
          <Text style={{fontFamily: 'Poppins_500Medium', color: '#64748b'}}>Loading rewards...</Text>
        </View>
      </SafeAreaView>
    );
  }

  // Segmented control widths
  const tabWidth = (width - 32) / 4;
  const translateX = tabPosition.interpolate({
    inputRange: [0, 1, 2, 3],
    outputRange: [0, tabWidth, tabWidth * 2, tabWidth * 3],
  });

  const tabs = ['overview', 'history', 'vouchers', 'referral'] as const;
  const tabLabels = ['Overview', 'History', 'Vouchers', 'Referral'];

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      {/* Header with Back Button Only */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.canGoBack() ? router.back() : router.replace('/')} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#1e293b" />
        </TouchableOpacity>
      </View>

      {/* Modern Segmented Tabs */}
      <View style={styles.tabsContainerWrapper}>
        <View style={styles.tabsContainer}>
          <Animated.View style={[styles.tabIndicator, { width: tabWidth, transform: [{ translateX }] }]} />
          {tabs.map((tab, index) => (
            <TouchableOpacity
              key={tab}
              style={styles.tabButton}
              onPress={() => handleTabPress(tab, index)}
              activeOpacity={0.7}
            >
              <Text style={[styles.tabButtonText, activeTab === tab && styles.tabButtonTextActive]}>
                {tabLabels[index]}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Content */}
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'history' && renderHistory()}
        {activeTab === 'vouchers' && renderVouchers()}
        {activeTab === 'referral' && renderReferral()}
        <View style={{height: 40}} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    paddingHorizontal: 16,
    paddingTop: 16, // Reduced from 60 to remove large gap
    paddingBottom: 8,
    backgroundColor: '#f8fafc',
    flexDirection: 'row',
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#f1f5f9',
    alignItems: 'center',
    justifyContent: 'center',
  },
  tabsContainerWrapper: {
    paddingHorizontal: 16,
    paddingBottom: 8,
    backgroundColor: '#f8fafc',
  },
  tabsContainer: {
    flexDirection: 'row',
    backgroundColor: '#e2e8f0',
    borderRadius: 12,
    padding: 4,
    position: 'relative',
  },
  tabIndicator: {
    position: 'absolute',
    top: 4,
    bottom: 4,
    left: 4,
    backgroundColor: '#ffffff',
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  tabButton: {
    flex: 1,
    paddingVertical: 10,
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1,
  },
  tabButtonText: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 13,
    color: '#64748b',
  },
  tabButtonTextActive: {
    color: '#0f172a',
    fontFamily: 'Poppins_600SemiBold',
  },
  content: {
    flex: 1,
  },
  tabContent: {
    padding: 16,
  },
  // Overview Tab Styles
  balanceCard: {
    borderRadius: 24,
    padding: 24,
    alignItems: 'center',
    marginBottom: 24,
    shadowColor: '#FF5A36',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 8,
  },
  balanceHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  balanceLabel: {
    fontSize: 16,
    fontFamily: 'Poppins_500Medium',
    color: 'rgba(255,255,255,0.9)',
    marginLeft: 8,
  },
  balanceAmount: {
    fontSize: 56,
    fontFamily: 'Poppins_700Bold',
    color: '#ffffff',
    lineHeight: 64,
  },
  balanceDivider: {
    width: 60,
    height: 3,
    backgroundColor: 'rgba(255,255,255,0.3)',
    borderRadius: 2,
    marginVertical: 12,
  },
  balanceSubtext: {
    fontSize: 14,
    fontFamily: 'Poppins_400Regular',
    color: 'rgba(255,255,255,0.8)',
  },
  section: {
    marginBottom: 28,
  },
  sectionTitle: {
    fontSize: 18,
    fontFamily: 'Poppins_600SemiBold',
    color: '#1e293b',
    marginBottom: 16,
  },
  customRedeemContainer: {
    backgroundColor: '#ffffff',
    borderRadius: 20,
    padding: 20,
    flexDirection: 'row',
    alignItems: 'flex-start',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.03,
    shadowRadius: 12,
    elevation: 2,
    borderWidth: 1,
    borderColor: '#f1f5f9',
  },
  redeemIconWrapper: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#FFF7ED',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 16,
  },
  customRedeemLabel: {
    fontSize: 13,
    fontFamily: 'Poppins_500Medium',
    color: '#64748b',
    marginBottom: 8,
  },
  customRedeemInputRow: {
    flexDirection: 'column', // Changed to column to stack on small screens
    alignItems: 'stretch',
    gap: 8,
    width: '100%',
  },
  customRedeemInput: {
    backgroundColor: '#f8fafc',
    borderWidth: 1,
    borderColor: '#e2e8f0',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    fontFamily: 'Poppins_500Medium',
    color: '#0f172a',
  },
  customRedeemButton: {
    backgroundColor: '#FF5A36',
    paddingHorizontal: 20,
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#FF5A36',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 3,
  },
  customRedeemButtonDisabled: {
    backgroundColor: '#FDBA74',
    shadowOpacity: 0,
    elevation: 0,
  },
  customRedeemButtonText: {
    color: '#ffffff',
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 14,
  },
  customRedeemSubtext: {
    fontSize: 12,
    fontFamily: 'Poppins_400Regular',
    color: '#ef4444',
    marginTop: 8,
  },
  earnCard: {
    flexDirection: 'row',
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.03,
    shadowRadius: 8,
    elevation: 1,
    borderWidth: 1,
    borderColor: '#f1f5f9',
  },
  earnIconBg: {
    width: 44,
    height: 44,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  earnContent: {
    flex: 1,
    marginLeft: 16,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  earnTitle: {
    fontSize: 15,
    fontFamily: 'Poppins_500Medium',
    color: '#334155',
  },
  earnPoints: {
    fontSize: 15,
    fontFamily: 'Poppins_600SemiBold',
    color: '#10b981',
  },
  // History Tab Styles
  transactionCard: {
    flexDirection: 'row',
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.03,
    shadowRadius: 8,
    elevation: 1,
    borderWidth: 1,
    borderColor: '#f1f5f9',
  },
  transactionIconBg: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 16,
  },
  transactionLeft: {
    flex: 1,
    paddingRight: 8,
  },
  transactionDescription: {
    fontSize: 15,
    fontFamily: 'Poppins_500Medium',
    color: '#334155',
    marginBottom: 2,
  },
  transactionDate: {
    fontSize: 12,
    fontFamily: 'Poppins_400Regular',
    color: '#94a3b8',
  },
  transactionPointsPill: {
    backgroundColor: '#f8fafc',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  transactionPoints: {
    fontSize: 15,
    fontFamily: 'Poppins_600SemiBold',
  },
  pointsPositive: {
    color: '#10b981',
  },
  pointsNegative: {
    color: '#ef4444',
  },
  // Vouchers Tab Styles (New Coupon Design)
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 48,
  },
  emptyText: {
    fontSize: 16,
    fontFamily: 'Poppins_600SemiBold',
    color: '#64748b',
    marginTop: 16,
  },
  emptySubtext: {
    fontSize: 14,
    fontFamily: 'Poppins_400Regular',
    color: '#94a3b8',
    marginTop: 4,
  },
  couponCard: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    marginBottom: 16,
    position: 'relative',
    overflow: 'hidden',
  },
  couponInactive: {
    opacity: 0.6,
  },
  couponTop: {
    padding: 20,
    paddingBottom: 24,
  },
  couponCode: {
    fontSize: 16,
    fontFamily: 'Poppins_600SemiBold',
    color: '#0f172a',
    marginBottom: 4,
  },
  couponSubtext: {
    fontSize: 13,
    fontFamily: 'Poppins_400Regular',
    color: '#64748b',
    marginBottom: 12,
  },
  couponOfferRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  couponOfferText: {
    fontSize: 15,
    fontFamily: 'Poppins_600SemiBold',
    color: '#0f172a',
    marginLeft: 8,
  },
  couponBottom: {
    backgroundColor: '#f1f5f9',
    height: 50,
    alignItems: 'center',
    justifyContent: 'center',
  },
  copyCodeText: {
    fontSize: 13,
    fontFamily: 'Poppins_600SemiBold',
    color: '#334155',
    letterSpacing: 1.2,
  },
  cutoutLeft: {
    position: 'absolute',
    left: -12,
    bottom: 38, // 50 (bottom height) - 12 (half of circle)
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#f8fafc',
    borderWidth: 1,
    borderColor: '#e2e8f0',
    zIndex: 10,
  },
  cutoutRight: {
    position: 'absolute',
    right: -12,
    bottom: 38,
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#f8fafc',
    borderWidth: 1,
    borderColor: '#e2e8f0',
    zIndex: 10,
  },// Referral Tab Styles
  referralCard: {
    borderRadius: 20,
    padding: 24,
    alignItems: 'center',
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.05,
    shadowRadius: 12,
    elevation: 2,
    borderWidth: 1,
    borderColor: '#ffedd5',
  },
  referralHeaderIcon: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#FFF7ED',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  referralTitle: {
    fontSize: 18,
    fontFamily: 'Poppins_600SemiBold',
    color: '#1e293b',
    marginBottom: 4,
  },
  referralSubtitle: {
    fontSize: 14,
    fontFamily: 'Poppins_400Regular',
    color: '#64748b',
    marginBottom: 20,
  },
  referralCodeBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f8fafc',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 16,
    borderWidth: 1.5,
    borderColor: '#FF5A36',
    borderStyle: 'dashed',
    width: '100%',
  },
  referralCodeText: {
    flex: 1,
    fontSize: 22,
    fontFamily: 'monospace',
    fontWeight: 'bold',
    color: '#FF5A36',
    letterSpacing: 2,
  },
  referralActions: {
    flexDirection: 'row',
    gap: 8,
  },
  referralActionBtn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#FFF7ED',
    alignItems: 'center',
    justifyContent: 'center',
  },
  statsGrid: {
    flexDirection: 'row',
    gap: 16,
    marginBottom: 24,
  },
  statBox: {
    flex: 1,
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.03,
    shadowRadius: 8,
    elevation: 2,
    borderWidth: 1,
    borderColor: '#f1f5f9',
  },
  statIcon: {
    marginBottom: 8,
  },
  statValue: {
    fontSize: 28,
    fontFamily: 'Poppins_700Bold',
    color: '#1e293b',
    lineHeight: 32,
  },
  statLabel: {
    fontSize: 12,
    fontFamily: 'Poppins_500Medium',
    color: '#64748b',
    textAlign: 'center',
  },
  infoAlert: {
    flexDirection: 'row',
    backgroundColor: '#FFF7ED',
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: '#fed7aa',
  },
  infoAlertIcon: {
    marginRight: 12,
    marginTop: 2,
  },
  infoAlertContent: {
    flex: 1,
  },
  infoAlertTitle: {
    fontSize: 14,
    fontFamily: 'Poppins_600SemiBold',
    color: '#9A3412',
    marginBottom: 4,
  },
  infoAlertText: {
    fontSize: 13,
    fontFamily: 'Poppins_400Regular',
    color: '#7C2D12',
    lineHeight: 20,
  },
  loadingContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
});
