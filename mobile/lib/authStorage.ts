import { Platform } from 'react-native';
import * as SecureStore from 'expo-secure-store';

const isWeb = Platform.OS === 'web';

const webStorage = {
  async getItemAsync(key: string) {
    try {
      return globalThis.localStorage?.getItem(key) ?? null;
    } catch {
      return null;
    }
  },
  async setItemAsync(key: string, value: string) {
    try {
      globalThis.localStorage?.setItem(key, value);
    } catch {
      return;
    }
  },
  async deleteItemAsync(key: string) {
    try {
      globalThis.localStorage?.removeItem(key);
    } catch {
      return;
    }
  },
};

export const authStorage = {
  getItemAsync(key: string) {
    return isWeb ? webStorage.getItemAsync(key) : SecureStore.getItemAsync(key);
  },
  setItemAsync(key: string, value: string) {
    return isWeb ? webStorage.setItemAsync(key, value) : SecureStore.setItemAsync(key, value);
  },
  deleteItemAsync(key: string) {
    return isWeb ? webStorage.deleteItemAsync(key) : SecureStore.deleteItemAsync(key);
  },
};