import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, TextInput, ActivityIndicator, Alert, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Stack, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { authStorage } from '../lib/authStorage';
import { changePassword } from '../services/api';

export default function PasswordManagerScreen() {
  const router = useRouter();
  
  const handleBack = () => {
    if (router.canGoBack()) {
      router.back();
    } else {
      router.replace('/settings');
    }
  };
  
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  
  const [currentPasswordError, setCurrentPasswordError] = useState('');
  const [newPasswordError, setNewPasswordError] = useState('');
  const [confirmPasswordError, setConfirmPasswordError] = useState('');
  
  const [isLoading, setIsLoading] = useState(false);

  const clearErrors = () => {
    setCurrentPasswordError('');
    setNewPasswordError('');
    setConfirmPasswordError('');
  };

  const handleChangePassword = async () => {
    clearErrors();
    let hasError = false;

    if (!currentPassword) {
      setCurrentPasswordError('Please enter your current password');
      hasError = true;
    }
    
    if (!newPassword) {
      setNewPasswordError('Please enter a new password');
      hasError = true;
    } else if (newPassword.length < 8) {
      setNewPasswordError('New password must be at least 8 characters long');
      hasError = true;
    }
    
    if (!confirmPassword) {
      setConfirmPasswordError('Please confirm your new password');
      hasError = true;
    } else if (newPassword !== confirmPassword) {
      setConfirmPasswordError('New passwords do not match');
      hasError = true;
    }

    if (hasError) return;

    const token = await authStorage.getItemAsync('token');
    if (!token) {
      Alert.alert('Error', 'You must be logged in to change your password');
      return;
    }

    setIsLoading(true);
    try {
      await changePassword(token, currentPassword, newPassword);
      Alert.alert('Success', 'Your password has been changed successfully.', [
        { text: 'OK', onPress: handleBack }
      ]);
    } catch (error: any) {
      const msg = error.message || '';
      if (msg.toLowerCase().includes('incorrect') || msg.toLowerCase().includes('current password')) {
        setCurrentPasswordError('Incorrect password');
      } else {
        Alert.alert('Error', msg || 'Failed to change password. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container} edges={['top', 'bottom']}>
      <Stack.Screen options={{ headerShown: false }} />
      
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity style={styles.backButton} onPress={handleBack}>
          <Ionicons name="arrow-back" size={24} color="#111111" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Password Manager</Text>
        <View style={{ width: 40 }} />
      </View>

      <KeyboardAvoidingView 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={{ flex: 1 }}
      >
        <ScrollView style={styles.content} keyboardShouldPersistTaps="handled">
          
          <Text style={styles.label}>Current Password</Text>
          <View style={[styles.inputContainer, currentPasswordError ? styles.inputErrorBorder : null, { marginBottom: currentPasswordError ? 8 : 8 }]}>
            <TextInput
              style={styles.input}
              placeholder="*****************"
              placeholderTextColor="#999"
              secureTextEntry={!showCurrentPassword}
              value={currentPassword}
              onChangeText={(text) => {
                setCurrentPassword(text);
                if (currentPasswordError) setCurrentPasswordError('');
              }}
            />
            <TouchableOpacity onPress={() => setShowCurrentPassword(!showCurrentPassword)}>
              <Ionicons name={!showCurrentPassword ? "eye-off-outline" : "eye-outline"} size={22} color="#111" />
            </TouchableOpacity>
          </View>
          {currentPasswordError ? <Text style={styles.errorText}>{currentPasswordError}</Text> : null}
          
          <TouchableOpacity style={[styles.forgotPasswordContainer, currentPasswordError ? { marginTop: 8 } : { marginTop: -4 }]} onPress={() => Alert.alert('Notice', 'Forgot Password flow not implemented yet.')}>
            <Text style={styles.forgotPasswordText}>Forgot Password?</Text>
          </TouchableOpacity>

          <Text style={styles.label}>New Password</Text>
          <View style={[styles.inputContainer, newPasswordError ? styles.inputErrorBorder : null, { marginBottom: newPasswordError ? 8 : 24 }]}>
            <TextInput
              style={styles.input}
              placeholder="*****************"
              placeholderTextColor="#999"
              secureTextEntry={!showNewPassword}
              value={newPassword}
              onChangeText={(text) => {
                setNewPassword(text);
                if (newPasswordError) setNewPasswordError('');
              }}
            />
            <TouchableOpacity onPress={() => setShowNewPassword(!showNewPassword)}>
              <Ionicons name={!showNewPassword ? "eye-off-outline" : "eye-outline"} size={22} color="#111" />
            </TouchableOpacity>
          </View>
          {newPasswordError ? <Text style={[styles.errorText, { marginBottom: 24 }]}>{newPasswordError}</Text> : null}

          <Text style={styles.label}>Confirm New Password</Text>
          <View style={[styles.inputContainer, confirmPasswordError ? styles.inputErrorBorder : null, { marginBottom: confirmPasswordError ? 8 : 24 }]}>
            <TextInput
              style={styles.input}
              placeholder="*****************"
              placeholderTextColor="#999"
              secureTextEntry={!showConfirmPassword}
              value={confirmPassword}
              onChangeText={(text) => {
                setConfirmPassword(text);
                if (confirmPasswordError) setConfirmPasswordError('');
              }}
            />
            <TouchableOpacity onPress={() => setShowConfirmPassword(!showConfirmPassword)}>
              <Ionicons name={!showConfirmPassword ? "eye-off-outline" : "eye-outline"} size={22} color="#111" />
            </TouchableOpacity>
          </View>
          {confirmPasswordError ? <Text style={[styles.errorText, { marginBottom: 24 }]}>{confirmPasswordError}</Text> : null}
          
        </ScrollView>
        
        <View style={styles.footer}>
          <TouchableOpacity 
            style={[styles.button, isLoading && styles.buttonDisabled]} 
            onPress={handleChangePassword}
            disabled={isLoading}
          >
            {isLoading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.buttonText}>Change Password</Text>
            )}
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FAFAFA',
    paddingTop: Platform.OS === 'android' ? 25 : 0,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingBottom: 16,
    paddingTop: 8,
    backgroundColor: '#FAFAFA',
  },
  backButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    borderWidth: 1,
    borderColor: '#EAEAEA',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#FFFFFF',
  },
  headerTitle: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 16,
    color: '#111111',
  },
  content: {
    flex: 1,
    paddingHorizontal: 24,
    paddingTop: 16,
  },
  label: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 13,
    color: '#111111',
    marginBottom: 8,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#EAEAEA',
    borderRadius: 8,
    paddingHorizontal: 16,
    height: 52,
    marginBottom: 24,
  },
  inputErrorBorder: {
    borderColor: '#EF4444',
  },
  input: {
    flex: 1,
    fontFamily: 'Poppins_400Regular',
    fontSize: 14,
    color: '#111111',
    height: '100%',
  },
  errorText: {
    fontFamily: 'Poppins_400Regular',
    fontSize: 12,
    color: '#EF4444',
    marginLeft: 4,
    marginTop: -4,
  },
  forgotPasswordContainer: {
    alignSelf: 'flex-end',
    marginBottom: 24,
    marginTop: -4,
  },
  forgotPasswordText: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 13,
    color: '#8B5A2B',
    textDecorationLine: 'underline',
  },
  footer: {
    padding: 24,
    backgroundColor: '#FAFAFA',
  },
  button: {
    backgroundColor: '#6E4B3A',
    height: 52,
    borderRadius: 26,
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonDisabled: {
    opacity: 0.7,
  },
  buttonText: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 15,
    color: '#FFFFFF',
  },
});
