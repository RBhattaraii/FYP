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
  // Android emulator uses 10.0.2.2 to reach host machine's localhost
  // Check if we're on Android and if the debuggerHost is localhost/127.0.0.1
  const debuggerHost = Constants.expoConfig?.hostUri;

  if (debuggerHost) {
    // Extract IP address from debuggerHost (format: "192.168.x.x:8081")
    const ip = debuggerHost.split(':')[0];

    // If running on Android emulator, the LAN IP won't work.
    // Use 10.0.2.2 which is the special alias for host machine's localhost.
    if (Platform.OS === 'android' && (ip === '127.0.0.1' || ip === 'localhost')) {
      return 'http://10.0.2.2:8000';
    }

    return `http://${ip}:8000`;
  }

  // If no debuggerHost is available (common in Android emulator builds),
  // use the emulator-specific address on Android, LAN IP otherwise
  if (Platform.OS === 'android') {
    return 'http://10.0.2.2:8000';
  }

  // Fallback for production or if debuggerHost is not available
  return "http://192.168.50.1:8000";
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
      throw new Error('Request timed out. Make sure your backend server is running.');
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
};

console.log('🔗 API URL:', API_URL);
console.log('📱 Platform:', Platform.OS);
