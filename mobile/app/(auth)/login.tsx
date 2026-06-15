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
import { useRouter } from 'expo-router';
import * as SecureStore from 'expo-secure-store';
import { Ionicons } from '@expo/vector-icons';
import { API_URL, fetchWithTimeout } from '../../constants/api';
import { colors, typography, spacing, borderRadius, shadows } from '../../constants/theme';

export default function LoginScreen() {
  const router = useRouter();
  
  // State for form inputs
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  
  // Focus states for iOS-like effects
  const [isEmailFocused, setIsEmailFocused] = useState(false);
  const [isPasswordFocused, setIsPasswordFocused] = useState(false);

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
        const savedRememberMe = await SecureStore.getItemAsync('rememberMe');
        if (savedRememberMe === 'true') {
          setRememberMe(true);
          const savedEmail = await SecureStore.getItemAsync('savedEmail');
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
      const response = await fetchWithTimeout(`${API_URL}/auth/login`, {
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
        await SecureStore.setItemAsync('token', data.token);
        await SecureStore.setItemAsync('email', email.trim());
        
        // Handle Remember Me securely
        if (rememberMe) {
          await SecureStore.setItemAsync('rememberMe', 'true');
          await SecureStore.setItemAsync('savedEmail', email.trim());
        } else {
          await SecureStore.setItemAsync('rememberMe', 'false');
          await SecureStore.deleteItemAsync('savedEmail');
        }
        
        router.replace('/(tabs)/home');
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
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.container}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          {/* Header */}
          <View style={styles.header}>
            <Text style={styles.title}>Welcome back</Text>
            <Text style={styles.subtitle}>
              Log in to compare prices, track deals, and save money on your favorite products.
            </Text>
          </View>
          
          {/* API Error Message */}
          {apiError ? (
            <View style={styles.errorContainer}>
              <Ionicons name="alert-circle" size={20} color={colors.errorRed} />
              <Text style={styles.errorText}>{apiError}</Text>
            </View>
          ) : null}
          
          {/* Email Input */}
          <View style={styles.inputContainer}>
            <Text style={styles.label}>Email address</Text>
            <View style={[
              styles.inputWrapper, 
              isEmailFocused && styles.inputWrapperFocused,
              emailError ? styles.inputWrapperError : null
            ]}>
              <Ionicons 
                name="mail-outline" 
                size={20} 
                color={isEmailFocused ? colors.warningOrange : colors.gray400} 
                style={styles.inputIcon} 
              />
              <TextInput
                style={styles.input}
                placeholder="hello@example.com"
                placeholderTextColor={colors.gray400}
                value={email}
                onFocus={() => setIsEmailFocused(true)}
                onBlur={() => setIsEmailFocused(false)}
                onChangeText={(text) => {
                  setEmail(text);
                  setEmailError('');
                  setApiError('');
                }}
                keyboardType="email-address"
                autoCapitalize="none"
                autoComplete="email"
                editable={!loading}
                cursorColor={colors.warningOrange}
              />
            </View>
            {emailError ? <Text style={styles.fieldError}>{emailError}</Text> : null}
          </View>
          
          {/* Password Input */}
          <View style={styles.inputContainer}>
            <Text style={styles.label}>Password</Text>
            <View style={[
              styles.inputWrapper, 
              isPasswordFocused && styles.inputWrapperFocused,
              passwordError ? styles.inputWrapperError : null
            ]}>
              <Ionicons 
                name="lock-closed-outline" 
                size={20} 
                color={isPasswordFocused ? colors.warningOrange : colors.gray400} 
                style={styles.inputIcon} 
              />
              <TextInput
                style={styles.input}
                placeholder="Password"
                placeholderTextColor={colors.gray400}
                value={password}
                onFocus={() => setIsPasswordFocused(true)}
                onBlur={() => setIsPasswordFocused(false)}
                onChangeText={(text) => {
                  setPassword(text);
                  setPasswordError('');
                  setApiError('');
                }}
                secureTextEntry={!showPassword}
                autoCapitalize="none"
                autoComplete="password"
                editable={!loading}
                cursorColor={colors.warningOrange}
              />
              <TouchableOpacity
                style={styles.eyeIcon}
                onPress={() => setShowPassword(!showPassword)}
                disabled={loading}
                activeOpacity={0.7}
              >
                <Ionicons
                  name={showPassword ? 'eye-off-outline' : 'eye-outline'}
                  size={20}
                  color={colors.gray400}
                />
              </TouchableOpacity>
            </View>
            {passwordError ? <Text style={styles.fieldError}>{passwordError}</Text> : null}
          </View>
          
          {/* Remember Me & Forgot Password */}
          <View style={styles.optionsRow}>
            <TouchableOpacity 
              style={styles.rememberMeContainer}
              onPress={() => setRememberMe(!rememberMe)}
              activeOpacity={0.7}
              disabled={loading}
            >
              <View style={[styles.checkbox, rememberMe && styles.checkboxActive]}>
                {rememberMe && <Ionicons name="checkmark" size={14} color={colors.white} />}
              </View>
              <Text style={styles.rememberMeText}>Remember me</Text>
            </TouchableOpacity>
            <TouchableOpacity disabled={loading} activeOpacity={0.7}>
              <Text style={styles.forgotPasswordText}>Forgot password?</Text>
            </TouchableOpacity>
          </View>
          
          {/* Login Button */}
          <TouchableOpacity
            style={[styles.button, loading ? styles.buttonDisabled : null]}
            onPress={handleLogin}
            disabled={loading}
            activeOpacity={0.8}
          >
            {loading ? (
              <ActivityIndicator color={colors.white} />
            ) : (
              <Text style={styles.buttonText}>Log In</Text>
            )}
          </TouchableOpacity>
          
          {/* Register Link */}
          <View style={styles.registerContainer}>
            <Text style={styles.registerText}>Don't have an account? </Text>
            <TouchableOpacity
              onPress={() => router.push('/(auth)/register')}
              disabled={loading}
              activeOpacity={0.7}
            >
              <Text style={styles.registerLink}>Sign Up</Text>
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
    backgroundColor: colors.white,
  },
  container: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    padding: spacing.xl,
    paddingTop: 80,
    paddingBottom: 40,
  },
  header: {
    marginBottom: spacing['4xl'],
    alignItems: 'center',
  },
  title: {
    fontSize: typography.fontSize.h1,
    fontFamily: typography.fontFamily.primary,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
    marginBottom: spacing.sm,
    textAlign: 'center',
    letterSpacing: -0.5,
  },
  subtitle: {
    fontSize: typography.fontSize.body,
    fontFamily: typography.fontFamily.primary,
    color: colors.gray600,
    textAlign: 'center',
    lineHeight: typography.lineHeight.bodyLarge,
    paddingHorizontal: spacing.lg,
  },
  errorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FEF2F2',
    padding: spacing.md,
    borderRadius: borderRadius.large,
    marginBottom: spacing.lg,
    gap: spacing.sm,
    borderWidth: 1,
    borderColor: '#FEE2E2',
  },
  errorText: {
    flex: 1,
    color: colors.errorRed,
    fontSize: typography.fontSize.body,
    fontFamily: typography.fontFamily.primary,
  },
  inputContainer: {
    marginBottom: spacing.lg,
  },
  label: {
    fontSize: typography.fontSize.body,
    fontFamily: typography.fontFamily.primary,
    fontWeight: typography.fontWeight.semibold,
    color: colors.gray900,
    marginBottom: spacing.sm,
    marginLeft: spacing.xs,
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.gray50,
    borderWidth: 1,
    borderColor: colors.gray100,
    borderRadius: borderRadius.full,
    paddingHorizontal: spacing.lg,
    height: 56,
  },
  inputWrapperFocused: {
    borderColor: colors.warningOrange,
    backgroundColor: colors.white,
  },
  inputWrapperError: {
    borderColor: colors.errorRed,
    backgroundColor: '#FEF2F2',
  },
  inputIcon: {
    marginRight: spacing.sm,
  },
  input: {
    flex: 1,
    fontSize: typography.fontSize.bodyLarge,
    fontFamily: typography.fontFamily.primary,
    color: colors.gray900,
  },
  eyeIcon: {
    padding: spacing.xs,
  },
  fieldError: {
    color: colors.errorRed,
    fontSize: typography.fontSize.caption,
    fontFamily: typography.fontFamily.primary,
    marginTop: spacing.xs,
    marginLeft: spacing.md,
  },
  optionsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing['2xl'],
    paddingHorizontal: spacing.xs,
  },
  rememberMeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  checkbox: {
    width: 22,
    height: 22,
    borderWidth: 2,
    borderColor: colors.gray400,
    borderRadius: 6,
    backgroundColor: colors.white,
    alignItems: 'center',
    justifyContent: 'center',
  },
  checkboxActive: {
    backgroundColor: colors.warningOrange,
    borderColor: colors.warningOrange,
  },
  rememberMeText: {
    fontSize: typography.fontSize.body,
    fontFamily: typography.fontFamily.primary,
    color: colors.gray600,
  },
  forgotPasswordText: {
    fontSize: typography.fontSize.body,
    fontFamily: typography.fontFamily.primary,
    color: colors.warningOrange,
    fontWeight: typography.fontWeight.semibold,
  },
  button: {
    backgroundColor: colors.warningOrange,
    height: 56,
    borderRadius: borderRadius.full,
    alignItems: 'center',
    justifyContent: 'center',
    ...shadows.button,
  },
  buttonDisabled: {
    backgroundColor: colors.gray400,
    ...shadows.card,
  },
  buttonText: {
    color: colors.white,
    fontSize: typography.fontSize.button,
    fontFamily: typography.fontFamily.primary,
    fontWeight: typography.fontWeight.bold,
  },
  registerContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: spacing['2xl'],
  },
  registerText: {
    fontSize: typography.fontSize.body,
    fontFamily: typography.fontFamily.primary,
    color: colors.gray600,
  },
  registerLink: {
    fontSize: typography.fontSize.body,
    fontFamily: typography.fontFamily.primary,
    color: colors.warningOrange,
    fontWeight: typography.fontWeight.bold,
  },
});
