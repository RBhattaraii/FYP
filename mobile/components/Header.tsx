import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';

interface HeaderProps {
  hasUnreadNotifications?: boolean;
  onNotificationPress?: () => void;
  onProfilePress?: () => void;
  balance?: number;
}

export default function Header({ 
  hasUnreadNotifications = true,
  onNotificationPress,
  onProfilePress,
  balance
}: HeaderProps) {
  const router = useRouter();

  const handleProfilePress = () => {
    if (onProfilePress) {
      onProfilePress();
    } else {
      router.push('/(tabs)/profile');
    }
  };

  return (
    <View style={styles.container}>
      {/* Points Balance Widget */}
      <TouchableOpacity 
        style={styles.balanceContainer} 
        onPress={handleProfilePress} 
        activeOpacity={0.8}
      >
        <View style={styles.walletIconWrapper}>
          <Ionicons name="wallet" size={20} color="#704F38" />
        </View>
        <View style={styles.balanceTextWrapper}>
          <Text style={styles.balanceLabel}>Your balance</Text>
          <Text style={styles.balanceValue}>{balance !== undefined ? `${balance.toLocaleString()} pts` : 'Loading...'}</Text>
        </View>
      </TouchableOpacity>

      {/* Notification Bell */}
      <TouchableOpacity 
        style={styles.bellButton} 
        onPress={onNotificationPress} 
        activeOpacity={0.7}
      >
        <Ionicons name="notifications-outline" size={22} color="#111111" />
        {hasUnreadNotifications && <View style={styles.notificationDot} />}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 24,
    paddingTop: 16,
    paddingBottom: 8,
    backgroundColor: 'transparent',
  },
  balanceContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  walletIconWrapper: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#F5EBE1', // Light brown theme
    justifyContent: 'center',
    alignItems: 'center',
  },
  balanceTextWrapper: {
    justifyContent: 'center',
  },
  balanceLabel: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 11,
    color: '#757575',
    marginBottom: -2,
  },
  balanceValue: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 16,
    color: '#111111',
  },
  locationLabel: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 12,
    color: '#9E9E9E',
    marginBottom: 2,
  },
  locationRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  locationText: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 16,
    color: '#111111',
  },
  bellButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#F5F5F5',
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },
  notificationDot: {
    position: 'absolute',
    top: 10,
    right: 12,
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#EF4444', // Red dot for unread
    borderWidth: 1,
    borderColor: '#F5F5F5',
  },
});
