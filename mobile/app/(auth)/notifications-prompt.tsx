import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Dimensions, ActivityIndicator, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter, Stack } from 'expo-router';
import { authStorage } from '../../lib/authStorage';
import type * as NotificationsType from 'expo-notifications';
import Constants from 'expo-constants';
import { registerForPushNotificationsAsync } from '../../services/notifications';

const { width } = Dimensions.get('window');

const isExpoGoAndroid = Platform.OS === 'android' && Constants.appOwnership === 'expo';
let Notifications: typeof NotificationsType | null = null;
if (!isExpoGoAndroid) {
  try {
    Notifications = require('expo-notifications');
  } catch (e) {
    console.warn("Could not require expo-notifications", e);
  }
}

export default function NotificationsPromptScreen() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const handleAllow = async () => {
    setLoading(true);
    try {
      const token = await registerForPushNotificationsAsync();
      // Wait for user to grant or deny permissions
      let status = 'granted';
      if (Notifications) {
        const { status: currentStatus } = await Notifications.getPermissionsAsync();
        status = currentStatus;
      }
      
      if (status === 'granted') {
        // They accepted
      } else {
        // They denied the native prompt
      }
      
      // Regardless of the OS outcome, they made a choice on our screen.
      await authStorage.setItemAsync('notifications_opt_in', 'true');
      
      const role = await authStorage.getItemAsync('role');
      if (role === 'admin') {
        router.replace('/(tabs)/admin');
      } else {
        router.replace('/(tabs)/home');
      }
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeny = async () => {
    // They selected "Don't Allow". We mark it as completed so they aren't asked again.
    await authStorage.setItemAsync('notifications_opt_in', 'true');
    const role = await authStorage.getItemAsync('role');
    if (role === 'admin') {
      router.replace('/(tabs)/admin');
    } else {
      router.replace('/(tabs)/home');
    }
  };

  const handleSkip = async () => {
    // They skipped. We DON'T set notifications_opt_in, so they will be asked again next time.
    const role = await authStorage.getItemAsync('role');
    if (role === 'admin') {
      router.replace('/(tabs)/admin');
    } else {
      router.replace('/(tabs)/home');
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <Stack.Screen options={{ headerShown: false }} />
      <View style={styles.header}>
        <TouchableOpacity onPress={handleSkip} style={styles.skipButton}>
          <Text style={styles.skipText}>Skip</Text>
        </TouchableOpacity>
      </View>
      <View style={styles.container}>
        <View style={styles.content}>
          
          <View style={styles.iconCircle}>
            <Ionicons name="notifications" size={48} color="#704F38" />
          </View>
          
          <Text style={styles.title}>Enable Notifications?</Text>
          
          <Text style={styles.subtitle}>
            We need to send you notifications in order to keep you updated on price drops, order status, and nearby deals.
          </Text>

        </View>

        <View style={styles.buttonContainer}>
          <TouchableOpacity 
            style={styles.primaryButton} 
            onPress={handleAllow}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#FFFFFF" />
            ) : (
              <Text style={styles.primaryButtonText}>Allow Notifications</Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.secondaryButton} 
            onPress={handleDeny}
            disabled={loading}
          >
            <Text style={styles.secondaryButtonText}>Don't Allow</Text>
          </TouchableOpacity>
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    paddingHorizontal: 24,
    paddingTop: 20,
    width: '100%',
  },
  skipButton: {
    padding: 8,
  },
  skipText: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 16,
    color: '#704F38',
  },
  container: {
    flex: 1,
    justifyContent: 'space-between',
    paddingHorizontal: 24,
    paddingTop: 80,
    paddingBottom: 40,
  },
  content: {
    alignItems: 'center',
  },
  iconCircle: {
    width: 140,
    height: 140,
    borderRadius: 70,
    backgroundColor: '#F5F5F5',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 40,
  },
  title: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 24,
    color: '#111111',
    textAlign: 'center',
    marginBottom: 16,
  },
  subtitle: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 14,
    color: '#757575',
    textAlign: 'center',
    lineHeight: 22,
    paddingHorizontal: 10,
  },
  buttonContainer: {
    width: '100%',
    gap: 16,
  },
  primaryButton: {
    backgroundColor: '#704F38',
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    width: '100%',
  },
  primaryButtonText: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 16,
    color: '#FFFFFF',
  },
  secondaryButton: {
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    width: '100%',
  },
  secondaryButtonText: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 16,
    color: '#704F38',
  },
});
