import { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  ScrollView,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, Stack } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import Svg, { Path } from 'react-native-svg';
import { API_URL, fetchWithTimeout } from '../../constants/api';
import { authStorage } from '../../lib/authStorage';

const GoogleLogo = () => (
  <Svg width="28" height="28" viewBox="0 0 24 24">
    <Path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
    <Path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
    <Path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
    <Path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
  </Svg>
);

export default function LoginScreen() {
  const router = useRouter();
  
  // State for form inputs
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  
  // State for validation errors
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  
  // State for API call
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState('');

  // Email validation regex
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

  // Load remember me state on mount
  useEffect(() => {
    const loadRememberedUser = async () => {
      try {
        const savedRememberMe = await authStorage.getItemAsync('rememberMe');
        if (savedRememberMe === 'true') {
          setRememberMe(true);
          const savedEmail = await authStorage.getItemAsync('savedEmail');
          if (savedEmail) {
            setEmail(savedEmail);
          }
        }
      } catch (e) {
        console.log('Error loading saved credentials', e);
      }
    };
    loadRememberedUser();
  }, []);

  const validateForm = () => {
    let isValid = true;
    setEmailError('');
    setPasswordError('');
    setApiError('');
    
    if (!email.trim()) {
      setEmailError('Email is required');
      isValid = false;
    } else if (!emailRegex.test(email.trim())) {
      setEmailError('Please enter a valid email address');
      isValid = false;
    }
    
    if (!password) {
      setPasswordError('Password is required');
      isValid = false;
    }
    
    return isValid;
  };

  const handleLogin = async () => {
    if (!validateForm()) return;
    
    setLoading(true);
    setApiError('');
    
    try {
      const isAdminLogin = email.trim() === 'admin@pricepilot.com';
      const endpoint = isAdminLogin ? '/auth/admin-login' : '/auth/login';
      
      const response = await fetchWithTimeout(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email.trim(),
          password: password,
        }),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        await authStorage.setItemAsync('token', data.token);
        await authStorage.setItemAsync('email', email.trim());
        await authStorage.setItemAsync('role', data.role || 'user');
        
        if (data.full_name) {
          await authStorage.setItemAsync('full_name', data.full_name);
        }
        if (data.phone) {
          await authStorage.setItemAsync('phone', data.phone);
        }
        
        if (rememberMe) {
          await authStorage.setItemAsync('rememberMe', 'true');
          await authStorage.setItemAsync('savedEmail', email.trim());
        } else {
          await authStorage.setItemAsync('rememberMe', 'false');
          await authStorage.deleteItemAsync('savedEmail');
        }
        // Redirect to index so the root routing logic (which handles profile completion and notifications) kicks in
        router.replace('/');
      } else {
        setApiError(data.detail || 'Login failed. Please try again.');
        setPassword('');
      }
    } catch (error: any) {
      console.log('❌ Login error:', error.message);
      if (error.message?.includes('timed out')) {
        setApiError('Connection timed out. Make sure the backend server is running on your computer.');
      } else {
        setApiError('Unable to connect to server. Please check your connection and ensure the backend is running.');
      }
      setPassword('');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea} edges={['top', 'bottom']}>
      <Stack.Screen options={{ headerShown: false }} />
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.flex}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          {/* Header */}
          <View style={styles.header}>
            <Text style={styles.title}>Sign In</Text>
            <Text style={styles.subtitle}>
              Hi! Welcome back, you've been missed
            </Text>
          </View>

          {/* API Error Message */}
          {apiError ? (
            <View style={styles.errorBanner}>
              <Ionicons name="alert-circle" size={18} color="#EF4444" />
              <Text style={styles.errorBannerText}>{apiError}</Text>
            </View>
          ) : null}

          {/* Email Input */}
          <View style={styles.fieldGroup}>
            <Text style={styles.label}>Email</Text>
            <View style={[styles.inputBox, emailError && styles.inputBoxError]}>
              <TextInput
                style={styles.input}
                placeholder="example@gmail.com"
                placeholderTextColor="#999"
                value={email}
                onChangeText={(text) => { setEmail(text); setEmailError(''); setApiError(''); }}
                keyboardType="email-address"
                autoCapitalize="none"
                autoComplete="email"
                editable={!loading}
              />
            </View>
            {emailError ? <Text style={styles.fieldError}>{emailError}</Text> : null}
          </View>

          {/* Password Input */}
          <View style={styles.fieldGroup}>
            <Text style={styles.label}>Password</Text>
            <View style={[styles.inputBox, passwordError && styles.inputBoxError]}>
              <TextInput
                style={styles.inputPassword}
                placeholder="****************"
                placeholderTextColor="#999"
                value={password}
                onChangeText={(text) => { setPassword(text); setPasswordError(''); setApiError(''); }}
                secureTextEntry={!showPassword}
                autoCapitalize="none"
                autoComplete="password"
                editable={!loading}
              />
              <TouchableOpacity
                onPress={() => setShowPassword(!showPassword)}
                disabled={loading}
                activeOpacity={0.7}
                hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
              >
                <Ionicons
                  name={showPassword ? 'eye-outline' : 'eye-off-outline'}
                  size={24}
                  color="#1F2029"
                />
              </TouchableOpacity>
            </View>
            {passwordError ? <Text style={styles.fieldError}>{passwordError}</Text> : null}
          </View>

          {/* Forgot Password Row */}
          <View style={styles.optionsRow}>
            <TouchableOpacity 
              disabled={loading} 
              activeOpacity={0.7}
              onPress={() => router.push('/(auth)/forgot-password')}
            >
              <Text style={styles.forgotPasswordText}>Forgot Password?</Text>
            </TouchableOpacity>
          </View>

          {/* Sign In Button */}
          <TouchableOpacity
            style={[styles.signInButton, loading && styles.signInButtonDisabled]}
            onPress={handleLogin}
            disabled={loading}
            activeOpacity={0.8}
          >
            {loading ? (
              <ActivityIndicator color="#FFF" />
            ) : (
              <Text style={styles.signInButtonText}>Sign In</Text>
            )}
          </TouchableOpacity>

          {/* Divider */}
          <View style={styles.dividerRow}>
            <View style={styles.dividerLine} />
            <Text style={styles.dividerText}>Or sign in with</Text>
            <View style={styles.dividerLine} />
          </View>

          {/* Social Login Buttons */}
          <View style={styles.socialRow}>
            <TouchableOpacity style={styles.socialButton} activeOpacity={0.7}>
              <Ionicons name="logo-apple" size={28} color="#000" />
            </TouchableOpacity>
            <TouchableOpacity style={styles.socialButton} activeOpacity={0.7}>
              <GoogleLogo />
            </TouchableOpacity>
            <TouchableOpacity style={styles.socialButton} activeOpacity={0.7}>
              <Ionicons name="logo-facebook" size={28} color="#1877F2" />
            </TouchableOpacity>
          </View>

          {/* Sign Up Link */}
          <View style={[styles.signUpRow, { paddingBottom: 40 }]}>
            <Text style={styles.signUpText}>Don't have an account? </Text>
            <TouchableOpacity
              onPress={() => router.push('/(auth)/register')}
              disabled={loading}
              activeOpacity={0.7}
            >
              <Text style={styles.signUpLink}>Sign Up</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#FDFDFD', // Pure/very light background
  },
  flex: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: 24,
    paddingTop: 80, // Lots of top padding to match design
    paddingBottom: 60, // Padding to keep it far from the bottom edge
  },

  // ── Header ──
  header: {
    alignItems: 'center',
    marginBottom: 40,
  },
  title: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 28,
    color: '#1F2029',
    marginBottom: 10,
  },
  subtitle: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 14,
    color: '#797979',
    textAlign: 'center',
    lineHeight: 22,
  },

  // ── Error Banner ──
  errorBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FEF2F2',
    padding: 12,
    borderRadius: 12,
    marginBottom: 16,
    gap: 8,
    borderWidth: 1,
    borderColor: '#FEE2E2',
  },
  errorBannerText: {
    flex: 1,
    color: '#EF4444',
    fontFamily: 'Poppins_400Regular',
    fontSize: 13,
  },

  // ── Form Fields ──
  fieldGroup: {
    marginBottom: 20,
  },
  label: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 14,
    color: '#1F2029',
    marginBottom: 8,
    marginLeft: 4,
  },
  inputBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderWidth: 1.5,
    borderColor: '#EDEDED',
    borderRadius: 30, // Pill shape
    paddingHorizontal: 20,
    height: 56,
  },
  inputBoxError: {
    borderColor: '#EF4444',
  },
  input: {
    flex: 1,
    fontFamily: 'Poppins_400Regular',
    fontSize: 14,
    color: '#1F2029',
  },
  inputPassword: {
    flex: 1,
    fontFamily: 'Poppins_400Regular',
    fontSize: 14,
    color: '#1F2029',
    letterSpacing: 2, // Spacing for asterisks
  },
  fieldError: {
    color: '#EF4444',
    fontFamily: 'Poppins_400Regular',
    fontSize: 12,
    marginTop: 4,
    marginLeft: 4,
  },

  // ── Options (Forgot Password) ──
  optionsRow: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    marginBottom: 35,
  },
  forgotPasswordText: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 13,
    color: '#704F38', // Brown color
    textDecorationLine: 'underline',
  },

  // ── Sign In Button ──
  signInButton: {
    backgroundColor: '#704F38',
    height: 54,
    borderRadius: 27, // Pill shape
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 35,
  },
  signInButtonDisabled: {
    backgroundColor: '#9E9E9E',
  },
  signInButtonText: {
    color: '#FFFFFF',
    fontFamily: 'Poppins_400Regular', // Lighter font weight for elegance
    fontSize: 16,
  },

  // ── Divider ──
  dividerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 30,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: '#EEEEEE',
  },
  dividerText: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 12,
    color: '#999',
    marginHorizontal: 16,
  },

  // ── Social Buttons ──
  socialRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 20,
    marginBottom: 40,
  },
  socialButton: {
    width: 56,
    height: 56,
    borderRadius: 28,
    borderWidth: 1,
    borderColor: '#EEEEEE',
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
  },

  // ── Sign Up Link ──
  signUpRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  signUpText: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 13,
    color: '#1F2029',
  },
  signUpLink: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 13,
    color: '#704F38', // Brown color
    textDecorationLine: 'underline',
  },
});
