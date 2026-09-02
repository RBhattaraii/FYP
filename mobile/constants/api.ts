/**
 * API Configuration
 * Automatically detects the backend URL based on Expo's manifest
 * Handles Android emulator (10.0.2.2) vs physical device (LAN IP)
 */

import Constants from 'expo-constants';
import { Platform } from 'react-native';

// Get the local network URL from Expo's debug server
// This automatically uses the same IP as your Expo dev server
const getApiUrl = () => {
  const overrideUrl =
    (Constants.expoConfig as any)?.extra?.API_URL ||
    (typeof process !== 'undefined' ? process.env?.EXPO_PUBLIC_API_URL : undefined);

  if (overrideUrl) {
    return overrideUrl;
  }

  const debuggerHost = Constants.expoConfig?.hostUri || Constants.manifest?.debuggerHost;
  const getHostFromDebug = (hostUri?: string) => {
    if (!hostUri || typeof hostUri !== 'string') {
      return null;
    }
    return hostUri.split(':')[0].replace('localhost', '127.0.0.1');
  };

  if (Platform.OS === 'web') {
    const hostname = typeof window !== 'undefined' ? window.location.hostname : 'localhost';
    const webHost = hostname === 'localhost' || hostname === '127.0.0.1' ? hostname : 'localhost';
    console.warn(`Using web API host ${webHost} for backend requests. If your backend runs elsewhere, set EXPO_PUBLIC_API_URL.`);
    return `http://${webHost}:8000`;
  }

  const hostIp = getHostFromDebug(debuggerHost);
  if (hostIp) {
    if (Platform.OS === 'android' && (hostIp === '127.0.0.1' || hostIp === 'localhost')) {
      return 'http://10.0.2.2:8000';
    }
    return `http://${hostIp}:8000`;
  }

  if (Platform.OS === 'android') {
    return 'http://10.0.2.2:8000';
  }

  // Force local IP for physical devices testing Expo
  return 'http://192.168.1.94:8000';
};

export const API_URL = getApiUrl();

/**
 * Fetch with timeout - prevents requests from spinning forever
 * @param url - The URL to fetch
 * @param options - Fetch options
 * @param timeoutMs - Timeout in milliseconds (default: 10 seconds)
 */
export const fetchWithTimeout = async (
  url: string,
  options: RequestInit = {},
  timeoutMs: number = 10000
): Promise<Response> => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    return response;
  } catch (error: any) {
    if (error.name === 'AbortError') {
      throw new Error(`Request timed out after ${timeoutMs}ms while calling ${url}. Make sure your backend server is running.`);
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
};

console.log('🔗 API URL:', API_URL);
console.log('📱 Platform:', Platform.OS);
