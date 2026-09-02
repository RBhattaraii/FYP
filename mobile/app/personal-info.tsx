import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, ScrollView, KeyboardAvoidingView, Platform, Alert, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Stack, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { fetchUserProfile, updateUserProfile } from '../services/api';
import { authStorage } from '../lib/authStorage';

const THEME_BROWN = '#6E4B3A';
const THEME_BG = '#FFFFFF';

export default function PersonalInfoScreen() {
  const router = useRouter();
  
  const handleBack = () => {
    if (router.canGoBack()) {
      router.back();
    } else {
      router.replace('/settings');
    }
  };
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
  });
  const [originalData, setOriginalData] = useState({
    full_name: '',
    email: '',
    phone: '',
  });

  useEffect(() => {
    loadUserProfile();
  }, []);

  const loadUserProfile = async () => {
    try {
      setLoading(true);
      const token = await authStorage.getItemAsync('token');
      
      if (!token) {
        Alert.alert('Error', 'Not authenticated. Please login again.');
        router.replace('/(auth)/login');
        return;
      }

      const profile = await fetchUserProfile(token);
      
      const profileData = {
        full_name: profile.full_name || '',
        email: profile.email || '',
        phone: profile.phone || '',
      };
      
      setFormData(profileData);
      setOriginalData(profileData);
    } catch (error: any) {
      console.error('Failed to load profile:', error);
      Alert.alert('Error', 'Failed to load profile information.');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      if (formData.full_name === originalData.full_name && formData.phone === originalData.phone) {
        Alert.alert('No Changes', 'No changes to save.');
        return;
      }

      if (!formData.full_name || formData.full_name.trim().length < 2) {
        Alert.alert('Validation Error', 'Full name must be at least 2 characters.');
        return;
      }

      setSaving(true);
      const token = await authStorage.getItemAsync('token');
      
      if (!token) {
        Alert.alert('Error', 'Not authenticated. Please login again.');
        router.replace('/(auth)/login');
        return;
      }

      const updateData: any = {};
      if (formData.full_name !== originalData.full_name) {
        updateData.full_name = formData.full_name.trim();
      }
      if (formData.phone !== originalData.phone) {
        updateData.phone = formData.phone.trim();
      }

      const response = await updateUserProfile(token, updateData);
      
      setOriginalData({
        full_name: response.full_name,
        email: response.email,
        phone: response.phone || '',
      });
      
      await authStorage.setItemAsync('full_name', response.full_name);
      if (response.phone) {
        await authStorage.setItemAsync('phone', response.phone);
      } else {
        await authStorage.deleteItemAsync('phone');
      }

      Alert.alert('Success', 'Personal information updated successfully.', [
        { text: 'OK', onPress: handleBack }
      ]);
    } catch (error: any) {
      console.error('Failed to update profile:', error);
      Alert.alert('Error', error.message || 'Failed to update profile.');
    } finally {
      setSaving(false);
    }
  };

  const renderInput = (label: string, value: string, key: keyof typeof formData, editable = true, keyboardType: any = 'default') => (
    <View style={styles.inputGroup}>
      <Text style={styles.label}>{label}</Text>
      <View style={[styles.inputWrapper, !editable && styles.inputWrapperDisabled]}>
        <TextInput
          style={[styles.input, !editable && styles.inputTextDisabled]}
          value={value}
          onChangeText={(text) => setFormData(prev => ({ ...prev, [key]: text }))}
          editable={editable && !saving}
          keyboardType={keyboardType}
          placeholderTextColor="#A0A0A0"
        />
        {!editable && <Ionicons name="lock-closed" size={16} color="#A0A0A0" style={styles.inputIcon} />}
      </View>
    </View>
  );

  if (loading) {
    return (
      <SafeAreaView style={styles.container} edges={['top']}>
        <Stack.Screen options={{ headerShown: false }} />
        <View style={styles.header}>
          <TouchableOpacity style={styles.headerIcon} onPress={handleBack}>
            <Ionicons name="arrow-back" size={24} color="#111111" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Personal Info</Text>
          <View style={styles.headerPlaceholder} />
        </View>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={THEME_BROWN} />
          <Text style={styles.loadingText}>Loading profile...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <Stack.Screen options={{ headerShown: false }} />
      <View style={styles.header}>
        <TouchableOpacity style={styles.headerIcon} onPress={handleBack}>
          <Ionicons name="arrow-back" size={24} color="#111111" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Personal Info</Text>
        <View style={styles.headerPlaceholder} />
      </View>
      
      <KeyboardAvoidingView style={styles.keyboardAvoid} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
        <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
          {renderInput('FULL NAME', formData.full_name, 'full_name')}
          {renderInput('EMAIL ADDRESS', formData.email, 'email', false, 'email-address')}
          {renderInput('PHONE NUMBER', formData.phone, 'phone', true, 'phone-pad')}
        </ScrollView>
        
        <View style={styles.footer}>
          <TouchableOpacity 
            style={[styles.saveButton, saving && styles.saveButtonDisabled]} 
            onPress={handleSave} 
            activeOpacity={0.8}
            disabled={saving}
          >
            {saving ? (
              <ActivityIndicator size="small" color="#FFFFFF" />
            ) : (
              <Text style={styles.saveButtonText}>Save Changes</Text>
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
    backgroundColor: THEME_BG,
    paddingTop: Platform.OS === 'android' ? 25 : 0,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 24,
    paddingBottom: 16,
    paddingTop: 8,
  },
  headerIcon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    borderWidth: 1,
    borderColor: '#EEEEEE',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
  },
  headerTitle: {
    fontFamily: 'Poppins_600SemiBold',
    fontSize: 18,
    color: '#111111',
  },
  headerPlaceholder: {
    width: 44,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontFamily: 'Poppins_400Regular',
    fontSize: 14,
    color: '#757575',
  },
  keyboardAvoid: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 24,
    paddingTop: 16,
    paddingBottom: 40,
  },
  inputGroup: {
    marginBottom: 24,
  },
  label: {
    fontFamily: 'Poppins_500Medium',
    fontSize: 12,
    color: '#7A7A7A',
    marginBottom: 8,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#EEEEEE',
    borderRadius: 12,
    backgroundColor: '#FFFFFF',
  },
  inputWrapperDisabled: {
    backgroundColor: '#F5F5F5',
    borderColor: '#EEEEEE',
  },
  input: {
    flex: 1,
    height: 52,
    paddingHorizontal: 16,
    fontFamily: 'Poppins_400Regular',
    fontSize: 16,
    color: '#111111',
  },
  inputTextDisabled: {
    color: '#757575',
  },
  inputIcon: {
    paddingRight: 16,
  },
  footer: {
    padding: 24,
    backgroundColor: THEME_BG,
    borderTopWidth: 1,
    borderTopColor: '#F5F5F5',
  },
  saveButton: {
    backgroundColor: THEME_BROWN,
    height: 52,
    borderRadius: 9999,
    justifyContent: 'center',
    alignItems: 'center',
  },
  saveButtonDisabled: {
    opacity: 0.6,
  },
  saveButtonText: {
    fontFamily: 'Poppins_600SemiBold',
    color: '#FFFFFF',
    fontSize: 16,
  },
});
