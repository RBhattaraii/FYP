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
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import * as SecureStore from 'expo-secure-store';
import { Ionicons } from '@expo/vector-icons';
import { API_URL } from '../../constants/api';
import { colors, typography, spacing, borderRadius, shadows } from '../../constants/theme';

export default function RegisterScreen() {
  const router = useRouter();
  
  // State for form inputs
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // Focus states
  const [isFirstNameFocused, setIsFirstNameFocused] = useState(false);
  const [isLastNameFocused, setIsLastNameFocused] = useState(false);
  const [isEmailFocused, setIsEmailFocused] = useState(false);
  const [isPasswordFocused, setIsPasswordFocused] = useState(false);
  const [isConfirmPasswordFocused, setIsConfirmPasswordFocused] = useState(false);
  
  // State for validation errors
  const [firstNameError, setFirstNameError] = useState('');
  const [lastNameError, setLastNameError] = useState('');
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [confirmPasswordError, setConfirmPasswordError] = useState('');
  
  // State for API call
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState('');

  // Email validation regex
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

  const validateForm = () => {
    let isValid = true;
    
    setFirstNameError('');
    setLastNameError('');
    setEmailError('');
    setPasswordError('');
    setConfirmPasswordError('');
    setApiError('');
    
    if (!firstName.trim()) {
      setFirstNameError('First name is required');
      isValid = false;
    }
    
    if (!lastName.trim()) {
      setLastNameError('Last name is required');
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
    
    if (!confirmPassword) {
      setConfirmPasswordError('Please confirm your password');
      isValid = false;
    } else if (password !== confirmPassword) {
      setConfirmPasswordError('Passwords do not match');
      isValid = false;
    }
    
    return isValid;
  };

  const handleRegister = async () => {
    if (!validateForm()) return;
    
    setLoading(true);
    setApiError('');
    
    try {
      const response = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email.trim(),
          password: password,
          full_name: `${firstName.trim()} ${lastName.trim()}`,
        }),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        await SecureStore.setItemAsync('token', data.token);
        await SecureStore.setItemAsync('email', email.trim());
        router.replace('/(tabs)/home');
      } else {
        if (data.detail) {
          if (typeof data.detail === 'string') {
            setApiError(data.detail);
          } else if (Array.isArray(data.detail)) {
            const errorMessages = data.detail.map((err: any) => err.msg).join(', ');
            setApiError(errorMessages);
          } else {
            setApiError('Registration failed. Please try again.');
          }
        } else {
          setApiError('Registration failed. Please try again.');
        }
        setPassword('');
        setConfirmPassword('');
      }
    } catch (error) {
      setApiError('Unable to connect to server. Please check your connection.');
      setPassword('');
      setConfirmPassword('');
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
          {/* Back Button */}
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => router.back()}
            disabled={loading}
            activeOpacity={0.7}
          >
            <Ionicons name="arrow-back" size={24} color={colors.gray900} />
          </TouchableOpacity>
          
          {/* Header */}
          <View style={styles.header}>
            <Text style={styles.title}>Create Account</Text>
            <Text style={styles.subtitle}>
              Sign up to start comparing prices and finding the best deals on products.
            </Text>
          </View>
          
          {/* API Error Message */}
          {apiError ? (
            <View style={styles.errorContainer}>
              <Ionicons name="alert-circle" size={20} color={colors.errorRed} />
              <Text style={styles.errorText}>{apiError}</Text>
            </View>
          ) : null}
          
          {/* Name Row */}
          <View style={styles.nameRow}>
            {/* First Name Input */}
            <View style={styles.nameInputContainer}>
              <Text style={styles.label}>First Name</Text>
              <View style={[
                styles.inputWrapper, 
                isFirstNameFocused && styles.inputWrapperFocused,
                firstNameError ? styles.inputWrapperError : null
              ]}>
                <Ionicons 
                  name="person-outline" 
                  size={20} 
                  color={isFirstNameFocused ? colors.warningOrange : colors.gray400} 
                  style={styles.inputIcon} 
                />
                <TextInput
                  style={styles.input}
                  placeholder="John"
                  placeholderTextColor={colors.gray400}
                  value={firstName}
                  onFocus={() => setIsFirstNameFocused(true)}
                  onBlur={() => setIsFirstNameFocused(false)}
                  onChangeText={(text) => {
                    setFirstName(text);
                    setFirstNameError('');
                    setApiError('');
                  }}
                  autoCapitalize="words"
                  autoComplete="name-given"
                  editable={!loading}
                  cursorColor={colors.warningOrange}
                />
              </View>
              {firstNameError ? <Text style={styles.fieldError}>{firstNameError}</Text> : null}
            </View>
            
            {/* Last Name Input */}
            <View style={styles.nameInputContainer}>
              <Text style={styles.label}>Last Name</Text>
              <View style={[
                styles.inputWrapper, 
                isLastNameFocused && styles.inputWrapperFocused,
                lastNameError ? styles.inputWrapperError : null
              ]}>
                <Ionicons 
                  name="person-outline" 
                  size={20} 
                  color={isLastNameFocused ? colors.warningOrange : colors.gray400} 
                  style={styles.inputIcon} 
                />
                <TextInput
                  style={styles.input}
                  placeholder="Doe"
                  placeholderTextColor={colors.gray400}
                  value={lastName}
                  onFocus={() => setIsLastNameFocused(true)}
                  onBlur={() => setIsLastNameFocused(false)}
                  onChangeText={(text) => {
                    setLastName(text);
                    setLastNameError('');
                    setApiError('');
                  }}
                  autoCapitalize="words"
                  autoComplete="name-family"
                  editable={!loading}
                  cursorColor={colors.warningOrange}
                />
              </View>
              {lastNameError ? <Text style={styles.fieldError}>{lastNameError}</Text> : null}
            </View>
          </View>
          
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
                placeholder="••••••••"
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
                autoComplete="password-new"
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
          
          {/* Confirm Password Input */}
          <View style={styles.inputContainer}>
            <Text style={styles.label}>Confirm Password</Text>
            <View style={[
              styles.inputWrapper, 
              isConfirmPasswordFocused && styles.inputWrapperFocused,
              confirmPasswordError ? styles.inputWrapperError : null
            ]}>
              <Ionicons 
                name="lock-closed-outline" 
                size={20} 
                color={isConfirmPasswordFocused ? colors.warningOrange : colors.gray400} 
                style={styles.inputIcon} 
              />
              <TextInput
                style={styles.input}
                placeholder="••••••••"
                placeholderTextColor={colors.gray400}
                value={confirmPassword}
                onFocus={() => setIsConfirmPasswordFocused(true)}
                onBlur={() => setIsConfirmPasswordFocused(false)}
                onChangeText={(text) => {
                  setConfirmPassword(text);
                  setConfirmPasswordError('');
                  setApiError('');
                }}
                secureTextEntry={!showConfirmPassword}
                autoCapitalize="none"
                autoComplete="password-new"
                editable={!loading}
                cursorColor={colors.warningOrange}
              />
              <TouchableOpacity
                style={styles.eyeIcon}
                onPress={() => setShowConfirmPassword(!showConfirmPassword)}
                disabled={loading}
                activeOpacity={0.7}
              >
                <Ionicons
                  name={showConfirmPassword ? 'eye-off-outline' : 'eye-outline'}
                  size={20}
                  color={colors.gray400}
                />
              </TouchableOpacity>
            </View>
            {confirmPasswordError ? <Text style={styles.fieldError}>{confirmPasswordError}</Text> : null}
          </View>
          
          {/* Sign Up Button */}
          <TouchableOpacity
            style={[styles.button, loading ? styles.buttonDisabled : null]}
            onPress={handleRegister}
            disabled={loading}
            activeOpacity={0.8}
          >
            {loading ? (
              <ActivityIndicator color={colors.white} />
            ) : (
              <Text style={styles.buttonText}>Sign Up</Text>
            )}
          </TouchableOpacity>
          
          {/* Login Link */}
          <View style={styles.loginContainer}>
            <Text style={styles.loginText}>Already have an account? </Text>
            <TouchableOpacity
              onPress={() => router.push('/(auth)/login')}
              disabled={loading}
              activeOpacity={0.7}
            >
              <Text style={styles.loginLink}>Log In</Text>
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
    paddingTop: 20,
    paddingBottom: 40,
  },
  backButton: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    marginBottom: spacing.lg,
  },
  header: {
    marginBottom: spacing['2xl'],
  },
  title: {
    fontSize: typography.fontSize.h1,
    fontFamily: typography.fontFamily.primary,
    fontWeight: typography.fontWeight.bold,
    color: colors.gray900,
    marginBottom: spacing.sm,
    letterSpacing: -0.5,
  },
  subtitle: {
    fontSize: typography.fontSize.body,
    fontFamily: typography.fontFamily.primary,
    color: colors.gray600,
    lineHeight: typography.lineHeight.bodyLarge,
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
  nameRow: {
    flexDirection: 'row',
    gap: spacing.md,
    marginBottom: spacing.lg,
  },
  nameInputContainer: {
    flex: 1,
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
  button: {
    backgroundColor: colors.warningOrange,
    height: 56,
    borderRadius: borderRadius.full,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: spacing.sm,
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
  loginContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: spacing['2xl'],
  },
  loginText: {
    fontSize: typography.fontSize.body,
    fontFamily: typography.fontFamily.primary,
    color: colors.gray600,
  },
  loginLink: {
    fontSize: typography.fontSize.body,
    fontFamily: typography.fontFamily.primary,
    color: colors.warningOrange,
    fontWeight: typography.fontWeight.bold,
  },
});
