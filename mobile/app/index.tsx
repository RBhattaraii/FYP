import { useEffect, useState } from 'react';
import { Redirect } from 'expo-router';
import * as SecureStore from 'expo-secure-store';

export default function Index() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = await SecureStore.getItemAsync('token');
      setIsAuthenticated(!!token);
    } catch (error) {
      setIsAuthenticated(false);
    }
  };

  // Show nothing while checking auth
  if (isAuthenticated === null) {
    return null;
  }

  // Redirect based on auth status
  return <Redirect href={isAuthenticated ? "/(tabs)/home" : "/(auth)/login"} />;
}
