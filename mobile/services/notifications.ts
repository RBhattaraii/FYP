import * as Device from 'expo-device';
import type * as NotificationsType from 'expo-notifications';
import Constants from 'expo-constants';
import { Platform } from 'react-native';
import { authStorage } from '../lib/authStorage';
import { API_URL } from '../constants/api';

const isExpoGoAndroid = Platform.OS === 'android' && Constants.appOwnership === 'expo';
let Notifications: typeof NotificationsType | null = null;
if (!isExpoGoAndroid) {
  try {
    Notifications = require('expo-notifications');
    Notifications?.setNotificationHandler({
      handleNotification: async () => ({
        shouldShowAlert: true,
        shouldPlaySound: true,
        shouldSetBadge: false,
        shouldShowBanner: true,
        shouldShowList: true,
      }),
    });
  } catch (e) {
    console.warn("Could not require expo-notifications", e);
  }
}

export async function registerForPushNotificationsAsync() {
  let token;

  if (Platform.OS === 'android' && Notifications) {
    await Notifications.setNotificationChannelAsync('default', {
      name: 'default',
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: '#FF231F7C',
    });
  }

  if (Device.isDevice && Notifications) {
    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;
    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }
    if (finalStatus !== 'granted') {
      console.log('Failed to get push token for push notification!');
      return;
    }
    try {
      // Expo Go removed Android Push Notifications in SDK 53
      if (Platform.OS === 'android' && Constants.appOwnership === 'expo') {
        console.log('Skipping push token fetch: Not supported in Expo Go on Android.');
        return 'mock-token-expo-go-android';
      }

      const projectId =
        Constants?.expoConfig?.extra?.eas?.projectId ?? Constants?.easConfig?.projectId;
      
      if (!projectId) {
        // Fallback for local development if EAS is not configured
        token = (await Notifications.getExpoPushTokenAsync()).data;
      } else {
        token = (
          await Notifications.getExpoPushTokenAsync({
            projectId,
          })
        ).data;
      }
      
      // Save token to backend
      await savePushTokenToBackend(token);
    } catch (e: unknown) {
      console.log('Error getting push token', e);
    }
  } else {
    console.log('Must use physical device for Push Notifications');
  }

  return token;
}

export async function savePushTokenToBackend(pushToken: string) {
  try {
    const token = await authStorage.getItemAsync('token');
    if (!token) return;

    await fetch(`${API_URL}/auth/push-token`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ token: pushToken }),
    });
    console.log("Push token saved to backend");
  } catch (error) {
    console.error("Error saving push token to backend", error);
  }
}

export interface PriceAlert {
  id?: number;
  product_id: number;
  target_price: number;
  product_title: string;
  store_name?: string;
  product_url?: string;
  current_price: number;
  created_at: string;
  product_image_url: string;
  is_active: boolean;
  triggered_at?: string;
}

export async function createPriceAlert(token: string, payload: Partial<PriceAlert>): Promise<any> {
  const response = await fetch(`${API_URL}/notifications/alerts`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
  
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to create price alert');
  }
  
  return await response.json();
}

export async function getPriceAlerts(token: string): Promise<any> {
  const response = await fetch(`${API_URL}/notifications/alerts`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch price alerts');
  }
  
  return await response.json();
}

export async function deletePriceAlert(token: string, alertId: number): Promise<any> {
  const response = await fetch(`${API_URL}/notifications/alerts/${alertId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  
  if (!response.ok) {
    throw new Error('Failed to delete price alert');
  }
  
  return await response.json();
}

export interface Notification {
  id: string;
  user_id: string;
  notification_type: string;
  title: string;
  message: string;
  is_read: boolean;
  product_id?: string;
  created_at: string;
}

export async function getNotifications(token: string): Promise<{ notifications: Notification[]; unread_count: number }> {
  return { notifications: [], unread_count: 0 };
}

export async function markNotificationRead(token: string, id: string): Promise<void> {}

export async function markAllNotificationsRead(token: string): Promise<void> {}

export async function getLocalNotifications(): Promise<Notification[]> {
  return [];
}

export async function markLocalNotificationRead(id: string): Promise<void> {}

export async function markAllLocalNotificationsRead(): Promise<void> {}

export async function addLocalNotification(title: string, message: string, type: string, productId?: number) {}
