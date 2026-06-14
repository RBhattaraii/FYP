/**
 * API Configuration
 * Automatically detects the backend URL based on Expo's manifest
 */

import Constants from 'expo-constants';

// Get the local network URL from Expo's debug server
// This automatically uses the same IP as your Expo dev server
const getApiUrl = () => {
  // In development, use Expo's debugger host IP
  const debuggerHost = Constants.expoConfig?.hostUri;
  
  if (debuggerHost) {
    // Extract IP address from debuggerHost (format: "192.168.x.x:8081")
    const ip = debuggerHost.split(':')[0];
    return `http://${ip}:8000`;
  }
  
  // Fallback for production or if debuggerHost is not available
  return "http://192.168.50.1:8000";
};

export const API_URL = getApiUrl();

console.log('🔗 API URL:', API_URL);
