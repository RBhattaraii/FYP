import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, ScrollView, KeyboardAvoidingView, Platform, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { colors, typography, spacing, borderRadius } from '../constants/theme';
import Header from '../components/Header';

export default function PersonalInfoScreen() {
  const router = useRouter();
  
  // Mock State
  const [formData, setFormData] = useState({
    firstName: 'Alex',
    lastName: 'Johnson',
    email: 'alex.johnson@example.com',
    phone: '+1 (555) 123-4567',
  });

  const handleSave = () => {
    Alert.alert('Success', 'Personal information updated successfully.');
    router.back();
  };

  const renderInput = (label: string, value: string, key: keyof typeof formData, editable = true, keyboardType: any = 'default') => (
    <View style={styles.inputGroup}>
      <Text style={styles.label}>{label}</Text>
      <View style={[styles.inputWrapper, !editable && styles.inputWrapperDisabled]}>
        <TextInput
          style={[styles.input, !editable && styles.inputTextDisabled]}
          value={value}
          onChangeText={(text) => setFormData(prev => ({ ...prev, [key]: text }))}
          editable={editable}
          keyboardType={keyboardType}
          placeholderTextColor={colors.gray400}
        />
        {!editable && <Ionicons name="lock-closed" size={16} color={colors.gray400} style={styles.inputIcon} />}
      </View>
    </View>
  );

  return (
    <SafeAreaView style={styles.safeArea} edges={['top']}>
      <Header title="Personal Info" showBackBtn={true} onBackPress={() => router.back()} />
      
      <KeyboardAvoidingView 
        style={styles.keyboardAvoid} 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
          
          <View style={styles.formCard}>
            {renderInput('First Name', formData.firstName, 'firstName')}
            {renderInput('Last Name', formData.lastName, 'lastName')}
            {renderInput('Email Address', formData.email, 'email', false, 'email-address')}
            {renderInput('Phone Number', formData.phone, 'phone', true, 'phone-pad')}
            
            <View style={styles.inputGroup}>
              <Text style={styles.label}>Password</Text>
              <TouchableOpacity style={styles.passwordButton} activeOpacity={0.7}>
                <Text style={styles.passwordText}>••••••••</Text>
                <Text style={styles.changePasswordText}>Change</Text>
              </TouchableOpacity>
            </View>
          </View>

        </ScrollView>
        
        <View style={styles.footer}>
          <TouchableOpacity style={styles.saveButton} onPress={handleSave} activeOpacity={0.8}>
            <Text style={styles.saveButtonText}>Save Changes</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: colors.gray50,
  },
  keyboardAvoid: {
    flex: 1,
  },
  scrollContent: {
    padding: spacing.lg,
  },
  formCard: {
    backgroundColor: colors.white,
    borderRadius: borderRadius.medium,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: colors.gray100,
  },
  inputGroup: {
    marginBottom: spacing.lg,
  },
  label: {
    fontSize: typography.fontSize.caption,
    fontWeight: typography.fontWeight.semibold,
    color: colors.gray600,
    marginBottom: spacing.xs,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.gray200,
    borderRadius: borderRadius.small,
    backgroundColor: colors.white,
  },
  inputWrapperDisabled: {
    backgroundColor: colors.gray50,
    borderColor: colors.gray100,
  },
  input: {
    flex: 1,
    height: 48,
    paddingHorizontal: spacing.md,
    fontSize: typography.fontSize.bodyLarge,
    color: colors.gray900,
  },
  inputTextDisabled: {
    color: colors.gray500,
  },
  inputIcon: {
    paddingRight: spacing.md,
  },
  passwordButton: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    height: 48,
    paddingHorizontal: spacing.md,
    borderWidth: 1,
    borderColor: colors.gray200,
    borderRadius: borderRadius.small,
    backgroundColor: colors.white,
  },
  passwordText: {
    fontSize: typography.fontSize.bodyLarge,
    color: colors.gray900,
    letterSpacing: 2,
  },
  changePasswordText: {
    fontSize: typography.fontSize.body,
    fontWeight: typography.fontWeight.medium,
    color: colors.primary,
  },
  footer: {
    padding: spacing.lg,
    backgroundColor: colors.white,
    borderTopWidth: 1,
    borderTopColor: colors.gray100,
  },
  saveButton: {
    backgroundColor: colors.primary,
    height: 48,
    borderRadius: borderRadius.full,
    justifyContent: 'center',
    alignItems: 'center',
  },
  saveButtonText: {
    color: colors.white,
    fontSize: typography.fontSize.bodyLarge,
    fontWeight: typography.fontWeight.bold,
  },
});
