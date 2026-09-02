import { useState } from 'react';
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
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useRouter, Stack } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import Svg, { Path } from 'react-native-svg';
import { API_URL } from '../../constants/api';
import { authStorage } from '../../lib/authStorage';

// Google Logo SVG Component
const GoogleLogo = () => (
  <Svg width="22" height="22" viewBox="0 0 48 48">
    <Path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.7 17.74 9.5 24 9.5z" />
    <Path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z" />
    <Path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z" />
    <Path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z" />
  </Svg>
);

export default function RegisterScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  
  // State for form inputs
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  // Defaulting to true to match the design's visual state
  const [agreeTerms, setAgreeTerms] = useState(true);

  // State for validation errors
  const [nameError, setNameError] = useState('');
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  
  // State for API call
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState('');

  // Email validation regex
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

  const validateForm = () => {
    let isValid = true;
    
    setNameError('');
    setEmailError('');
    setPasswordError('');
    setApiError('');
    
    if (!fullName.trim()) {
      setNameError('Name is required');
      isValid = false;
    }
    
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
    } else if (password.length < 8) {
      setPasswordError('Password must be at least 8 characters');
      isValid = false;
    } else if (!/\d/.test(password)) {
      setPasswordError('Password must contain at least one number');
      isValid = false;
    }

    if (!agreeTerms) {
      setApiError('Please agree to the Terms & Conditions');
      isValid = false;
    }
    
    return isValid;
  };

  const handleRegister = async () => {
    if (!validateForm()) return;
    
    setLoading(true);
    setApiError('');
    
    try {
      const names = fullName.trim().split(' ');
      const first_name = names[0];
      const last_name = names.length > 1 ? names.slice(1).join(' ') : ' ';

      const response = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email.trim(),
          password: password,
          first_name: first_name,
          last_name: last_name,
        }),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        await authStorage.setItemAsync('token', data.token);
        await authStorage.setItemAsync('email', email.trim());
        await authStorage.setItemAsync('full_name', fullName.trim());
        if (data.phone) {
          await authStorage.setItemAsync('phone', data.phone);
        }
        
        router.replace('/(auth)/complete-profile');
      } else {
        if (data.detail) {
          if (typeof data.detail === 'string') {
            if (data.detail.toLowerCase().includes('email')) {
              setEmailError(data.detail);
            } else {
              setApiError(data.detail);
            }
          } else if (Array.isArray(data.detail)) {
            let hasFieldError = false;
            data.detail.forEach((err: any) => {
              const field = err.loc && err.loc.length > 0 ? err.loc[err.loc.length - 1] : '';
              if (field === 'password') { setPasswordError(err.msg); hasFieldError = true; }
              else if (field === 'email') { setEmailError(err.msg); hasFieldError = true; }
              else if (field === 'first_name' || field === 'last_name') { setNameError(err.msg); hasFieldError = true; }
            });
            if (!hasFieldError) {
              const errorMessages = data.detail.map((err: any) => err.msg).join(', ');
              setApiError(errorMessages);
            }
          } else {
            setApiError('Registration failed. Please try again.');
          }
        } else {
          setApiError('Registration failed. Please try again.');
        }
      }
    } catch (error) {
      setApiError('Unable to connect to server. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={[styles.safeArea, { paddingTop: insets.top, paddingBottom: insets.bottom }]}>
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
            <Text style={styles.title}>Create Account</Text>
            <Text style={styles.subtitle}>
              Fill your information below or register{'\n'}with your social account.
            </Text>
          </View>

          {/* API Error Message */}
          {apiError ? (
            <View style={styles.errorBanner}>
              <Ionicons name="alert-circle" size={18} color="#EF4444" />
              <Text style={styles.errorBannerText}>{apiError}</Text>
            </View>
          ) : null}

          {/* Name Input */}
          <View style={styles.fieldGroup}>
            <Text style={styles.label}>Name</Text>
            <View style={[styles.inputBox, nameError && styles.inputBoxError]}>
              <TextInput
                style={styles.input}
                placeholder="John Doe"
                placeholderTextColor="#999"
                value={fullName}
                onChangeText={(text) => { setFullName(text); setNameError(''); setApiError(''); }}
                autoCapitalize="words"
                autoComplete="name"
                editable={!loading}
              />
            </View>
            {nameError ? <Text style={styles.fieldError}>{nameError}</Text> : null}
          </View>

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
                autoComplete="password-new"
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
                  size={22}
                  color="#1F2029"
                />
              </TouchableOpacity>
            </View>
            {passwordError ? <Text style={styles.fieldError}>{passwordError}</Text> : null}
          </View>

          {/* Terms & Conditions Checkbox */}
          <TouchableOpacity
            style={styles.termsRow}
            onPress={() => setAgreeTerms(!agreeTerms)}
            activeOpacity={0.7}
            disabled={loading}
          >
            <View style={[styles.checkbox, agreeTerms && styles.checkboxChecked]}>
              {agreeTerms && <Ionicons name="checkmark" size={16} color="#FFF" />}
            </View>
            <Text style={styles.termsText}>
              Agree with <Text style={styles.termsLink}>Terms & Condition</Text>
            </Text>
          </TouchableOpacity>

          {/* Sign Up Button */}
          <TouchableOpacity
            style={[styles.signUpButton, loading && styles.signUpButtonDisabled]}
            onPress={handleRegister}
            disabled={loading}
            activeOpacity={0.8}
          >
            {loading ? (
              <ActivityIndicator color="#FFF" />
            ) : (
              <Text style={styles.signUpButtonText}>Sign Up</Text>
            )}
          </TouchableOpacity>

          {/* Divider */}
          <View style={styles.dividerRow}>
            <View style={styles.dividerLine} />
            <Text style={styles.dividerText}>Or sign up with</Text>
            <View style={styles.dividerLine} />
          </View>

          {/* Social Login Buttons */}
          <View style={styles.socialRow}>
            <TouchableOpacity style={styles.socialButton} activeOpacity={0.7}>
              <Ionicons name="logo-apple" size={24} color="#000" />
            </TouchableOpacity>
            <TouchableOpacity style={styles.socialButton} activeOpacity={0.7}>
              <GoogleLogo />
            </TouchableOpacity>
            <TouchableOpacity style={styles.socialButton} activeOpacity={0.7}>
              <Ionicons name="logo-facebook" size={24} color="#1877F2" />
            </TouchableOpacity>
          </View>

          {/* Sign In Link */}
          <View style={[styles.signInRow, { paddingBottom: 40 }]}>
            <Text style={styles.signInText}>Already have an account? </Text>
            <TouchableOpacity
              onPress={() => router.push('/(auth)/login')}
              disabled={loading}
              activeOpacity={0.7}
            >
              <Text style={styles.signInLink}>Sign In</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#FFFFFF', // Pure white background
  },
  flex: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: 28,
    paddingTop: 60,
    paddingBottom: 80, // Massive padding to keep it far from the bottom edge
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

  // ── Terms Checkbox ──
  termsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 35,
    marginTop: 4,
  },
  checkbox: {
    width: 24,
    height: 24,
    borderRadius: 6,
    borderWidth: 2,
    borderColor: '#704F38',
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
  },
  checkboxChecked: {
    backgroundColor: '#704F38',
    borderColor: '#704F38',
  },
  termsText: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 14,
    color: '#1F2029',
  },
  termsLink: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 14,
    color: '#704F38', // Brown color for link
    textDecorationLine: 'underline',
  },

  // ── Sign Up Button ──
  signUpButton: {
    backgroundColor: '#704F38',
    height: 54,
    borderRadius: 27,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 35,
  },
  signUpButtonDisabled: {
    backgroundColor: '#9E9E9E',
  },
  signUpButtonText: {
    color: '#FFFFFF',
    fontFamily: 'Poppins_400Regular', // Lighter font weight
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

  // ── Sign In Link ──
  signInRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  signInText: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 13,
    color: '#1F2029',
  },
  signInLink: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 13,
    color: '#704F38', // Brown color
    textDecorationLine: 'underline',
  },
});
