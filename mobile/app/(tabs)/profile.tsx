import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert, Image, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import * as SecureStore from 'expo-secure-store';
import { Ionicons } from '@expo/vector-icons';
import { colors, typography, spacing, borderRadius, shadows } from '../../constants/theme';
import Header from '../../components/Header';

const MOCK_USER = {
  name: 'Alex Johnson',
  email: 'alex.johnson@example.com',
  avatar: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=200&h=200&fit=crop',
};

const QUICK_ACTIONS = [
  { id: 'orders', icon: 'cube-outline', label: 'My Orders' },
  { id: 'wishlist', icon: 'heart-outline', label: 'Wishlist', route: '/wishlist' },
  { id: 'vouchers', icon: 'ticket-outline', label: 'Vouchers' },
];

const MENU_SECTIONS = [
  {
    title: 'Account Settings',
    items: [
      { id: 'personal', icon: 'person-outline', label: 'Personal Information' },
      { id: 'shipping', icon: 'location-outline', label: 'Shipping Addresses' },
      { id: 'payment', icon: 'card-outline', label: 'Payment Methods' },
    ]
  },
  {
    title: 'App Settings',
    items: [
      { id: 'notifications', icon: 'notifications-outline', label: 'Notifications' },
      { id: 'language', icon: 'globe-outline', label: 'Language' },
    ]
  },
  {
    title: 'Support',
    items: [
      { id: 'help', icon: 'help-circle-outline', label: 'Help Center' },
      { id: 'terms', icon: 'document-text-outline', label: 'Terms & Privacy' },
    ]
  }
];

export default function ProfileScreen() {
  const router = useRouter();

  const handleLogout = async () => {
    Alert.alert(
      'Log Out',
      'Are you sure you want to log out?',
      [
        {
          text: 'Cancel',
          style: 'cancel',
        },
        {
          text: 'Log Out',
          style: 'destructive',
          onPress: async () => {
            try {
              await SecureStore.deleteItemAsync('token');
              await SecureStore.deleteItemAsync('email');
              await SecureStore.deleteItemAsync('rememberMe');
              await SecureStore.deleteItemAsync('savedEmail');
              router.replace('/(auth)/login');
            } catch (error) {
              console.error('Error logging out:', error);
              Alert.alert('Error', 'Failed to log out. Please try again.');
            }
          },
        },
      ]
    );
  };

  return (
    <SafeAreaView style={styles.safeArea} edges={['top']}>
      <Header title="Profile" />
      
      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {/* User Header Block */}
        <View style={styles.userHeaderContainer}>
          <Image source={{ uri: MOCK_USER.avatar }} style={styles.avatar} />
          <View style={styles.userInfo}>
            <Text style={styles.userName}>{MOCK_USER.name}</Text>
            <Text style={styles.userEmail}>{MOCK_USER.email}</Text>
          </View>
          <TouchableOpacity style={styles.editButton} activeOpacity={0.7}>
            <Ionicons name="pencil" size={16} color={colors.primary} />
          </TouchableOpacity>
        </View>

        {/* Quick Action Grid */}
        <View style={styles.quickActionGrid}>
          {QUICK_ACTIONS.map(action => (
            <TouchableOpacity 
              key={action.id} 
              style={styles.actionCard}
              activeOpacity={0.7}
              onPress={() => action.route ? router.push(action.route as any) : null}
            >
              <View style={styles.actionIconContainer}>
                <Ionicons name={action.icon as any} size={24} color={colors.primary} />
              </View>
              <Text style={styles.actionLabel}>{action.label}</Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Menu Sections */}
        {MENU_SECTIONS.map(section => (
          <View key={section.title} style={styles.menuSection}>
            <Text style={styles.sectionTitle}>{section.title}</Text>
            <View style={styles.menuCard}>
              {section.items.map((item, index) => (
                <TouchableOpacity 
                  key={item.id} 
                  style={[styles.menuItem, index === section.items.length - 1 && styles.menuItemLast]}
                  activeOpacity={0.7}
                >
                  <View style={styles.menuItemIcon}>
                    <Ionicons name={item.icon as any} size={22} color={colors.gray600} />
                  </View>
                  <Text style={styles.menuItemLabel}>{item.label}</Text>
                  <Ionicons name="chevron-forward" size={20} color={colors.gray300} />
                </TouchableOpacity>
              ))}
            </View>
          </View>
        ))}

        {/* Logout Button */}
        <View style={styles.logoutSection}>
          <TouchableOpacity
            style={styles.logoutButton}
            onPress={handleLogout}
            activeOpacity={0.7}
          >
            <Ionicons name="log-out-outline" size={22} color={colors.errorRed} />
            <Text style={styles.logoutText}>Log Out</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: colors.gray50,
  },
  scrollContent: {
    paddingBottom: spacing['4xl'],
  },
  userHeaderContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.xl,
    backgroundColor: colors.white,
    borderBottomWidth: 1,
    borderBottomColor: colors.gray100,
  },
  avatar: {
    width: 64,
    height: 64,
    borderRadius: 32,
    marginRight: spacing.lg,
    backgroundColor: colors.gray100,
  },
  userInfo: {
    flex: 1,
  },
  userName: {
    fontSize: typography.fontSize.h2,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
    marginBottom: 4,
  },
  userEmail: {
    fontSize: typography.fontSize.body,
    color: colors.gray600,
  },
  editButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.primary + '1A', // Light primary tint
    justifyContent: 'center',
    alignItems: 'center',
  },
  quickActionGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.lg,
    marginTop: spacing.md,
  },
  actionCard: {
    flex: 1,
    backgroundColor: colors.white,
    marginHorizontal: spacing.xs,
    paddingVertical: spacing.md,
    borderRadius: borderRadius.medium,
    alignItems: 'center',
    ...shadows.card,
  },
  actionIconContainer: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.gray50,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  actionLabel: {
    fontSize: typography.fontSize.caption,
    fontWeight: typography.fontWeight.medium,
    color: colors.gray900,
  },
  menuSection: {
    marginTop: spacing.lg,
    paddingHorizontal: spacing.lg,
  },
  sectionTitle: {
    fontSize: typography.fontSize.bodyLarge,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
    marginBottom: spacing.sm,
    marginLeft: spacing.xs,
  },
  menuCard: {
    backgroundColor: colors.white,
    borderRadius: borderRadius.medium,
    overflow: 'hidden',
    ...shadows.card,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    borderBottomWidth: 1,
    borderBottomColor: colors.gray100,
  },
  menuItemLast: {
    borderBottomWidth: 0,
  },
  menuItemIcon: {
    width: 32,
    height: 32,
    borderRadius: 8,
    backgroundColor: colors.gray50,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  menuItemLabel: {
    flex: 1,
    fontSize: typography.fontSize.body,
    fontWeight: typography.fontWeight.medium,
    color: colors.gray900,
  },
  logoutSection: {
    marginTop: spacing.xl,
    paddingHorizontal: spacing.lg,
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.white,
    paddingVertical: spacing.md,
    borderRadius: borderRadius.medium,
    borderWidth: 1,
    borderColor: colors.errorRed,
    gap: spacing.sm,
  },
  logoutText: {
    fontSize: typography.fontSize.bodyLarge,
    fontWeight: typography.fontWeight.semibold,
    color: colors.errorRed,
  },
});
