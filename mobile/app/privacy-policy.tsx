import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Stack, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

export default function PrivacyPolicyScreen() {
  const router = useRouter();
  
  const handleBack = () => {
    if (router.canGoBack()) {
      router.back();
    } else {
      router.replace('/(tabs)/profile');
    }
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <Stack.Screen options={{ headerShown: false }} />
      
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity style={styles.headerIcon} onPress={handleBack}>
          <Ionicons name="arrow-back" size={24} color="#111111" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Privacy Policy</Text>
        <View style={styles.headerPlaceholder} />
      </View>

      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        
        <Text style={styles.sectionTitle}>Cancelation Policy</Text>
        <Text style={styles.paragraph}>
          You can cancel your order at any time before it is dispatched from our warehouse. To cancel an order, simply go to your Orders section, select the order, and tap the Cancel button.
        </Text>
        <Text style={styles.paragraph}>
          If your order has already been dispatched, you will not be able to cancel it directly. However, you can refuse the delivery or return the item within our standard return window once you receive it. Refunds for canceled orders will be processed within 3-5 business days to your original payment method.
        </Text>

        <Text style={styles.sectionTitle}>Terms & Condition</Text>
        <Text style={styles.paragraph}>
          Welcome to PricePilot. By accessing and using our application, you agree to comply with and be bound by the following terms and conditions of use, which together with our privacy policy govern our relationship with you in relation to this app.
        </Text>
        <Text style={styles.paragraph}>
          The content of the pages of this app is for your general information and use only. It is subject to change without notice. We provide price comparisons and historical data based on third-party retailers. We are not responsible for pricing errors, out-of-stock items, or changes made by the respective stores.
        </Text>
        <Text style={styles.paragraph}>
          Unauthorized use of this application may give rise to a claim for damages and/or be a criminal offense. You may not use the platform for any illegal or unauthorized purpose, including but not limited to violating any intellectual property rights or distributing malicious software.
        </Text>
        <Text style={styles.paragraph}>
          Our app features a points and voucher system. Vouchers are subject to expiration dates and minimum spend requirements as specified. They are non-transferable and cannot be exchanged for cash. We reserve the right to modify or cancel the rewards program at any time.
        </Text>
        <Text style={styles.paragraph}>
          By creating an account, you agree to provide accurate information and are responsible for maintaining the confidentiality of your account password. If you choose to delete your account, all associated data, including price alerts, wishlists, and order history, will be permanently removed from our systems in accordance with data protection laws.
        </Text>

        <View style={{ height: 40 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
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
    backgroundColor: '#FAFAFA',
  },
  headerIcon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    borderWidth: 1,
    borderColor: '#EAEAEA',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
  },
  headerTitle: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 18,
    color: '#111111',
  },
  headerPlaceholder: {
    width: 44,
  },
  content: {
    paddingHorizontal: 24,
    paddingTop: 16,
    paddingBottom: 40,
  },
  sectionTitle: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 17,
    color: '#6E4B3A',
    marginBottom: 12,
    marginTop: 8,
  },
  paragraph: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 14,
    color: '#666666',
    lineHeight: 22,
    marginBottom: 16,
  },
});
