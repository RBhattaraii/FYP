import { useState, useEffect } from 'react';
import { authStorage } from '../lib/authStorage';
import { API_BASE_URL } from '../lib/config';

interface User {
  email: string;
  role: string;
  full_name?: string;
  phone?: string;
  user_id?: string;
}

interface AdminLoginResponse {
  token: string;
  token_type: string;
  user_id: string;
  email: string;
  role: string;
  full_name: string;
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUser();
  }, []);

  const loadUser = async () => {
    try {
      const token = await authStorage.getItemAsync('token');
      if (!token) {
        setLoading(false);
        return;
      }

      // Load user data from storage
      const email = await authStorage.getItemAsync('email');
      const role = await authStorage.getItemAsync('role');
      const full_name = await authStorage.getItemAsync('full_name');
      const phone = await authStorage.getItemAsync('phone');

      if (email && role) {
        const userData: User = {
          email,
          role,
          full_name: full_name || undefined,
          phone: phone || undefined,
        };
        
        setUser(userData);
        setIsAdmin(role === 'admin');
      }
    } catch (error) {
      console.error('Failed to load user:', error);
    } finally {
      setLoading(false);
    }
  };

  const loginAdmin = async (email: string, password: string): Promise<AdminLoginResponse> => {
    const response = await fetch(`${API_BASE_URL}/auth/admin-login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data: AdminLoginResponse = await response.json();
    
    // Store admin token and info in expo-secure-store
    await authStorage.setItemAsync('token', data.token);
    await authStorage.setItemAsync('email', data.email);
    await authStorage.setItemAsync('role', data.role);
    
    if (data.full_name) {
      await authStorage.setItemAsync('full_name', data.full_name);
    }
    
    // Update state
    const userData: User = {
      email: data.email,
      role: data.role,
      full_name: data.full_name,
      user_id: data.user_id,
    };
    
    setUser(userData);
    setIsAdmin(true);
    
    return data;
  };

  return { user, isAdmin, loading, loadUser, loginAdmin };
}
