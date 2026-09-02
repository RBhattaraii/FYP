import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { Stack, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { colors, typography, spacing, borderRadius } from '../constants/theme';
import { validateVoucher, redeemCheckoutVoucher } from '../services/api';
import { authStorage } from '../lib/authStorage';

export default function MockCheckoutScreen() {
  const router = useRouter();
  const [voucherCode, setVoucherCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [redeeming, setRedeeming] = useState(false);
  
  // Mock order details
  const subtotal = 10500;
  const shipping = 150;
  const [discountAmount, setDiscountAmount] = useState(0);
  const [voucherApplied, setVoucherApplied] = useState(false);
  const [voucherMessage, setVoucherMessage] = useState('');
  const [isVoucherValid, setIsVoucherValid] = useState(false);

  const currentTotal = subtotal + shipping - discountAmount;

  const handleApplyVoucher = async () => {
    if (!voucherCode) return;
    
    try {
      setLoading(true);
      const token = await authStorage.getItemAsync('token');
      if (!token) throw new Error('Not authenticated');

      const response = await validateVoucher(token, {
        voucher_code: voucherCode.toUpperCase(),
        order_total: subtotal
      });

      setVoucherMessage(response.message);
      setIsVoucherValid(response.is_valid);
      
      if (response.is_valid) {
        setDiscountAmount(parseFloat(response.discount_amount));
        setVoucherApplied(true);
      } else {
        setDiscountAmount(0);
        setVoucherApplied(false);
      }
    } catch (error: any) {
      setVoucherMessage(error.message);
      setIsVoucherValid(false);
      setDiscountAmount(0);
      setVoucherApplied(false);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveVoucher = () => {
    setVoucherCode('');
    setDiscountAmount(0);
    setVoucherApplied(false);
    setVoucherMessage('');
  };

  const handleCompleteOrder = async () => {
    if (voucherApplied && voucherCode) {
      try {
        setRedeeming(true);
        const token = await authStorage.getItemAsync('token');
        if (!token) throw new Error('Not authenticated');

        await redeemCheckoutVoucher(token, {
          voucher_code: voucherCode.toUpperCase(),
          order_total: subtotal
        });
        
        Alert.alert('Order Placed!', `Your mock order was successfully placed and the voucher has been redeemed.`, [
          { text: 'Awesome!', onPress: () => router.push('/(tabs)/profile') }
        ]);
      } catch (error: any) {
        Alert.alert('Error', error.message);
      } finally {
        setRedeeming(false);
      }
    } else {
      Alert.alert('Order Placed!', `Your mock order was successfully placed without a voucher.`, [
        { text: 'Awesome!', onPress: () => router.push('/(tabs)/profile') }
      ]);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Stack.Screen options={{ title: 'Checkout (Mock)', headerShadowVisible: false }} />
      
      <View style={styles.content}>
        <Text style={styles.headerText}>Order Summary</Text>
        
        <View style={styles.card}>
          <View style={styles.productRow}>
            <View style={styles.productIcon}>
              <Ionicons name="headset-outline" size={24} color={colors.primary} />
            </View>
            <View style={styles.productDetails}>
              <Text style={styles.productName}>Sony WH-1000XM4 Headphones</Text>
              <Text style={styles.productStore}>Sold by Daraz</Text>
            </View>
            <Text style={styles.productPrice}>Rs 10,500</Text>
          </View>
        </View>

        <Text style={styles.sectionTitle}>Promo Code</Text>
        <View style={styles.promoContainer}>
          <TextInput
            style={styles.promoInput}
            value={voucherCode}
            onChangeText={setVoucherCode}
            placeholder="Enter voucher code"
            autoCapitalize="characters"
            editable={!voucherApplied}
          />
          {voucherApplied ? (
            <TouchableOpacity style={styles.removeButton} onPress={handleRemoveVoucher}>
              <Text style={styles.removeButtonText}>Remove</Text>
            </TouchableOpacity>
          ) : (
            <TouchableOpacity 
              style={[styles.applyButton, (!voucherCode || loading) && styles.buttonDisabled]} 
              onPress={handleApplyVoucher}
              disabled={!voucherCode || loading}
            >
              {loading ? (
                <ActivityIndicator size="small" color="#fff" />
              ) : (
                <Text style={styles.applyButtonText}>Apply</Text>
              )}
            </TouchableOpacity>
          )}
        </View>

        {voucherMessage ? (
          <Text style={[styles.messageText, isVoucherValid ? styles.messageSuccess : styles.messageError]}>
            {voucherMessage}
          </Text>
        ) : null}

        <View style={styles.totalsCard}>
          <View style={styles.totalsRow}>
            <Text style={styles.totalsLabel}>Subtotal</Text>
            <Text style={styles.totalsValue}>Rs {subtotal.toLocaleString()}</Text>
          </View>
          <View style={styles.totalsRow}>
            <Text style={styles.totalsLabel}>Shipping</Text>
            <Text style={styles.totalsValue}>Rs {shipping.toLocaleString()}</Text>
          </View>
          {voucherApplied && (
            <View style={styles.totalsRow}>
              <Text style={[styles.totalsLabel, styles.discountText]}>Discount ({voucherCode})</Text>
              <Text style={[styles.totalsValue, styles.discountText]}>- Rs {discountAmount.toLocaleString()}</Text>
            </View>
          )}
          <View style={styles.divider} />
          <View style={styles.totalsRow}>
            <Text style={styles.grandTotalLabel}>Total</Text>
            <Text style={styles.grandTotalValue}>Rs {currentTotal.toLocaleString()}</Text>
          </View>
        </View>

        <TouchableOpacity 
          style={styles.checkoutButton}
          onPress={handleCompleteOrder}
          disabled={redeeming}
        >
          {redeeming ? (
            <ActivityIndicator size="small" color="#fff" />
          ) : (
            <Text style={styles.checkoutButtonText}>Place Mock Order</Text>
          )}
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.gray50,
  },
  content: {
    padding: spacing.lg,
  },
  headerText: {
    fontSize: typography.fontSize.h2,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
    marginBottom: spacing.md,
  },
  sectionTitle: {
    fontSize: typography.fontSize.bodyLarge,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
    marginTop: spacing.xl,
    marginBottom: spacing.md,
  },
  card: {
    backgroundColor: colors.white,
    borderRadius: borderRadius.large,
    padding: spacing.md,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  productRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  productIcon: {
    width: 48,
    height: 48,
    backgroundColor: colors.gray50,
    borderRadius: borderRadius.medium,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.md,
  },
  productDetails: {
    flex: 1,
  },
  productName: {
    fontSize: typography.fontSize.small,
    fontWeight: typography.fontWeight.medium,
    color: colors.gray900,
    marginBottom: 4,
  },
  productStore: {
    fontSize: typography.fontSize.caption,
    color: colors.gray500,
  },
  productPrice: {
    fontSize: typography.fontSize.small,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
  },
  promoContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  promoInput: {
    flex: 1,
    backgroundColor: colors.white,
    borderWidth: 1,
    borderColor: colors.gray200,
    borderRadius: borderRadius.medium,
    padding: spacing.md,
    fontSize: typography.fontSize.bodyLarge,
    color: colors.gray900,
    marginRight: spacing.sm,
  },
  applyButton: {
    backgroundColor: colors.primary,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    borderRadius: borderRadius.medium,
    justifyContent: 'center',
    alignItems: 'center',
  },
  removeButton: {
    backgroundColor: colors.errorRed,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    borderRadius: borderRadius.medium,
    justifyContent: 'center',
    alignItems: 'center',
  },
  applyButtonText: {
    color: '#fff',
    fontWeight: typography.fontWeight.bold,
    fontSize: typography.fontSize.small,
  },
  removeButtonText: {
    color: '#fff',
    fontWeight: typography.fontWeight.bold,
    fontSize: typography.fontSize.small,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  messageText: {
    marginTop: spacing.sm,
    fontSize: typography.fontSize.small,
  },
  messageSuccess: {
    color: colors.successGreen,
  },
  messageError: {
    color: colors.errorRed,
  },
  totalsCard: {
    backgroundColor: colors.white,
    borderRadius: borderRadius.large,
    padding: spacing.lg,
    marginTop: spacing.xl,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  totalsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.sm,
  },
  totalsLabel: {
    fontSize: typography.fontSize.small,
    color: colors.gray500,
  },
  totalsValue: {
    fontSize: typography.fontSize.small,
    color: colors.gray900,
    fontWeight: typography.fontWeight.medium,
  },
  discountText: {
    color: colors.successGreen,
  },
  divider: {
    height: 1,
    backgroundColor: colors.gray200,
    marginVertical: spacing.md,
  },
  grandTotalLabel: {
    fontSize: typography.fontSize.bodyLarge,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
  },
  grandTotalValue: {
    fontSize: typography.fontSize.h2,
    fontWeight: typography.fontWeight.bold,
    color: colors.primary,
  },
  checkoutButton: {
    backgroundColor: colors.primary,
    padding: spacing.lg,
    borderRadius: borderRadius.large,
    alignItems: 'center',
    marginTop: spacing.xl,
  },
  checkoutButtonText: {
    color: '#fff',
    fontSize: typography.fontSize.button,
    fontWeight: typography.fontWeight.bold,
  }
});
