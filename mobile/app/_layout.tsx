import { Stack } from 'expo-router';
import { FavoritesProvider } from '../context/FavoritesContext';
import { useFonts, Poppins_400Regular, Poppins_500Medium, Poppins_600SemiBold, Poppins_700Bold, Poppins_800ExtraBold } from '@expo-google-fonts/poppins';
import * as SplashScreen from 'expo-splash-screen';
import { useEffect, useRef, useState } from 'react';
import type * as NotificationsType from 'expo-notifications';
import { Platform } from 'react-native';
import Constants from 'expo-constants';
import { registerForPushNotificationsAsync } from '../services/notifications';

const isExpoGoAndroid = Platform.OS === 'android' && Constants.appOwnership === 'expo';
let Notifications: typeof NotificationsType | null = null;
if (!isExpoGoAndroid) {
  try {
    Notifications = require('expo-notifications');
  } catch (e) {
    console.warn("Could not require expo-notifications", e);
  }
}

SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const [loaded, error] = useFonts({
    Poppins_400Regular,
    Poppins_500Medium,
    Poppins_600SemiBold,
    Poppins_700Bold,
    Poppins_800ExtraBold,
  });

  const [expoPushToken, setExpoPushToken] = useState('');
  const notificationListener = useRef<NotificationsType.Subscription | null>(null);
  const responseListener = useRef<NotificationsType.Subscription | null>(null);

  useEffect(() => {
    if (loaded || error) {
      SplashScreen.hideAsync();
    }
  }, [loaded, error]);

  useEffect(() => {
    registerForPushNotificationsAsync().then(token => {
      if (token) setExpoPushToken(token);
    });

    if (Notifications) {
      notificationListener.current = Notifications.addNotificationReceivedListener(notification => {
        // Handle notification received while app is foregrounded
      });

      responseListener.current = Notifications.addNotificationResponseReceivedListener(response => {
        // Handle user tapping on notification
      });
    }

    return () => {
      if (notificationListener.current) {
        notificationListener.current.remove();
      }
      if (responseListener.current) {
        responseListener.current.remove();
      }
    };
  }, []);

  if (!loaded && !error) {
    return null;
  }

  return (
    <FavoritesProvider>
      <Stack>
        <Stack.Screen name="(auth)" options={{ headerShown: false }} />
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen name="product/[id]" options={{ title: 'Product Details' }} />
        <Stack.Screen name="category/[name]" options={{ headerShown: false }} />
        <Stack.Screen name="search" options={{ headerShown: false, animation: 'fade' }} />
        <Stack.Screen name="search-results" options={{ headerShown: false, animation: 'fade' }} />
        <Stack.Screen name="personal-info" options={{ headerShown: false }} />
        <Stack.Screen name="notifications" options={{ headerShown: false }} />
        <Stack.Screen name="points" options={{ headerShown: false }} />
        <Stack.Screen name="price-alerts" options={{ headerShown: false }} />
        <Stack.Screen name="preferred-stores" options={{ headerShown: false }} />
      </Stack>
    </FavoritesProvider>
  );
}
